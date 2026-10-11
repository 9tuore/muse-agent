#!/usr/bin/env python3
"""Prepare a SHA-bound proposal only; do not edit formal main.splash."""
import argparse
import difflib
import hashlib
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True
from test_recovery import function

OWN = Path(__file__).resolve().parent
BASE_SHA = '0c17e4cc3168d5c85518c2e177424a4803eb19297c665edcaa392cd3381fce2c'
HELPERS = '''// Optional follow-up draft; calendar success never requires sending Mail.
fn mail_calendar_link_valid(link){
    if !gm_object(link) || !gm_string(link["request_id"],160) || link.request_id == ""
        || !gm_string(link["turn_id"],160) || link.turn_id == ""
        || !gm_string(link["mail_account"],200) || link.mail_account == ""
        || !calendar_agent_binding_valid(link["binding"]) { return false }
    return link.binding.receipt_status == "verified" && link.binding.payload.request_id == link.request_id
}
fn mail_calendar_verified(){
    let binding = calendar_agent_state["binding"]
    return calendar_agent_state.status == "turn_completed" && calendar_agent_state.turn_id != ""
        && calendar_agent_binding_current(binding) && binding.receipt_status == "verified"
        && binding.payload.request_id == calendar_agent_state.request_id
}
fn mail_calendar_current(draft){
    if !gm_has(draft,"official_calendar") { return true }
    let link = draft.official_calendar
    if !mail_calendar_link_valid(link) || !mail_calendar_verified()
        || link.request_id != calendar_agent_state.request_id || link.turn_id != calendar_agent_state.turn_id
        || link.binding.to_json() != calendar_agent_state.binding.to_json()
        || draft.link_goal_id != link.binding.goal_id || draft.link_event_id != link.binding.verification.event_id
        || draft.link_run_id != "" || mail_account == nil || mail_account.id != link.mail_account
        || draft.account != link.mail_account || !gm_account_allowed(link.mail_account)
        || mail_watch_account(link.mail_account) == nil { return false }
    return link.binding.account_id == "local" || link.binding.account_id == link.mail_account
}
fn mail_calendar_context_current(context){
    if !gm_has(context,"official_calendar_json") { return !gm_has(mail_draft,"official_calendar") }
    return gm_has(mail_draft,"official_calendar") && mail_calendar_current(mail_draft)
        && context.official_calendar_json == mail_draft.official_calendar.to_json()
}
fn mail_calendar_hold(context){
    if mail_draft.request_id != context.request_id { return }
    // Preserve actual accepted/verified history; only an unfinished send is UNKNOWN.
    if mail_draft.status == "sending" {
        mail_draft.status = "unknown"
        mail_save()
        let ai = core_action_index(context.request_id)
        if ai >= 0 && actions[ai].status == "in_flight" { core_finish_action(context.request_id,"unknown") }
    }
    mail_sending = false
    mail_error = "关联事项、身份或版本已变化；原文与原请求保留，旧回执不会完成当前事项，也不会重发。"
    mail_redraw()
}
fn mail_calendar_late(context,r){
    if mail_draft.request_id != context.request_id { return }
    let raw = r.to_json()
    if gm_string(raw,16000) { mail_draft.calendar_late_host_receipt = raw }
    // Retain a valid late composer ID for later read-only reconciliation.
    if r.is_ok && gm_object(r["data"]) && gm_string(r.data["compose_id"],128)
        && regex("^compose-[a-zA-Z0-9-]+$","").test(r.data.compose_id)
        && gm_number(r.data["revision"]) && r.data.revision >= 1 && floor(r.data.revision) == r.data.revision
        && r.data["account"] == context.snapshot.account && r.data["to"] == context.snapshot.to
        && r.data["subject"] == context.snapshot.subject && r.data["body"] == context.snapshot.body {
        mail_draft.host_compose_id = r.data.compose_id
        mail_draft.host_revision = r.data.revision
    }
    mail_save()
    mail_calendar_hold(context)
}
fn mail_compose_from_agent_calendar(){
    if !mail_calendar_verified() || mail_account == nil || !gm_account_allowed(mail_account.id)
        || mail_watch_account(mail_account.id) == nil {
        mail_error = "请先精确读回当前事项，并选择已授权的发送账号。" calendar_agent_notice = mail_error mail_redraw() return
    }
    let binding = calendar_agent_state.binding
    if binding.account_id != "local" && binding.account_id != mail_account.id {
        mail_error = "发送账号与当前事项来源账号不同，未创建关联草稿。" calendar_agent_notice = mail_error mail_redraw() return
    }
    if gm_has(mail_draft,"official_calendar") && mail_calendar_current(mail_draft) {
        mail_compose()
        set_page("Mail")
        return
    }
    if !mail_draft_writable || mail_sending || mail_pending || mail_model_pending
        || mail_draft.status == "waiting_user" || mail_draft.status == "sending"
        || mail_draft.status == "accepted" || mail_draft.status == "unknown" {
        mail_error = "已有邮件待确认或待对账；保留原文，请先处理原动作。" calendar_agent_notice = mail_error mail_redraw() return
    }
    if !mail_watch_archive_current() { mail_error = mail_reply_error calendar_agent_notice = mail_error mail_redraw() return }
    mail_new_draft()
    if !mail_draft_writable { return }
    mail_draft.official_calendar = {request_id: calendar_agent_state.request_id turn_id: calendar_agent_state.turn_id
        mail_account: mail_account.id binding: binding.to_json().parse_json()}
    mail_draft.link_goal_id = binding.goal_id
    mail_draft.link_event_id = binding.verification.event_id
    mail_draft.link_run_id = ""
    let event = binding.verification.event
    ui.mail_to.set_text("")
    ui.mail_subject.set_text("关于 " + event.title)
    ui.mail_body.set_text("已核对日历安排：" + event.start + " 至 " + event.end + "（" + event.timezone
        + "）。\\n地点：" + event.location + "。请核对后回复。")
    mail_edit()
    if !mail_save() { return }
    mail_notice = "已建立可选关联草稿；请本人填写收件人、核对内容，再单独进入官方审阅。尚未发送，事项尚未整体完成。"
    core_record_event("MAIL_DRAFT_CREATED","当前版本的官方日历已精确读回；关联草稿尚未发送。",binding.goal_id,"","",mail_account.id)
    set_page("Mail")
}

'''

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True)
    a = p.parse_args()
    old = a.source.read_text()
    sha = lambda s: hashlib.sha256(s.encode()).hexdigest()
    assert sha(old) == BASE_SHA, 'Source drift; reprepare by named boundaries'
    new = old
    changed = []
    def edit(name,transform):
        nonlocal new
        before = function(new,name)
        after = transform(before)
        assert after != before, name
        assert new.count(before) == 1, name
        new = new.replace(before,after,1)
        changed.append(name)
    def sub(text,before,after):
        assert text.count(before) == 1, before[:100]
        return text.replace(before,after,1)
    guard = '    if !mail_calendar_current(mail_draft) { mail_error = "关联事项、身份或版本已变化；原文保留，请先核对当前日历。" mail_redraw() return }\n'
    edit('mail_draft_valid',lambda s:sub(s,'    if gm_has(draft,"memory_refs")',
        '    if gm_has(draft,"official_calendar") && !mail_calendar_link_valid(draft.official_calendar) { return false }\n'
        '    if gm_has(draft,"calendar_late_host_receipt") && !gm_string(draft.calendar_late_host_receipt,16000) { return false }\n'
        '    if gm_has(draft,"memory_refs")'))
    for name in ['mail_preview','mail_send_confirmed','mail_check_host_status','mail_verify_received']:
        edit(name,lambda s:s.replace('{\n','{\n'+guard,1))
    def confirm(s):
        s=sub(s,'    let goal_id = mail_draft.link_goal_id','    let goal_id = mail_draft.link_goal_id\n    // Follow-up Mail has an independent action journal, not a new Goal phase.\n    if gm_has(mail_draft,"official_calendar") { goal_id = "" }')
        return sub(s,'    start_timeout(0.05,|| mail_send_step(context,0))',
            '    if gm_has(mail_draft,"official_calendar") { context.official_calendar_json = mail_draft.official_calendar.to_json() }\n    start_timeout(0.05,|| mail_send_step(context,0))')
    edit('mail_send_confirmed',confirm)
    ctx_guard = '    if !mail_calendar_context_current(context) { mail_calendar_hold(context) return }\n'
    for name in ['mail_send_step','mail_compose_before_review','mail_review_host','mail_send_receipt_step']:
        edit(name,lambda s:s.replace('{\n','{\n'+ctx_guard,1))
    edit('mail_review_current',lambda s:sub(s,'    return ai >= 0','    return mail_calendar_context_current(context) && ai >= 0'))
    edit('mail_compose_before_review',lambda s:sub(s,'    host.request("mail.compose",context.snapshot,fn(r){\n',
        '    host.request("mail.compose",context.snapshot,fn(r){\n        if !mail_calendar_context_current(context) { mail_calendar_late(context,r) return }\n'))
    edit('mail_review_host',lambda s:sub(s,'        if mail_draft.request_id != context.request_id || mail_draft.status != "sending" { return }\n',
        '        if mail_draft.request_id != context.request_id || mail_draft.status != "sending" { return }\n        if !mail_calendar_context_current(context) { mail_calendar_late(context,r) return }\n'))
    def status(s):
        s=sub(s,'    let requested = mail_draft.request_id let compose = mail_draft.host_compose_id',
            '    let requested = mail_draft.request_id let compose = mail_draft.host_compose_id\n    let linked = ""\n    if gm_has(mail_draft,"official_calendar") { linked = mail_draft.official_calendar.to_json() }')
        s=sub(s,'        let snapshot = mail_draft.attempt.parse_json()',
            '        if !mail_calendar_current(mail_draft) || (linked != "" && mail_draft.official_calendar.to_json() != linked) {\n            mail_error = "只读核对期间关联事项已变化；保留原状态，不会重发。" mail_redraw() return\n        }\n        let snapshot = mail_draft.attempt.parse_json()')
        return sub(s,'        start_timeout(0.05,|| mail_send_receipt_step(context,0))',
            '        if linked != "" { context.goal_id = "" context.run_id = "" context.official_calendar_json = linked }\n        start_timeout(0.05,|| mail_send_receipt_step(context,0))')
    edit('mail_check_host_status',status)
    edit('mail_verify_received_step',lambda s:s.replace('{\n','{\n    if !mail_calendar_current(mail_draft) { mail_verifying = false mail_error = "关联版本已变化；原收件声明不用于完成当前事项。" mail_redraw() return }\n',1))
    edit('mail_finish_linked_result',lambda s:s.replace('{\n','{\n    if gm_has(mail_draft,"official_calendar") { return mail_calendar_current(mail_draft) }\n',1))
    # Keep ordinary drafts and the disabled historical Calendar route unchanged.
    def projection(s):
        s=sub(s,'        && gm_account_allowed(ac_field(mail_draft,"account")) {',
            '        && gm_account_allowed(ac_field(mail_draft,"account"))\n        && (!gm_has(mail_draft,"official_calendar") || mail_calendar_current(mail_draft)) {')
        return sub(s,'        if ac_field(mail_draft,"link_event_id") != "" {',
            '        if ac_field(mail_draft,"link_event_id") != "" && !gm_has(mail_draft,"official_calendar") {')
    edit('ac_projection',projection)
    edit('calendar_agent_project',lambda s:sub(s,'日历已精确核验；关联确认邮件和改期尚未接通，事项尚未整体完成。',
        '日历已精确核验；可选准备关联确认草稿，邮件需另行审阅和收件声明。改期及整体事项完成尚未接通。'))
    new=sub(new,'fn mail_compose_from_calendar(goal_id){',HELPERS+'fn mail_compose_from_calendar(goal_id){')
    new=sub(new,'候选联动目前支持新建与精确读回；关联确认邮件、改期和整体事项完成尚未接通。',
        '候选联动支持新建、精确读回和可选确认草稿；发送须单独原生审阅，改期和整体事项完成尚未接通。')
    new=sub(new,'                        Secondary{text: "回读当前请求的官方记录"',
        '                        if mail_calendar_verified() {\n                            Label{width: Fill text: "可选确认邮件：先在邮件页选择发送账号；关联草稿的收件人由本人填写。" draw_text.color: muted draw_text.wrap: Words draw_text.text_style.font_size: 12}\n                            Secondary{text: "准备或打开关联确认草稿" enabled: !calendar_agent_busy && mail_account != nil on_click: || mail_compose_from_agent_calendar()}\n                        }\n'
        '                        Secondary{text: "回读当前请求的官方记录"')
    patch=''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/official_muse/app/source/main.splash',tofile='b/official_muse/app/source/main.splash',n=0))
    (OWN/'calendar-mail.patch').write_text(patch)
    identity=dict(source_sha256=sha(old),expected_source_sha256=sha(new),patch_sha256=sha(patch),applied_to_formal_source=False,
        base_central_head='691bf7c4b22bda3197c03fa5b82e5351253e01f1',changed_functions=sorted(set(changed)),
        boundary='Optional exact-Calendar-bound Mail draft; existing compose/review_send/compose_status; independent action journal; no Goal completion or automatic send.')
    (OWN/'calendar-mail-identity.json').write_text(json.dumps(identity,indent=2)+'\n')
    a.source.with_name('after.splash').write_text(new)
    print(json.dumps(identity))

if __name__=='__main__': main()
