"""Split the unchanged Store test unit from five-crate wiring preparation."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent


def prepare(full, prior, hub, out):
    assert 'build' in out.resolve().parts
    out.mkdir(parents=True, exist_ok=False)
    for name in ['app-contract', 'app-policy', 'app-hub']:
        shutil.copytree(full / 'crates' / name, out / 'crates' / name)
    # Reuse the three-crate workspace that central actually resolved and
    # tested in r3. Only these new Store sources/tests differ; no appstore,
    # CardApp or Shell dependency is hidden inside this build claim.
    shutil.copyfile(prior / 'Cargo.toml', out / 'Cargo.toml')
    shutil.copyfile(prior / 'Cargo.lock', out / 'Cargo.lock')
    sources = {}
    for relative in ['crates/app-hub/src/client.rs', 'crates/app-hub/src/lib.rs',
                     'crates/app-hub/tests/per_app_offer.rs']:
        source = full / relative
        target = out / relative
        assert source.read_bytes() == target.read_bytes()
        sources[relative] = hashlib.sha256(target.read_bytes()).hexdigest()
    wanted = '33dea2f1f3ad3f1346a219aa8cf6e91b31361e23'
    sdk = hub.parent / 'octoscript-makepad'
    head = (sdk / '.git/HEAD').read_text().strip()
    result = {'kind':'STORE_ONLY_SHARED_OFFER_PREPARED_NOT_COMPILED',
        'members':['app-contract','app-policy','app-hub'],'source_matches_full_workspace':sources,
        'workspace_sha256':hashlib.sha256((out/'Cargo.toml').read_bytes()).hexdigest(),
        'initial_lock_sha256':hashlib.sha256((out/'Cargo.lock').read_bytes()).hexdigest(),
        'nominal_octoscript_makepad_rev':{'hub_manifest_requested':wanted,'local_checkout_head':head,
            'head_matches':head==wanted,'full_source_byte_identity':'NOT_VERIFIED',
            'cargo_offline_cache_rev':'MISSING_PER_FULL_WORKSPACE_LOG'},
        'tests_prepared':10,'cargo_started':False,'store_tests':'NOT_RUN',
        'appstore_cardapp_shell_wiring':'NOT_COMPILED','formal_status':'BLOCKED'}
    (HERE/'store-only-preparation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__ == '__main__':
    p=argparse.ArgumentParser()
    for name in ['full','prior','hub','out']: p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args(); prepare(a.full.resolve(),a.prior.resolve(),a.hub.resolve(),a.out.resolve())
