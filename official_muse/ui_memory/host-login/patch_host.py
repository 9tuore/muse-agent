#!/usr/bin/env python3
"""Apply only the mail sheet/account parsing change to the isolated source copy."""
import difflib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
provenance = json.loads((HERE / 'source_provenance.json').read_text())
rel = 'apps/mail/host-service/src/lib.rs'
origin = Path(provenance['source']) / rel
target = Path(provenance['isolated_source']) / rel
before = origin.read_text()
assert hashlib.sha256(origin.read_bytes()).hexdigest() == provenance['baseline_sha256'][rel]
assert target.read_text() == before, 'isolated source already modified'
after = before.replace('["address", "username", "password", "host", "port", "security", "smtp_host", "smtp_port", "smtp_security"]',
                       '["address", "password", "host", "port", "security", "smtp_host", "smtp_port", "smtp_security"]', 1)
after = after.replace('    if text(&account, "username").is_empty() {\n        account["username"] = account["address"].clone();\n    }',
                      '    // New sign-ins always use the full email; stored legacy usernames remain compatible.\n    account["username"] = account["address"].clone();', 1)
after = after.replace('address: ui.address.text() username: ui.username.text()', 'address: ui.address.text().trim()', 1)
lines = after.splitlines(keepends=True)
index = next(i for i, line in enumerate(lines) if 'username := Field{' in line)
assert 'Caption{' in lines[index-1]
del lines[index-1:index+1]
after = ''.join(lines)
after = after.replace('\u5bc6\u7801\u6216\u90ae\u7bb1\u5e94\u7528\u4e13\u7528\u5bc6\u7801', '\u5bc6\u7801\u6216\u6388\u6743\u7801', 1)
after = after.replace('\u8bf7\u8f93\u5165\u5bc6\u7801', '\u8bf7\u8f93\u5165\u5bc6\u7801\u6216\u6388\u6743\u7801', 1)
tests = '''    #[test]
    fn new_signins_use_trimmed_email_and_ignore_separate_username() {
        for protocol in ["imap", "pop3"] {
            let account = account_from_form(&json!({
                "address": "  reader@example.com  ", "username": "different-login-name",
                "password": " fixture-only-value ", "protocol": protocol,
            })).unwrap();
            assert_eq!(account["address"], "reader@example.com");
            assert_eq!(account["username"], "reader@example.com");
            assert_eq!(account["password"], " fixture-only-value ");
            assert_eq!(account["protocol"], protocol);
        }
    }

    #[test]
    fn signin_sheet_has_no_username_widget_or_binding() {
        let sheet = signin_sheet();
        assert!(!sheet.contains("username :="));
        assert!(!sheet.contains("ui.username"));
        assert!(sheet.contains("address: ui.address.text().trim()"));
        assert!(sheet.contains("password: ui.password.text()"));
        assert!(sheet.contains("is_password: true"));
    }

    #[test]
    fn missing_email_does_not_report_an_uneditable_username_error() {
        let error = account_from_form(&json!({"address": "  ", "password": "fixture-only-value"})).unwrap_err();
        assert!(error.contains("\\u{90ae}\\u{7bb1}\\u{5730}\\u{5740}"));
        assert!(!error.contains("\\u{7528}\\u{6237}\\u{540d}"));
    }

'''
mark = '    /// A mailbox in memory: `test` checks the password'
assert after.count(mark) == 1
after = after.replace(mark, tests + mark, 1)
assert 'ui.username' not in after[:after.index('#[cfg(test)]')]
target.write_text(after)
patch = ''.join(difflib.unified_diff(before.splitlines(keepends=True), after.splitlines(keepends=True),
                                   fromfile='a/'+rel, tofile='b/'+rel))
(HERE / 'mail-login-simplification.patch').write_text(patch)
print(json.dumps(dict(baseline_sha256=hashlib.sha256(before.encode()).hexdigest(),
                      patched_sha256=hashlib.sha256(after.encode()).hexdigest(),
                      patch_sha256=hashlib.sha256(patch.encode()).hexdigest(), changed_file=rel)))
