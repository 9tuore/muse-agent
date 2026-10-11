#!/usr/bin/env python3
"""Generate a proposal only; never modify formal main.splash."""
from pathlib import Path
import difflib, hashlib, json
ROOT = Path(__file__).resolve().parents[4]
OWN = Path(__file__).resolve().parent
p = ROOT/'official_muse/app/source/main.splash'
old = p.read_text()
helper = '''// Reconcile only an exact terminal Host attempt; never authorize a retry.
fn mail_host_receipt_status(data){
    if !gm_object(data) || !gm_array(data["attempts"]) || data.attempts.len() == 0 { return "unknown" }
    let attempt = data.attempts[data.attempts.len() - 1]
    if !gm_object(attempt) || !gm_string(attempt["operation_id"],128) || attempt.operation_id == ""
        || attempt["revision"] != data["revision"] || attempt["status"] != data["status"]
        || !gm_object(attempt["payload"]) || attempt.payload["to"] != data["to"]
        || attempt.payload["subject"] != data["subject"] || attempt.payload["body"] != data["body"] { return "unknown" }
    if data["status"] == "accepted" && gm_object(attempt["receipt"])
        && attempt.receipt["accepted"] == true { return "accepted" }
    if data["status"] == "failed_before_delivery" {
        if gm_object(attempt["receipt"]) && attempt.receipt["accepted"] == true { return "unknown" }
        return "failed_before_delivery"
    }
    return "unknown"
}

'''
a = 'fn mail_check_host_status(){'
assert old.count(a) == 1
new = old.replace(a,helper+a,1)
oldbranch = '''        if r.data["status"] != "accepted" { mail_notice = "原记录尚未确认受理；继续保留，不自动重发。" mail_redraw() return }
        let context = {request_id: requested goal_id: mail_draft.link_goal_id run_id: mail_draft.link_run_id
            snapshot: snapshot accepted: true unsent: false}'''
newbranch = '''        let terminal = mail_host_receipt_status(r.data)
        if terminal == "unknown" { mail_notice = "原记录尚未确认受理；继续保留，不自动重发。" mail_redraw() return }
        let context = {request_id: requested goal_id: mail_draft.link_goal_id run_id: mail_draft.link_run_id
            snapshot: snapshot accepted: terminal == "accepted" unsent: terminal == "failed_before_delivery"
            notice: "官方回执确认投递前失败，正文仍保留；不会自动重发。"}'''
assert new.count(oldbranch)==1
new=new.replace(oldbranch,newbranch,1)
patch=''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/official_muse/app/source/main.splash',tofile='b/official_muse/app/source/main.splash',n=0))
(OWN/'mail-terminal-recovery.patch').write_text(patch)
sha=lambda b:hashlib.sha256(b).hexdigest()
identity=dict(base_commit='e962e4183d844002a22e4f8c91268dfb5b004b19',source_sha256=sha(p.read_bytes()),patch_sha256=sha(patch.encode()),expected_source_sha256=sha(new.encode()),applied=False)
(OWN/'patch_identity.json').write_text(json.dumps(identity,indent=2)+'\n')
print(json.dumps(identity))
