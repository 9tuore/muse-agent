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
static BOOL cloudPrimary(NSDictionary *llm) {
    id primary = llm[@"primary"];
    if (![primary isKindOfClass:NSDictionary.class]) return NO;
    // Canonical cloud families in the paired Native registry. No inference or key validation here.
    NSArray *families = @[@"anthropic", @"openai", @"gemini", @"vertex", @"r9s", @"openrouter",
        @"deepseek", @"groq", @"moonshot-coding", @"moonshot", @"dashscope", @"minimax-cn",
        @"minimax", @"zai-coding", @"zhipu", @"zai", @"nvidia", @"vllm"];
    if (![families containsObject:primary[@"family_id"] ?: @""]) return NO;
    id route = primary[@"route"];
    if (route && ![route isKindOfClass:NSDictionary.class]) return NO;
    id base = route[@"base_url"];
    if (base) {
        if (![base isKindOfClass:NSString.class]) return NO;
        NSURL *url = [NSURL URLWithString:base];
        if (!url.host.length || [url.host isEqual:@"localhost"] || [url.host hasPrefix:@"127."]
            || [url.host isEqual:@"::1"] || [url.host isEqual:@"[::1]"]) return NO;
    } else if ([primary[@"family_id"] isEqual:@"vllm"]) return NO;
    return YES;
}
static BOOL updateLocalRoute(NSString *profilePath, NSDictionary *llm, NSString *base) {
    NSArray *fallbacks = [llm[@"fallbacks"] isKindOfClass:NSArray.class] ? llm[@"fallbacks"] : @[];
    for (NSUInteger i = 0; i < fallbacks.count; i++) {
        NSDictionary *selection = fallbacks[i];
        if (![selection isKindOfClass:NSDictionary.class] || ![selection[@"family_id"] isEqual:@"local"]
            || ![selection[@"model_id"] isEqual:@"Qwen2.5-0.5B-Instruct-Q4_0-offline"]) continue;
        NSString *path = [NSString stringWithFormat:@"config.llm.fallbacks.%lu.route", (unsigned long)i];
        NSTask *task = [NSTask new];
        task.executableURL = [NSURL fileURLWithPath:@"/usr/bin/plutil"];
        id route = selection[@"route"];
        if ([route isKindOfClass:NSDictionary.class]) {
            task.arguments = @[route[@"base_url"] ? @"-replace" : @"-insert", [path stringByAppendingString:@".base_url"],
                @"-string", base, @"--", profilePath];
        } else if (!route) {
            NSData *data = [NSJSONSerialization dataWithJSONObject:@{@"base_url":base, @"api_type":@"openai", @"label":@"内置基础离线模型"} options:0 error:nil];
            task.arguments = @[@"-insert", path, @"-json", [[NSString alloc] initWithData:data encoding:NSUTF8StringEncoding], @"--", profilePath];
        } else return NO;
        task.standardOutput = NSFileHandle.fileHandleWithNullDevice;
        task.standardError = NSFileHandle.fileHandleWithNullDevice;
        if (![task launchAndReturnError:nil]) return NO;
        [task waitUntilExit];
        if (task.terminationStatus != 0) return NO;
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
        BOOL workbuddy = [NSBundle.mainBundle.infoDictionary[@"MuseHostLaunchMethod"] isEqual:@"workbuddy"];
        NSArray *required = @[@"OctoSense Host.app/Contents/MacOS/octosense", @"mirror/catalog.json",
            @"mirror/artifacts/muse-goals-0.4.0-rc4.bundle/manifest.json",
            @"mirror/artifacts/muse-goals-0.4.0-rc4.bundle.pack.json",
            @"OctoSense Host.app/Contents/MacOS/octos-kernel",
            @"OctoSense Host.app/Contents/Resources/octos-kernel.json"];
        if (workbuddy) required = [required arrayByAddingObject:@"WorkBuddy Launcher.app/Contents/MacOS/Launcher"];
        BOOL check = argc == 2 && strcmp(argv[1], "--check") == 0;
        BOOL models = argc == 2 && strcmp(argv[1], "--models") == 0;
        BOOL gptCheck = argc == 2 && strcmp(argv[1], "--gpt-check") == 0;
        NSString *mode = NSBundle.mainBundle.infoDictionary[@"MuseModelMode"] ?: @"offline";
        if (argc == 2 && strcmp(argv[1], "--gpt") == 0) mode = @"gpt";
        if (argc == 2 && strcmp(argv[1], "--hybrid") == 0) mode = @"hybrid";
        BOOL gpt = gptCheck || [mode isEqual:@"gpt"];
        BOOL hybrid = !gpt && [mode isEqual:@"hybrid"];
        BOOL headless = check || gptCheck;
        if (argc > 1 && !check && !models && !gptCheck && strcmp(argv[1], "--gpt") != 0 && strcmp(argv[1], "--hybrid") != 0) {
            fprintf(stderr, "使用方式：muse-launcher [--check|--models|--gpt|--gpt-check|--hybrid]\n"); return 2;
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
            puts("PASS：Muse 0.4.0-rc4 包资源与签名；未验证模型调用，未启动窗口或创建配置。");
            return 0;
        }
        NSDictionary *inherited = NSProcessInfo.processInfo.environment;
        NSString *state = inherited[@"MUSE_INTEGRATED_STATE"] ?: NSBundle.mainBundle.infoDictionary[@"MuseStateRoot"]
            ?: join(NSBundle.mainBundle.bundlePath.stringByDeletingLastPathComponent, @"Muse Data");
        if (![state isAbsolutePath]) {
            if (headless) fprintf(stderr, "MUSE_INTEGRATED_STATE 必须是绝对路径。\n");
            else fail(@"MUSE_INTEGRATED_STATE 必须是绝对路径。");
            return 2;
        }
        NSString *core = join(state, @"kernel/.octos");
        NSString *profilePath = join(core, @"profiles/_main.json");
        if (gpt) {
            BOOL configured = nativeGPT(modelMetadata(profilePath));
            puts(configured ? "GPT_CONFIG_ONLY：已识别原生 OpenAI GPT 配置；凭证、连通性与实调尚未验证。"
                : "GPT_SETUP_REQUIRED：请在宿主 Models 面板选择 OpenAI/GPT，设置官方路由并由本人输入凭证；移除非 GPT 回退后重开。启动器不复制凭证。");
            if (gptCheck) return configured ? 0 : 3;
            if (!configured) models = YES;
        }
        if (hybrid && !models) {
            NSDictionary *llm = modelMetadata(profilePath);
            BOOL cloud = cloudPrimary(llm);
            if (!cloud) {
                puts("HYBRID_SETUP_REQUIRED：请在 Models 中由本人配置云端主模型（保留已有 MiniMax 等提供方）；现有配置保留，本次设置入口不启动 Qwen。");
                models = YES;
            }
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
        for (NSString *path in @[join(state, @"shell"), join(core, @"profiles"), join(state, @"apps"), join(state, @"logs"), join(state, @"rinx"), join(state, @"config"), join(state, @"data"), join(state, @"cache")]) {
            if (![files createDirectoryAtPath:path withIntermediateDirectories:YES attributes:@{NSFilePosixPermissions:@0700} error:&error]) {
                fail(error.localizedDescription); return 1;
            }
        }
        NSTask *model = nil;
        NSDictionary *localStatus = nil;
        if (!gpt && !models) {
        BOOL first = ![files fileExistsAtPath:profilePath];
        NSMutableDictionary *profile = nil;
        if (hybrid) {
            NSDictionary *metadata = modelMetadata(profilePath);
            if (!metadata) { fail(@"现有云端模型元数据无法读取，启动器不会覆盖配置。"); return 1; }
            profile = [@{@"config":@{@"llm":metadata}} mutableCopy];
        } else profile = first ? [@{@"id":@"_main", @"name":@"Muse 整合版本", @"enabled":@YES,
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
        BOOL localSelected = NO;
        for (NSDictionary *selection in selections) {
            if ([selection[@"family_id"] isEqual:@"local"] && [selection[@"model_id"] isEqual:modelID]) localSelected = YES;
        }
        if (localSelected || hybrid) {
            int port = localPort();
            if (!port) { fail(@"无法分配本地模型端口。"); return 1; }
            NSString *base = [NSString stringWithFormat:@"http://127.0.0.1:%d", port];
            NSString *modelLog = join(state, @"logs/model.log");
            if (![files fileExistsAtPath:modelLog]) [files createFileAtPath:modelLog contents:nil attributes:@{NSFilePosixPermissions:@0600}];
            NSFileHandle *output = [NSFileHandle fileHandleForWritingAtPath:modelLog];
            [output seekToEndOfFile];
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
            // A cloud-only profile is byte-preserved. Only a pre-existing bundled-local selection needs a route update.
            if (localSelected && !(hybrid ? updateLocalRoute(profilePath,llm,[base stringByAppendingString:@"/v1"])
                : saveJSON(profile, profilePath, &error))) { finishTask(model); fail(@"无法保存本机离线模型路由，现有云端主配置保留。"); return 1; }
            localStatus = @{@"model_id":modelID, @"quality":@"basic offline fallback; not a strong model",
                @"base_url":base, @"route_base_url":[base stringByAppendingString:@"/v1"],
                @"pid":@(model.processIdentifier), @"service_status":@"ready",
                @"native_local_selected":@(localSelected), @"inference_verified":@NO};
            saveJSON(localStatus, join(state, @"local-model.json"), nil);
            if (hybrid) puts(localSelected
                ? "HYBRID_LOCAL_READY_ONLY：云端主配置保留；已配置的本地路由更新，尚未验证协同推理或持续代理运行。"
                : "HYBRID_LOCAL_READY_ONLY：云端配置原字节保留；本地服务已就绪但未进入 Native 提供方列表。可在 Models 添加 local 回退；路由见本机 local-model.json。尚未验证协同推理。");
        }
        }
        NSMutableDictionary *environment = [inherited mutableCopy];
        for (NSString *key in @[@"MAKEPAD_REMOTE", @"MAKEPAD_HIDE_WINDOWS", @"MAKEPAD_APP_CONFIG", @"OCTOSENSE_HOME", @"OCTOSENSE_APP_DATA", @"OCTOS_APP_CORE_DIR", @"OCTOSENSE_HUB", @"OCTOSENSE_HUB_ANCHOR", @"OCTOSENSE_HUB_CATALOG", @"OCTOS_APP_CORE_BIN", @"OCTOSENSE_KERNEL_ANY_REVISION", @"OCTOSENSE_KERNEL_BIN", @"OCTOSENSE_ALLOW_ANY_KERNEL_REVISION", @"OCTOSENSE_DEV_MODE", @"OCTOSENSE_CONTAINED_APPS", @"MAKEPAD_WM_TEST_APP", @"MAKEPAD_SPLASH_BUDGET_MS", @"MAKEPAD_SPLASH_THEME", @"MAKEPAD_STYLE", @"MAKEPAD_NO_GAUSS", @"MAKEPAD_DISABLE_GAUSS", @"MAKEPAD_NO_FOCUS"]) {
            [environment removeObjectForKey:key];
        }
        environment[@"OCTOSENSE_HOME"] = join(state, @"shell");
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
        NSString *remote = inherited[@"MUSE_INTEGRATED_REMOTE"] ?: @"9696";
        NSInteger remotePort = remote.integerValue;
        NSString *directory = join(resources, @"OctoSense Host.app/Contents/MacOS");
        NSString *log = join(state, @"logs/host.log");
        if (![files fileExistsAtPath:log]) [files createFileAtPath:log contents:nil attributes:@{NSFilePosixPermissions:@0600}];
        NSFileHandle *output = [NSFileHandle fileHandleForWritingAtPath:log];
        [output seekToEndOfFile];
        NSTask *host = [NSTask new];
        host.executableURL = [NSURL fileURLWithPath:join(directory, @"octosense")];
        NSString *installed = join(state, @"apps/.bundles/muse-goals/bundle/main.splash");
        NSString *action = @"launch-apphub";
        if ([files fileExistsAtPath:installed]) {
            NSData *expected = [NSData dataWithContentsOfFile:join(resources, @"mirror/artifacts/muse-goals-0.4.0-rc4.bundle/main.splash")];
            if (![expected isEqualToData:[NSData dataWithContentsOfFile:installed]]) {
                action = @"launch-apphub"; // Normal signed Store update, preserving the app jail.
            } else {
                action = @"launch-hub:muse-goals";
            }
        }
        // WorkBuddy opens the linked Native module first; the requested Muse/Models surface follows it.
        NSMutableArray *arguments = [NSMutableArray arrayWithArray:@[@"--test-action", @"launch-muse-native-prototype",
            @"--test-action", models ? @"launch-ai-providers" : action]];
        if (remote.length && remotePort >= 1024 && remotePort <= 65535) {
            [arguments insertObject:[NSString stringWithFormat:@"--remote=%ld", (long)remotePort] atIndex:0];
        }
        host.arguments = arguments;
        host.environment = environment;
        host.standardOutput = output; host.standardError = output;
        __block NSRunningApplication *application = nil;
        if (workbuddy) {
            environment[@"MUSE_HOST_LOG"] = log;
            NSWorkspaceOpenConfiguration *configuration = [NSWorkspaceOpenConfiguration configuration];
            configuration.createsNewApplicationInstance = YES;
            configuration.allowsRunningApplicationSubstitution = NO;
            configuration.environment = environment;
            configuration.arguments = arguments;
            __block BOOL completed = NO;
            __block NSError *launchError = nil;
            [NSWorkspace.sharedWorkspace openApplicationAtURL:
                [NSURL fileURLWithPath:join(resources, @"WorkBuddy Launcher.app")]
                configuration:configuration completionHandler:^(NSRunningApplication *app, NSError *failure) {
                    dispatch_async(dispatch_get_main_queue(), ^{
                        application = app; launchError = failure; completed = YES;
                    });
                }];
            while (!completed) [NSRunLoop.currentRunLoop runUntilDate:[NSDate dateWithTimeIntervalSinceNow:0.2]];
            error = launchError;
        }
        if (workbuddy ? !application : ![host launchAndReturnError:&error]) {
            [output closeFile]; finishTask(model); fail([NSString stringWithFormat:@"宿主未启动：%@\n日志：%@", error.localizedDescription, log]); return 1;
        }
        [output closeFile];
        BOOL localStopped = NO;
        while ((workbuddy ? !application.terminated : host.running) && !stopping) {
            if (model && !model.running && !localStopped) {
                localStopped = YES;
                NSMutableDictionary *status = [localStatus mutableCopy];
                status[@"service_status"] = @"failed";
                saveJSON(status, join(state, @"local-model.json"), nil);
                fprintf(stderr, "Muse 本地服务已退出；云端配置保留，不能称本地持续运行。\n");
            }
            [NSRunLoop.currentRunLoop runUntilDate:[NSDate dateWithTimeIntervalSinceNow:0.2]];
        }
        if (workbuddy) {
            if (!application.terminated) [application terminate];
            while (!application.terminated) [NSRunLoop.currentRunLoop runUntilDate:[NSDate dateWithTimeIntervalSinceNow:0.2]];
        } else {
            if (host.running) [host terminate];
            [host waitUntilExit];
        }
        finishTask(model);
        if (localStatus && !localStopped) {
            NSMutableDictionary *status = [localStatus mutableCopy];
            status[@"service_status"] = @"stopped";
            saveJSON(status, join(state, @"local-model.json"), nil);
        }
        flock(lock, LOCK_UN); close(lock);
        return workbuddy ? 0 : host.terminationStatus;
    }
}
