#import <AppKit/AppKit.h>
#include <sys/file.h>
#include <fcntl.h>
#include <signal.h>
#include <unistd.h>
#include <string.h>
#include <sys/socket.h>
#include <netinet/in.h>

static volatile sig_atomic_t stopping = 0;
static void stop(int unused) { stopping = 1; }
static NSString *join(NSString *base, NSString *path) {
    return [base stringByAppendingPathComponent:path];
}
static BOOL saveJSON(NSDictionary *value, NSString *path, NSError **error) {
    NSData *data = [NSJSONSerialization dataWithJSONObject:value options:NSJSONWritingPrettyPrinted error:error];
    if (!data || ![data writeToFile:path options:NSDataWritingAtomic error:error]) return NO;
    return [NSFileManager.defaultManager setAttributes:@{NSFilePosixPermissions:@0600} ofItemAtPath:path error:error];
}
// Extract only provider metadata; never load config.env_vars or resolve Keychain entries.
static NSDictionary *modelMetadata(NSString *profilePath) {
    NSTask *task = [NSTask new];
    task.executableURL = [NSURL fileURLWithPath:@"/usr/bin/plutil"];
    task.arguments = @[@"-extract", @"config.llm", @"json", @"-o", @"-", @"--", profilePath];
    NSPipe *pipe = [NSPipe pipe];
    task.standardOutput = pipe;
    task.standardError = NSFileHandle.fileHandleWithNullDevice;
    if (![task launchAndReturnError:nil]) return nil;
    NSData *data = [pipe.fileHandleForReading readDataToEndOfFile];
    [task waitUntilExit];
    if (task.terminationStatus != 0) return nil;
    id value = [NSJSONSerialization JSONObjectWithData:data options:0 error:nil];
    return [value isKindOfClass:NSDictionary.class] ? value : nil;
}
static BOOL nativeGPT(NSDictionary *llm) {
    if (![llm[@"primary"] isKindOfClass:NSDictionary.class]) return NO;
    id fallbacks = llm[@"fallbacks"];
    if (fallbacks && ![fallbacks isKindOfClass:NSArray.class]) return NO;
    NSMutableArray *selections = [NSMutableArray arrayWithObject:llm[@"primary"]];
    if (fallbacks) [selections addObjectsFromArray:fallbacks];
    for (id selection in selections) {
        if (![selection isKindOfClass:NSDictionary.class] || ![selection[@"family_id"] isEqual:@"openai"]
            || ![selection[@"model_id"] isKindOfClass:NSString.class]
            || ![selection[@"model_id"] hasPrefix:@"gpt-"]) return NO;
        id route = selection[@"route"];
        if (route && ![route isKindOfClass:NSDictionary.class]) return NO;
        // OpenAI-compatible transport alone does not establish an OpenAI provider.
        id base = route[@"base_url"];
        if (base && ![base isEqual:@"https://api.openai.com/v1"] && ![base isEqual:@"https://api.openai.com/v1/"]) return NO;
        id type = route[@"api_type"];
        if (type && ![type isEqual:@"openai"] && ![type isEqual:@"responses"]) return NO;
    }
    return YES;
}
static int localPort(void) {
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    struct sockaddr_in address = {0};
    address.sin_family = AF_INET; address.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    socklen_t size = sizeof(address);
    int port = 0;
    if (fd >= 0 && bind(fd, (struct sockaddr *)&address, size) == 0 &&
        getsockname(fd, (struct sockaddr *)&address, &size) == 0) port = ntohs(address.sin_port);
    if (fd >= 0) close(fd);
    return port;
}
static BOOL healthy(NSURLSession *session, NSString *base) {
    dispatch_semaphore_t ready = dispatch_semaphore_create(0);
    __block BOOL ok = NO;
    NSURLSessionDataTask *task = [session dataTaskWithURL:[NSURL URLWithString:[base stringByAppendingString:@"/health"]]
        completionHandler:^(NSData *data, NSURLResponse *response, NSError *error) {
            ok = !error && [(NSHTTPURLResponse *)response statusCode] == 200;
            dispatch_semaphore_signal(ready);
        }];
    [task resume];
    if (dispatch_semaphore_wait(ready, dispatch_time(DISPATCH_TIME_NOW, 2 * NSEC_PER_SEC))) [task cancel];
    return ok;
}
static void finishTask(NSTask *task) {
    if (!task) return;
    if (task.running) [task terminate];
    NSDate *limit = [NSDate dateWithTimeIntervalSinceNow:10];
    while (task.running && [limit timeIntervalSinceNow] > 0) [NSThread sleepForTimeInterval:0.1];
    if (task.running) kill(task.processIdentifier, SIGKILL);
    [task waitUntilExit];
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
            @"mirror/artifacts/muse-goals-0.4.0-rc3.bundle/manifest.json",
            @"mirror/artifacts/muse-goals-0.4.0-rc3.bundle.pack.json",
            @"OctoSense Host.app/Contents/MacOS/octos-kernel",
            @"OctoSense Host.app/Contents/Resources/octos-kernel.json"];
        BOOL check = argc == 2 && strcmp(argv[1], "--check") == 0;
        BOOL models = argc == 2 && strcmp(argv[1], "--models") == 0;
        BOOL gptCheck = argc == 2 && strcmp(argv[1], "--gpt-check") == 0;
        BOOL gpt = gptCheck || (argc == 2 && strcmp(argv[1], "--gpt") == 0)
            || [NSBundle.mainBundle.infoDictionary[@"MuseModelMode"] isEqual:@"gpt"];
        BOOL headless = check || gptCheck;
        if (argc > 1 && !check && !models && !gptCheck && strcmp(argv[1], "--gpt") != 0) {
            fprintf(stderr, "使用方式：muse-launcher [--check|--models|--gpt|--gpt-check]\n"); return 2;
        }
        if (!gpt && !models) required = [required arrayByAddingObjectsFromArray:
            @[@"local-model/llama/llama-server", @"local-model/qwen2.5-0.5b-instruct-q4_0.gguf"]];
        for (NSString *relative in required) {
            if (![files fileExistsAtPath:join(resources, relative)]) {
                NSString *message = [NSString stringWithFormat:@"包内文件缺失：%@。请重新解压完整 ZIP。", relative];
                if (headless) fprintf(stderr, "%s\n", message.UTF8String); else fail(message);
                return 1;
            }
        }
        // The outer signature covers the pinned Host, catalog, runner and model weight.
        NSTask *signature = [NSTask new];
        signature.executableURL = [NSURL fileURLWithPath:@"/usr/bin/codesign"];
        signature.arguments = @[@"--verify", @"--deep", @"--strict", NSBundle.mainBundle.bundlePath];
        signature.standardOutput = NSFileHandle.fileHandleWithNullDevice;
        signature.standardError = NSFileHandle.fileHandleWithNullDevice;
        NSError *signatureError = nil;
        if (![signature launchAndReturnError:&signatureError]) {
            if (headless) fprintf(stderr, "Muse 签名检查无法启动。\n"); else fail(@"Muse 签名检查无法启动。");
            return 1;
        }
        [signature waitUntilExit];
        if (signature.terminationStatus != 0) {
            if (headless) fprintf(stderr, "Muse 包文件检查失败。\n"); else fail(@"Muse 包文件检查失败，请重新解压完整 ZIP。");
            return 1;
        }
        if (check) {
            puts("PASS：Muse 0.4.0-rc3 包资源与签名；未验证模型调用，未启动窗口或创建配置。");
            return 0;
        }
        NSDictionary *inherited = NSProcessInfo.processInfo.environment;
        NSString *state = inherited[@"MUSE_INTEGRATED_STATE"] ?: join(NSHomeDirectory(), @"Library/Application Support/Muse Integrated 0.4");
        if (![state isAbsolutePath]) {
            if (headless) fprintf(stderr, "MUSE_INTEGRATED_STATE 必须是绝对路径。\n");
            else fail(@"MUSE_INTEGRATED_STATE 必须是绝对路径。");
            return 2;
        }
        NSString *core = join(state, @"home/octos-home/.octos");
        NSString *profilePath = join(core, @"profiles/_main.json");
        if (gpt) {
            BOOL configured = nativeGPT(modelMetadata(profilePath));
            puts(configured ? "GPT_CONFIG_ONLY：已识别原生 OpenAI GPT 配置；凭证、连通性与实调尚未验证。"
                : "GPT_SETUP_REQUIRED：请在宿主 Models 面板选择 OpenAI/GPT，设置官方路由并由本人输入凭证；移除非 GPT 回退后重开。启动器不复制凭证。");
            if (gptCheck) return configured ? 0 : 3;
            if (!configured) models = YES;
        }
        NSError *error = nil;
        if (![files createDirectoryAtPath:state withIntermediateDirectories:YES attributes:@{NSFilePosixPermissions:@0700} error:&error]) {
            fail([NSString stringWithFormat:@"无法建立数据目录：%@\n%@", state, error.localizedDescription]); return 1;
        }
        int lock = open(join(state, @"launch.flock").fileSystemRepresentation, O_CREAT | O_RDWR, 0600);
        if (lock < 0 || flock(lock, LOCK_EX | LOCK_NB) != 0) {
            fail(@"这个 Muse 整合版已在运行。请切回 OctoSense 窗口；需要重开时先用 ⌘Q 退出 OctoSense。"); return 1;
        }
        fcntl(lock, F_SETFD, FD_CLOEXEC);
        signal(SIGTERM, stop); signal(SIGINT, stop);
        for (NSString *path in @[join(core, @"profiles"), join(state, @"apps"), join(state, @"logs"), join(state, @"rinx"), join(state, @"config"), join(state, @"data"), join(state, @"cache")]) {
            if (![files createDirectoryAtPath:path withIntermediateDirectories:YES attributes:@{NSFilePosixPermissions:@0700} error:&error]) {
                fail(error.localizedDescription); return 1;
            }
        }
        NSTask *model = nil;
        if (!gpt && !models) {
        BOOL first = ![files fileExistsAtPath:profilePath];
        NSMutableDictionary *profile = first ? [@{@"id":@"_main", @"name":@"Muse 整合版本", @"enabled":@YES,
            @"config":@{@"llm":@{@"primary":@{@"family_id":@"local", @"model_id":@"Qwen2.5-0.5B-Instruct-Q4_0-offline",
                @"context_window":@4096}, @"fallbacks":@[]}, @"env_vars":@{}}} mutableCopy] :
            [NSJSONSerialization JSONObjectWithData:[NSData dataWithContentsOfFile:profilePath]
                options:NSJSONReadingMutableContainers error:&error];
        if (![profile isKindOfClass:NSMutableDictionary.class]) {
            fail(@"现有模型配置无法读取，请查看本机配置文件；启动器不会覆盖它。"); return 1;
        }
        NSString *modelID = @"Qwen2.5-0.5B-Instruct-Q4_0-offline";
        NSDictionary *llm = profile[@"config"][@"llm"];
        NSMutableArray *selections = [NSMutableArray new];
        if ([llm[@"primary"] isKindOfClass:NSDictionary.class]) [selections addObject:llm[@"primary"]];
        if ([llm[@"fallbacks"] isKindOfClass:NSArray.class]) [selections addObjectsFromArray:llm[@"fallbacks"]];
        BOOL bundled = NO;
        for (NSDictionary *selection in selections) {
            if ([selection[@"family_id"] isEqual:@"local"] && [selection[@"model_id"] isEqual:modelID]) bundled = YES;
        }
        if (bundled) {
            int port = localPort();
            if (!port) { fail(@"无法分配本地模型端口。"); return 1; }
            NSString *base = [NSString stringWithFormat:@"http://127.0.0.1:%d", port];
            NSString *modelLog = join(state, @"logs/model.log");
            [files createFileAtPath:modelLog contents:nil attributes:@{NSFilePosixPermissions:@0600}];
            NSFileHandle *output = [NSFileHandle fileHandleForWritingAtPath:modelLog];
            model = [NSTask new];
            model.executableURL = [NSURL fileURLWithPath:join(resources, @"local-model/llama/llama-server")];
            model.arguments = @[@"--model", join(resources, @"local-model/qwen2.5-0.5b-instruct-q4_0.gguf"),
                @"--host", @"127.0.0.1", @"--port", [NSString stringWithFormat:@"%d", port],
                @"--alias", modelID, @"--ctx-size", @"4096", @"--parallel", @"1",
                @"--threads", @"4", @"--gpu-layers", @"0", @"--offline", @"--no-webui",
                @"--temp", @"0.2", @"--reasoning", @"off"];
            model.environment = @{@"PATH":@"/usr/bin:/bin", @"HOME":state, @"TMPDIR":NSTemporaryDirectory()};
            model.standardOutput = output; model.standardError = output;
            if (![model launchAndReturnError:&error]) {
                [output closeFile]; fail([NSString stringWithFormat:@"离线模型未启动：%@\n日志：%@", error.localizedDescription, modelLog]); return 1;
            }
            [output closeFile];
            NSURLSessionConfiguration *config = NSURLSessionConfiguration.ephemeralSessionConfiguration;
            config.timeoutIntervalForRequest = 2;
            NSURLSession *session = [NSURLSession sessionWithConfiguration:config];
            NSDate *deadline = [NSDate dateWithTimeIntervalSinceNow:45];
            BOOL ready = NO;
            while (!stopping && model.running && [deadline timeIntervalSinceNow] > 0) {
                if (healthy(session, base) && model.running) { ready = YES; break; }
                [NSThread sleepForTimeInterval:0.2];
            }
            [session invalidateAndCancel];
            if (!ready) { finishTask(model); fail([NSString stringWithFormat:@"离线模型未就绪，请查看日志：%@", modelLog]); return 1; }
            // Update only selections belonging to this bundled model; preserve user providers and credentials.
            NSMutableDictionary *configData = [profile[@"config"] mutableCopy];
            NSMutableDictionary *llmData = [configData[@"llm"] mutableCopy];
            for (NSString *key in @[@"primary", @"fallbacks"]) {
                NSArray *items = [key isEqual:@"primary"] ? (llmData[key] ? @[llmData[key]] : @[]) : (llmData[key] ?: @[]);
                NSMutableArray *updated = [NSMutableArray new];
                for (NSDictionary *selection in items) {
                    NSMutableDictionary *copy = [selection mutableCopy];
                    if ([copy[@"family_id"] isEqual:@"local"] && [copy[@"model_id"] isEqual:modelID]) {
                        copy[@"route"] = @{@"base_url":[base stringByAppendingString:@"/v1"], @"api_type":@"openai", @"label":@"内置基础离线模型"};
                    }
                    [updated addObject:copy];
                }
                if ([key isEqual:@"primary"]) { if (updated.count) llmData[key] = updated[0]; }
                else llmData[key] = updated;
            }
            configData[@"llm"] = llmData; profile[@"config"] = configData;
            NSString *now = [[NSISO8601DateFormatter new] stringFromDate:NSDate.date];
            if (first) profile[@"created_at"] = now;
            profile[@"updated_at"] = now;
            if (!saveJSON(profile, profilePath, &error)) { finishTask(model); fail(@"无法保存本机离线模型配置。"); return 1; }
            saveJSON(@{@"model_id":modelID, @"quality":@"basic offline fallback; not a strong model",
                @"base_url":base, @"pid":@(model.processIdentifier)}, join(state, @"local-model.json"), nil);
        }
        }
        NSMutableDictionary *environment = [inherited mutableCopy];
        for (NSString *key in @[@"MAKEPAD_REMOTE", @"MAKEPAD_HIDE_WINDOWS", @"MAKEPAD_APP_CONFIG", @"OCTOSENSE_HOME", @"OCTOSENSE_APP_DATA", @"OCTOS_APP_CORE_DIR", @"OCTOSENSE_HUB", @"OCTOSENSE_HUB_ANCHOR", @"OCTOSENSE_HUB_CATALOG", @"OCTOSENSE_KERNEL_BIN", @"OCTOSENSE_ALLOW_ANY_KERNEL_REVISION", @"OCTOSENSE_DEV_MODE", @"OCTOSENSE_CONTAINED_APPS", @"MAKEPAD_WM_TEST_APP", @"MAKEPAD_SPLASH_BUDGET_MS", @"MAKEPAD_SPLASH_THEME", @"MAKEPAD_STYLE", @"MAKEPAD_DISABLE_GAUSS", @"MAKEPAD_NO_FOCUS"]) {
            [environment removeObjectForKey:key];
        }
        environment[@"OCTOSENSE_HOME"] = join(state, @"home");
        environment[@"HOME"] = state;
        environment[@"OCTOSENSE_APP_DATA"] = join(state, @"apps");
        environment[@"OCTOS_APP_CORE_DIR"] = core;
        environment[@"OCTOSENSE_HUB"] = join(resources, @"mirror");
        environment[@"OCTOSENSE_HUB_ANCHOR"] = @"543ffbe45b6700c23e1824157ea694f8bd7839090e0ede464c11758d350b1412";
        // Only the fresh local catalog uses legacy Ed25519. Existing v2 floors
        // are still enforced by the host and never downgraded by the launcher.
        environment[@"OCTOSENSE_HUB_CATALOG"] = @"legacy";
        environment[@"OCTOSENSE_DEV_MODE"] = @"0";
        environment[@"MAKEPAD_FOCUS"] = @"1";
        environment[@"RINX_DATA_DIR"] = join(state, @"rinx");
        environment[@"ROBRIX_DATA_DIR"] = join(state, @"rinx");
        environment[@"XDG_CONFIG_HOME"] = join(state, @"config");
        environment[@"XDG_DATA_HOME"] = join(state, @"data");
        environment[@"XDG_CACHE_HOME"] = join(state, @"cache");
        environment[@"MAKEPAD_APP_CONFIG"] = @"{}";
        NSString *remote = inherited[@"MUSE_INTEGRATED_REMOTE"];
        NSInteger remotePort = remote.integerValue;
        if (remote.length && remotePort >= 1024 && remotePort <= 65535) environment[@"MAKEPAD_REMOTE"] = [NSString stringWithFormat:@"%ld", (long)remotePort];
        NSString *directory = join(resources, @"OctoSense Host.app/Contents/MacOS");
        NSString *log = join(state, @"logs/host.log");
        [files createFileAtPath:log contents:nil attributes:@{NSFilePosixPermissions:@0600}];
        NSFileHandle *output = [NSFileHandle fileHandleForWritingAtPath:log];
        NSTask *host = [NSTask new];
        host.executableURL = [NSURL fileURLWithPath:join(directory, @"octosense")];
        NSString *installed = join(state, @"apps/.bundles/muse-goals/bundle/main.splash");
        NSString *action = @"launch-apphub";
        if ([files fileExistsAtPath:installed]) {
            NSData *expected = [NSData dataWithContentsOfFile:join(resources, @"mirror/artifacts/muse-goals-0.4.0-rc3.bundle/main.splash")];
            if (![expected isEqualToData:[NSData dataWithContentsOfFile:installed]]) {
                action = @"launch-apphub"; // Normal signed Store update, preserving the app jail.
            } else {
                action = @"launch-hub:muse-goals";
            }
        }
        host.arguments = @[@"--test-action", models ? @"launch-ai-providers" : action];
        host.environment = environment;
        host.currentDirectoryURL = [NSURL fileURLWithPath:directory];
        host.standardOutput = output; host.standardError = output;
        if (![host launchAndReturnError:&error]) {
            [output closeFile]; finishTask(model); fail([NSString stringWithFormat:@"宿主未启动：%@\n日志：%@", error.localizedDescription, log]); return 1;
        }
        [output closeFile];
        while (host.running && !stopping) [NSThread sleepForTimeInterval:0.2];
        if (host.running) [host terminate];
        [host waitUntilExit];
        finishTask(model);
        flock(lock, LOCK_UN); close(lock);
        return host.terminationStatus;
    }
}
