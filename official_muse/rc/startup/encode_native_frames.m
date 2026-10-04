// Encode time-stamped captures from the real native Remote window.
// This evidence utility does not render app UI, call a model or perform actions.
#import <AppKit/AppKit.h>
#import <AVFoundation/AVFoundation.h>
#import <CoreVideo/CoreVideo.h>

int main(int argc, const char **argv) {
    @autoreleasepool {
        if (argc != 3) return 2;
        NSDictionary *manifest = [NSJSONSerialization JSONObjectWithData:
            [NSData dataWithContentsOfFile:@(argv[1])] options:0 error:nil];
        NSArray *frames = manifest[@"frames"];
        int width = [manifest[@"width"] intValue], height = [manifest[@"height"] intValue];
        if (!frames.count || width <= 0 || height <= 0 || width % 2 || height % 2) return 3;
        NSError *error = nil;
        AVAssetWriter *writer = [[AVAssetWriter alloc] initWithURL:
            [NSURL fileURLWithPath:@(argv[2])] fileType:AVFileTypeQuickTimeMovie error:&error];
        if (!writer) { fprintf(stderr, "%s\n", error.description.UTF8String); return 4; }
        AVAssetWriterInput *input = [AVAssetWriterInput assetWriterInputWithMediaType:AVMediaTypeVideo
            outputSettings:@{AVVideoCodecKey: AVVideoCodecTypeH264,
                AVVideoWidthKey: @(width), AVVideoHeightKey: @(height),
                AVVideoCompressionPropertiesKey: @{AVVideoAverageBitRateKey: @2500000}}];
        input.expectsMediaDataInRealTime = NO;
        NSDictionary *attributes = @{(id)kCVPixelBufferPixelFormatTypeKey: @(kCVPixelFormatType_32BGRA),
            (id)kCVPixelBufferWidthKey: @(width), (id)kCVPixelBufferHeightKey: @(height),
            (id)kCVPixelBufferCGImageCompatibilityKey: @YES,
            (id)kCVPixelBufferCGBitmapContextCompatibilityKey: @YES};
        AVAssetWriterInputPixelBufferAdaptor *adaptor =
            [AVAssetWriterInputPixelBufferAdaptor assetWriterInputPixelBufferAdaptorWithAssetWriterInput:
                input sourcePixelBufferAttributes:attributes];
        if (![writer canAddInput:input]) return 5;
        [writer addInput:input];
        if (![writer startWriting]) return 6;
        [writer startSessionAtSourceTime:kCMTimeZero];
        double previous = -1;
        for (NSDictionary *frame in frames) {
            @autoreleasepool {
                double seconds = [frame[@"time_seconds"] doubleValue];
                if (seconds < 0 || seconds <= previous) return 7;
                previous = seconds;
                NSBitmapImageRep *image = [[NSBitmapImageRep alloc] initWithData:
                    [NSData dataWithContentsOfFile:frame[@"file"]]];
                if (!image.CGImage) return 8;
                CVPixelBufferRef buffer = NULL;
                if (CVPixelBufferCreate(kCFAllocatorDefault, width, height, kCVPixelFormatType_32BGRA,
                        (__bridge CFDictionaryRef)attributes, &buffer) != kCVReturnSuccess) return 9;
                CVPixelBufferLockBaseAddress(buffer, 0);
                CGColorSpaceRef colors = CGColorSpaceCreateDeviceRGB();
                CGContextRef context = CGBitmapContextCreate(CVPixelBufferGetBaseAddress(buffer),
                    width, height, 8, CVPixelBufferGetBytesPerRow(buffer), colors,
                    kCGImageAlphaPremultipliedFirst | kCGBitmapByteOrder32Little);
                if (!context) return 10;
                CGContextDrawImage(context, CGRectMake(0, 0, width, height), image.CGImage);
                CGContextRelease(context); CGColorSpaceRelease(colors);
                CVPixelBufferUnlockBaseAddress(buffer, 0);
                NSDate *deadline = [NSDate dateWithTimeIntervalSinceNow:10];
                while (!input.readyForMoreMediaData && writer.status == AVAssetWriterStatusWriting
                        && deadline.timeIntervalSinceNow > 0) [NSThread sleepForTimeInterval:.01];
                BOOL ok = input.readyForMoreMediaData && [adaptor appendPixelBuffer:buffer
                    withPresentationTime:CMTimeMakeWithSeconds(seconds, 600)];
                CVPixelBufferRelease(buffer);
                if (!ok) return 11;
            }
        }
        [writer endSessionAtSourceTime:CMTimeMakeWithSeconds(previous + .5, 600)];
        [input markAsFinished];
        dispatch_semaphore_t done = dispatch_semaphore_create(0);
        [writer finishWritingWithCompletionHandler:^{ dispatch_semaphore_signal(done); }];
        if (dispatch_semaphore_wait(done, dispatch_time(DISPATCH_TIME_NOW, 15 * NSEC_PER_SEC))) return 12;
        if (writer.status != AVAssetWriterStatusCompleted) return 13;
        AVAssetImageGenerator *decoder = [[AVAssetImageGenerator alloc] initWithAsset:
            [AVAsset assetWithURL:[NSURL fileURLWithPath:@(argv[2])]]];
        CGImageRef decoded = [decoder copyCGImageAtTime:kCMTimeZero actualTime:nil error:&error];
        if (!decoded) return 14;
        NSBitmapImageRep *thumbnail = [[NSBitmapImageRep alloc] initWithCGImage:decoded];
        BOOL saved = [[thumbnail representationUsingType:NSBitmapImageFileTypePNG properties:@{}]
            writeToFile:[@(argv[2]) stringByAppendingString:@".first-frame.png"] atomically:YES];
        CGImageRelease(decoded);
        if (!saved) return 15;
        printf("Encoded %lu native frames; last timestamp %.3f seconds\n", frames.count, previous);
        return 0;
    }
}
