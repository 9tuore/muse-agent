#import "muse_model_manager.h"
#import <CommonCrypto/CommonDigest.h>
#import <arpa/inet.h>
#import <sys/socket.h>
#import <unistd.h>

static NSString *const MuseModelFile = @"Qwen3-0.6B-Q8_0.gguf";
static NSString *const MuseModelSHA256 = @"9465e63a22add5354d9bb4b99e90117043c7124007664907259bd16d043bb031";
static const unsigned long long MuseModelBytes = 639446688;
static NSString *const MuseModelURL = @"https://huggingface.co/Qwen/Qwen3-0.6B-GGUF/resolve/1eaf4d9657fe65ad10a51eab76a8db5b363bddaa/Qwen3-0.6B-Q8_0.gguf?download=true";

@interface MuseModelManager ()
@property(nonatomic, copy) NSString *resources;
@property(nonatomic, copy) NSString *support;
@property(nonatomic, strong) NSURLSession *session;
@property(nonatomic, strong) NSURLSessionDownloadTask *downloadTask;
@property(nonatomic, readwrite, strong) NSTask *ownedServer;
@property(nonatomic, assign) BOOL stopped;
@end

@implementation MuseModelManager

- (instancetype)initWithResources:(NSString *)resources support:(NSString *)support {
    if ((self = [super init])) {
        _resources = [resources copy];
        _support = [support copy];
    }
    return self;
}

- (NSString *)modelsDirectory { return [self.support stringByAppendingPathComponent:@"models"]; }
- (NSString *)modelPath { return [[self modelsDirectory] stringByAppendingPathComponent:MuseModelFile]; }
- (NSString *)resumePath { return [[self modelsDirectory] stringByAppendingPathComponent:@".qwen3-0.6b.resume"]; }
- (NSString *)partialPath { return [[self modelsDirectory] stringByAppendingPathComponent:@".qwen3-0.6b.partial"]; }

- (BOOL)modelInstalled {
    NSDictionary *attributes = [[NSFileManager defaultManager] attributesOfItemAtPath:self.modelPath error:nil];
    return [attributes[NSFileType] isEqualToString:NSFileTypeRegular] &&
           [attributes[NSFileSize] unsignedLongLongValue] == MuseModelBytes;
}

- (NSString *)sha256:(NSString *)path {
    NSInputStream *stream = [NSInputStream inputStreamWithFileAtPath:path];
    if (!stream) return nil;
    [stream open];
    CC_SHA256_CTX ctx;
    CC_SHA256_Init(&ctx);
    uint8_t buffer[64 * 1024];
    NSInteger count;
    while ((count = [stream read:buffer maxLength:sizeof(buffer)]) > 0) {
        CC_SHA256_Update(&ctx, buffer, (CC_LONG)count);
    }
    [stream close];
    if (count < 0) return nil;
    unsigned char digest[CC_SHA256_DIGEST_LENGTH];
    CC_SHA256_Final(digest, &ctx);
    NSMutableString *hex = [NSMutableString string];
    for (NSUInteger i = 0; i < sizeof(digest); i++) [hex appendFormat:@"%02x", digest[i]];
    return hex;
}

- (void)finish:(BOOL)installed message:(NSString *)message {
    void (^done)(BOOL, NSString *) = self.completion;
    self.completion = nil;
    self.progress = nil;
    self.downloadTask = nil;
    [self.session invalidateAndCancel];
    self.session = nil;
    if (done) done(installed, message);
}

- (void)downloadDefault {
    if (self.downloadTask) return;
    NSFileManager *files = [NSFileManager defaultManager];
    NSError *error = nil;
    if (![files createDirectoryAtPath:[self modelsDirectory] withIntermediateDirectories:YES attributes:nil error:&error]) {
        [self finish:NO message:@"无法创建模型目录；请检查磁盘权限。"];
        return;
    }
    if ([self.modelPath hasPrefix:self.support] &&
        [self modelInstalled] && [[self sha256:self.modelPath] isEqualToString:MuseModelSHA256]) {
        [self finish:YES message:@"默认模型已验证，可直接使用。"];
        return;
    }
    NSDictionary *space = [files attributesOfFileSystemForPath:[self modelsDirectory] error:&error];
    if ([space[NSFileSystemFreeSize] unsignedLongLongValue] < MuseModelBytes * 2) {
        [self finish:NO message:@"可用空间不足；下载前至少需要约 1.3 GB。"];
        return;
    }
    NSURLSessionConfiguration *config = [NSURLSessionConfiguration defaultSessionConfiguration];
    config.timeoutIntervalForRequest = 60;
    config.timeoutIntervalForResource = 7200;
    self.session = [NSURLSession sessionWithConfiguration:config delegate:self delegateQueue:[NSOperationQueue mainQueue]];
    NSData *resume = [NSData dataWithContentsOfFile:[self resumePath]];
    self.downloadTask = resume.length > 0 ? [self.session downloadTaskWithResumeData:resume] :
        [self.session downloadTaskWithURL:[NSURL URLWithString:MuseModelURL]];
    [self.downloadTask resume];
}

- (void)cancelDownload {
    if (!self.downloadTask) return;
    [self.downloadTask cancelByProducingResumeData:^(NSData *resumeData) {
        if (resumeData.length > 0) [resumeData writeToFile:[self resumePath] atomically:YES];
    }];
}

- (void)URLSession:(NSURLSession *)session downloadTask:(NSURLSessionDownloadTask *)task
        didWriteData:(int64_t)written totalBytesWritten:(int64_t)received
 totalBytesExpectedToWrite:(int64_t)expected {
    if (self.progress) self.progress(received, expected);
}

- (void)URLSession:(NSURLSession *)session downloadTask:(NSURLSessionDownloadTask *)task
                               didFinishDownloadingToURL:(NSURL *)location {
    NSHTTPURLResponse *response = (NSHTTPURLResponse *)task.response;
    if (![response isKindOfClass:[NSHTTPURLResponse class]] || response.statusCode != 200) {
        [self finish:NO message:@"模型来源没有返回完整文件；请检查网络并重试。"];
        return;
    }
    NSFileManager *files = [NSFileManager defaultManager];
    [files removeItemAtPath:[self partialPath] error:nil];
    NSError *error = nil;
    if (![files moveItemAtURL:location toURL:[NSURL fileURLWithPath:[self partialPath]] error:&error]) {
        [self finish:NO message:@"下载文件暂存失败；请检查可用空间。"];
        return;
    }
    dispatch_async(dispatch_get_global_queue(QOS_CLASS_UTILITY, 0), ^{
        NSDictionary *attributes = [files attributesOfItemAtPath:[self partialPath] error:nil];
        BOOL valid = [attributes[NSFileSize] unsignedLongLongValue] == MuseModelBytes &&
                     [[self sha256:self.partialPath] isEqualToString:MuseModelSHA256];
        dispatch_async(dispatch_get_main_queue(), ^{
            if (!valid) {
                [files removeItemAtPath:[self partialPath] error:nil];
                [self finish:NO message:@"模型 SHA-256 校验失败，文件未启用；请重试。"];
                return;
            }
            [files removeItemAtPath:self.modelPath error:nil];
            NSError *moveError = nil;
            if (![files moveItemAtPath:[self partialPath] toPath:self.modelPath error:&moveError]) {
                [self finish:NO message:@"校验通过，但保存模型失败；请重试。"];
                return;
            }
            [files removeItemAtPath:[self resumePath] error:nil];
            [self finish:YES message:@"默认模型已下载并校验。"];
        });
    });
}

- (void)URLSession:(NSURLSession *)session task:(NSURLSessionTask *)task didCompleteWithError:(NSError *)error {
    if (!error || !self.completion) return;
    NSData *resume = error.userInfo[NSURLSessionDownloadTaskResumeData];
    if (resume.length > 0) [resume writeToFile:[self resumePath] atomically:YES];
    [self finish:NO message:(error.code == NSURLErrorCancelled ? @"下载已暂停，可稍后继续。" : @"下载未完成；请检查网络并重试。")];
}

- (BOOL)portInUse {
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) return YES;
    struct sockaddr_in address = {0};
    address.sin_family = AF_INET;
    address.sin_port = htons(8080);
    address.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    BOOL occupied = connect(sock, (struct sockaddr *)&address, sizeof(address)) == 0;
    close(sock);
    return occupied;
}

- (BOOL)startOwnedServer:(NSString **)message {
    @synchronized (self) {
        if (self.stopped) { if (message) *message = @"本应用服务已停止；重新打开 Muse 后可恢复。"; return NO; }
        if (self.ownedServer.isRunning) { if (message) *message = @"本应用模型服务已在运行。"; return YES; }
    }
    if (![self modelInstalled]) { if (message) *message = @"默认模型尚未安装。"; return NO; }
    if (![[self sha256:self.modelPath] isEqualToString:MuseModelSHA256]) {
        if (message) *message = @"默认模型 SHA-256 校验失败；服务未启动，请重新下载。";
        return NO;
    }
    NSString *server = [[self.resources stringByAppendingPathComponent:@"llama"] stringByAppendingPathComponent:@"llama-server"];
    if (![[NSFileManager defaultManager] isExecutableFileAtPath:server]) {
        if (message) *message = @"应用包缺少模型运行时，请重新安装。";
        return NO;
    }
    @synchronized (self) {
        if (self.stopped) { if (message) *message = @"本应用服务已停止；重新打开 Muse 后可恢复。"; return NO; }
        if (self.ownedServer.isRunning) { if (message) *message = @"本应用模型服务已在运行。"; return YES; }
        if ([self portInUse]) {
            if (message) *message = @"8080 端口已有服务；Muse 不会接管或停止它。请确认服务身份。";
            return NO;
        }
        NSTask *serverTask = [[NSTask alloc] init];
        serverTask.launchPath = server;
        serverTask.arguments = @[@"-m", self.modelPath, @"--host", @"127.0.0.1", @"--port", @"8080",
                                 @"--ctx-size", @"4096", @"--reasoning", @"off", @"--alias", @"qwen3-0.6b"];
        NSMutableDictionary *environment = [[[NSProcessInfo processInfo] environment] mutableCopy];
        environment[@"DYLD_LIBRARY_PATH"] = [self.resources stringByAppendingPathComponent:@"llama"];
        serverTask.environment = environment;
        serverTask.standardOutput = [NSFileHandle fileHandleWithNullDevice];
        serverTask.standardError = [NSFileHandle fileHandleWithNullDevice];
        @try {
            [serverTask launch];
            self.ownedServer = serverTask;
            if (message) *message = @"本应用模型服务正在启动。";
            return YES;
        } @catch (NSException *exception) {
            if (message) *message = @"模型服务启动失败；请检查安装包或端口。";
            return NO;
        }
    }
}

- (void)stopOwnedServer {
    @synchronized (self) {
        self.stopped = YES;
        if (self.ownedServer.isRunning) [self.ownedServer terminate];
        self.ownedServer = nil;
    }
}

@end
