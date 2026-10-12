#!/usr/bin/env python3
"""Finalize explicit human-visible observations; this file never drives product state."""
import argparse,json,hashlib
from pathlib import Path
from ua_gui import now
from record_acceptance import record
p=argparse.ArgumentParser();p.add_argument('attempt',type=Path);p.add_argument('--status',required=True);p.add_argument('--observed',required=True);p.add_argument('--expected',required=True);p.add_argument('--steps',required=True);p.add_argument('--result-class',default='NO_EXECUTION');p.add_argument('--last-image-observed',required=True);a=p.parse_args();d=a.attempt;h=json.loads((d/'identity.json').read_text());images=[]
for image in sorted(d.glob('*.png')):
 proof=image.with_suffix('.visual-inspected.json');v=json.loads(proof.read_text()) if proof.exists() else {};images.append({'file':image.name,'observed':v.get('observed') or a.last_image_observed,'inspected_at_utc':v.get('inspected_at_utc') or now()})
(d/'visual-inspection.json').write_text(json.dumps({'images':images},ensure_ascii=False,indent=2)+'\n')
r={'test_id':d.parent.name,'round_id':d.parent.parent.name,'candidate_id':h['candidate_id'],'started_at_utc':json.loads((d/'attempt.json').read_text())['started_at_utc'],'ended_at_utc':now(),'status':a.status,'expected':a.expected,'observed':a.observed,'actual_gui_steps':a.steps.split('|'),'result_class':a.result_class,'readback_required':False};(d/'result.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');record(d/'result.json')
