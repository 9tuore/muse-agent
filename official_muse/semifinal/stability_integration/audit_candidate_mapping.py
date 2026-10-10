"""Read-only candidate mapping/freeze inventory. Does not certify runtime or 20 runs."""
import argparse
import hashlib
import json
from pathlib import Path
import re


def sha(data):
    return hashlib.sha256(data).hexdigest()


def view_contract(source):
    """Static interface check only: exact helper shape and action-chain call."""
    text = source.decode('utf-8')
    helper = re.search(r'fn\s+dsl_view\s*\(\s*kind\s*,\s*records\s*\)\s*\{\s*return\s*\{([^{}]*)\}\s*\}', text)
    expected = 'schema_version:"muse.view/1"kind:kindread_only:truetool_authority:falserecords:records'
    return {
        'view_helper_read_only': helper is not None and re.sub(r'\s+', '', helper.group(1)) == expected,
        'action_chain_view_call': re.search(r'dsl_view\s*\(\s*"action_chain"\s*,\s*\[\s*chain\s*\]\s*\)\s*\.\s*to_json\s*\(\s*\)', text) is not None,
    }


def audit(candidate, current_source=None, require_view_envelope=False):
    required = ['identity.json', 'readable-bundle/main.splash', 'bundle/main.splash',
                'readable-bundle/manifest.json', 'bundle/manifest.json']
    missing = [name for name in required if not (candidate / name).is_file()]
    if missing:
        return {'status': 'NOT_TESTED', 'missing_evidence': missing}, 2
    try:
        identity = json.loads((candidate / 'identity.json').read_text())
        source = (candidate / 'readable-bundle/main.splash').read_bytes()
        artifact = (candidate / 'bundle/main.splash').read_bytes()
        manifests = [json.loads((candidate / p).read_text()) for p in required[-2:]]
        transform = identity.get('source_transform', {})
        checks = {
            'source_sha': identity.get('source_sha256') == sha(source),
            'artifact_sha': identity.get('artifact_sha256') == sha(artifact),
            'transform_source_sha': transform.get('source_sha256') == sha(source),
            'transform_artifact_sha': transform.get('artifact_sha256') == sha(artifact),
            'transform_source_bytes': transform.get('bytes_before') == len(source),
            'transform_artifact_bytes': transform.get('bytes_after') == len(artifact),
            'manifest_identity': all(m.get('id') == identity.get('id') and m.get('version') == identity.get('version') for m in manifests),
            'manifest_required': all(m.get('host_api', {}).get('required') == identity.get('required') for m in manifests),
            'manifest_capabilities': all(m.get('capabilities') == identity.get('capabilities') for m in manifests),
        }
        if current_source is not None:
            checks['current_source_sha'] = sha(current_source.read_bytes()) == sha(source)
        if require_view_envelope:
            for prefix, data in [('readable', source), ('compact', artifact)]:
                checks.update({prefix + '_' + name: value for name, value in view_contract(data).items()})
        inventory = {str(p.relative_to(candidate)): sha(p.read_bytes())
                     for p in sorted(candidate.rglob('*')) if p.is_file()}
    except (OSError, ValueError, TypeError, AttributeError) as error:
        return {'status': 'NOT_TESTED', 'unreadable_evidence': str(error)}, 2
    passed = all(checks.values())
    result = {'status': 'PASS_STATIC_MAPPING_ONLY' if passed else 'FAIL_MAPPING',
              'checks': checks, 'source_sha256': sha(source), 'artifact_sha256': sha(artifact),
              'source_bytes': len(source), 'artifact_bytes': len(artifact),
              'file_sha256': inventory,
              'inventory_sha256': sha(json.dumps(inventory, sort_keys=True).encode()),
              'token_opcode_equivalence': 'NOT_TESTED', 'final_20_runs': 'NOT_TESTED',
              'boundary': 'Hashes record current bytes, not admission, semantic equivalence, native consent, Mail/Calendar success or a full-chain freeze receipt.'}
    return result, 0 if passed else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate-dir', required=True, type=Path)
    parser.add_argument('--current-source', type=Path)
    parser.add_argument('--require-view-envelope', action='store_true',
                        help='Require integrated muse.view/1 helper and action-chain call in both sources')
    args = parser.parse_args()
    result, code = audit(args.candidate_dir, args.current_source, args.require_view_envelope)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
