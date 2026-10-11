#!/usr/bin/env python3
"""Verify retained SDK stdio/raw bytes and persisted Main terminal state; no rerun."""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--evidence',type=Path,default=HERE/'evidence')
parser.add_argument('--source-sha',default='c892bff3a0148e78727d257acc8bb381258b6b01c3f6dcfb9b4888a0aac22ae4')
args=parser.parse_args()
evidence=args.evidence.resolve();evidence.relative_to(HERE/'evidence')
load = lambda path: json.loads(path.read_text())
sha = lambda data: hashlib.sha256(data).hexdigest()
summary = load(evidence / 'summary.json')
assert summary['status'] == 'PASS' and summary['checks'] == 54 and len(summary['cases']) == 3
assert summary['source_sha256'] == args.source_sha
assert summary['sdk_library_unchanged'] is True
assert sha((evidence/'executed-parent-r1.py').read_bytes()) == summary['parent_sha256']
build = load(evidence / 'build-identity.json')
assert sha((evidence/'executed-sdk-driver-r1.rs').read_bytes()) == build['driver_source_sha256']
for name, expected in build['sdk_source_sha256'].items():
    assert sha((evidence/'sdk-source'/name).read_bytes()) == expected
identity = load(evidence/'main-prepare/identity.json')
assert identity['source_sha256'] == summary['source_sha256']
assert identity['all_other_functions_byte_equal_after_transport_normalization'] is True
assert sha((evidence/'main-prepare/executed.splash').read_bytes()) == identity['executed_sha256']
for mode in ('invalid-calendar','invalid-mail-fenced','valid-control'):
    directory = evidence/mode
    report = load(directory/'report.json')
    assert report['source_sha256']==args.source_sha
    assert report['status']=='PASS' and not report['failed'] and all(value is True for value in report['checks'].values())
    raw=(directory/'raw-model-output.bin').read_bytes()
    assert sha(raw)==report['raw_model_sha256'] and len(raw)==report['raw_model_bytes']
    sdk=report['actual_sdk_observation']
    original=[json.loads(line) for line in (directory/'sdk-stdout.log').read_text().splitlines() if '"reply"' in line]
    assert len(original)==1 and original[0]['reply']==sdk['reply'] and original[0]['actual_sdk_response']==sdk['actual_sdk_response']
    requests=[row for row in report['trace'] if row['request']['method']=='model.complete']
    assert len(requests)==1 and requests[0]['reply']==original[0]['reply']
    assert load(directory/'actual-main-model-request.json')==requests[0]['request']['payload']
    attempts=sdk['provider_attempts']
    assert len(attempts)==(1 if mode=='valid-control' else 2)
    for index, attempt in enumerate(attempts):
        response=(directory/('raw-provider-response-'+str(index)+'.bin')).read_bytes()
        assert response==attempt['raw_provider_response_utf8'].encode()
        assert json.loads(response)['choices'][0]['message']['content'].encode()==raw
    saved=load(directory/'main-state/chat-sessions.json')
    selected=next(session for session in saved['sessions'] if session['id']==saved['selected_id'])
    assert len(selected['messages'])==2 and not selected['proposals']
    trace=load(directory/'main-state/model-last-response.json')
    if mode=='valid-control':
        assert sdk['reply']['is_ok'] is True and 'Ok' in sdk['actual_sdk_response']
        assert selected['messages'][-1]['state']=='success' and trace['known_usage'] is True
    else:
        assert sdk['reply']['is_ok'] is False and 'Err' in sdk['actual_sdk_response']
        assert sdk['reply']['error']==sdk['actual_sdk_response']['Err']
        assert sdk['reply']['error'].startswith('invalid_output: ') and 'not valid JSON' in sdk['reply']['error']
        assert 'not valid JSON' in json.dumps(attempts[1]['request'])
        assert selected['messages'][-1]['state']=='error' and trace['error_code']=='invalid_output' and trace['format_error']=='invalid_json'
        assert sdk['budget']['calls_today']==1 and sdk['budget']['tokens_today']==240
    observations=report['probe']['observations']
    assert not observations['goals'] and not observations['runs'] and not observations['actions'] and not observations['memory']
    assert observations['receiver']['transport_calls']==0 and not observations['receiver']['received']
    assert not any(method.startswith('octos.') or method in ('mail.compose','mail.review_send') or method.startswith('device_calendar.')
        for method in report['counters'])
print(json.dumps(dict(status='PASS',runtime_checks=54,cases=3,
    verified='Raw provider bytes → actual SDK stdio Err/Ok → unchanged Main response → persisted chat error/success and zero side effects',
    boundary='Evidence verification only; no additional runtime check count or live model claim.')))
