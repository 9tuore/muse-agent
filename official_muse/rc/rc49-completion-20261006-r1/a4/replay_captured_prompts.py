#!/usr/bin/env python3
"""Two native completions of synthetic prompts captured from real rc49 Host calls."""
import importlib.util
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from urllib.request import Request, urlopen

sys.dont_write_bytecode = True
E = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('diagnosis', E/'diagnose_local_model.py')
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)
case = E/'raw-replay'
case.mkdir(exist_ok=False)
local = case/'.local-state'
local.mkdir()
with socket.socket() as probe:
    probe.bind(('127.0.0.1',0))
    port=probe.getsockname()[1]
base='http://127.0.0.1:'+str(port)
env={k:os.environ[k] for k in ('HOME','USER','TMPDIR','LANG') if k in os.environ}
env['PATH']='/usr/bin:/bin'
command=[str(d.RES/'local-model/llama/llama-server'),'--model',str(d.RES/'local-model/Qwen3-0.6B-Q4_K_S-pure.gguf'),
    '--host','127.0.0.1','--port',str(port),'--ctx-size','4096','--parallel','1','--threads','4',
    '--gpu-layers','0','--offline','--no-webui','--temp','0.2','--reasoning','off',
    '--chat-template-kwargs','{"enable_thinking":false}']
result=dict(scope='two exact captured tokenized prompts to existing native runner; not Host model.complete',
            status='FAIL',calls=[],host_or_weights_changed=False,new_runtime=False)
server=None
with (local/'server.log').open('w') as log:
    try:
        server=subprocess.Popen(command,env=env,stdout=log,stderr=log)
        for _ in range(240):
            if server.poll() is not None:raise RuntimeError('own server exited')
            try:
                with urlopen(base+'/health',timeout=1) as response:
                    if response.status==200:break
            except OSError:pass
            time.sleep(.25)
        else:raise RuntimeError('own server health timeout')
        prompts=sorted((E/'baseline-initialized').glob('PROMPT-*.json'))
        assert len(prompts)==2
        for i,path in enumerate(prompts,1):
            prompt=json.loads(path.read_text())['prompt']
            assert d.QUESTIONS[i-1][0] in prompt
            req=Request(base+'/completion',data=json.dumps(dict(prompt=prompt,stream=False)).encode(),
                        headers={'Content-Type':'application/json'})
            with urlopen(req,timeout=120) as response:raw=json.load(response)
            content=raw['content']
            try:decoded=json.loads(content)
            except ValueError:decoded=None
            row=dict(index=i,source_prompt_file=str(path.relative_to(E)),raw_response=raw,
                     decoded_json=decoded,host_saved_text=json.loads((E/'baseline-initialized'/('host-%d.json'%i)).read_text())['answer']['text'])
            row['matches_host_saved_text']=isinstance(decoded,dict) and decoded.get('reply')==row['host_saved_text']
            result['calls'].append(row)
            d.dump(case/('raw-%d.json'%i),row)
            print('native replay',i,repr(content),'matches Host:',row['matches_host_saved_text'],flush=True)
        result['status']='PASS' if all(x['matches_host_saved_text'] for x in result['calls']) else 'PARTIAL'
    finally:
        d.stop(server)
        result['own_model_stopped']=server is None or server.poll() is not None
        d.dump(case/'RESULT.json',result)
