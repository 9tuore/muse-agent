#include <ApplicationServices/ApplicationServices.h>
#include <stdio.h>
#include <stdlib.h>
int main(int argc, char **argv) {
    if (argc != 2) return 2;
    int wanted = atoi(argv[1]);
    CFArrayRef rows = CGWindowListCopyWindowInfo(kCGWindowListOptionAll, kCGNullWindowID);
    if (!rows) return 2;
    int largest_id = 0;
    double largest_area = 0;
    for (CFIndex i = 0; i < CFArrayGetCount(rows); i++) {
        CFDictionaryRef row = (CFDictionaryRef)CFArrayGetValueAtIndex(rows, i);
        int pid = 0, id = 0;
        CFNumberRef owner = CFDictionaryGetValue(row, kCGWindowOwnerPID);
        CFNumberRef number = CFDictionaryGetValue(row, kCGWindowNumber);
        CFDictionaryRef bounds = CFDictionaryGetValue(row, kCGWindowBounds);
        CGRect rect;
        if (owner && number && bounds && CFNumberGetValue(owner, kCFNumberIntType, &pid)
            && pid == wanted && CFNumberGetValue(number, kCFNumberIntType, &id)
            && CGRectMakeWithDictionaryRepresentation(bounds, &rect)
            && rect.size.width >= 400 && rect.size.height >= 300
            && rect.size.width * rect.size.height > largest_area) {
            largest_area = rect.size.width * rect.size.height;
            largest_id = id;
        }
    }
    CFRelease(rows);
    if (largest_id) printf("%d\n", largest_id);
    return 0;
}
