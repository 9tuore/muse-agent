#!/usr/bin/env python3
"""Read only the authorized test profile; emit no routes, env, keys or suffixes."""
from pathlib import Path
import datetime
import json
import re
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[4]
PROFILE = ROOT / 'official_muse/app/build/ui-memory-20261003/morning-final-live-r2/private/home/octos-home/.octos/profiles/_main.json'
REGISTRY = ROOT / 'vendor/octosense/apps/ai-providers/config/src/registry.rs'
CATALOG = ROOT / 'vendor/octosense/apps/ai-providers/config/data/model_catalog.json'


def project():
    pattern = re.compile(r'fam\("([^"]+)", "[^"]+", &\[([^\]]*)\], (?:Some\("[^"]*"\)|None), &\[[^\]]*\],\s*(?:Some\("([^"]*)"\)|None),\s*(?:Some\("([^"]*)"\)|None), (?:true|false)\)')
    families = {}
    for family, aliases, base, model in pattern.findall(REGISTRY.read_text()):
        row = (family, base or None, model or None)
        for name in [family, *re.findall(r'"([^"]+)"', aliases)]:
            families.setdefault(name.lower(), row)
    assert len(families) > 20, 'Registry parser does not match this version'
    catalog = {row['provider']: row.get('type') for row in json.loads(CATALOG.read_text())['models']}
    # Do not inspect env_vars or resolve any keychain marker. Whole JSON is
    # decoded in memory only; errors never print the document or its values.
    try:
        root = json.loads(PROFILE.read_text())
    except (OSError, ValueError):
        raise SystemExit('Authorized profile could not be decoded; no content emitted')
    llm = root.get('config', {}).get('llm', {})
    choices = [llm.get('primary'), *llm.get('fallbacks', [])]
    rows = []
    route_shapes = []
    for choice in choices:
        if not isinstance(choice, dict) or not isinstance(choice.get('family_id'), str):
            continue
        found = families.get(choice['family_id'].lower())
        family, default_base, default_model = found or ('<unknown>', None, None)
        model = choice.get('model_id')
        if not isinstance(model, str) or not model.strip():
            model = default_model
        # Emit only a catalog model id; unknown arbitrary profile strings are withheld.
        if not isinstance(model, str) or family+'/'+model not in catalog:
            model = '<unknown>'
        route = choice.get('route') or {}
        if not isinstance(route, dict):
            route = {}
        base = route.get('base_url')
        if not isinstance(base, str) or not base.strip():
            base = default_base
        try:
            parsed = urlsplit(base or '')
            host = (parsed.hostname or '').lower()
            origin = (parsed.scheme.lower(), host, parsed.port)
            api = route.get('api_type')
            if api not in ('openai', 'anthropic', 'responses'):
                api = 'anthropic' if family == 'anthropic' or (base or '').rstrip('/').endswith('/anthropic') else 'openai'
            route_shapes.append((origin, parsed.path.rstrip('/'), api))
        except ValueError:
            host = ''
            route_shapes.append(None)
        rows.append({'family': family, 'model': model,
                     'effective_route_matches_family_official': bool(default_base and base and base.rstrip('/') == default_base.rstrip('/')),
                     'effective_route_is_loopback': host in ('localhost', '127.0.0.1', '::1') or host.startswith('127.') or host.endswith('.localhost'),
                     'static_catalog_strong': catalog.get(family+'/'+model) == 'strong'})
    return {'checked_at_beijing': datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
            'scope': 'AUTHORIZED_ISOLATED_PROFILE_READ_ONLY_NO_CREDENTIAL_RESOLUTION_NO_MODEL_CALL',
            'configured_candidate_count': len(rows), 'runtime_eligible_candidate_count': 'NOT_CHECKED_NO_KEY_RESOLUTION',
            'providers': rows,
            'first_two_same_effective_origin': len(route_shapes) >= 2 and route_shapes[0] is not None and route_shapes[1] is not None and route_shapes[0][0] == route_shapes[1][0],
            'first_two_same_effective_path': len(route_shapes) >= 2 and route_shapes[0] is not None and route_shapes[1] is not None and route_shapes[0][1] == route_shapes[1][1],
            'first_two_same_effective_api_type': len(route_shapes) >= 2 and route_shapes[0] is not None and route_shapes[1] is not None and route_shapes[0][2] == route_shapes[1][2],
            'distinct_configured_model_count': len({(r['family'], r['model']) for r in rows}),
            'catalog_distinct_non_m3_strong_configured': any(r['model'] not in ('MiniMax-M3', '<unknown>') and r['static_catalog_strong'] for r in rows),
            'limits': ['Configured family/model or static catalog strong is not proof of actual backend identity or successful invocation.',
                       'Custom route mismatch is an observation, not a product failure or original T17 requirement.',
                       'No env_vars, endpoint, credential value, marker or suffix is emitted.',
                       'Configured count is not the Host key-filtered runnable candidate count.']}


if __name__ == '__main__':
    print(json.dumps(project(), ensure_ascii=False, indent=2))
