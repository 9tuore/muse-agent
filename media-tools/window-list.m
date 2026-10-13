#import <Foundation/Foundation.h>
#import <CoreGraphics/CoreGraphics.h>
int main(int argc,const char**argv){@autoreleasepool{int pid=argc>1?atoi(argv[1]):0;NSArray *a=CFBridgingRelease(CGWindowListCopyWindowInfo(kCGWindowListOptionAll,kCGNullWindowID));for(NSDictionary*d in a){if(pid && [d[(__bridge id)kCGWindowOwnerPID]intValue]!=pid)continue;NSData*j=[NSJSONSerialization dataWithJSONObject:d options:0 error:nil];puts([[NSString alloc]initWithData:j encoding:NSUTF8StringEncoding].UTF8String);}}}
