#import <Cocoa/Cocoa.h>

@interface MuseModelManager : NSObject <NSURLSessionDownloadDelegate>
@property(nonatomic, readonly, copy) NSString *modelPath;
@property(nonatomic, readonly, strong) NSTask *ownedServer;
@property(nonatomic, copy) void (^progress)(int64_t received, int64_t expected);
@property(nonatomic, copy) void (^completion)(BOOL installed, NSString *message);
- (instancetype)initWithResources:(NSString *)resources support:(NSString *)support;
- (BOOL)modelInstalled;
- (void)downloadDefault;
- (void)cancelDownload;
- (BOOL)startOwnedServer:(NSString **)message;
- (void)stopOwnedServer;
@end
