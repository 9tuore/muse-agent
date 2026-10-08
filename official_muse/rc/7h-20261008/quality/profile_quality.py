#!/usr/bin/env python3
"""Instrument only a diagnostic copy; timings never constitute candidate PASS."""
import argparse,hashlib,json,re
from pathlib import Path
WRAPPERS={'boot':'','boot_load':'step,boot_error','ui_layout_boot':'','notification_boot':'','chat_boot_begin':'boot_error','chat_boot_read':'from_backup,boot_error','chat_boot_check_header':'boot_error','chat_boot_check':'session_index,entry_start,boot_error','chat_boot_complete':'boot_error','chat_boot_apply':'saved,snapshot','chat_boot_finish':'','core_boot_activity':'','core_boot_memory':'','core_boot_goals':'','gm_boot':'','gm_boot_begin':'','gm_boot_index_part':'phase,start','gm_boot_part':'phase,start','gm_finish_boot':'saved,generated_profile','calendar_boot':'','boot_restore':'boot_error','mail_watch_boot':'','redraw':''}
def main():
 p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();source=a.source.read_text();binding=hashlib.sha256(source.encode()).hexdigest()
 diagnostic='''let rc_started=time_now()
let rc_profile={schema:1 diagnostic_only:true stages:{} events:[]}
fn rc_record(name,began){
 let elapsed=(time_now()-began)*1000
 if rc_profile.stages[name]==nil { rc_profile.stages[name]=[] }
 rc_profile.stages[name].push(elapsed)
 rc_profile.events.push({name:name began_ms:(began-rc_started)*1000 end_ms:(time_now()-rc_started)*1000})
 rc_profile.elapsed_ms=(time_now()-rc_started)*1000
 fs.write("rc-startup-profile.json",rc_profile.to_json())
}
'''
 wrappers=''
 for name,params in WRAPPERS.items():
  source,count=re.subn(r'\bfn '+re.escape(name)+r'\(', 'fn rc_impl_'+name+'(',source);assert count==1,(name,count)
  wrappers+=f'fn {name}({params}){{let began=time_now() let value=rc_impl_{name}({params}) rc_record("{name}",began) return value}}\n'
 marker='start_timeout(0.05, || boot())';assert source.count(marker)==1;source=source.replace(marker,wrappers+marker)
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(diagnostic+source)
 a.out.with_suffix('.binding.json').write_text(json.dumps({'diagnostic_only':True,'production_readable_sha256':binding,'diagnostic_readable_sha256':hashlib.sha256(a.out.read_bytes()).hexdigest(),'stages':list(WRAPPERS),'timings':'Inclusive callback time; diagnostic JSON writes add overhead and are excluded from own callback.'},indent=2)+'\n')
if __name__=='__main__':main()
