// Emits only selected NSWorkspace app activation events; no screen or notification access.
#import <AppKit/AppKit.h>

static NSSet<NSString *> *AllowedBundles;

static void Emit(NSString *kind, NSRunningApplication *app) {
    NSString *bundle = app.bundleIdentifier ?: @"";
    if (![AllowedBundles containsObject:bundle]) return;
    NSDateFormatter *formatter = [NSDateFormatter new];
    formatter.locale = [NSLocale localeWithLocaleIdentifier:@"en_US_POSIX"];
    formatter.timeZone = [NSTimeZone timeZoneForSecondsFromGMT:0];
    formatter.dateFormat = @"yyyy-MM-dd'T'HH:mm:ss.SSS'Z'";
    NSDictionary *record = @{@"status": @"EVENT", @"type": kind, @"bundle_id": bundle,
                             @"observed_at": [formatter stringFromDate:[NSDate date]],
                             @"source": @"NSWorkspace"};
    NSData *data = [NSJSONSerialization dataWithJSONObject:record options:0 error:NULL];
    if (!data) return;
    fwrite(data.bytes, 1, data.length, stdout);
    fputc('\n', stdout);
    fflush(stdout);
}

@interface ActivityObserver : NSObject
@end

@implementation ActivityObserver
- (void)activated:(NSNotification *)notification {
    NSRunningApplication *app = notification.userInfo[NSWorkspaceApplicationKey];
    if ([app isKindOfClass:NSRunningApplication.class]) Emit(@"frontmost_changed", app);
}
@end

int main(int argc, const char *argv[]) {
    @autoreleasepool {
        if (argc != 2) return 2;
        NSData *raw = [[NSString stringWithUTF8String:argv[1]] dataUsingEncoding:NSUTF8StringEncoding];
        if (raw.length > 2048) return 2;
        NSArray *allowed = [NSJSONSerialization JSONObjectWithData:raw options:0 error:NULL];
        if (![allowed isKindOfClass:NSArray.class] || allowed.count < 1 || allowed.count > 16) return 2;
        NSCharacterSet *valid = [NSCharacterSet characterSetWithCharactersInString:@"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-"];
        for (id item in allowed) {
            if (![item isKindOfClass:NSString.class] || [item length] > 160 ||
                ![item containsString:@"."] ||
                [item rangeOfCharacterFromSet:valid.invertedSet].location != NSNotFound) return 2;
        }
        AllowedBundles = [NSSet setWithArray:allowed];
        NSWorkspace *workspace = NSWorkspace.sharedWorkspace;
        ActivityObserver *observer = [ActivityObserver new];
        [workspace.notificationCenter addObserver:observer selector:@selector(activated:)
                                            name:NSWorkspaceDidActivateApplicationNotification object:nil];
        Emit(@"frontmost_snapshot", workspace.frontmostApplication);
        [[NSRunLoop currentRunLoop] run];
        [workspace.notificationCenter removeObserver:observer];
    }
    return 0;
}
