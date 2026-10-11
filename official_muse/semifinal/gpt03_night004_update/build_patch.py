#!/usr/bin/env python3
"""Create the isolated native update patch from the exact accepted safety source."""
import difflib
import hashlib
import importlib.util
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = ROOT / 'build/gpt03-night004/safety-main.splash'
SHA = 'c183a5c4e7fcb5d543fb7b43ea72cced03a46819827e5b7ee0db1e80be968539'
HELPERS = Path('/Users/mima0000/.codex/worktrees/muse-semifinal-a-20261009/Agent APP黑客松/official_muse/semifinal/tests/run_official_api.py')
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location('verified_vm_helpers', HELPERS)
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)
base = BASE.read_text()
assert hashlib.sha256(base.encode()).hexdigest() == SHA
source = base

def replace(name, body):
    global source
    source = helpers.replace_function(source, name, body)

def adapt(name, old, new):
    global source
    body = helpers.functions_in(source)[name]
    assert body.count(old) == 1, (name, old)
    replace(name, body.replace(old, new))

# Keep ordinary binding checks strict. Only explicit update lineage checks a
# retained creation candidate against the newly frozen plan revision.
body = helpers.functions_in(source)['calendar_agent_binding_current']
at_revision = body.replace('calendar_agent_binding_current(binding)', 'calendar_agent_binding_at_revision(binding,revision)').replace('goal.version != binding.plan_revision', 'goal.version != revision')
replace('calendar_agent_binding_current', 'fn calendar_agent_binding_current(binding){ return calendar_agent_binding_at_revision(binding,binding["plan_revision"]) }\n' + at_revision)
adapt('calendar_agent_boot', '    calendar_agent_delete_boot()', '    calendar_agent_update_boot()\n    calendar_agent_delete_boot()')
adapt('calendar_agent_project', '    let binding = calendar_agent_state["binding"]', '    if calendar_agent_update_project(view,goal) { return true }\n    let binding = calendar_agent_state["binding"]')
adapt('calendar_agent_submit_candidate', '    for previous in calendar_agent_state.previous_requests {', '    for mutation in calendar_agent_update_state.records {\n        if mutation.binding.goal_id == calendar_agent_candidate.goal_id {\n            calendar_agent_notice = "此事项已有改期记录；请按原稳定ID继续核对或准备新改期，不能改为重复创建。" redraw() return\n        }\n    }\n    for previous in calendar_agent_state.previous_requests {')

# Optional authority field preserves old persisted delete records byte-for-byte.
adapt('calendar_agent_delete_expected', '    if expected.id != binding.verification.event_id', '    expected = expected.to_json().parse_json()\n    if expected.id != binding.verification.event_id')
adapt('calendar_agent_delete_valid', '    let expected = calendar_agent_delete_expected(record.binding)', '    let expected = calendar_agent_delete_expected(record.binding)\n    if gm_has(record,"authority") {\n        if !calendar_agent_authority_valid(record.authority) || record.authority.binding.to_json() != record.binding.to_json() { return false }\n        expected = record.authority.event\n    }')
adapt('calendar_agent_delete_current', '    return calendar_agent_delete_valid(record) && calendar_agent_binding_current(record.binding)', '    let current = calendar_agent_binding_current(record.binding)\n    if gm_has(record,"authority") { current = calendar_agent_authority_current(record.authority) }\n    else if !calendar_agent_update_writable || calendar_agent_update_index(record.binding) >= 0 { current = false }\n    return calendar_agent_delete_valid(record) && current')
adapt('calendar_agent_delete_history', 'let snapshot = record.to_json()', 'let snapshot = calendar_agent_delete_state.records[index].to_json()')
replace('calendar_agent_delete_target', '''fn calendar_agent_delete_target(){
    let authority = calendar_agent_authority()
    if authority == nil || !calendar_agent_writable || !calendar_agent_delete_writable || calendar_agent_busy
        || calendar_agent_delete_blocks(authority.binding) { return nil }
    return {creation_request_id: authority.creation_request_id creation_turn_id: authority.creation_turn_id
        binding: authority.binding.to_json().parse_json() expected: authority.event.to_json().parse_json()
        authority: authority.to_json().parse_json()}
}''')

adapt('mail_calendar_link_valid', '    return link.binding.receipt_status == "verified" && link.binding.payload.request_id == link.request_id', '    if gm_has(link,"authority") && (!calendar_agent_authority_valid(link.authority)\n        || link.authority.binding.to_json() != link.binding.to_json()\n        || link.authority.creation_request_id != link.request_id || link.authority.creation_turn_id != link.turn_id) { return false }\n    return link.binding.receipt_status == "verified" && link.binding.payload.request_id == link.request_id')
replace('mail_calendar_verified', '''fn mail_calendar_verified(){
    let authority = calendar_agent_authority()
    return authority != nil && !calendar_agent_delete_blocks(authority.binding)
}''')
adapt('mail_calendar_current', '    return link.binding.account_id == "local" || link.binding.account_id == link.mail_account', '    let authority = calendar_agent_authority()\n    if authority == nil { return false }\n    if gm_has(link,"authority") {\n        if !calendar_agent_authority_current(link.authority) { return false }\n    } else if gm_has(authority,"update") { return false }\n    return authority.current_binding.account_id == "local" || authority.current_binding.account_id == link.mail_account')
adapt('mail_compose_from_agent_calendar', '    let binding = calendar_agent_state.binding', '    let authority = calendar_agent_authority()\n    let binding = authority.binding')
adapt('mail_compose_from_agent_calendar', '    mail_draft.link_goal_id = binding.goal_id', '    if gm_has(authority,"update") { mail_draft.official_calendar.authority = authority.to_json().parse_json() }\n    mail_draft.link_goal_id = binding.goal_id')
adapt('mail_compose_from_agent_calendar', '    let event = binding.verification.event', '    let event = authority.event')

# A follow-up edit must retain the immutable candidate behind an existing
# official event. It appends an explicit new proposal for the same matter.
adapt('chat_add_proposal', '    if editing {\n        for i in chat_sessions[index].proposals.len() {', '''    if editing && action == "calendar_candidate" && !calendar_enabled()
        && calendar_agent_binding_valid(calendar_agent_state["binding"])
        && calendar_agent_state.binding.receipt_status == "verified"
        && calendar_agent_state.binding.session_id == session_id {
        let authority = calendar_agent_authority()
        if authority == nil || chat_sessions[index].proposals.len() >= 8
            || payload.to_json() == request.candidate_payload
            || (account != "" && account != authority.current_binding.account_id) { return false }
        chat_sessions[index].proposals.push({id: request_id session_id: session_id
            account_id: authority.current_binding.account_id action: action payload: payload state: "candidate"
            memory_refs: refs revision: 1 project: authority.current_binding.project_id owner: authority.current_binding.owner_id
            goal_id: authority.current_binding.goal_id})
        return true
    }
    if editing {
        for i in chat_sessions[index].proposals.len() {''')

source = source.replace('改期及整体事项完成尚未接通。', '可本人选择新候选同ID改期；整体事项完成尚未接通。')
source = source.replace('自动改期尚未开放。', '同一事项的新候选可本人选择原事件、核对并确认改期。')
source = source.replace('改期和整体事项完成尚未接通。', '同ID改期需另行选择和确认；整体事项完成尚未接通。')
anchor = '                        let delete_target = calendar_agent_delete_target()'
assert source.count(anchor) == 1
source = source.replace(anchor, '''                        let update_target = calendar_agent_update_target()
                        if update_target != nil {
                            Secondary{text: "选择原事件并准备同ID改期" enabled: !calendar_agent_busy on_click: || calendar_agent_update_select()}
                        }
                        let update_index = calendar_agent_update_index(calendar_agent_state["binding"])
                        if update_index >= 0 {
                            let update_record = calendar_agent_update_state.records[update_index]
                            if calendar_agent_update_current(update_record) {
                                Label{width: Fill text: "同ID改期 · " + update_record.expected.id + " · 状态 " + ac_state(update_record.status) + "\\n原安排：" + calendar_agent_event_json(update_record.expected) + "\\n新安排：" + calendar_agent_event_json(update_record.event) draw_text.color: ink draw_text.wrap: Words draw_text.text_style.font_size: 12}
                                if update_record.status == "prepared" && calendar_agent_update_selected == update_record.to_json() {
                                    Secondary{text: "确认所选事件同ID改期" enabled: !calendar_agent_busy && calendar_agent_update_writable on_click: || calendar_agent_update_confirm()}
                                }
                                if update_record.turn_id != "" && update_record.receipt_status != "verified" {
                                    Secondary{text: "核对原改期请求" enabled: !calendar_agent_busy on_click: || calendar_agent_update_history(update_index)}
                                }
                            }
                        }
''' + anchor)
anchor = 'let calendar_agent_delete_state = '
assert source.count(anchor) == 1
source = source.replace(anchor, HERE.joinpath('update.splash').read_text() + '\n' + anchor)

out = ROOT / 'build/gpt03-night004/update-main.splash'
out.write_text(source)
patch = ''.join(difflib.unified_diff(base.splitlines(True), source.splitlines(True),
    fromfile='a/official_muse/app/source/main.splash', tofile='b/official_muse/app/source/main.splash'))
HERE.joinpath('calendar-update.patch').write_text(patch)
print(hashlib.sha256(source.encode()).hexdigest())
