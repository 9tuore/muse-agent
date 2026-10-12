#!/usr/bin/env python3
"""Compile and execute the actual create-only profile and port helper functions."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

p = argparse.ArgumentParser()
p.add_argument('--source', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
a.output.mkdir(parents=True, exist_ok=False)
with tempfile.TemporaryDirectory(prefix='muse-create-only-') as temp:
    work = Path(temp)
    wrapper = work / 'wrapper.m'
    wrapper.write_text('#define main muse_launcher_original_main\n#include ' + json.dumps(str(a.source.resolve()), ensure_ascii=False) + '\n#undef main\n' + r'''
int main(int argc, const char **argv) {
    @autoreleasepool {
        NSString *path = [NSString stringWithUTF8String:argv[1]];
        NSError *error = nil;
        BOOL created = createLocalProfile(path, @"http://127.0.0.1:54321", &error);
        NSData *first = [NSData dataWithContentsOfFile:path];
        BOOL duplicate = createLocalProfile(path, @"http://127.0.0.1:54322", &error);
        NSData *after = [NSData dataWithContentsOfFile:path];
        NSDictionary *llm = modelMetadata(path);
        NSDictionary *selection = bundledLocalSelection(llm);
        NSArray *ports = @[
            @(registeredLocalPort(@{})),
            @(registeredLocalPort(@{@"route":@{@"base_url":@"http://127.0.0.1:54321/v1", @"api_type":@"openai"}})),
            @(registeredLocalPort(@{@"route":@{@"base_url":@"http://127.0.0.1:54321/v1/"}})),
            @(registeredLocalPort(@{@"route":@{@"base_url":@"https://127.0.0.1:54321/v1"}})),
            @(registeredLocalPort(@{@"route":@{@"base_url":@"http://example.invalid:54321/v1"}})),
            @(registeredLocalPort(@{@"route":@{@"base_url":@"http://127.0.0.1:54321/v1?x=1"}})),
            @(registeredLocalPort(@{@"route":@{@"api_type":@"responses"}})),
            @(registeredLocalPort(@{@"route":@{@"base_url":@"http://127.0.0.1:0/v1"}}))];
        BOOL portsOK = [ports isEqual:@[@8080,@54321,@54321,@-1,@-1,@-1,@-1,@-1]];
        struct stat st; stat(path.fileSystemRepresentation, &st);
        BOOL stable = created && !duplicate && error.code == EEXIST && [first isEqualToData:after];
        BOOL roundtrip = [selection[@"model_id"] isEqual:bundledModelID]
            && [selection[@"route"][@"base_url"] isEqual:@"http://127.0.0.1:54321/v1"];
        NSDictionary *result = @{@"create_only":@(stable), @"metadata_readback":@(roundtrip),
            @"private_mode":@((st.st_mode & 0777) == 0600), @"port_validation":@(portsOK), @"ports":ports};
        NSData *data = [NSJSONSerialization dataWithJSONObject:result options:0 error:nil];
        puts([[NSString alloc] initWithData:data encoding:NSUTF8StringEncoding].UTF8String);
        return stable && roundtrip && portsOK && (st.st_mode & 0777) == 0600 ? 0 : 1;
    }
}
''')
    build = subprocess.run(['clang', '-fobjc-arc', '-O2', '-framework', 'AppKit', str(wrapper), '-o', str(work/'check')], capture_output=True, text=True)
    (a.output/'build.log').write_text(build.stdout + build.stderr)
    if build.returncode:
        raise SystemExit(build.returncode)
    run = subprocess.run([str(work/'check'), str(work/'profile.json')], capture_output=True, text=True)
    (a.output/'run.log').write_text(run.stdout + run.stderr)
    result = json.loads(run.stdout)
    result.update(source_sha256=hashlib.sha256(a.source.read_bytes()).hexdigest(),
                  status='PASS' if run.returncode == 0 else 'FAIL', level='ACTUAL_COMPILED_PROFILE_HELPERS')
    (a.output/'receipt.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(result))
    raise SystemExit(run.returncode)
