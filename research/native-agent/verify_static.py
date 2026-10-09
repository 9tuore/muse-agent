#!/usr/bin/env python3
"""Read-only static evidence. Does not execute native admission, Splash, or Agent."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'research/native-agent'
CACHE = ROOT / '.local-state/native-agent-upstream'

def sha(data):
    return hashlib.sha256(data).hexdigest()

main = (ROOT / 'bundle/main.splash').read_text()
manifest = json.loads((ROOT / 'bundle/manifest.json').read_text())
inventory = json.loads((OUT / 'upstream-sources.json').read_text())
verified = []
for item in inventory:
    data = (CACHE / item['repository'] / item['path']).read_bytes()
    blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
    assert blob == item['blob'] and sha(data) == item['sha256'], item['path']
    verified.append(item['path'])
policy_path = CACHE / 'OctoSense-App-Hub/crates/app-policy/src/agent.rs'
policy = policy_path.read_text()
assert 'pub const MAX_NAMESPACE: usize = 24;' in policy
assert "c.is_ascii_lowercase() || c.is_ascii_digit() || c == '_'" in policy
assert 'a module id, or the last segment of an app id' in policy
namespace = manifest['id'].rsplit('.', 1)[-1]
assert namespace == 'muse-goals'
allowed = re.fullmatch(r'[a-z0-9_]{1,24}', namespace) is not None
assert not allowed
# This predicate is a transparent static reproduction, NOT a run of ToolsManifest::validate.
lines = policy.splitlines()
(OUT / 'namespace-policy-excerpt.txt').write_text(
    'Pinned Hub 18cd41d91b326db199fbed4129484a9ba1a8c63d\n'
    'crates/app-policy/src/agent.rs; Git blob verified by inventory\n'
    + '\n'.join(f'{i+1}: {lines[i]}' for i in [62, *range(324, 337)]) + '\n')
tools = json.loads((OUT / 'prototype/tools.json').read_text())['tools']
proto = (OUT / 'prototype/read_tools.splash').read_text()
helpers = ['gm_has', 'gm_field', 'gm_score', 'gm_entry_access', 'gm_account_allowed',
           'core_action_index', 'core_goal_index']
globals_ = ['memory', 'goals', 'actions', 'calendar_receipts', 'gm_enabled', 'gm_ready',
            'core_memory_ready', 'core_storage_ready', 'gm_project', 'gm_owner']
for name in helpers:
    assert re.search(r'\bfn\s+' + name + r'\(', main), name
for name in globals_:
    assert re.search(r'\blet\s+' + name + r'\s*=', main), name
for tool in tools:
    assert tool['name'].startswith(namespace + '.')
    assert tool['risk'] == 'read' and tool['implemented_by'] == 'app'
    assert tool['private_data'] is True
    assert tool['background'] is False and tool['shareable'] is False
    assert 'host_method' not in tool
    assert tool['input_schema']['additionalProperties'] is False
    assert {'project', 'owner'} <= set(tool['input_schema']['required'])
    assert tool['name'] in proto
assert len(tools) == 3
for forbidden in ['host.request(', 'fs.write', 'gm_context(', 'gm_save(', 'gm_correct(',
                  'gm_forget(', 'core_begin_action(', 'core_finish_action(', 'core_goals_ready']:
    assert forbidden not in proto, forbidden
assert 'fn app_tool(' not in main
assert 'mod.app_tools.' not in main
assert not (ROOT / 'bundle/tools.json').exists()
assert not (ROOT / 'bundle/AGENT.md').exists()
assert manifest['agent'] is None
calendar_root = CACHE / 'OctoSense/apps/calendar'
calendar_tools = json.loads((calendar_root / 'bundle/tools.json').read_text())['tools']
calendar_service = (calendar_root / 'host-service/src/lib.rs').read_text()
calendar_ui = (calendar_root / 'host-service/src/ui.rs').read_text()
relay = (CACHE / 'OctoSense/crates/shell/src/host_tools/relay.rs').read_text()
calendar_names = {t['name'] for t in calendar_tools}
shared = sorted(t['name'] for t in calendar_tools if t.get('shareable', False))
assert shared == ['calendar.add_event', 'calendar.events', 'calendar.notify']
assert 'calendar.get' not in calendar_names
assert '"get" =>' not in calendar_service
assert 'if app != APP' in calendar_service and 'pub const APP: &str = "os.calendar";' in calendar_service
assert '"update_event" => {' in calendar_service and 'ui::update(host_dir,args)?' in calendar_service
assert 'pub fn update(' in calendar_ui and 'if *event != expected' in calendar_ui
assert 'Self::shareable(entry) &&' in relay and 'consent_pending' in relay
contained = (CACHE / 'OctoSense/crates/ai-host/src/contained.rs').read_text()
octos_services = ['octos.session.open', 'octos.session.history', 'octos.turn.start', 'octos.turn.interrupt']
for service in octos_services:
    assert service in contained
assert '"octos.turn.start" => &["text", "trigger", "from"]' in contained
assert 's.contains(&call.service)' in contained and 'ContainedGate::Consent' in contained
assert 'Ok(None) => Vec::new()' in policy

calendar_evidence = {
    'kind': 'STATIC_ONLY', 'owner': 'os.calendar', 'storage': '<host_dir>/calendar/events.json',
    'tools': [{'name': t['name'], 'risk': t['risk'], 'shareable': t.get('shareable', False),
               'confirm': t.get('confirm'), 'implemented_by': t['implemented_by']} for t in calendar_tools],
    'cross_app_shareable': shared, 'direct_muse_service_access': 'REFUSED_BY_OWNER_CHECK',
    'update_implemented': True, 'update_cross_app_shareable': False,
    'get_tool_declared': False, 'readback': 'calendar.events then exact ID/fields comparison; not an execution receipt',
    'list_limit_max': 200, 'live_relay': 'NOT_TESTED', 'model_choice': 'NOT_TESTED',
    'device_calendar': 'ISOLATED_RESEARCH_NOT_DEFAULT_PRODUCT_ROUTE',
    'splash_app_agent_services': octos_services, 'octos_runtime': 'NOT_TESTED',
    'own_namespace_gate_applies_to': 'Muse-owned tools.json; no-file outbound Agent is separate untested path',
}
(OUT / 'CALENDAR_STATIC_EVIDENCE.json').write_text(json.dumps(calendar_evidence, indent=2) + '\n')
report = {
    'kind': 'STATIC_ONLY', 'branch': subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip(),
    'source_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
    'bundle': {'id': manifest['id'], 'version': manifest['version'], 'main_sha256': sha((ROOT / 'bundle/main.splash').read_bytes()),
               'manifest_sha256': sha((ROOT / 'bundle/manifest.json').read_bytes()), 'agent': manifest['agent'],
               'tools_json_present': False, 'agent_md_present': False, 'app_tool_present': False},
    'namespace': {'value': namespace, 'rule': '[a-z0-9_]{1,24}', 'static_predicate_matches': allowed,
                  'status': 'BLOCKED', 'native_gate': 'NOT_RUN', 'identity_renamed': False},
    'upstream_blobs_verified': len(verified), 'prototype_helpers_verified': helpers,
    'prototype_globals_verified': globals_, 'prototype_declarations': len(tools),
    'prototype_static_checks': 'PASS', 'splash_vm': 'NOT_RUN', 'model_tool_selection': 'NOT_TESTED',
    'installed_target_host_abi': 'UNKNOWN_NOT_TESTED', 'external_actions': 'NONE', 'calendar_static_checks': 'PASS',
}
(OUT / 'STATIC_EVIDENCE.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(report, ensure_ascii=False, indent=2))
