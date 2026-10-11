#!/usr/bin/env python3
"""Directed fixture-plan contract checks; no Kernel or Calendar success simulated."""
import argparse, copy, hashlib, json, sys
from pathlib import Path
sys.dont_write_bytecode = True
from kernel_rpc import fixture_turn_payload

p = argparse.ArgumentParser(); p.add_argument('--observed-report',type=Path,required=True); p.add_argument('--out',type=Path,required=True)
a = p.parse_args(); root = Path(__file__).resolve().parents[6]
out = a.out.resolve(); out.relative_to(root/'build'); out.mkdir(parents=True,exist_ok=False)
report = json.loads(a.observed_report.read_text())
observed = report['probe']['observations']['create_state']['binding']['payload']
# This text is a parser fixture based on the actually observed production candidate,
# not a Kernel prompt/result or proof that a turn executed.
payload = {'text':'本次日历请求。\n精确 calendar.add_event 参数：'+json.dumps(observed,ensure_ascii=False)+'\n以该id精确读回。',
           'trigger':'app','binding_id':'fixture-opaque-binding'}
checks = {}; original = copy.deepcopy(payload); create = fixture_turn_payload(payload)
checks['original_payload_unchanged'] = payload == original
checks['original_text_trigger_binding_preserved'] = all(create[k] == v for k,v in payload.items())
checks['create_uses_exact_observed_payload'] = create['fixture_tool_plan'][0] == {'tool':'calendar.add_event','args':observed}
checks['create_get_uses_actual_previous_id'] = create['fixture_tool_plan'][1]['args'] == {'id':{'$tool_result':0,'path':['id']}}
checks['explicit_once_separate_from_prompt'] = create['fixture_approval']=='once' and 'fixture_tool_plan' not in create['text']
expected = dict(observed,id='synthetic-parser-event')
update_args = {k:v for k,v in observed.items() if k != 'request_id'}
update_args.update(id=expected['id'],expected=expected,start='2026-10-13T16:00',end='2026-10-13T16:30',notes='Quoted "value", braces {} and newline\n合成')
update_payload = {'text':'2. calendar.update_event 精确参数：'+json.dumps(update_args,ensure_ascii=False)+'\n3. 同id读回。','trigger':'app'}
updated = fixture_turn_payload(update_payload); steps = updated['fixture_tool_plan']
checks['update_exact_cas_snapshot_preserved'] = steps[1]['args'] == update_args and steps[1]['args']['expected']==expected
checks['update_get_old_then_update_then_get_new'] = [s['tool'] for s in steps]==['calendar.get_event','calendar.update_event','calendar.get_event']
checks['same_id_all_three_steps'] = all(s['args']['id']==expected['id'] for s in steps)
checks['escaped_json_notes_and_prompt_preserved'] = steps[1]['args']['notes']==update_args['notes'] and updated['text']==update_payload['text']

def refuses(value):
    try: fixture_turn_payload(value)
    except (ValueError,TypeError,KeyError): return True
    return False

checks['unsupported_prompt_refused'] = refuses({'text':'Please do something','trigger':'app'})
checks['vm_injected_fixture_fields_refused'] = refuses(dict(payload,fixture_approval='once'))
checks['missing_create_field_refused'] = refuses({'text':'精确 calendar.add_event 参数：'+json.dumps({'title':'x'})})
bad = dict(update_args,id='different-event')
checks['mismatched_update_id_refused'] = refuses({'text':'2. calendar.update_event 精确参数：'+json.dumps(bad)})
bad = dict(update_args,request_id='replacement')
checks['update_replacing_creation_request_refused'] = refuses({'text':'2. calendar.update_event 精确参数：'+json.dumps(bad)})
checks['missing_text_refused'] = refuses({'trigger':'app'})
result = {'kind':'FIXTURE_PLAN_PARSER_ONLY','checks':checks,'status':'PASS' if all(checks.values()) else 'FAIL',
    'observed_report_sha256':hashlib.sha256(a.observed_report.read_bytes()).hexdigest(),
    'source_main_sha256':report['source_identity']['source_sha256'],
    'kernel_calendar_calls':0,'full_chain_status':'NOT_TESTED','plans':{'create':create,'update':updated}}
(out/'report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':result['status'],'checks':len(checks),'failed':[k for k,v in checks.items() if not v]}))
raise SystemExit(0 if result['status']=='PASS' else 1)
