"""Read-only source-contract experiment; not runtime or signed admission."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SDK = ROOT / '.local-state/official-rc2-source'
HUB = ROOT / '.local-state/hub-contract-sdk/app-hub'
HERE = Path(__file__).resolve().parent
tools = json.loads((SDK / 'apps/calendar/bundle/tools.json').read_text())['tools']
shared = sorted(t['name'] for t in tools if t.get('shareable'))
assert shared == ['calendar.add_event', 'calendar.events', 'calendar.notify']
relay = (SDK / 'crates/shell/src/host_tools/relay.rs').read_text()
assert 'Self::shareable(entry) &&' in relay
assert 'if !env.consent(&calling)' in relay
assert 'Self::check_admission' in relay
delegation = (SDK / 'crates/shell/src/host_tools/script_apps.rs').read_text()
assert 'loaded.asks = agent.generic_tools' in delegation
assert 'super::grant(app, &owner, tool)' in delegation
patch = (HERE / 'desktop-store-calendar-offer.patch').read_text()
assert '+++ b/crates/shell/src/host_tools/relay.rs' not in patch
assert 'with_require_signature(false)' not in patch
hub_patch = (HERE / 'hub-store-calendar-offer.patch').read_text()
assert 'limits.offered_tools' in hub_patch
assert 'limits.require_signature =' not in hub_patch
assert 'system::set_agent_tool_offer("muse' not in patch
result = {'kind': 'SOURCE_CONTRACT_ONLY', 'checks': 11, 'status': 'PASS',
          'original_shared_tools': shared, 'signed_admission': 'NOT_RUN',
          'full_relay': 'NOT_RUN', 'builtin_calendar_crud': 'NOT_REPEATED'}
(HERE / 'source-contract-evidence.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result))
