#!/usr/bin/env python3
"""Narrow existing Memory DSL forget and scope variants; actual jailed storage."""
import argparse,hashlib,json,os,shutil,socket,subprocess,sys,time
from pathlib import Path
from urllib.request import urlopen
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
HOST=ROOT/'official_muse/rc/packaging/.local-state/chunk-delta-r2/Muse Chunk RC Card Host.app/Contents/MacOS/card-host'
SOURCE=HERE/'capacity-relation-short-circuit-r1/readable'
EXPECTED='5e9318464390741f31c5deb12cf94571521aefd22efe2d02d1731ba0174c6f0a'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def third_process(first,out,regression_run):
    with socket.socket() as s:assert s.connect_ex(('127.0.0.1',8509))!=0,'Existing process protected'
    code=(first/'bundle/main.splash').read_text();assert code.count('let cc_phase="first"')==1
    bundle=out/'forgotten-bundle';shutil.copytree(first/'bundle',bundle)
    (bundle/'main.splash').write_text(code.replace('let cc_phase="first"','let cc_phase="forgotten"'))
    state=first/'state';target=state/'muse-goals/probe.json';target.unlink()
    env=dict(os.environ,MAKEPAD_REMOTE='8509',MAKEPAD_HIDE_WINDOWS='1');env.pop('MAKEPAD_FOCUS',None)
    with (out/'forgotten-runtime.log').open('w') as log:
        proc=subprocess.Popen([str(HOST),'--bundle',str(bundle),'--app-data',str(state),'--allow-unsigned','--stamp','--size','600x700'],cwd=HOST.parents[2],env=env,stdout=log,stderr=log)
        try:
            deadline=time.monotonic()+25
            while not target.exists():
                if proc.poll() is not None or time.monotonic()>deadline:raise RuntimeError('No forgotten-process probe; logs preserved')
                time.sleep(.1)
            time.sleep(.1);r=json.loads(target.read_text());runtime=(out/'forgotten-runtime.log').read_text()
            if '[E]' in runtime or 'script time budget exceeded' in runtime:raise RuntimeError('Forgotten-process runtime error; logs/probe preserved')
            r['failed']=[k for k,v in r.items() if isinstance(v,bool) and not v];r['passed']=sum(isinstance(v,bool) and v for v in r.values())
            (out/'forgotten-report.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');return r
        finally:
            try:urlopen('http://127.0.0.1:8509/quit',timeout=2).read()
            except OSError:proc.terminate()
            try:proc.wait(timeout=5)
            except subprocess.TimeoutExpired:proc.kill();proc.wait()
def main():
    assert sha(SOURCE/'main.splash')==EXPECTED
    assert sha(HOST)=='52768f5750b51574c892f7d51dbf33422511c0a615bd2027687e34874e0c6837'
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',default='forget-final-r1')
    parser.add_argument('--cases',nargs='+',choices=['choose_old','other_project','other_owner'],default=['choose_old','other_project','other_owner'])
    parser.add_argument('--settle-save-activity',action='store_true')
    args=parser.parse_args()
    out=HERE/args.out;assert out.parent==HERE and not out.exists();out.mkdir()
    readable=out/'readable';shutil.copytree(SOURCE,readable);compact=out/'compact'
    c=subprocess.run([sys.executable,str(ROOT/'official_muse/ui_memory/compact_bundle.py'),'--source',str(readable),'--out',str(compact)],check=True,capture_output=True,text=True)
    (out/'compact-binding.json').write_text(c.stdout);assert sha(compact/'main.splash')=='4ce3a734d94e1cedea8260f9b74ca54ce2a8339d0db2e6200f702b5f2bb71ee6'
    os.environ['MUSE_CARD_HOST']=str(HOST);sys.path.insert(0,str(ROOT/'official_muse/ui_memory/tests'));sys.path.insert(0,str(ROOT/'official_muse/rc/core_chain'))
    import regression_run
    from run_calendar_clarification import restart
    old=ROOT/'official_muse/rc/core_chain/morning-memory-resolve-r1/probe.splash';template=old.read_text()
    if args.settle_save_activity:
        assert template.count('    start_timeout(0.03,|| rr_before())')==1
        template=template.replace('    start_timeout(0.03,|| rr_before())','    start_timeout(0.15,|| rr_before())')
    isolation='''
    if rr_case=="other_project" || rr_case=="other_owner" {
        let ctx=gm_context("合成事实","synthetic-isolation","")
        rr_checks.original_scope_only=ctx.hits.len()==1 && ctx.hits[0].id==rr_old && ctx.text.search(rr_new_value)<0
        if rr_case=="other_project" {gm_set_focus("synthetic-other-project","synthetic-owner")}
        else {gm_set_focus("synthetic-project","synthetic-other-owner")}
        ctx=gm_context("合成事实","synthetic-isolation","")
        rr_checks.other_scope_only=ctx.hits.len()==1 && ctx.hits[0].id==rr_new && ctx.text.search(rr_old_value)<0
        gm_set_focus("synthetic-project","synthetic-owner")
    }
'''
    assert template.count('    start_timeout(0.03,|| rr_resolve())')==1
    template=template.replace('    start_timeout(0.03,|| rr_resolve())',isolation+'    start_timeout(0.03,|| rr_resolve())')
    forgotten='''
fn rr_forgotten_restore(){
    let before=fs.read("memory.json") let backup=fs.read("memory.backup.json")
    rr_baseline=fs.read("resolve-baseline.json").parse_json()
    rr_old=rr_baseline.old_id rr_new=rr_baseline.new_id rr_keep=rr_baseline.keep_id rr_other=rr_baseline.other_id
    let i=core_memory_index(rr_keep,"local") let j=core_memory_index(rr_other,"local")
    rr_checks.restore_deleted=memory[i].document.payload.deleted && memory[j].document.payload.deleted
    rr_checks.restore_history_cleared=memory[i].history.len()==0 && memory[j].history.len()==0
        && memory[i].source_history.len()==0 && memory[j].source_history.len()==0
        && memory[i].document.payload.source_ids.len()==0 && memory[j].document.payload.source_ids.len()==0
    let sources_clean=true for source in memory_sources {if source.support_excerpt!="" {sources_clean=false}}
    rr_checks.restore_sources_clean=sources_clean
    rr_checks.restore_all_tombstones=gm_forgotten_text(rr_initial,"local") && gm_forgotten_text(rr_old_value,"local") && gm_forgotten_text(rr_new_value,"local")
    rr_checks.restore_no_retrieval=gm_context("合成事实","synthetic-fresh-forgotten","").hits.len()==0
    rr_checks.restore_old_import_blocked=!gm_import(fs.read("before-explicit-forget-export.json")) && fs.read("memory.json")==before && fs.read("memory.backup.json")==backup
    rr_checks.restore_reindex_blocked=!gm_save(rr_old_value,"fact","different-subject","different-predicate","synthetic-new","synthetic-project","synthetic-owner","local")
        && fs.read("memory.json")==before && fs.read("memory.backup.json")==backup
    rr_checks.restore_same_clean_bytes=before==backup
    rr_finish()
}
'''
    template=template.replace('fn rr_probe(){',forgotten+'\nfn rr_probe(){',1)
    template=template.replace('    if cc_phase=="restart" {','    if cc_phase=="forgotten" {rr_forgotten_restore() return}\n    if cc_phase=="restart" {',1)
    (out/'probe-template.splash').write_text(template)
    report={'status':'RUNNING','source_sha256':EXPECTED,'compact_sha256':sha(compact/'main.splash'),'host_sha256':sha(HOST),'default_budget_unchanged':True,'fixture_only':True,'real_model':False,'real_external_actions':False,'production_data_used':False,'existing_probe_sha256':sha(old),'save_activity_settle_ms':150 if args.settle_save_activity else 30,'cases':{}}
    for case in args.cases:
        co=out/case;co.mkdir();probe=co/'probe.splash';probe.write_text(template.replace('__CASE__',case))
        try:
            first=regression_run.run_suite('mail_calendar_chain',(compact/'main.splash').read_text(),compact,co/'first',8509,probe)
            second=restart(co/'first',co) if not first['failed'] and case=='choose_old' else None
            third=third_process(co/'first',co,regression_run) if second is not None and not second['failed'] else None
            results=[first]+([second] if second else [])+([third] if third else [])
            result={'status':'PASS' if not any(r['failed'] for r in results) else 'FAIL','first':first,'second':second,'third':third}
        except Exception as e:result={'status':'ERROR','error':str(e)}
        report['cases'][case]=result;(out/'summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(case,result['status'],flush=True)
    report['status']='FIXTURE_PASS' if all(v['status']=='PASS' for v in report['cases'].values()) else 'FAIL'
    report['checks']=sum((v.get(k) or {}).get('passed',0) for v in report['cases'].values() for k in ['first','second','third'])
    (out/'summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');return int(report['status']!='FIXTURE_PASS')
if __name__=='__main__':raise SystemExit(main())
