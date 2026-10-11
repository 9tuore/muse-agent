#!/usr/bin/env python3
"""Independent synthetic recipient over child stdio. No socket, SMTP, or credentials."""
import json,sys,os
from pathlib import Path
p=Path(sys.argv[1]); p.parent.mkdir(parents=True,exist_ok=True)
rows=json.loads(p.read_text()) if p.exists() else []
for line in sys.stdin:
    request=json.loads(line)
    payload=request['payload']
    assert payload['to']=='receiver@example.invalid'
    assert payload['message_id'].startswith('<')
    rows.append(payload)
    temporary=p.with_suffix('.tmp');temporary.write_text(json.dumps(rows,ensure_ascii=False))
    os.replace(str(temporary),str(p))
    print(json.dumps({'accepted':True,'message_id':payload['message_id']}),flush=True)
