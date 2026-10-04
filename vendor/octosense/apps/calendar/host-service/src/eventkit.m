#import <Foundation/Foundation.h>
#import <EventKit/EventKit.h>
#include <math.h>
#include <string.h>

static NSString *text(NSDictionary *object, NSString *key) {
    id value = object[key];
    return [value isKindOfClass:[NSString class]] ? value : nil;
}

static NSDictionary *failure(NSString *message) {
    return @{ @"error": message ?: @"Calendar operation failed" };
}

static NSString *permission(void) {
    EKAuthorizationStatus status = [EKEventStore authorizationStatusForEntityType:EKEntityTypeEvent];
    switch (status) {
        case EKAuthorizationStatusNotDetermined: return @"not_determined";
        case EKAuthorizationStatusRestricted: return @"restricted";
        case EKAuthorizationStatusDenied: return @"denied";
        case EKAuthorizationStatusFullAccess: return @"full_access";
        case EKAuthorizationStatusWriteOnly: return @"write_only";
    }
    return @"unavailable";
}

static NSISO8601DateFormatter *formatter(void) {
    NSISO8601DateFormatter *fmt = [[NSISO8601DateFormatter alloc] init];
    fmt.formatOptions = NSISO8601DateFormatWithInternetDateTime;
    fmt.timeZone = [NSTimeZone timeZoneForSecondsFromGMT:0];
    return fmt;
}

static NSDate *parseDate(NSString *value) {
    if (!value) return nil;
    NSISO8601DateFormatter *fmt = formatter();
    NSDate *date = [fmt dateFromString:value];
    if (date) return date;
    fmt.formatOptions = NSISO8601DateFormatWithInternetDateTime | NSISO8601DateFormatWithFractionalSeconds;
    return [fmt dateFromString:value];
}

static NSDictionary *eventValue(EKEvent *event) {
    NSISO8601DateFormatter *fmt = formatter();
    NSString *start = event.startDate ? [fmt stringFromDate:event.startDate] : @"";
    NSString *end = event.endDate ? [fmt stringFromDate:event.endDate] : @"";
    return @{
        @"id": event.eventIdentifier ?: @"",
        @"calendar_id": event.calendar.calendarIdentifier ?: @"",
        @"title": event.title ?: @"",
        @"start": start,
        @"end": end,
        @"time_zone": event.timeZone.name ?: @"",
        @"location": event.location ?: @"",
        @"last_modified": @([event.lastModifiedDate timeIntervalSince1970]),
        @"all_day": @(event.allDay),
        @"availability": @((NSInteger)event.availability),
        @"recurring": @(event.hasRecurrenceRules),
    };
}

static EKCalendar *calendar(EKEventStore *store, NSDictionary *args) {
    NSString *identifier = text(args, @"calendar_id");
    return identifier ? [store calendarWithIdentifier:identifier] : nil;
}

static EKEvent *event(EKEventStore *store, NSDictionary *args) {
    NSString *identifier = text(args, @"event_id");
    EKCalendar *wanted = calendar(store, args);
    EKEvent *found = identifier && wanted ? [store eventWithIdentifier:identifier] : nil;
    if (found && ![found.calendar.calendarIdentifier isEqualToString:wanted.calendarIdentifier]) return nil;
    return found;
}

static BOOL owned(EKEvent *event, NSString *owner) {
    NSURL *url = event.URL;
    return owner && [url.scheme isEqualToString:@"muse-calendar"] && [url.host isEqualToString:owner];
}

static BOOL mayModify(EKEvent *event) {
    return event && event.calendar.allowsContentModifications && event.recurrenceRules.count == 0 &&
           event.attendees.count == 0 && !event.isDetached;
}

static NSDictionary *perform(NSDictionary *request) {
    NSString *method = text(request, @"method");
    NSDictionary *args = request[@"args"];
    if (![args isKindOfClass:[NSDictionary class]]) args = @{};
    if ([method isEqualToString:@"status"]) {
        EKEventStore *store = [[EKEventStore alloc] init];
        NSString *access = permission();
        NSMutableArray *calendars = [NSMutableArray array];
        if ([access isEqualToString:@"full_access"]) {
            for (EKCalendar *item in [store calendarsForEntityType:EKEntityTypeEvent]) {
                [calendars addObject:@{ @"id": item.calendarIdentifier ?: @"",
                                        @"title": item.title ?: @"",
                                        @"writable": @(item.allowsContentModifications) }];
            }
        }
        return @{ @"result": @{ @"permission": access, @"calendars": calendars } };
    }

    EKEventStore *store = [[EKEventStore alloc] init];
    if ([method isEqualToString:@"request_access"]) {
        dispatch_semaphore_t done = dispatch_semaphore_create(0);
        __block NSString *message = nil;
        if (@available(macOS 14.0, *)) {
            [store requestFullAccessToEventsWithCompletion:^(BOOL granted, NSError *error) {
                (void)granted;
                if (error) message = error.localizedDescription;
                dispatch_semaphore_signal(done);
            }];
        } else {
            return failure(@"Full calendar access requires macOS 14 or newer in this build");
        }
        if (dispatch_semaphore_wait(done, dispatch_time(DISPATCH_TIME_NOW, 120 * NSEC_PER_SEC)) != 0)
            return failure(@"Calendar permission request timed out; check the system prompt");
        if (message) return failure(message);
        [store reset];
        return @{ @"result": @{ @"permission": permission() } };
    }

    if (![permission() isEqualToString:@"full_access"])
        return failure(@"Full calendar access is required; write-only is insufficient for readback");

    EKCalendar *target = calendar(store, args);
    if (!target) return failure(@"The selected system calendar is unavailable");

    if ([method isEqualToString:@"list"]) {
        NSDate *start = parseDate(text(args, @"start"));
        NSDate *end = parseDate(text(args, @"end"));
        if (!start || !end || [end timeIntervalSinceDate:start] <= 0 || [end timeIntervalSinceDate:start] > 31 * 86400)
            return failure(@"Invalid calendar date range");
        NSUInteger limit = [args[@"limit"] respondsToSelector:@selector(unsignedIntegerValue)] ? [args[@"limit"] unsignedIntegerValue] : 50;
        if (limit == 0 || limit > 100) return failure(@"Calendar limit must be 1-100");
        NSPredicate *predicate = [store predicateForEventsWithStartDate:start endDate:end calendars:@[target]];
        NSArray<EKEvent *> *found = [store eventsMatchingPredicate:predicate];
        NSMutableArray *events = [NSMutableArray array];
        for (EKEvent *item in found) {
            if (events.count == limit) break;
            [events addObject:eventValue(item)];
        }
        return @{ @"result": @{ @"calendar_id": target.calendarIdentifier,
                                  @"start": text(args, @"start"), @"end": text(args, @"end"),
                                  @"events": events, @"truncated": @(found.count > limit) } };
    }

    if ([method isEqualToString:@"get"]) {
        EKEvent *found = event(store, args);
        return found ? @{ @"result": @{ @"found": @YES, @"event": eventValue(found) } }
                     : @{ @"result": @{ @"found": @NO } };
    }

    NSString *owner = text(args, @"owner");
    NSString *requestID = text(args, @"request_id");
    if (owner.length != 64 || requestID.length < 8) return failure(@"Missing host action identity");
    if (!target.allowsContentModifications) return failure(@"The selected calendar is read-only");

    if ([method isEqualToString:@"create"]) {
        NSDate *start = parseDate(text(args, @"start"));
        NSDate *end = parseDate(text(args, @"end"));
        NSTimeZone *zone = [NSTimeZone timeZoneWithName:text(args, @"time_zone")];
        if (!start || !end || [end timeIntervalSinceDate:start] <= 0 || !zone)
            return failure(@"Invalid event time or time zone");
        EKEvent *created = [EKEvent eventWithEventStore:store];
        created.calendar = target;
        created.title = text(args, @"title");
        created.startDate = start;
        created.endDate = end;
        created.timeZone = zone;
        created.location = text(args, @"location") ?: @"";
        created.URL = [NSURL URLWithString:[NSString stringWithFormat:@"muse-calendar://%@/%@", owner, requestID]];
        NSError *error = nil;
        if (![store saveEvent:created span:EKSpanThisEvent error:&error])
            return failure(error.localizedDescription ?: @"EventKit could not create the event");
        return @{ @"result": eventValue(created) };
    }

    if ([method isEqualToString:@"update"] || [method isEqualToString:@"delete"]) {
        EKEvent *found = event(store, args);
        if (!mayModify(found) || !owned(found, owner))
            return failure(@"Only a nonrepeating, attendee-free event created by this app may be changed");
        NSNumber *expected = args[@"expected_last_modified"];
        if (![expected isKindOfClass:[NSNumber class]] || fabs([found.lastModifiedDate timeIntervalSince1970] - expected.doubleValue) > 0.001)
            return failure(@"The system event changed; review it again");
        NSError *error = nil;
        if ([method isEqualToString:@"delete"]) {
            if (![store removeEvent:found span:EKSpanThisEvent error:&error])
                return failure(error.localizedDescription ?: @"EventKit could not delete the event");
            return @{ @"result": @{ @"deleted": @YES } };
        }
        NSDictionary *changes = args[@"changes"];
        if (![changes isKindOfClass:[NSDictionary class]]) return failure(@"Invalid event changes");
        if (changes[@"title"]) found.title = text(changes, @"title");
        if (changes[@"start"]) found.startDate = parseDate(text(changes, @"start"));
        if (changes[@"end"]) found.endDate = parseDate(text(changes, @"end"));
        if (changes[@"time_zone"]) found.timeZone = [NSTimeZone timeZoneWithName:text(changes, @"time_zone")];
        if (changes[@"location"]) found.location = text(changes, @"location");
        if (!found.startDate || !found.endDate || !found.timeZone || [found.endDate timeIntervalSinceDate:found.startDate] <= 0)
            return failure(@"Invalid updated event time or time zone");
        if (![store saveEvent:found span:EKSpanThisEvent error:&error])
            return failure(error.localizedDescription ?: @"EventKit could not update the event");
        return @{ @"result": eventValue(found) };
    }
    return failure(@"Unknown calendar method");
}

char *muse_calendar_call(const char *request) {
    @autoreleasepool {
        NSString *input = request ? [NSString stringWithUTF8String:request] : nil;
        NSData *data = [input dataUsingEncoding:NSUTF8StringEncoding];
        NSDictionary *parsed = data ? [NSJSONSerialization JSONObjectWithData:data options:0 error:nil] : nil;
        NSDictionary *result = [parsed isKindOfClass:[NSDictionary class]] ? perform(parsed) : failure(@"Invalid calendar request");
        NSData *encoded = [NSJSONSerialization dataWithJSONObject:result options:0 error:nil];
        return encoded ? strdup([[NSString alloc] initWithData:encoded encoding:NSUTF8StringEncoding].UTF8String) : strdup("{\"error\":\"Calendar response encoding failed\"}");
    }
}

void muse_calendar_free(char *result) {
    free(result);
}
