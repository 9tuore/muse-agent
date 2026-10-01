// Bounded Accessibility probe/action helper. No prompt is requested here.
#import <AppKit/AppKit.h>
#import <ApplicationServices/ApplicationServices.h>
#include <string.h>

static NSString *Text(AXUIElementRef element, CFStringRef attribute) {
    CFTypeRef value = NULL;
    if (AXUIElementCopyAttributeValue(element, attribute, &value) != kAXErrorSuccess || !value) return @"";
    NSString *result = @"";
    if (CFGetTypeID(value) == CFStringGetTypeID()) result = [(__bridge NSString *)value copy];
    CFRelease(value);
    return result;
}

static NSString *DocumentURL(AXUIElementRef window) {
    CFTypeRef value = NULL;
    NSString *url = @"";
    if (AXUIElementCopyAttributeValue(window, kAXDocumentAttribute, &value) == kAXErrorSuccess && value) {
        if (CFGetTypeID(value) == CFStringGetTypeID()) url = [(__bridge NSString *)value copy];
        else if (CFGetTypeID(value) == CFURLGetTypeID())
            url = [(__bridge NSString *)CFURLGetString((CFURLRef)value) copy];
        CFRelease(value);
    }
    return url;
}

static NSArray *Children(AXUIElementRef element) {
    CFTypeRef value = NULL;
    if (AXUIElementCopyAttributeValue(element, kAXChildrenAttribute, &value) != kAXErrorSuccess || !value) return @[];
    NSArray *result = CFGetTypeID(value) == CFArrayGetTypeID() ? [(__bridge NSArray *)value copy] : @[];
    CFRelease(value);
    return result;
}

static BOOL Enabled(AXUIElementRef element, BOOL textSettable) {
    CFTypeRef value = NULL;
    if (AXUIElementCopyAttributeValue(element, kAXEnabledAttribute, &value) != kAXErrorSuccess || !value)
        return textSettable;
    BOOL enabled = CFGetTypeID(value) == CFBooleanGetTypeID() && CFBooleanGetValue(value);
    CFRelease(value);
    return enabled;
}

static NSString *Name(AXUIElementRef element) {
    for (NSString *key in @[(__bridge NSString *)kAXTitleAttribute,
                              (__bridge NSString *)kAXDescriptionAttribute,
                              (__bridge NSString *)kAXHelpAttribute,
                              (__bridge NSString *)kAXIdentifierAttribute]) {
        NSString *value = Text(element, (__bridge CFStringRef)key);
        if (value.length) return [value substringToIndex:MIN(value.length, 120)];
    }
    return @"";
}

static BOOL Sensitive(NSString *name) {
    NSString *lower = name.lowercaseString;
    for (NSString *word in @[@"password", @"passcode", @"密码", @"验证码", @"payment", @"credit card", @"keychain", @"game", @"steam"]) {
        if ([lower containsString:word]) return YES;
    }
    return NO;
}

static void Walk(AXUIElementRef element, NSString *path, NSString *windowTitle, NSUInteger depth,
                 NSMutableArray *rows, NSDictionary *selector, AXUIElementRef *selected) {
    if (depth > 10 || rows.count >= 400) return;
    NSString *role = Text(element, kAXRoleAttribute);
    NSString *name = Name(element);
    if ([path hasPrefix:@"menu"] && [role isEqual:@"AXMenuItem"] &&
        ![@[@"save", @"存储", @"保存", @"open", @"打开", @"new", @"新建",
            @"find", @"查找", @"search", @"搜索", @"next", @"下一页"] containsObject:name.lowercaseString]) return;
    NSString *subrole = Text(element, kAXSubroleAttribute);
    BOOL safe = [@[@"AXButton", @"AXTextField", @"AXTextArea", @"AXSearchField", @"AXMenuItem"] containsObject:role];
    if (safe && !Sensitive(name) && !Sensitive(subrole) && ![subrole.lowercaseString containsString:@"secure"]) {
        CFArrayRef actions = NULL;
        NSMutableArray *available = [NSMutableArray array];
        if (AXUIElementCopyActionNames(element, &actions) == kAXErrorSuccess && actions) {
            if ([(__bridge NSArray *)actions containsObject:(__bridge NSString *)kAXPressAction]) [available addObject:@"press"];
            CFRelease(actions);
        }
        Boolean settable = false;
        if ([@[@"AXTextField", @"AXTextArea", @"AXSearchField"] containsObject:role] &&
            AXUIElementIsAttributeSettable(element, kAXValueAttribute, &settable) == kAXErrorSuccess && settable)
            [available addObject:@"set_value"];
        NSMutableDictionary *row = [@{@"role": role, @"name": name, @"path": path,
                                       @"window_title": windowTitle,
                                       @"enabled": @(Enabled(element, [available containsObject:@"set_value"])),
                                       @"actions": available} mutableCopy];
        if ([available containsObject:@"set_value"]) {
            NSString *value = Text(element, kAXValueAttribute);
            row[@"value"] = [value substringToIndex:MIN(value.length, 8192)];
        }
        [rows addObject:row];
        if (selector && !*selected && [selector[@"role"] isEqual:role] &&
            [selector[@"name"] isEqual:name] &&
            (!selector[@"path"] || [selector[@"path"] isEqual:path]) &&
            [selector[@"window_title"] isEqual:windowTitle]) {
            *selected = element;
            CFRetain(element);
        }
    }
    NSArray *children = Children(element);
    for (NSUInteger index = 0; index < children.count && rows.count < 400; index++) {
        Walk((__bridge AXUIElementRef)children[index], [path stringByAppendingFormat:@"/%lu", (unsigned long)index],
             windowTitle, depth + 1, rows, selector, selected);
    }
}

static void Emit(NSDictionary *result) {
    NSData *data = [NSJSONSerialization dataWithJSONObject:result options:0 error:NULL];
    if (!data) data = [@"{\"status\":\"ERROR\",\"error\":\"json_encoding_failed\"}" dataUsingEncoding:NSUTF8StringEncoding];
    fwrite(data.bytes, 1, data.length, stdout);
    fputc('\n', stdout);
}

int main(int argc, const char *argv[]) {
    @autoreleasepool {
        if (argc == 2 && strcmp(argv[1], "status") == 0) {
            BOOL trusted = AXIsProcessTrusted();
            Emit(@{@"status": trusted ? @"TRUSTED" : @"BLOCKED_PERMISSION",
                   @"permission": @"accessibility", @"trusted": @(trusted),
                   @"prompt_requested": @NO}); return 0;
        }
        if (argc < 3 || ![@[@"snapshot", @"act", @"document", @"focus"] containsObject:[NSString stringWithUTF8String:argv[1]]]) {
            Emit(@{@"status": @"INVALID_CALL"}); return 2;
        }
        NSString *command = [NSString stringWithUTF8String:argv[1]];
        NSString *bundle = [NSString stringWithUTF8String:argv[2]];
        NSString *targetTitle = ([command isEqual:@"snapshot"] && argc == 4) ||
                                ([command isEqual:@"document"] && argc == 4) ||
                                ([command isEqual:@"focus"] && argc == 5)
                                ? [NSString stringWithUTF8String:argv[3]] : nil;
        if (([command isEqual:@"snapshot"] && argc != 3 && argc != 4) ||
            ([command isEqual:@"document"] && argc != 4) ||
            ([command isEqual:@"focus"] && argc != 5) ||
            (targetTitle && (targetTitle.length < 1 || targetTitle.length > 240))) {
            Emit(@{@"status": @"INVALID_CALL"}); return 2;
        }
        if (Sensitive(bundle) || bundle.length > 160 || ![bundle containsString:@"."]) {
            Emit(@{@"status": @"BLOCKED", @"error": @"sensitive_or_invalid_bundle"}); return 0;
        }
        if (!AXIsProcessTrusted()) {
            Emit(@{@"status": @"BLOCKED_PERMISSION", @"permission": @"accessibility", @"trusted": @NO}); return 0;
        }
        NSArray<NSRunningApplication *> *apps = [NSRunningApplication runningApplicationsWithBundleIdentifier:bundle];
        if (apps.count != 1) {
            Emit(@{@"status": @"BLOCKED_TARGET", @"error": @"application_not_running_or_ambiguous", @"count": @(apps.count)}); return 0;
        }
        AXUIElementRef app = AXUIElementCreateApplication(apps.firstObject.processIdentifier);
        CFTypeRef windowsValue = NULL;
        AXError error = AXUIElementCopyAttributeValue(app, kAXWindowsAttribute, &windowsValue);
        if (error != kAXErrorSuccess || !windowsValue || CFGetTypeID(windowsValue) != CFArrayGetTypeID()) {
            if (windowsValue) CFRelease(windowsValue);
            CFRelease(app);
            Emit(@{@"status": @"BLOCKED_AX_TARGET", @"ax_error": @(error)}); return 0;
        }
        NSArray *windows = [(__bridge NSArray *)windowsValue copy];
        CFRelease(windowsValue);
        if ([command isEqual:@"document"] || [command isEqual:@"focus"]) {
            NSUInteger matches = 0;
            NSString *documentURL = @"";
            AXUIElementRef matchedWindow = NULL;
            for (id candidate in windows) {
                AXUIElementRef window = (__bridge AXUIElementRef)candidate;
                if (![Text(window, kAXTitleAttribute) isEqual:targetTitle]) continue;
                matches++;
                documentURL = DocumentURL(window);
                matchedWindow = window;
            }
            if (matches != 1 || ![documentURL hasPrefix:@"file://"]) {
                CFRelease(app);
                Emit(@{@"status": @"BLOCKED_AX_DOCUMENT", @"matches": @(matches)}); return 0;
            }
            if ([command isEqual:@"focus"]) {
                NSString *expectedURL = [NSString stringWithUTF8String:argv[4]];
                if (![bundle isEqual:@"com.apple.TextEdit"] || expectedURL.length > 1024 ||
                    ![expectedURL isEqual:documentURL]) {
                    CFRelease(app); Emit(@{@"status": @"BLOCKED_AX_DOCUMENT", @"error": @"document_changed"}); return 0;
                }
                AXError mainError = AXUIElementSetAttributeValue(matchedWindow, kAXMainAttribute, kCFBooleanTrue);
                BOOL activated = [apps.firstObject activateWithOptions:0];
                AXError raiseError = AXUIElementPerformAction(matchedWindow, kAXRaiseAction);
                BOOL focused = NO;
                NSString *observedTitle = @"";
                NSString *observedDocument = @"";
                BOOL observedAXFrontmost = NO;
                for (NSUInteger attempt = 0; attempt < 15 && activated; attempt++) {
                    CFTypeRef frontValue = NULL;
                    if (AXUIElementCopyAttributeValue(app, kAXFrontmostAttribute, &frontValue) == kAXErrorSuccess &&
                        frontValue && CFGetTypeID(frontValue) == CFBooleanGetTypeID())
                        observedAXFrontmost = CFBooleanGetValue(frontValue);
                    if (frontValue) CFRelease(frontValue);
                    CFTypeRef focusedValue = NULL;
                    if (AXUIElementCopyAttributeValue(app, kAXFocusedWindowAttribute, &focusedValue) == kAXErrorSuccess &&
                        focusedValue) {
                        AXUIElementRef window = (AXUIElementRef)focusedValue;
                        observedTitle = Text(window, kAXTitleAttribute);
                        observedDocument = DocumentURL(window);
                        focused = observedAXFrontmost && [observedTitle isEqual:targetTitle] &&
                                  [observedDocument isEqual:expectedURL];
                    }
                    if (focusedValue) CFRelease(focusedValue);
                    if (focused) break;
                    [NSThread sleepForTimeInterval:0.1];
                }
                CFRelease(app);
                Emit(@{@"status": focused ? @"COMPLETED" : @"BLOCKED_FOCUS",
                       @"window_title": targetTitle, @"document_url": documentURL,
                       @"activated": @(activated), @"main_error": @(mainError),
                       @"raise_error": @(raiseError), @"ax_frontmost": @(observedAXFrontmost),
                       @"observed_title": observedTitle,
                       @"observed_document": observedDocument}); return 0;
            }
            CFRelease(app);
            Emit(@{@"status": @"COMPLETED", @"window_title": targetTitle,
                   @"document_url": documentURL}); return 0;
        }
        NSMutableArray *rows = [NSMutableArray array];
        NSDictionary *selector = nil;
        NSString *action = nil;
        NSString *input = nil;
        if ([command isEqual:@"act"]) {
            if (argc != 6) { CFRelease(app); Emit(@{@"status": @"INVALID_CALL"}); return 2; }
            NSData *data = [[NSString stringWithUTF8String:argv[3]] dataUsingEncoding:NSUTF8StringEncoding];
            selector = [NSJSONSerialization JSONObjectWithData:data options:0 error:NULL];
            action = [NSString stringWithUTF8String:argv[4]];
            input = [NSString stringWithUTF8String:argv[5]];
            if (![selector isKindOfClass:NSDictionary.class] || ![@[@"press", @"set_value"] containsObject:action] ||
                input.length > 8192) { CFRelease(app); Emit(@{@"status": @"INVALID_CALL"}); return 2; }
            targetTitle = selector[@"window_title"];
            if (![targetTitle isKindOfClass:NSString.class] || targetTitle.length < 1 || targetTitle.length > 240) {
                CFRelease(app); Emit(@{@"status": @"INVALID_CALL"}); return 2;
            }
        }
        AXUIElementRef selected = NULL;
        for (NSUInteger index = 0; index < windows.count && rows.count < 400; index++) {
            AXUIElementRef window = (__bridge AXUIElementRef)windows[index];
            if (targetTitle && ![Text(window, kAXTitleAttribute) isEqual:targetTitle]) continue;
            Walk(window, [NSString stringWithFormat:@"w%lu", (unsigned long)index],
                 Text(window, kAXTitleAttribute), 0, rows, selector, &selected);
        }
        CFTypeRef menuValue = NULL;
        if (AXUIElementCopyAttributeValue(app, kAXMenuBarAttribute, &menuValue) == kAXErrorSuccess && menuValue) {
            CFTypeRef focusedValue = NULL;
            NSString *focusedTitle = @"";
            if (AXUIElementCopyAttributeValue(app, kAXFocusedWindowAttribute, &focusedValue) == kAXErrorSuccess && focusedValue) {
                focusedTitle = Text((AXUIElementRef)focusedValue, kAXTitleAttribute);
                CFRelease(focusedValue);
            }
            if (!targetTitle || [focusedTitle isEqual:targetTitle])
                Walk((AXUIElementRef)menuValue, @"menu", focusedTitle, 0, rows, selector, &selected);
            CFRelease(menuValue);
        }
        CFRelease(app);
        if ([command isEqual:@"snapshot"]) {
            NSDateFormatter *formatter = [NSDateFormatter new];
            formatter.locale = [NSLocale localeWithLocaleIdentifier:@"en_US_POSIX"];
            formatter.timeZone = [NSTimeZone timeZoneForSecondsFromGMT:0];
            formatter.dateFormat = @"yyyy-MM-dd'T'HH:mm:ss'Z'";
            Emit(@{@"status": @"COMPLETED", @"bundle_id": bundle,
                   @"observed_at": [formatter stringFromDate:[NSDate date]], @"elements": rows}); return 0;
        }
        if (!selected) { Emit(@{@"status": @"BLOCKED", @"error": @"selector_not_found"}); return 0; }
        NSUInteger matches = 0;
        for (NSDictionary *row in rows) {
            if ([row[@"role"] isEqual:selector[@"role"]] && [row[@"name"] isEqual:selector[@"name"]] &&
                [row[@"window_title"] isEqual:selector[@"window_title"]] &&
                (!selector[@"path"] || [row[@"path"] isEqual:selector[@"path"]])) matches++;
        }
        Boolean settable = false;
        BOOL textSettable = [action isEqual:@"set_value"] &&
            AXUIElementIsAttributeSettable(selected, kAXValueAttribute, &settable) == kAXErrorSuccess && settable;
        if (matches != 1 || !Enabled(selected, textSettable)) {
            CFRelease(selected); Emit(@{@"status": @"BLOCKED", @"error": @"selector_ambiguous_or_disabled"}); return 0;
        }
        AXError actionError = [action isEqual:@"press"] ? AXUIElementPerformAction(selected, kAXPressAction) :
            AXUIElementSetAttributeValue(selected, kAXValueAttribute, (__bridge CFTypeRef)input);
        CFRelease(selected);
        Emit(@{@"status": actionError == kAXErrorSuccess ? @"COMPLETED" : @"BLOCKED",
               @"ax_error": @(actionError)});
        return 0;
    }
}
