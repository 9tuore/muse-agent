#include <Security/Security.h>
#include <CoreFoundation/CoreFoundation.h>
#include <stdio.h>
#include <stdlib.h>
#include <limits.h>
static void printString(const char *key, CFStringRef value) {
    char buf[8192] = {0};
    if (value && CFGetTypeID(value) == CFStringGetTypeID() && CFStringGetCString(value, buf, sizeof(buf), kCFStringEncodingUTF8))
        printf("%s=%s\n", key, buf);
    else printf("%s=\n", key);
}
int main(int argc, char **argv) {
    if (argc != 2) return 2;
    char *end = NULL; long n = strtol(argv[1], &end, 10);
    if (!end || *end || n <= 0 || n > INT_MAX) return 2;
    int pid = (int)n;
    CFNumberRef number = CFNumberCreate(kCFAllocatorDefault, kCFNumberIntType, &pid);
    const void *keys[] = { kSecGuestAttributePid };
    const void *values[] = { number };
    CFDictionaryRef attrs = CFDictionaryCreate(kCFAllocatorDefault, keys, values, 1, &kCFTypeDictionaryKeyCallBacks, &kCFTypeDictionaryValueCallBacks);
    SecCodeRef code = NULL;
    OSStatus guest = SecCodeCopyGuestWithAttributes(NULL, attrs, kSecCSDefaultFlags, &code);
    printf("pid=%d\nguest_status=%d\n", pid, (int)guest);
    if (guest != errSecSuccess) { CFRelease(attrs); CFRelease(number); return 1; }
    OSStatus valid = SecCodeCheckValidity(code, kSecCSDefaultFlags, NULL);
    printf("dynamic_validity_status=%d\n", (int)valid);
    CFDictionaryRef info = NULL;
    OSStatus copied = SecCodeCopySigningInformation(code, kSecCSSigningInformation, &info);
    printf("signing_information_status=%d\n", (int)copied);
    if (copied == errSecSuccess && info) {
        printString("identifier", CFDictionaryGetValue(info, kSecCodeInfoIdentifier));
        CFURLRef exe = (CFURLRef)CFDictionaryGetValue(info, kSecCodeInfoMainExecutable);
        CFStringRef path = exe ? CFURLCopyFileSystemPath(exe, kCFURLPOSIXPathStyle) : NULL;
        printString("main_executable", path);
        if (path) CFRelease(path);
        printf("secured_info_plist_present=%s\n", CFDictionaryContainsKey(info, kSecCodeInfoPList) ? "true" : "false");
        CFRelease(info);
    }
    CFRelease(code); CFRelease(attrs); CFRelease(number);
    return valid == errSecSuccess && copied == errSecSuccess ? 0 : 1;
}
