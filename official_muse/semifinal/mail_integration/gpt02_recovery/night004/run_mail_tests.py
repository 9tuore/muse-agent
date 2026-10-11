#!/usr/bin/env python3
"""Run actual production crate unit tests, one process per filter with synthetic state."""
import argparse,hashlib,json,os,re,subprocess
from pathlib import Path
P=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--binary',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
exe=a.binary.resolve(strict=True);out=a.out.resolve();out.relative_to(P.parents[4]/'build');out.mkdir(parents=True,exist_ok=False)
tmp=out/'synthetic-state';tmp.mkdir()
env=dict(os.environ,NIGHT004_TMP_ROOT=str(tmp),NIGHT004_RECEIVER_SCRIPT=str(P/'receiver.py'),TMPDIR=str(tmp))
listing=subprocess.run([str(exe),'--list'],capture_output=True,text=True,check=True).stdout
(out/'listed-tests.txt').write_text(listing)
filters=['night004_l2::'+n for n in ['l2_compose_edit_reject_cancel_accept_independent_recipient','l2_known_failure_and_unknown_never_automatically_resubmit','l2_persist_failure_keeps_transport_and_recipient_untouched','l2_late_reply_after_origin_closed_does_not_resend_or_publish','l2_claim_guard_rejection_and_removed_grant_prevent_transport','l2_real_process_restart_retains_same_id_without_resubmission']]
filters+=['drafts::tests::'+n for n in ['unknown_error_and_restart_are_not_automatic_retries','edited_public_composer_invalidates_review_and_exact_snapshot_sends_once','public_review_rechecks_grant_expiry_and_preserves_uncertain_outcome','failure_to_persist_claim_prevents_transport','simultaneous_review_cannot_resubmit_and_network_wait_does_not_hold_draft_lock','composer_returns_host_identity_and_cas_preserves_thread_binding','delayed_approval_worker_rechecks_host_selection_at_atomic_claim']]
filters+=['public_review::tests::discovery_distinguishes_staging_from_physical_review_and_hides_sheet_controls','tests::an_app_signs_in_reads_without_the_password_and_cannot_bypass_send_review']
results=[]
for i,name in enumerate(filters):
 assert name+': test' in listing,name
 cmd=[str(exe),'--exact',name,'--nocapture','--test-threads=1']
 r=subprocess.run(cmd,capture_output=True,text=True,env=env,timeout=45)
 log=r.stdout+r.stderr;(out/('%02d.txt'%i)).write_text(log)
 count=re.search(r'test result: \w+\. (\d+) passed; (\d+) failed;',log)
 row={'name':name,'exit_code':r.returncode,'passed':int(count[1]) if count else 0,'failed':int(count[2]) if count else None,'log':'%02d.txt'%i,'command':cmd}
 results.append(row);print(json.dumps(row),flush=True)
 (out/'results.json').write_text(json.dumps({'kind':'REAL_PRODUCTION_MAIL_RUST_WITH_SYNTHETIC_DEPENDENCIES','binary_sha256':hashlib.sha256(exe.read_bytes()).hexdigest(),'results':results,'real_smtp_calls':0,'real_keychain_calls':0,'native_physical_input':'fixture true/true only; no OS approval','shell_guard':'unchanged source; Shell runtime not part of this crate test'},indent=2)+'\n')
 if r.returncode!=0:raise SystemExit(1)
assert len(results)==15 and all(r['passed']==1 and r['failed']==0 for r in results)
