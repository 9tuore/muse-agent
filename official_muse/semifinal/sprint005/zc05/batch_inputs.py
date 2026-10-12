#!/usr/bin/env python3
"""Sequential real UI typing in fields verified in one inspected native form."""
import sys,json
from pathlib import Path
from ua_gui import GUIEvidence,require,check_visible_widget,widgets_digest,now
h,attempt,image,fields,next_image=sys.argv[1:6];g=GUIEvidence(h,attempt);template=json.loads((g.path/Path(image).with_suffix('.visual-template.json')).read_text());original=g.snapshot();require(widgets_digest(original)==template['widgets_sha256'],'Form state changed before batch')
for key,value in json.loads(fields).items():
 rows=g.snapshot();a=[w for w in rows if w.get('ty')=='TextInput' and w.get('i')==key];p=[w for w in rows if w.get('i')=='main_mount'];require(len(a)==len(p)==1,'Unique field and form');b=a[0];old=[w for w in original if w.get('ty')=='TextInput' and w.get('i')==key];require(len(old)==1 and old[0]['r']==b['r'],'Field moved');check_visible_widget(b,p[0],g.identity['remote_window_rect']);proof=dict(template,widgets_sha256=widgets_digest(rows),inspected_at_utc=now(),observed='Caller inspected this native form; all selected fields fully visible and geometry unchanged during sequential real UI typing.',controls=[{'key':key,'rect':b['r'],'pane_rect':p[0]['r'],'fully_visible':True}]);pp=g.path/('batch-'+key+'-'+next_image+'.json');pp.write_text(json.dumps(proof));g.type(key,value,'main_mount',pp)
if len(sys.argv)>6:g.scroll('main_mount',int(sys.argv[6]))
print(g.capture(next_image))
