#import <Cocoa/Cocoa.h>
#import "../app/muse_model_manager.h"

int main(int argc, const char *argv[]) {
    @autoreleasepool {
        if (argc != 2) return 2;
        NSString *source = [NSString stringWithUTF8String:argv[1]];
        NSString *root = [NSTemporaryDirectory() stringByAppendingPathComponent:[[NSUUID UUID] UUIDString]];
        NSString *models = [root stringByAppendingPathComponent:@"models"];
        NSFileManager *files = [NSFileManager defaultManager];
        [files createDirectoryAtPath:models withIntermediateDirectories:YES attributes:nil error:nil];
        MuseModelManager *manager = [[MuseModelManager alloc] initWithResources:@"/unused" support:root];
        NSError *error = nil;
        if (![files linkItemAtPath:source toPath:manager.modelPath error:&error]) {
            fprintf(stderr, "hardlink failed: %s\n", error.localizedDescription.UTF8String);
            return 2;
        }
        __block BOOL called = NO;
        __block BOOL reused = NO;
        __block NSString *note = nil;
        manager.completion = ^(BOOL installed, NSString *message) {
            called = YES;
            reused = installed;
            note = message;
        };
        [manager downloadDefault];
        if (!called) [manager cancelDownload];
        [files removeItemAtPath:root error:nil];
        if (!called || !reused || [note rangeOfString:@"已验证，可直接使用"].location == NSNotFound) {
            fprintf(stderr, "FAIL called=%d reused=%d message=%s\n", called, reused, note.UTF8String);
            return 1;
        }
        puts("PASS_LOCAL SHA-valid existing GGUF reused without download");
        return 0;
    }
}
