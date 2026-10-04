#import <AppKit/AppKit.h>
#include <sys/file.h>
#include <fcntl.h>
#include <signal.h>
#include <unistd.h>
#include <string.h>

static volatile sig_atomic_t stopping = 0;
static void stop(int unused) { stopping = 1; }
static NSString *join(NSString *base, NSString *path) {
    return [base stringByAppendingPathComponent:path];
}
static void fail(NSString *message) {
    fprintf(stderr, "%s\n", message.UTF8String);
    NSAlert *alert = [NSAlert new];
    alert.messageText = @"Muse 启动未完成";
    alert.informativeText = message;
    [alert addButtonWithTitle:@"知道了"];
    [alert runModal];
}
int main(int argc, const char *argv[]) {
    @autoreleasepool {
        NSString *resources = NSBundle.mainBundle.resourcePath;
        NSFileManager *files = NSFileManager.defaultManager;
        NSArray *required = @[@"OctoSense Host.app/Contents/MacOS/octosense", @"mirror/catalog.json",
            @"mirror/artifacts/muse-goals-0.3.26-rc5.bundle/manifest.json",
            @"mirror/artifacts/muse-goals-0.3.26-rc5.bundle.pack.json", @"tutorial.html"];
        BOOL check = argc == 2 && strcmp(argv[1], "--check") == 0;
        for (NSString *relative in required) {
            if (![files fileExistsAtPath:join(resources, relative)]) {
                NSString *message = [NSString stringWithFormat:@"包内文件缺失：%@。请重新解压完整 ZIP。", relative];
                if (check) fprintf(stderr, "%s\n", message.UTF8String); else fail(message);
                return 1;
            }
        }
        if (check) {
            puts("Muse 0.3.26-rc5 / b48618ac: packaged launch resources present; no window or account opened.");
            return 0;
        }
        NSDictionary *inherited = NSProcessInfo.processInfo.environment;
        NSString *state = inherited[@"MUSE_REPRO_STATE"] ?: join(NSHomeDirectory(), @"Library/Application Support/Muse Reproduction 0.3.26-rc5 b48618ac");
        NSError *error = nil;
        if (![files createDirectoryAtPath:state withIntermediateDirectories:YES attributes:@{NSFilePosixPermissions:@0700} error:&error]) {
            fail([NSString stringWithFormat:@"无法建立数据目录：%@\n%@", state, error.localizedDescription]); return 1;
        }
        int lock = open(join(state, @"launch.lock").fileSystemRepresentation, O_CREAT | O_RDWR, 0600);
        if (lock < 0 || flock(lock, LOCK_EX | LOCK_NB) != 0) {
            fail(@"这个复现包已在运行。请切回 OctoSense 窗口；需要重开时先用 ⌘Q 退出 OctoSense。"); return 1;
        }
        fcntl(lock, F_SETFD, FD_CLOEXEC);
        NSString *core = join(state, @"home/octos-home/.octos");
        for (NSString *path in @[join(core, @"profiles"), join(state, @"apps"), join(state, @"logs")]) {
            if (![files createDirectoryAtPath:path withIntermediateDirectories:YES attributes:@{NSFilePosixPermissions:@0700} error:&error]) {
                fail(error.localizedDescription); return 1;
            }
        }
        NSString *profilePath = join(core, @"profiles/_main.json");
        if (![files fileExistsAtPath:profilePath]) {
            // No account, credential, history or production profile is included.
            // The initial local route is deliberately inactive until the recipient configures a model.
            NSDictionary *profile = @{@"id":@"_main", @"name":@"Muse Intel 复现", @"enabled":@YES,
                @"config":@{@"llm":@{@"primary":@{@"family_id":@"local", @"model_id":@"local-default",
                    @"route":@{@"base_url":@"http://127.0.0.1:1/v1", @"api_type":@"openai"}},
                    @"fallbacks":@[]}, @"env_vars":@{}}};
            NSData *data = [NSJSONSerialization dataWithJSONObject:profile options:NSJSONWritingPrettyPrinted error:&error];
            if (!data || ![data writeToFile:profilePath options:NSDataWritingAtomic error:&error]) {
                fail(@"无法保存初始配置。"); return 1;
            }
            [files setAttributes:@{NSFilePosixPermissions:@0600} ofItemAtPath:profilePath error:nil];
        }
        NSMutableDictionary *environment = [inherited mutableCopy];
        for (NSString *key in @[@"MAKEPAD_REMOTE", @"MAKEPAD_HIDE_WINDOWS", @"MAKEPAD_APP_CONFIG", @"OCTOSENSE_HOME", @"OCTOSENSE_APP_DATA", @"OCTOS_APP_CORE_DIR", @"OCTOSENSE_HUB", @"OCTOSENSE_HUB_ANCHOR"]) {
            [environment removeObjectForKey:key];
        }
        environment[@"OCTOSENSE_HOME"] = join(state, @"home");
        environment[@"OCTOSENSE_APP_DATA"] = join(state, @"apps");
        environment[@"OCTOS_APP_CORE_DIR"] = core;
        environment[@"OCTOSENSE_HUB"] = join(resources, @"mirror");
        environment[@"OCTOSENSE_HUB_ANCHOR"] = @"3581c1c9087a917630bc8560495189c5f1bb842a797ad5203cad0ed94ab5a840";
        environment[@"MAKEPAD_APP_CONFIG"] = @"{}";
        NSString *directory = join(resources, @"OctoSense Host.app/Contents/MacOS");
        NSString *log = join(state, @"logs/host.log");
        [files createFileAtPath:log contents:nil attributes:@{NSFilePosixPermissions:@0600}];
        NSFileHandle *output = [NSFileHandle fileHandleForWritingAtPath:log];
        NSTask *host = [NSTask new];
        host.executableURL = [NSURL fileURLWithPath:join(directory, @"octosense")];
        host.arguments = @[@"--test-action", @"launch-apphub"];
        host.environment = environment;
        host.currentDirectoryURL = [NSURL fileURLWithPath:directory];
        host.standardOutput = output; host.standardError = output;
        signal(SIGTERM, stop); signal(SIGINT, stop);
        if (![host launchAndReturnError:&error]) {
            [output closeFile]; fail([NSString stringWithFormat:@"宿主未启动：%@\n日志：%@", error.localizedDescription, log]); return 1;
        }
        [output closeFile];
        while (host.running && !stopping) [NSThread sleepForTimeInterval:0.2];
        if (host.running) [host terminate];
        [host waitUntilExit];
        flock(lock, LOCK_UN); close(lock);
        return host.terminationStatus;
    }
}
