"""Original built-in Calendar lifecycle: each call uses a new real process."""
import hashlib
import json
import subprocess


def run(binary, out, patched=False):
    root = out / 'isolated-host'
    root.mkdir()
    calls, checks = [], {}

    def call(method, args=None, app='os.calendar', directory=root):
        value = json.loads(subprocess.check_output([str(binary), str(directory), app, method,
            json.dumps(args or {})], text=True, timeout=15))
        calls.append({'method': method, 'caller': app, 'args': args or {}, 'reply': value})
        return value

    event = dict(title='MUSE-PIVOT-BUILTIN-20261010', start='2026-10-11T15:00', end='2026-10-11T15:30',
                 timezone='Asia/Shanghai', location='Muse synthetic acceptance', notes='Synthetic fixture only',
                 request_id='MUSE-PIVOT-BUILTIN-20261010-UNIQUE')
    denied = call('add_event', event, app='muse-goals')
    checks['direct_third_party_denied'] = not denied['ok'] and not (root/'calendar/events.json').exists()
    added = call('add_event', event)
    assert added['ok'], added
    event_id = added['value']['id']
    records = call('raw-read')['value']
    saved = next(e for e in records if e['id'] == event_id)
    precise = call('get_event', {'id':event_id})
    by_request = call('get_event', {'request_id':event['request_id']})
    checks['create_independently_persisted'] = len(records) == 1 and all(saved.get(k) == v for k, v in event.items())
    retry = call('add_event', event)
    checks['restart_same_request_no_duplicate'] = retry['ok'] and retry['value']['id'] == event_id and retry['value']['reused'] and len(call('raw-read')['value']) == 1
    changed = call('add_event', dict(event, start='2026-10-11T16:00'))
    checks['changed_retry_rejected'] = not changed['ok'] and call('raw-read')['value'] == records
    listing = call('events', {'from':'2026-10-11', 'to':'2026-10-12', 'limit':200})
    checks['query_real_store'] = listing['ok'] and listing['value']['events'] == records
    args = dict(event, id=event_id, expected=saved, start='2026-10-11T16:00', end='2026-10-11T16:30')
    args.pop('request_id')
    edited = call('update_event', args)
    new_records = call('raw-read')['value']
    current = new_records[0]
    checks['update_original_id_independently_persisted'] = edited['ok'] and len(new_records) == 1 and current['id'] == event_id and current['request_id'] == event['request_id'] and current['start'] == args['start'] and current['end'] == args['end']
    stale = call('update_event', args)
    checks['stale_update_rejected_after_restart'] = not stale['ok'] and call('raw-read')['value'] == new_records
    view = call('view', {'month':'2026-10', 'day':'2026-10-11'})
    checks['same_event_in_official_month_day_projection'] = view['ok'] and view['value']['events'][0]['id'] == event_id and view['value']['events'][0]['start'] == args['start'] and any(d['marked'] for week in view['value']['weeks'] for d in week['days'] if d['date'] == '2026-10-11')
    stale_remove = call('remove_event', {'id':event_id, 'expected':saved})
    checks['stale_delete_rejected'] = not stale_remove['ok'] and call('raw-read')['value'] == new_records
    removed = call('remove_event', {'id':event_id, 'expected':current})
    checks['delete_independent_read_absence'] = removed['ok'] and removed['value']['removed'] and call('raw-read')['value'] == []
    checks['restart_absence_no_reexecution'] = call('events')['value']['events'] == []
    missing = call('get_event', {'id':event_id})
    # Preserve actual missing capability and destructive-corruption reproduction.
    corrupt = out / 'corrupt-store-reproduction'
    (corrupt/'calendar').mkdir(parents=True)
    original = b'{incomplete calendar store'
    store = corrupt/'calendar/events.json'; store.write_bytes(original)
    corruption = call('add_event', event, directory=corrupt)
    unreadable = call('get_event', {'id':event_id}, directory=corrupt)
    corrupt_update = call('update_event', args, directory=corrupt)
    corrupt_delete = call('remove_event', {'id':event_id,'expected':current}, directory=corrupt)
    corrupt_query = call('events', directory=corrupt)
    capped = out/'capped-list-fixture'; (capped/'calendar').mkdir(parents=True)
    many = [dict(saved,id=f'synthetic-cap-{i:04}',request_id=f'synthetic-cap-request-{i:04}') for i in range(201)]
    (capped/'calendar/events.json').write_text(json.dumps(many))
    cap_list = call('events', {'limit':200}, directory=capped)
    exact_beyond_cap = call('get_event', {'id':many[-1]['id']}, directory=capped)
    gaps = {'exact_get_event_supported': precise['ok'] and precise['value']['found'] and precise['value']['event']==saved,
            'unknown_reconciles_by_request_id': by_request['ok'] and by_request['value']['event']==saved,
            'exact_absence_after_delete': missing['ok'] and missing['value']['found'] is False and missing['value']['event'] is None,
            'corrupt_store_write_fails_closed': not corruption['ok'] and store.read_bytes() == original,
            'corrupt_store_not_false_absence':not unreadable['ok'],
            'corrupt_update_delete_query_refused':not corrupt_update['ok'] and not corrupt_delete['ok'] and not corrupt_query['ok'] and store.read_bytes()==original,
            'exact_lookup_beyond_list_cap':len(cap_list['value']['events'])==200 and exact_beyond_cap['ok'] and exact_beyond_cap['value']['event']==many[-1]}
    admission = call('admission-check')['value']
    checks.update({k:v for k,v in admission.items() if isinstance(v,bool)})
    descriptors = call('tools-check',{'path':str((out/'bundle/tools.json').resolve())})
    checks['original_contract_accepts_tool_descriptors']=descriptors['ok']
    if patched:
        protected = [t for t in descriptors.get('value',[]) if t['name'] in ('calendar.update_event','calendar.remove_event')]
        checks['shared_mutations_keep_host_confirmation']=len(protected)==2 and all(t['shareable'] and t['needs_person'] and not t['auto_approvable'] for t in protected)
    report = {'checks':checks, 'known_gaps':gaps, 'calls':calls, 'external_calls':0,
              'binary_sha256': hashlib.sha256(binary.read_bytes()).hexdigest(),
              'patched':patched,
              'boundary':('Isolated proposed Calendar patch' if patched else 'Actual original Calendar service')+', real store, independent processes and real policy/schema components. No Shell admission, Agent, native confirmation or production data.'}
    (out/'protocol.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    return report
