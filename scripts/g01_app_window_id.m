#include <ApplicationServices/ApplicationServices.h>
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv) {
    if (argc != 2) return 2;
    pid_t target = (pid_t)atoi(argv[1]);
    CFArrayRef windows = CGWindowListCopyWindowInfo(kCGWindowListOptionAll, kCGNullWindowID);
    if (!windows) return 3;
    int best_number = 0;
    double best_area = 0;
    CGRect best_rect = CGRectZero;
    int best_onscreen = 0;
    for (CFIndex i = 0; i < CFArrayGetCount(windows); i++) {
        CFDictionaryRef info = (CFDictionaryRef)CFArrayGetValueAtIndex(windows, i);
        CFNumberRef owner = (CFNumberRef)CFDictionaryGetValue(info, kCGWindowOwnerPID);
        CFNumberRef layer = (CFNumberRef)CFDictionaryGetValue(info, kCGWindowLayer);
        CFNumberRef number = (CFNumberRef)CFDictionaryGetValue(info, kCGWindowNumber);
        CFDictionaryRef bounds = (CFDictionaryRef)CFDictionaryGetValue(info, kCGWindowBounds);
        CFBooleanRef onscreen = (CFBooleanRef)CFDictionaryGetValue(info, kCGWindowIsOnscreen);
        if (!owner || !layer || !number || !bounds) continue;
        int pid = 0, window_layer = 0, window_number = 0;
        CGRect rect = CGRectZero;
        CFNumberGetValue(owner, kCFNumberIntType, &pid);
        CFNumberGetValue(layer, kCFNumberIntType, &window_layer);
        CFNumberGetValue(number, kCFNumberIntType, &window_number);
        if (!CGRectMakeWithDictionaryRepresentation(bounds, &rect)) continue;
        double area = rect.size.width * rect.size.height;
        if (pid == target) fprintf(stderr, "window=%d layer=%d width=%.0f height=%.0f onscreen=%d\n",
                                   window_number, window_layer, rect.size.width, rect.size.height,
                                   onscreen == kCFBooleanTrue);
        if (pid == target && window_layer == 0 && rect.size.width >= 300 &&
            rect.size.height >= 200 && area > best_area) {
            best_number = window_number;
            best_area = area;
            best_rect = rect;
            best_onscreen = onscreen == kCFBooleanTrue;
        }
    }
    CFRelease(windows);
    if (!best_number) return 3;
    printf("%d %.0f %.0f %.0f %.0f %d\n", best_number, best_rect.origin.x,
           best_rect.origin.y, best_rect.size.width, best_rect.size.height,
           best_onscreen);
    return 0;
}
