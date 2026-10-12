#!/usr/bin/env python3
"""Only public service configuration; seed no chat/Memory/Goal/Run/grant data."""
import argparse,json
from pathlib import Path
from urllib.parse import urlsplit
from fixture_scope import scope,atomic_json

def prepare(root):
    root=scope(root);ready=json.loads((root/'ready.json').read_text());url=ready['model_base_url'];parsed=urlsplit(url)
    if parsed.scheme!='http' or parsed.hostname!='127.0.0.1' or parsed.path!='/v1':raise ValueError('Explicit loopback fixture endpoint required')
    # The actual WorkBuddy launcher overrides OCTOS_APP_CORE_DIR to this path.
    core=root/'kernel/.octos';path=core/'profiles/_main.json'
    if path.exists():raise ValueError('Do not replace an existing GUI provider selection')
    profile={'id':'_main','name':'SPRINT005 Synthetic LocalFixture','enabled':True,'created_at':'2026-10-12T05:11:25Z','updated_at':'2026-10-12T05:11:25Z',
             'config':{'llm':{'primary':{'family_id':'local','model_id':'sprint005-fixture','route':{'base_url':url,'api_type':'openai'}}},'env_vars':{}}}
    atomic_json(path,profile);path.chmod(0o600)
    env={'MUSE_INTEGRATED_STATE':str(root),'OCTOS_APP_CORE_DIR':str(core),'OCTOSENSE_MAIL_VAULT':'file','OCTOSENSE_LLM_VAULT':'file'}
    atomic_json(root/'launch-environment.json',env)
    atomic_json(root/'tls-proposal-environment.json',dict(env,OCTOSENSE_MAIL_TLS_FIXTURE_ROOT=str(root)))
    return {'profile_path':str(path),'launch_environment':env,'business_data_seeded':False,'keychain_accessed':False,'kernel_executed':False}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);a=p.parse_args();print(json.dumps(prepare(a.root)))
