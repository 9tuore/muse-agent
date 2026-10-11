#!/usr/bin/env python3
"""One explicit synthetic owner update; no direct store edits or retry."""
import argparse,json,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
OWN=HERE.parents[3]
p=argparse.ArgumentParser()
p.add_argument('--config',type=Path,required=True)
p.add_argument('--event-id',required=True)
p.add_argument('--fixture-request-id',required=True)
p.add_argument('--expected-file',type=Path,required=True,help='Exact event object from an actual earlier owner/Kernel get_event result')
p.add_argument('--title')
p.add_argument('--notes')
p.add_argument('--check-only',action='store_true')
a=p.parse_args()
try:
    root=Path(json.loads(a.config.read_text())['fixture_root'])
    if root.is_symlink():raise ValueError('Fixture root cannot be a symlink')
    root=root.resolve(strict=True)
    event=json.loads(a.expected_file.read_text())
    if not isinstance(event,dict) or event.get('id')!=a.event_id or event.get('request_id')!=a.fixture_request_id:
        raise ValueError('Expected file must be the exact selected event object with its stable fixture request ID')
    if a.title is None and a.notes is None:raise ValueError('Explicit changed title or notes is required')
    fields=('title','start','end','timezone','location','notes')
    if any(k not in event for k in fields):raise ValueError('Complete original event fields are required')
    args={k:event[k] for k in fields}
    if a.title is not None:args['title']=a.title
    if a.notes is not None:args['notes']=a.notes
    if all(args[k]==event[k] for k in fields):raise ValueError('Replacement must actually change the selected event')
    args.update(id=a.event_id,expected=event)
    request={'owner':'os.calendar','method':'update_event','args':args}
    binary=OWN/'build/gpt01-calendar-history/target/debug/gpt01-night004-external-owner'
    command=[str(binary)]+(['--check-only'] if a.check_only else [])+[str(root),a.event_id,a.fixture_request_id]
    result=subprocess.run(command,input=json.dumps(request),capture_output=True,text=True,timeout=10)
    if result.returncode:raise RuntimeError('External owner helper failed: '+result.stderr.strip())
    reply=json.loads(result.stdout)
    print(json.dumps(reply),flush=True)
    if reply.get('result',{}).get('ok') is not True:sys.exit(2)
except (OSError,ValueError,RuntimeError,subprocess.SubprocessError) as error:
    print(json.dumps({'fixture_authorization':True,'kernel':False,'result':{'ok':False,'error':str(error)}}),flush=True)
    sys.exit(2)
