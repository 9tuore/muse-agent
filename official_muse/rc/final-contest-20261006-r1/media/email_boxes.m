#import <Foundation/Foundation.h>
#import <Vision/Vision.h>
int main(int argc, const char **argv) {
    @autoreleasepool {
        NSMutableDictionary *result = [NSMutableDictionary new];
        for (int i=1; i<argc; i++) { @autoreleasepool {
            NSString *path = @(argv[i]);
            VNRecognizeTextRequest *request = [VNRecognizeTextRequest new];
            request.recognitionLevel = VNRequestTextRecognitionLevelAccurate;
            request.recognitionLanguages = @[@"zh-Hans", @"en-US"];
            request.usesLanguageCorrection = NO;
            NSError *error = nil;
            VNImageRequestHandler *handler = [[VNImageRequestHandler alloc] initWithURL:[NSURL fileURLWithPath:path] options:@{}];
            if (![handler performRequests:@[request] error:&error]) { return 2; }
            NSMutableArray *boxes = [NSMutableArray new];
            for (VNRecognizedTextObservation *observation in request.results) {
                NSString *text = [[observation topCandidates:1] firstObject].string;
                NSString *lower = text.lowercaseString;
                if ([text containsString:@"@"] || [lower containsString:@"qq.com"] || [lower containsString:@"gmail.com"]) {
                    CGRect b = observation.boundingBox;
                    [boxes addObject:@[@(b.origin.x), @(1-b.origin.y-b.size.height), @(b.size.width), @(b.size.height)]];
                }
            }
            result[path] = boxes;
        }}
        NSData *data = [NSJSONSerialization dataWithJSONObject:result options:NSJSONWritingSortedKeys error:nil];
        [[NSFileHandle fileHandleWithStandardOutput] writeData:data];
    }
    return 0;
}
