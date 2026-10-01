#import <Cocoa/Cocoa.h>
#import "../app/muse_model_manager.h"

int main(int argc, const char *argv[]) {
    @autoreleasepool {
        if (argc != 2) return 2;
        NSString *root = [NSTemporaryDirectory() stringByAppendingPathComponent:[[NSUUID UUID] UUIDString]];
        NSString *models = [root stringByAppendingPathComponent:@"models"];
        [[NSFileManager defaultManager] createDirectoryAtPath:models withIntermediateDirectories:YES attributes:nil error:nil];
        MuseModelManager *manager = [[MuseModelManager alloc] initWithResources:[NSString stringWithUTF8String:argv[1]]
                                                                       support:root];
        [[NSFileManager defaultManager] createFileAtPath:manager.modelPath contents:nil attributes:nil];
        NSFileHandle *file = [NSFileHandle fileHandleForWritingAtPath:manager.modelPath];
        [file truncateFileAtOffset:639446688];
        [file closeFile];
        NSString *message = nil;
        BOOL installed = [manager modelInstalled];
        BOOL started = [manager startOwnedServer:&message];
        [manager stopOwnedServer];
        [[NSFileManager defaultManager] removeItemAtPath:root error:nil];
        if (!installed || started || [message rangeOfString:@"SHA-256 校验失败"].location == NSNotFound) {
            fprintf(stderr, "FAIL installed=%d started=%d message=%s\n", installed, started, message.UTF8String);
            return 1;
        }
        puts("PASS_LOCAL size-matched corrupt GGUF refused before service launch");
        return 0;
    }
}
