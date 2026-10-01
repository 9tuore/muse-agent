// EventKit transport. Read/write operations only check existing access. The
// sole exception is the explicit "request-full-access" operation, which raises
// the standard macOS Calendar prompt for the current responsible app; it never
// bypasses TCC and reports whatever the user chose.
#import <Foundation/Foundation.h>
#import <EventKit/EventKit.h>

static NSString * const MarkerPrefix = @"Muse synthetic test action:";

static void Emit(NSDictionary *value) {
    NSData *data = [NSJSONSerialization dataWithJSONObject:value options:0 error:NULL];
    if (!data) data = [@"{\"status\":\"BLOCKED\",\"error\":\"json_output_failed\"}" dataUsingEncoding:NSUTF8StringEncoding];
    fwrite(data.bytes, 1, data.length, stdout);
    fputc('\n', stdout);
}

static NSDate *ParseDate(NSString *text) {
    if (![text isKindOfClass:NSString.class] || text.length > 40) return nil;
    NSISO8601DateFormatter *formatter = [NSISO8601DateFormatter new];
    formatter.formatOptions = NSISO8601DateFormatWithInternetDateTime | NSISO8601DateFormatWithFractionalSeconds;
    NSDate *result = [formatter dateFromString:text];
    if (!result) {
        formatter.formatOptions = NSISO8601DateFormatWithInternetDateTime;
        result = [formatter dateFromString:text];
    }
    return result;
}

static NSString *FormatDate(NSDate *date) {
    NSISO8601DateFormatter *formatter = [NSISO8601DateFormatter new];
    formatter.timeZone = [NSTimeZone timeZoneForSecondsFromGMT:0];
    formatter.formatOptions = NSISO8601DateFormatWithInternetDateTime;
    return [formatter stringFromDate:date] ?: @"";
}

static NSDictionary *EventRecord(EKEvent *event) {
    NSString *notes = event.notes ?: @"";
    NSString *marker = [notes hasPrefix:MarkerPrefix] ? [notes substringFromIndex:MarkerPrefix.length] : @"";
    return @{@"event_id": event.eventIdentifier ?: @"", @"calendar_id": event.calendar.calendarIdentifier ?: @"",
             @"title": event.title ?: @"", @"start": FormatDate(event.startDate),
             @"end": FormatDate(event.endDate), @"marker": marker};
}

static NSArray *Events(EKEventStore *store, EKCalendar *calendar, NSDate *start, NSDate *end) {
    NSPredicate *predicate = [store predicateForEventsWithStartDate:start endDate:end calendars:@[calendar]];
    NSArray *events = [store eventsMatchingPredicate:predicate];
    return [events sortedArrayUsingComparator:^NSComparisonResult(EKEvent *a, EKEvent *b) {
        return [a.startDate compare:b.startDate];
    }];
}

static BOOL TestEvent(EKEvent *event, EKCalendar *calendar, NSString *marker) {
    return event && [event.calendar.calendarIdentifier isEqual:calendar.calendarIdentifier] &&
           [event.notes isEqual:[MarkerPrefix stringByAppendingString:marker ?: @""]] &&
           [event.title hasPrefix:@"[Muse Test] "] && event.attendees.count == 0;
}

static NSString *AccessName(EKAuthorizationStatus access) {
    if (access == EKAuthorizationStatusFullAccess) return @"FULL_ACCESS";
    if (access == EKAuthorizationStatusWriteOnly) return @"WRITE_ONLY";
    if (access == EKAuthorizationStatusDenied) return @"DENIED";
    if (access == EKAuthorizationStatusRestricted) return @"RESTRICTED";
    return @"NOT_DETERMINED";
}

int main(int argc, const char *argv[]) {
    @autoreleasepool {
        if (argc != 2) { Emit(@{@"status": @"INVALID_CALL"}); return 2; }
        NSString *operation = [NSString stringWithUTF8String:argv[1]];
        EKAuthorizationStatus access = [EKEventStore authorizationStatusForEntityType:EKEntityTypeEvent];
        if ([operation isEqual:@"status"]) {
            Emit(@{@"status": AccessName(access), @"raw_status": @(access), @"prompt_requested": @NO}); return 0;
        }
        if ([operation isEqual:@"request-full-access"]) {
            // The only operation allowed to raise the system prompt. If full
            // access is already granted it reports that without prompting;
            // otherwise macOS shows the user dialog and this process waits for
            // the user's own choice, then reports the resulting status.
            if (access == EKAuthorizationStatusFullAccess) {
                Emit(@{@"status": @"FULL_ACCESS", @"raw_status": @(access),
                       @"prompt_requested": @NO, @"granted_full_access": @YES}); return 0;
            }
            EKEventStore *requestStore = [EKEventStore new];
            __block BOOL finished = NO;
            void (^completion)(BOOL, NSError *) = ^(BOOL granted, NSError *error) {
                (void)granted; (void)error; finished = YES;
            };
            if (@available(macOS 14.0, *)) {
                [requestStore requestFullAccessToEventsWithCompletion:completion];
            } else {
                [requestStore requestAccessToEntityType:EKEntityTypeEvent completion:completion];
            }
            NSDate *deadline = [NSDate dateWithTimeIntervalSinceNow:120];
            while (!finished && [deadline timeIntervalSinceNow] > 0) {
                [[NSRunLoop currentRunLoop] runMode:NSDefaultRunLoopMode
                                         beforeDate:[NSDate dateWithTimeIntervalSinceNow:0.05]];
            }
            EKAuthorizationStatus after = [EKEventStore authorizationStatusForEntityType:EKEntityTypeEvent];
            Emit(@{@"status": finished ? AccessName(after) : @"TIMEOUT", @"raw_status": @(after),
                   @"prompt_requested": @YES,
                   @"granted_full_access": @(after == EKAuthorizationStatusFullAccess)});
            return 0;
        }
        if (access != EKAuthorizationStatusFullAccess) {
            Emit(@{@"status": @"WAITING_USER_PERMISSION", @"authorization": AccessName(access)}); return 0;
        }
        NSData *input = [[NSFileHandle fileHandleWithStandardInput] readDataToEndOfFile];
        if (input.length > 16384) { Emit(@{@"status": @"INVALID_CALL"}); return 2; }
        NSDictionary *request = [NSJSONSerialization JSONObjectWithData:input options:0 error:NULL];
        if (![request isKindOfClass:NSDictionary.class]) { Emit(@{@"status": @"INVALID_CALL"}); return 2; }
        EKEventStore *store = [EKEventStore new];
        if ([operation isEqual:@"calendars"]) {
            EKCalendar *defaultCalendar = [store defaultCalendarForNewEvents];
            NSMutableArray *rows = [NSMutableArray array];
            for (EKCalendar *calendar in [store calendarsForEntityType:EKEntityTypeEvent]) {
                [rows addObject:@{@"id": calendar.calendarIdentifier ?: @"", @"title": calendar.title ?: @"",
                                  @"writable": @(calendar.allowsContentModifications),
                                  @"default": @(defaultCalendar != nil &&
                                                [defaultCalendar.calendarIdentifier isEqual:calendar.calendarIdentifier])}];
            }
            Emit(@{@"status": @"COMPLETED", @"calendars": rows}); return 0;
        }
        NSString *calendarID = request[@"calendar_id"];
        if (![calendarID isKindOfClass:NSString.class] || calendarID.length < 1 || calendarID.length > 160) {
            Emit(@{@"status": @"BLOCKED", @"error": @"calendar_id_invalid"}); return 0;
        }
        EKCalendar *calendar = [store calendarWithIdentifier:calendarID];
        if (!calendar) {
            Emit(@{@"status": @"BLOCKED", @"error": @"calendar_missing"}); return 0;
        }
        if (![operation isEqual:@"events"] && !calendar.allowsContentModifications) {
            Emit(@{@"status": @"BLOCKED", @"error": @"calendar_read_only"}); return 0;
        }
        if ([operation isEqual:@"create-event"]) {
            // A real, user-approved event: any bounded title is allowed. The app
            // owns the confirmation; this transport only writes and reads back.
            NSDate *start = ParseDate(request[@"start"]);
            NSDate *end = ParseDate(request[@"end"]);
            NSString *title = request[@"title"];
            NSString *timezoneName = request[@"timezone"];
            NSString *notes = request[@"notes"];
            NSTimeZone *zone = [timezoneName isKindOfClass:NSString.class]
                ? [NSTimeZone timeZoneWithName:timezoneName] : nil;
            if (!start || !end || [start compare:end] != NSOrderedAscending ||
                [end timeIntervalSinceDate:start] > 31 * 86400 ||
                ![title isKindOfClass:NSString.class] || title.length < 1 || title.length > 160 ||
                !zone || (notes && (![notes isKindOfClass:NSString.class] || notes.length > 400))) {
                Emit(@{@"status": @"BLOCKED", @"error": @"user_event_invalid"}); return 0;
            }
            EKEvent *event = [EKEvent eventWithEventStore:store];
            event.calendar = calendar;
            event.title = title;
            event.startDate = start;
            event.endDate = end;
            event.timeZone = zone;
            if ([notes isKindOfClass:NSString.class] && notes.length > 0) event.notes = notes;
            NSError *error = nil;
            if (![store saveEvent:event span:EKSpanThisEvent error:&error]) {
                Emit(@{@"status": @"RESULT_UNCERTAIN", @"error_code": @(error.code)}); return 0;
            }
            EKEvent *readback = [store eventWithIdentifier:event.eventIdentifier];
            if (!readback || ![readback.title isEqual:title] ||
                ![readback.startDate isEqualToDate:start] || ![readback.endDate isEqualToDate:end] ||
                ![readback.calendar.calendarIdentifier isEqual:calendar.calendarIdentifier]) {
                Emit(@{@"status": @"RESULT_UNCERTAIN", @"error": @"event_readback_mismatch"}); return 0;
            }
            Emit(@{@"status": @"COMPLETED", @"event": EventRecord(readback), @"readback_matches": @YES}); return 0;
        }
        if ([operation isEqual:@"events"] || [operation isEqual:@"create"] || [operation isEqual:@"update"]) {
            NSDate *start = ParseDate(request[@"start"]);
            NSDate *end = ParseDate(request[@"end"]);
            if (!start || !end || [start compare:end] != NSOrderedAscending ||
                [end timeIntervalSinceDate:start] > 31 * 86400) {
                Emit(@{@"status": @"BLOCKED", @"error": @"calendar_window_invalid"}); return 0;
            }
            if ([operation isEqual:@"events"]) {
                NSArray *events = Events(store, calendar, start, end);
                if (events.count > 100) { Emit(@{@"status": @"BLOCKED", @"error": @"too_many_events"}); return 0; }
                NSMutableArray *rows = [NSMutableArray array];
                for (EKEvent *event in events) [rows addObject:EventRecord(event)];
                Emit(@{@"status": @"COMPLETED", @"events": rows}); return 0;
            }
            NSString *title = request[@"title"];
            NSString *marker = request[@"marker"];
            NSString *timezoneName = request[@"timezone"];
            NSTimeZone *zone = [timezoneName isKindOfClass:NSString.class] ? [NSTimeZone timeZoneWithName:timezoneName] : nil;
            if (![title isKindOfClass:NSString.class] || ![title hasPrefix:@"[Muse Test] "] || title.length > 160 ||
                ![marker isKindOfClass:NSString.class] || marker.length < 1 || marker.length > 100 || !zone) {
                Emit(@{@"status": @"BLOCKED", @"error": @"synthetic_event_invalid"}); return 0;
            }
            EKEvent *event = nil;
            if ([operation isEqual:@"create"]) {
                for (EKEvent *existing in Events(store, calendar, start, end)) {
                    if (TestEvent(existing, calendar, marker)) {
                        Emit(@{@"status": @"COMPLETED", @"event": EventRecord(existing), @"replayed": @YES}); return 0;
                    }
                    Emit(@{@"status": @"CONFLICT", @"event_id": existing.eventIdentifier ?: @""}); return 0;
                }
                event = [EKEvent eventWithEventStore:store];
                event.calendar = calendar;
                event.notes = [MarkerPrefix stringByAppendingString:marker];
            } else {
                NSString *eventID = request[@"event_id"];
                event = [eventID isKindOfClass:NSString.class] ? [store eventWithIdentifier:eventID] : nil;
                if (!TestEvent(event, calendar, marker)) {
                    Emit(@{@"status": @"BLOCKED", @"error": @"test_event_not_found"}); return 0;
                }
            }
            event.title = title;
            event.startDate = start;
            event.endDate = end;
            event.timeZone = zone;
            NSError *error = nil;
            if (![store saveEvent:event span:EKSpanThisEvent error:&error]) {
                Emit(@{@"status": @"RESULT_UNCERTAIN", @"error_code": @(error.code)}); return 0;
            }
            EKEvent *readback = [store eventWithIdentifier:event.eventIdentifier];
            if (!TestEvent(readback, calendar, marker) || ![readback.title isEqual:title] ||
                ![readback.startDate isEqualToDate:start] || ![readback.endDate isEqualToDate:end]) {
                Emit(@{@"status": @"RESULT_UNCERTAIN", @"error": @"event_readback_mismatch"}); return 0;
            }
            Emit(@{@"status": @"COMPLETED", @"event": EventRecord(readback), @"readback_matches": @YES}); return 0;
        }
        if ([operation isEqual:@"delete"]) {
            NSString *eventID = request[@"event_id"];
            NSString *marker = request[@"marker"];
            EKEvent *event = [eventID isKindOfClass:NSString.class] ? [store eventWithIdentifier:eventID] : nil;
            if (![marker isKindOfClass:NSString.class] || !TestEvent(event, calendar, marker)) {
                Emit(@{@"status": @"BLOCKED", @"error": @"test_event_not_found"}); return 0;
            }
            NSError *error = nil;
            if (![store removeEvent:event span:EKSpanThisEvent error:&error]) {
                Emit(@{@"status": @"RESULT_UNCERTAIN", @"error_code": @(error.code)}); return 0;
            }
            Emit(@{@"status": [store eventWithIdentifier:eventID] ? @"RESULT_UNCERTAIN" : @"COMPLETED",
                   @"event_id": eventID, @"readback_absent": @([store eventWithIdentifier:eventID] == nil)}); return 0;
        }
        Emit(@{@"status": @"INVALID_CALL"}); return 2;
    }
}
