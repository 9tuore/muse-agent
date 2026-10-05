"""Small synthetic verified matter from A2's actual prior CardHost fixture."""
import copy
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ORIGIN=HERE/'calendar-binding-final-r1/dense/first/state/muse-goals'

def profile():
    load=lambda name: json.loads((ORIGIN/name).read_text())
    memory=load('memory.json')
    claims=copy.deepcopy([memory['claims'][0],memory['claims'][-1]])
    ids=set()
    for claim in claims:
        ids.update(claim['document']['payload']['source_ids'])
        ids.update(claim['source_history'])
        for old in claim['history']: ids.update(old['payload']['source_ids'])
    memory={'schema':1,'claims':claims,'sources':[copy.deepcopy(s) for s in memory['sources'] if s['source_id'] in ids],'forget':[]}
    goals=load('goals.json')
    selected={'schema':2,'goals':[goals['goals'][0]],'runs':[goals['runs'][-1]],'actions':[goals['actions'][-1]],'selected_id':'a2-goal'}
    calendar=load('calendar-state.json')
    calendar={'schema':1,'links':[calendar['links'][0]],'receipts':[calendar['receipts'][-1]],'local_states':[]}
    result=load(selected['goals'][0]['result_path'])
    assert selected['goals'][0]['status']=='completed'
    assert selected['actions'][0]['status']=='verified' and calendar['links'][0]['status']=='verified'
    assert selected['runs'][0]['id']==calendar['links'][0]['run_id']==result['run_id']
    assert selected['actions'][0]['id']==result['request_id']
    data={'memory.json':memory,'global-memory-settings.json':load('global-memory-settings.json'),
          'goals.json':selected,'calendar-state.json':calendar,'chat-sessions.json':load('chat-sessions.json'),
          'activity.json':load('activity.json'),selected['goals'][0]['result_path']:result}
    return data
