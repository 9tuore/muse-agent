#import <Foundation/Foundation.h>
#import <AVFoundation/AVFoundation.h>
#import <CoreGraphics/CoreGraphics.h>
#import <CoreVideo/CoreVideo.h>
#import <mach/mach_time.h>
#include <signal.h>
static volatile sig_atomic_t stopped=0;
static void stop_recording(int sig){stopped=1;}
static double seconds(){static mach_timebase_info_data_t t;if(!t.denom)mach_timebase_info(&t);return (double)mach_absolute_time()*t.numer/t.denom/1e9;}
int main(int argc,const char**argv){@autoreleasepool{
 if(argc!=4)return 2;signal(SIGINT,stop_recording);signal(SIGTERM,stop_recording);CGWindowID wid=(CGWindowID)strtoul(argv[1],NULL,10);double duration=atof(argv[2]);NSURL *url=[NSURL fileURLWithPath:@(argv[3])];
 if([[NSFileManager defaultManager]fileExistsAtPath:url.path])return 3;
 CGImageRef first=CGWindowListCreateImage(CGRectNull,kCGWindowListOptionIncludingWindow,wid,kCGWindowImageBoundsIgnoreFraming);if(!first)return 4;
 size_t w=CGImageGetWidth(first),h=CGImageGetHeight(first);CGImageRelease(first);w=w/2*2;h=h/2*2;
 NSError *error=nil;AVAssetWriter *writer=[[AVAssetWriter alloc]initWithURL:url fileType:AVFileTypeQuickTimeMovie error:&error];
 AVAssetWriterInput *input=[AVAssetWriterInput assetWriterInputWithMediaType:AVMediaTypeVideo outputSettings:@{AVVideoCodecKey:AVVideoCodecTypeH264,AVVideoWidthKey:@(w),AVVideoHeightKey:@(h),AVVideoCompressionPropertiesKey:@{AVVideoAverageBitRateKey:@10000000,AVVideoExpectedSourceFrameRateKey:@15}}];input.expectsMediaDataInRealTime=YES;
 AVAssetWriterInputPixelBufferAdaptor *adaptor=[AVAssetWriterInputPixelBufferAdaptor assetWriterInputPixelBufferAdaptorWithAssetWriterInput:input sourcePixelBufferAttributes:@{(id)kCVPixelBufferPixelFormatTypeKey:@(kCVPixelFormatType_32ARGB),(id)kCVPixelBufferWidthKey:@(w),(id)kCVPixelBufferHeightKey:@(h),(id)kCVPixelBufferCGImageCompatibilityKey:@YES,(id)kCVPixelBufferCGBitmapContextCompatibilityKey:@YES}];
 [writer addInput:input];if(![writer startWriting]){fprintf(stderr,"%s\n",writer.error.description.UTF8String);return 5;}[writer startSessionAtSourceTime:kCMTimeZero];
 double start=seconds(),next=0;int frames=0;printf("RECORDING window=%u size=%zux%zu unix=%.6f\n",wid,w,h,NSDate.date.timeIntervalSince1970);fflush(stdout);
 while(!stopped && seconds()-start<duration){@autoreleasepool{double elapsed=seconds()-start;if(elapsed<next){[NSThread sleepForTimeInterval:MIN(next-elapsed,.01)];continue;}next=elapsed+1.0/15;
 if(!input.readyForMoreMediaData)continue;CGImageRef image=CGWindowListCreateImage(CGRectNull,kCGWindowListOptionIncludingWindow,wid,kCGWindowImageBoundsIgnoreFraming);if(!image)break;
 CVPixelBufferRef pixel=NULL;CVPixelBufferPoolCreatePixelBuffer(NULL,adaptor.pixelBufferPool,&pixel);if(!pixel){CGImageRelease(image);break;}
 CVPixelBufferLockBaseAddress(pixel,0);CGColorSpaceRef cs=CGColorSpaceCreateDeviceRGB();CGContextRef ctx=CGBitmapContextCreate(CVPixelBufferGetBaseAddress(pixel),w,h,8,CVPixelBufferGetBytesPerRow(pixel),cs,kCGImageAlphaNoneSkipFirst);CGContextDrawImage(ctx,CGRectMake(0,0,w,h),image);CGContextRelease(ctx);CGColorSpaceRelease(cs);CGImageRelease(image);CVPixelBufferUnlockBaseAddress(pixel,0);
 BOOL ok=[adaptor appendPixelBuffer:pixel withPresentationTime:CMTimeMakeWithSeconds(elapsed,600)];CVPixelBufferRelease(pixel);if(!ok)break;frames++;
 }}
 duration=MIN(duration,seconds()-start);[input markAsFinished];[writer endSessionAtSourceTime:CMTimeMakeWithSeconds(duration,600)];__block BOOL done=NO;[writer finishWritingWithCompletionHandler:^{done=YES;}];while(!done){[[NSRunLoop currentRunLoop]runUntilDate:[NSDate dateWithTimeIntervalSinceNow:.05]];}
 if(writer.status!=AVAssetWriterStatusCompleted){fprintf(stderr,"%s\n",writer.error.description.UTF8String);return 6;}printf("SAVED frames=%d duration=%.3f\n",frames,duration);return 0;
}}
