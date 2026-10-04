#import <Foundation/Foundation.h>

// Boundary regression for EventKit's native JSON bridge. No EventKit calls,
// permission requests or system writes occur in this Foundation-only test.
int main(void) {
    @autoreleasepool {
        for (NSNumber *input in @[@0, @100, @101]) {
            NSUInteger count = input.unsignedIntegerValue;
            NSUInteger limit = 100;
            NSDictionary *values = @{
                @"count": input,
                @"original": @(count > limit),
                @"fixed": count > limit ? @YES : @NO
            };
            NSError *error = nil;
            NSData *encoded = [NSJSONSerialization dataWithJSONObject:values options:0 error:&error];
            if (!encoded || error) return 1;
            NSDictionary *readback = [NSJSONSerialization JSONObjectWithData:encoded options:0 error:&error];
            if (!readback || error) return 2;
            if (CFGetTypeID((__bridge CFTypeRef)readback[@"fixed"]) != CFBooleanGetTypeID()) return 3;
            if ([readback[@"fixed"] boolValue] != (count > limit)) return 4;
            if (CFGetTypeID((__bridge CFTypeRef)readback[@"original"]) == CFBooleanGetTypeID()) return 5;
            puts([[NSString alloc] initWithData:encoded encoding:NSUTF8StringEncoding].UTF8String);
        }
    }
    return 0;
}
