#!/usr/bin/env python3
"""Verify saved timings against real VM mark requests and persisted production records; no rerun."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import statistics

HERE=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--evidence',type=Path,default=HERE/'evidence/baseline-r1')
parser.add_argument('--source-sha',default='c892bff3a0148e78727d257acc8bb381258b6b01c3f6dcfb9b4888a0aac22ae4')
parser.add_argument('--export-directory',default='gui-scale-export-r2')
args=parser.parse_args()
evidence=args.evidence.resolve();evidence.relative_to(HERE/'evidence')
export_directory=evidence/args.export_directory;export_directory.resolve().relative_to(evidence)
load=lambda name:json.loads((evidence/name).read_text())
sha=lambda data:hashlib.sha256(data).hexdigest()
report=load('report.json');rows=load('samples.json');identity=load('identity.json')
assert report['status']=='PASS' and not report['failed'] and all(value is True for value in report['checks'].values())
assert report['source_sha256']==identity['source_sha256']==args.source_sha
assert report['clock']['name']=='time.perf_counter_ns' and report['clock']['monotonic'] is True
assert identity['all_other_functions_byte_equal_after_transport_normalization'] is True
assert sha((evidence/'executed.splash').read_bytes())==identity['executed_sha256']
assert sha((evidence/'executed-parent-r1.py').read_bytes())==report['parent_sha256']
for name in ['samples.json','executed.splash','identity.json','invocation.json','vm-stderr.log']:
    assert sha((evidence/name).read_bytes())==report['raw_file_sha256'][name]
markers=[json.loads(line[len('MUSE_VM_REQUEST '):])['payload'] for line in (evidence/'actual-perf-marker-requests.log').read_text().splitlines()]
assert len(markers)==2*len(rows)==204
for index,row in enumerate(rows):
    start,end=markers[index*2:index*2+2]
    for key in ['name','sample','warmup','iterations']:assert start[key]==end[key]==row[key]
    assert start['phase']=='start' and end['phase']=='end'
    assert row['elapsed_ns']==row['end_ns']-row['start_ns']>0
    expected={'fixture.perf_mark':1}
    if row['name']=='gm_context':expected.update({'fixture.clock':1,'fixture.fs.write':1})
    assert row['rpc_counts_within_interval']==expected
for name,summary in report['measurements'].items():
    selected=[row for row in rows if row['name']==name]
    values=sorted(row['elapsed_ns'] for row in selected if not row['warmup'])
    assert len(values)==summary['samples']==31 and len(selected)==34
    assert sorted(row['sample'] for row in selected if not row['warmup'])==list(range(31))
    assert summary['min_ms']==values[0]/1e6 and summary['max_ms']==values[-1]/1e6
    assert summary['median_ms']==statistics.median(values)/1e6 and summary['p95_ms']==values[math.ceil(.95*len(values))-1]/1e6
memory=load('main-state/memory.json');goals=load('main-state/goals.json');trace=load('main-state/memory-retrieval-last.json')
assert len(memory['claims'])==64 and len(memory['sources'])==128 and not memory['forget']
assert len(goals['goals'])==32 and len(goals['runs'])==32 and len(goals['actions'])==128
assert all(goal['status']=='running' for goal in goals['goals']) and all(run['status']=='running' for run in goals['runs'])
assert all(action['status']=='in_flight' for action in goals['actions'])
for goal in goals['goals']:
    runs=[run for run in goals['runs'] if run['goal_id']==goal['id']]
    actions=[action for action in goals['actions'] if action['goal_id']==goal['id']]
    assert len(runs)==1 and len(actions)==4
    assert all(action['run_id']==runs[0]['id'] and action['plan_revision']==goal['version']==runs[0]['plan_revision'] for action in actions)
assert len(trace['hits'])==5 and trace['bytes']==2125 and trace['truncated'] is True
assert trace['query_sha256']==sha('规模条目'.encode())
for hit in trace['hits']:
    entry=next(entry for entry in memory['claims'] if entry['document']['id']==hit['id'])
    assert entry['document']['scope']['project_id']=='fixture-project' and entry['document']['scope']['owner_id']=='fixture-owner'
observed=report['probe']['observations']
for name in ['goals','memory']:
    assert observed['before_'+name+'_sha256']==observed['after_'+name+'_sha256']==sha((evidence/'main-state'/(name+'.json')).read_bytes())
for name,expected in report['state_sha256'].items():assert sha((evidence/'main-state'/name).read_bytes())==expected
raw=load('raw-log-index.json')
assert raw['raw_stdout_sha256']==report['raw_file_sha256']['vm-stdout.log']
assert raw['marker_requests_sha256']==sha((evidence/'actual-perf-marker-requests.log').read_bytes())
assert not report['unknown_calls'] and report['full_chain_status']=='NOT_TESTED'
export=load(args.export_directory+'/manifest.json');scopes=load(args.export_directory+'/scope.json')
assert export['status']=='PASS' and export['source_run_report_sha256']==sha((evidence/'report.json').read_bytes())
assert export['exporter_sha256']==sha((export_directory/'executed-exporter-r2.py').read_bytes())
assert export['scope_sha256']==sha((export_directory/'scope.json').read_bytes())
assert export['completed_records']==export['verified_records']==0 and export['synthetic_literal_text_only'] is True
assert export['private_profile_or_credentials_read'] is False and export['gui_import_status']=='NOT_TESTED'
assert set(export['absent_whitelist_files'])=={'chat-sessions.json','chat-sessions.backup.json'}
assert len(export['files'])==8
for item in export['files']:
    assert item['byte_identical'] is True and item['sha256']==sha((evidence/'main-state'/item['file']).read_bytes())
assert sum(row['records'] for row in scopes['memory'])==64 and sum(row['records'] for row in scopes['sources'])==128
assert scopes['current_fixture_scope']['user_id']=='user:profile:1-2-3-4'
print(json.dumps(dict(status='PASS',saved_runtime_checks=len(report['checks']),measured_samples_per_api=31,warmups_per_api=3,
    verified='Real VM mark pairs, parent nanoseconds/statistics, actual persisted API-generated scoped records and no completion',boundary='Saved evidence only; no extra runtime count or new candidate performance claim.')))
