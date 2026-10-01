#import <AppKit/AppKit.h>
#include <stdlib.h>

int main(int argc, char **argv) {
    if (argc != 2) return 2;
    pid_t target = (pid_t)atoi(argv[1]);
    @autoreleasepool {
        NSRunningApplication *app = [NSRunningApplication runningApplicationWithProcessIdentifier:target];
        if (!app) return 3;
        return [app activateWithOptions:NSApplicationActivateAllWindows] ? 0 : 4;
    }
}
