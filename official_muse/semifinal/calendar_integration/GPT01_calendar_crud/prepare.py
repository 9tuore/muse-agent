"""Prepare exact-baseline Calendar CRUD increments only in this owned worktree."""
from pathlib import Path
import difflib
import hashlib
import json
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
OWN = HERE.parents[3]
CENTRAL = Path('/Users/mima0000/.codex/worktrees/muse-semifinal-a-20261009/Agent APP黑客松')
SDK = CENTRAL / 'build/runtime-closure-full-shell-r1/sdk'
HUB = SDK.parent / 'hub'
STAGE = OWN / 'build/gpt01-calendar-crud'
SIX = ['calendar.events', 'calendar.get_event', 'calendar.add_event',
       'calendar.update_event', 'calendar.remove_event', 'calendar.notify']
changes = {'sdk': {}, 'hub': {}, 'release': {}}
roots = {'sdk': SDK, 'hub': HUB, 'release': CENTRAL}


def edit(tree, path, before, after):
    old, new = changes[tree].get(path, ((roots[tree] / path).read_text(), (roots[tree] / path).read_text()))
    assert new.count(before) == 1, (tree, path, new.count(before))
    changes[tree][path] = old, new.replace(before, after)


def append_tests(tree, path, tests):
    old, new = changes[tree][path]
    assert new.rstrip().endswith('}')
    changes[tree][path] = old, new.rstrip()[:-1] + '\n' + tests + '}\n'


def main():
    STAGE.mkdir(parents=True, exist_ok=False)
    for path in ['crates/app-peers/src/calendar_history.rs', 'crates/shell/src/app_chat/calendar_history.rs']:
        edit('sdk', path,
             '        "calendar.add_event" | "calendar_add_event" => Some("calendar.add_event"),\n',
             '        "calendar.add_event" | "calendar_add_event" => Some("calendar.add_event"),\n'
             '        "calendar.update_event" | "calendar_update_event" => Some("calendar.update_event"),\n'
             '        "calendar.remove_event" | "calendar_remove_event" => Some("calendar.remove_event"),\n')
    p = 'crates/app-peers/src/calendar_history.rs'
    edit('sdk', p, 'exact_scope_and_four_tools_only', 'exact_scope_and_six_tools_only')
    edit('sdk', p, '["calendar.events","calendar.get_event","calendar.add_event","calendar.notify"]', json.dumps(SIX, separators=(',', ':')))
    edit('sdk', p, '["calendar.update_event","calendar.remove_event","calendar_events","calendar.events_extra"]',
         '["calendar.delete_event","calendar.agenda","calendar_events","calendar.events_extra"]')
    append_tests('sdk', p, (HERE / 'history_tests.rs').read_text())
    p = 'crates/shell/src/app_chat/history_receipt_tests.rs'
    edit('sdk', p, 'r["tool_name"]=json!("calendar.remove_event");assert!(row_detail(&r,None).is_none());',
         'r["tool_name"]=json!("calendar.delete_event");assert!(row_detail(&r,None).is_none());')
    old, new = changes['sdk'][p]
    changes['sdk'][p] = old, new + '\n' + (HERE / 'display_tests.rs').read_text()
    edit('sdk', 'crates/shell/src/host_tools/mod.rs',
         '                | "calendar.add_event" | "calendar.notify")',
         '                | "calendar.add_event" | "calendar.update_event"\n'
         '                | "calendar.remove_event" | "calendar.notify")')
    edit('hub', 'crates/appstore/src/lib.rs',
         '    "calendar.events", "calendar.get_event", "calendar.add_event", "calendar.notify",',
         '    "calendar.events", "calendar.get_event", "calendar.add_event",\n'
         '    "calendar.update_event", "calendar.remove_event", "calendar.notify",')
    edit('sdk', 'apps/calendar/host-service/src/lib.rs', 'mod cards;',
         'mod cards;\n#[cfg(test)]\nmod gpt01_crud_tests;')
    changes['sdk']['apps/calendar/host-service/src/gpt01_crud_tests.rs'] = '', (HERE / 'crud_tests.rs').read_text()
    p = 'apps/calendar/bundle/tools.json'
    edit('sdk', p, 'First read calendar.events and pass that exact event as expected;',
         'First use calendar.get_event to read the exact id and pass that event as expected;')
    edit('sdk', p, "Remove an event from the person's calendar by its id (from calendar.events). It is gone for good, so the person approves it.",
         "Remove one saved Calendar event by its exact id. First use calendar.get_event and pass its exact event as expected; a stale snapshot is refused. The Host requires the person's approval. After removal, verify the same id with calendar.get_event: only found:false and event:null establish absence. A card warning does not undo an event deletion.")
    p = 'official_muse/integrated_release/prepare_bundle.py'
    edit('release', p, "            'calendar.add_event', 'calendar.notify'],", "            'calendar.add_event', 'calendar.update_event', 'calendar.remove_event', 'calendar.notify'],")
    edit('release', p,
         "'全局记忆支持来源、范围、更正和遗忘。官方助手申请内置日历查询、回读、新建和通知，'\n        '使用前需要宿主本人启用；当前事项可绑定请求和精确读回回执；自动安排、改期仍待接通。'",
         "'全局记忆支持来源、范围、更正和遗忘。官方助手申请内置日历查询、回读、新建、更新、删除和通知，'\n        '使用前需要宿主本人启用；更新与删除仍需 Host 本人批准；真实调动须经过同身份验收。'")
    edit('release', 'official_muse/integrated_release/AGENT.md',
         'calendar.add_event、calendar.notify；不修改或删除旧事件，不借用系统应用身份。',
         'calendar.add_event、calendar.update_event、calendar.remove_event、calendar.notify；不借用系统应用身份。\n'
         '更新或删除必须先用 get_event 精确读出 id 和完整事件，将该快照原样作为 expected。\n'
         '更新提供全部替换字段，保留未要求修改的标题、起止时间、时区、地点和备注；不猜未知结束时间。\n'
         '更新和删除都需 Host 本人批准；工具授权、等待确认、助手文字或出现卡片都不代表已批准或已完成。\n'
         '快照过期时重新读回并核对本人意图，不拿新快照自动重试破坏性操作。更新后按同一 id 精确回读核对字段；\n'
         '删除须有 removed:true 的真实结果，并且同一 id 的 get_event 回读为 found:false、event:null。\n'
         '超时或未知结果先按原 id 对账；不存在可报告已对账缺失，不能伪造一次成功删除。卡片警告保留为独立警告。')
    p = 'official_muse/integrated_release/muse_calendar_offers.rs'
    edit('release', p, 'const FOUR: &[&str] = &["calendar.events", "calendar.get_event", "calendar.add_event", "calendar.notify"];',
         'const SIX: &[&str] = &["calendar.events", "calendar.get_event", "calendar.add_event",\n    "calendar.update_event", "calendar.remove_event", "calendar.notify"];')
    old, new = changes['release'][p]
    changes['release'][p] = old, new.replace('Fixture::new(FOUR)', 'Fixture::new(SIX)').replace('FOUR.iter()', 'SIX.iter()')
    edit('release', p, 'Fixture::new(&["calendar.events", "calendar.update_event", "calendar.remove_event"])',
         'Fixture::new(&["calendar.events", "calendar.agenda", "calendar.delete_event"])')
    edit('release', p, 'error.contains("update_event") || error.contains("remove_event")',
         'error.contains("agenda") || error.contains("delete_event")')

    evidence = {'state': 'PREPARED_TARGETED_TEST_PENDING', 'source_roots': {k:str(v) for k,v in roots.items()},
                'patches': {}, 'files': {}, 'schema_rules': {}, 'writes_shared': False, 'live_actions': 0}
    for tree, files in changes.items():
        patch = ''.join(''.join(difflib.unified_diff(a.splitlines(True), b.splitlines(True), fromfile='a/'+p, tofile='b/'+p)) for p,(a,b) in files.items())
        dest = HERE / ('GPT01-calendar-crud-' + tree + '.patch')
        dest.write_text(patch)
        evidence['patches'][tree] = {'path':dest.name, 'sha256':hashlib.sha256(patch.encode()).hexdigest()}
        evidence['files'][tree] = {}
        for path,(old,new) in files.items():
            local = STAGE / tree / path
            local.parent.mkdir(parents=True, exist_ok=True)
            if old: local.write_text(old)
            evidence['files'][tree][path] = {'before':hashlib.sha256(old.encode()).hexdigest(), 'after':hashlib.sha256(new.encode()).hexdigest()}
        log = []
        for mode in [['-C'], []]:
            result = subprocess.run(['/usr/bin/patch', *mode, '-p1', '-F', '0', '-i', str(dest)], cwd=STAGE/tree, capture_output=True, text=True)
            log.append(result.stdout + result.stderr)
            assert result.returncode == 0, log[-1]
        (HERE / (tree+'-patchcheck.log')).write_text('\n'.join(log))
        assert all((STAGE/tree/path).read_text()==new for path,(_,new) in files.items())
        evidence['patches'][tree]['zero_fuzz_apply_and_byte_compare'] = True
    declarations = json.loads((STAGE/'sdk/apps/calendar/bundle/tools.json').read_text())['tools']
    for tool in ['calendar.update_event','calendar.remove_event']:
        d = next(d for d in declarations if d['name']==tool)
        assert d['confirm']=='host' and d['auto_approvable'] is False and d['risk']=='destructive'
        assert set(['id','expected']).issubset(d['input_schema']['required']) and d['shareable'] is True
        evidence['schema_rules'][tool] = {k:d[k] for k in ['risk','confirm','auto_approvable','shareable']}
    evidence['source_heads'] = {k:subprocess.check_output(['git','rev-parse','HEAD'],cwd=v,text=True).strip() for k,v in roots.items()}
    evidence['source_git_roots'] = {k:subprocess.check_output(['git','rev-parse','--show-toplevel'],cwd=v,text=True).strip() for k,v in roots.items()}
    evidence['source_heads_note'] = 'Containing project repo heads, not claims of upstream SDK/Hub revisions; exact per-file hashes define this incremental baseline.'

    # Real broker/Conversation sources. Only the agents strip-note dependency is the existing owned adapter.
    peer = STAGE/'peer-harness'
    shutil.copytree(SDK/'crates/app-peers/src', peer/'src')
    shutil.copyfile(HERE/'peer-Cargo.toml', peer/'Cargo.toml')
    shutil.copyfile(HERE/'peer-Cargo.lock', peer/'Cargo.lock')
    for p,(_,new) in changes['sdk'].items():
        if p.startswith('crates/app-peers/src/'):
            (peer/'src'/p.removeprefix('crates/app-peers/src/')).write_text(new)
    adapter = (HERE/'agents_fixture.rs').read_text()
    with (peer/'src/lib.rs').open('a') as file:
        file.write('\n'+adapter+'\npub mod ai_host { pub mod app_peers { pub use crate::{split_origin_marker,host_tools}; } }\npub mod system_chat { pub mod model; pub mod continuity; pub mod session; }\npub mod app_chat { mod calendar_history; pub mod model; #[cfg(test)] mod history_receipt_tests; }\n')
    for family in ['system_chat','app_chat']:
        folder=peer/'src'/family; folder.mkdir()
        shutil.copyfile(SDK/f'crates/shell/src/{family}/model.rs', folder/'model.rs')
    for p in ['calendar_history.rs','history_receipt_tests.rs']:
        shutil.copyfile(STAGE/'sdk/crates/shell/src/app_chat'/p, peer/'src/app_chat'/p)
    shutil.copyfile(SDK/'crates/shell/src/system_chat/continuity.rs',peer/'src/system_chat/continuity.rs')
    constants = '\n'.join(line for line in (SDK/'crates/shell/src/system_chat/session.rs').read_text().splitlines()
                          if line.startswith('pub const SYSTEM_SESSION:') or line.startswith('pub const SYSTEM_PROFILE:'))
    (peer/'src/system_chat/session.rs').write_text(constants+'\n')
    service=STAGE/'service-harness'
    shutil.copytree(SDK/'apps/calendar/host-service/src', service/'src/calendar')
    shutil.copytree(SDK/'apps/calendar/host-service/resources', service/'src/resources')
    for p in ['lib.rs','gpt01_crud_tests.rs']:
        shutil.copyfile(STAGE/'sdk/apps/calendar/host-service/src'/p, service/'src/calendar'/p)
    shutil.copyfile(HERE/'service_fixture.rs',service/'src/lib.rs')
    (service/'Cargo.toml').write_text('[package]\nname="gpt01-calendar-owner-fixture"\nversion="0.0.0"\nedition="2021"\n[dependencies]\nserde={version="=1.0.229",features=["derive"]}\nserde_json="=1.0.151"\nchrono={version="=0.4.45",features=["serde"]}\nchrono-tz="=0.10.4"\n')
    shutil.copyfile(HERE/'service-Cargo.lock',service/'Cargo.lock')
    evidence['harness_scope'] = 'Real Calendar handle/storage/ui/cards and broker/history/Conversation; service registration and GUI adapters are explicit fixture doubles. No Host or Kernel build.'
    (HERE/'BASELINE.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'stage':str(STAGE),'patches':evidence['patches'],'schema_rules':evidence['schema_rules']}))


if __name__ == '__main__':
    main()
