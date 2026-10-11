#!/usr/bin/env python3
"""Directed fixture-plan contract checks; no Kernel or Calendar success simulated."""
import argparse, copy, hashlib, json, re, sys
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
native_probe = Path(__file__).with_name('native_full_chain_probe.splash').read_text()
query_text = re.search(r'calendar_agent_submit\("([^\n]+)"\)',native_probe).group(1)
query_payload = {'text':'本次日历请求 ID：synthetic-parser-query。\n用户请求：'+query_text,'trigger':'app','opaque':'unchanged'}
query_before = copy.deepcopy(query_payload); query = fixture_turn_payload(query_payload)
checks['query_one_read_only_events_step'] = query['fixture_tool_plan']==[{'tool':'calendar.events','args':{}}]
checks['query_native_user_text_trigger_opaque_preserved'] = query_payload==query_before and all(query[k]==v for k,v in query_payload.items())
checks['create_does_not_contain_query_events'] = all(s['tool']!='calendar.events' for s in create['fixture_tool_plan'])
checks['query_before_create_via_production_entries'] = native_probe.index('if !native_query_before_create()') < native_probe.index('    calendar_agent_submit_candidate()') and 'calendar_agent_history_settle = true calendar_agent_history()' in native_probe

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
checks['mixed_query_create_markers_refused'] = refuses({'text':query_text+'\n'+payload['text'],'trigger':'app'})
checks['duplicate_query_marker_refused'] = refuses({'text':query_text+'\n'+query_text})
checks['query_write_arguments_refused'] = refuses({'text':'精确 calendar.events 参数：'+json.dumps({'request_id':'not-a-query'})})
checks['query_boolean_limit_refused'] = refuses({'text':'精确 calendar.events 参数：'+json.dumps({'limit':True})})
checks['query_invalid_limits_refused'] = all(refuses({'text':'精确 calendar.events 参数：'+json.dumps({'limit':n})}) for n in [0,201,1.5,'50'])
checks['query_invalid_time_filter_types_lengths_refused'] = all(refuses({'text':'精确 calendar.events 参数：'+json.dumps(args)}) for args in [{'from':4},{'to':'x'*33}])
filtered_args = {'from':'2026-10-13','to':'2026-10-14','limit':200}
filtered = fixture_turn_payload({'text':'精确 calendar.events 参数：'+json.dumps(filtered_args)})
checks['query_official_optional_filters_preserved'] = filtered['fixture_tool_plan']==[{'tool':'calendar.events','args':filtered_args}]
denied = fixture_turn_payload(update_payload,'deny')
checks['explicit_mutation_deny_only_changes_approval'] = {k:v for k,v in denied.items() if k!='fixture_approval'}=={k:v for k,v in updated.items() if k!='fixture_approval'} and denied['fixture_approval']=='deny'
checks['mutation_deny_keeps_original_expected_text_trigger'] = denied['fixture_tool_plan'][1]['args']['expected']==expected and denied['text']==update_payload['text'] and denied['trigger']==update_payload['trigger']
checks['mutation_default_remains_once'] = updated['fixture_approval']=='once'
checks['mutation_deny_never_denies_create'] = fixture_turn_payload(payload,'deny')['fixture_approval']=='once'
checks['mutation_deny_never_changes_query_approval'] = fixture_turn_payload(query_payload,'deny')['fixture_approval']=='once'
try:
    fixture_turn_payload(update_payload,'standing')
    checks['invalid_mutation_approval_refused'] = False
except ValueError:
    checks['invalid_mutation_approval_refused'] = True
delete_args = {'id':expected['id'],'expected':copy.deepcopy(expected)}
delete_payload = {'text':'本人明确选择并确认删除。\n2. calendar.remove_event 参数：'+json.dumps(delete_args,ensure_ascii=False)+'\n3. 仅removed=true后同ID读回。',
                  'trigger':'app','opaque':'delete-original'}
delete_before = copy.deepcopy(delete_payload); deleted = fixture_turn_payload(delete_payload); delete_steps = deleted['fixture_tool_plan']
checks['delete_get_remove_get_exact_order'] = [s['tool'] for s in delete_steps]==['calendar.get_event','calendar.remove_event','calendar.get_event']
checks['delete_original_payload_text_trigger_opaque_preserved'] = delete_payload==delete_before and all(deleted[k]==v for k,v in delete_payload.items())
checks['delete_original_expected_eight_fields_preserved'] = delete_steps[1]['args']==delete_args and delete_steps[1]['args']['expected']==expected
checks['delete_same_id_all_three_steps'] = all(s['args']['id']==expected['id'] for s in delete_steps)
checks['delete_once_exact_plan_without_result_snapshot_substitution'] = deleted['fixture_approval']=='once' and '$tool_result' not in json.dumps(delete_steps)
checks['update_deny_option_keeps_delete_once'] = fixture_turn_payload(delete_payload,'deny')==deleted
checks['delete_missing_expected_refused'] = refuses({'text':'2. calendar.remove_event 参数：'+json.dumps({'id':expected['id']})})
checks['delete_wrong_id_refused'] = refuses({'text':'2. calendar.remove_event 参数：'+json.dumps(dict(delete_args,id='different'))})
checks['delete_unknown_top_field_refused'] = refuses({'text':'2. calendar.remove_event 参数：'+json.dumps(dict(delete_args,request_id='replacement'))})
checks['delete_incomplete_extra_wrong_type_expected_refused'] = all(refuses({'text':'2. calendar.remove_event 参数：'+json.dumps(dict(delete_args,expected=bad))}) for bad in [{k:v for k,v in expected.items() if k!='notes'},dict(expected,extra='x'),dict(expected,title=3),dict(expected,request_id='')])
checks['delete_invalid_id_refused'] = all(refuses({'text':'2. calendar.remove_event 参数：'+json.dumps({'id':bad,'expected':dict(expected,id=bad)})}) for bad in ['',7,'x'*65])
checks['delete_duplicate_or_mixed_markers_refused'] = all(refuses({'text':delete_payload['text']+'\n'+t}) for t in [delete_payload['text'],payload['text'],query_payload['text'],update_payload['text']])
result = {'kind':'FIXTURE_PLAN_PARSER_ONLY','checks':checks,'status':'PASS' if all(checks.values()) else 'FAIL',
    'observed_report_sha256':hashlib.sha256(a.observed_report.read_bytes()).hexdigest(),
    'source_main_sha256':report['source_identity']['source_sha256'],
    'kernel_calendar_calls':0,'full_chain_status':'NOT_TESTED','plans':{'query':query,'create':create,'update':updated,'update_deny':denied,'delete':deleted}}
(out/'report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':result['status'],'checks':len(checks),'failed':[k for k,v in checks.items() if not v]}))
raise SystemExit(0 if result['status']=='PASS' else 1)
