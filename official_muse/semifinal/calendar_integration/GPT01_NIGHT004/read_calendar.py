#!/usr/bin/env python3
"""Read real CalendarService from an explicitly marked synthetic host directory.

Runner protocol: argv[1]=host root; stdin={owner,method,args}; stdout={result}.
Human CLI: --host-dir ROOT --id ID. Both paths enforce read-only service methods.
"""
from pathlib import Path
import argparse,json,subprocess,sys
HERE=Path(__file__).resolve().parent
OWN=HERE.parents[3]
parser=argparse.ArgumentParser()
parser.add_argument('root',type=Path,nargs='?')
parser.add_argument('--host-dir',type=Path)
parser.add_argument('--id')
args=parser.parse_args()
assert bool(args.root) != bool(args.host_dir),'Specify exactly one host directory'
root=(args.root or args.host_dir).resolve()
assert root.joinpath('FIXTURE_ONLY').is_file(),'Central must explicitly mark its synthetic GUI host directory; this helper does not create the marker.'
request={'owner':'os.calendar','method':'get_event','args':{'id':args.id}} if args.id else json.load(sys.stdin)
assert request.get('owner')=='os.calendar','Only the Calendar owner may be read'
assert request.get('method') in ('events','get_event'),'Independent GUI helper is read-only'
binary=OWN/'build/gpt01-calendar-history/target/debug/gpt01-night004-calendar'
r=subprocess.run([str(binary),'--read-only',str(root)],input=json.dumps(request),capture_output=True,text=True,timeout=10)
assert r.returncode==0,r.stderr
print(r.stdout.strip())
