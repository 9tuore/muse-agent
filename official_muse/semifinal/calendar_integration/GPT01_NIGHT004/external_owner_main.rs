//! Explicit synthetic external owner update; unchanged production CalendarService.
use serde_json::{json, Value};
use std::{io::{self, Read}, path::{Path, PathBuf}};

fn regular(path: &Path) -> Result<(), String> {
    let meta=std::fs::symlink_metadata(path).map_err(|e|e.to_string())?;
    if meta.file_type().is_symlink() { return Err("Fixture paths must not be symlinks".into()); }
    Ok(())
}

fn run() -> Result<Value,String> {
    let mut argv=std::env::args_os().skip(1);
    let first=argv.next().ok_or("Explicit fixture root required")?;
    let check=first=="--check-only";
    let input_root=PathBuf::from(if check { argv.next().ok_or("Explicit fixture root required")? } else { first });
    regular(&input_root)?;
    let root=input_root.canonicalize().map_err(|e|e.to_string())?;
    let id=argv.next().ok_or("Explicit event ID required")?.into_string().map_err(|_|"Invalid event ID")?;
    let request_id=argv.next().ok_or("Explicit fixture request ID required")?.into_string().map_err(|_|"Invalid request ID")?;
    if argv.next().is_some() || id.is_empty() || id.len()>64 || request_id.is_empty() || request_id.len()>160
        || id.chars().chain(request_id.chars()).any(|c|c.is_whitespace()||c.is_control()) {
        return Err("Exact bounded event/request IDs and no extra arguments required".into());
    }
    let central=Path::new("/Users/mima0000/.codex/worktrees/muse-semifinal-a-20261009/Agent APP黑客松/build/night-004").canonicalize().map_err(|e|e.to_string())?;
    let temporary=root.starts_with(std::env::temp_dir().canonicalize().map_err(|e|e.to_string())?)
        && root.file_name().is_some_and(|s|s.to_string_lossy().starts_with("gpt01-night004-"));
    if !(temporary || (root.starts_with(&central)&&root!=central)) { return Err("Only isolated NIGHT-004 fixture roots are allowed".into()); }
    let host=root.join("apps/.host");
    let marker=host.join("EXTERNAL_CALENDAR_OWNER_WRITE_OK.json");
    for path in [root.join("FIXTURE_ONLY"),root.join("apps"),host.clone(),host.join("FIXTURE_ONLY"),host.join("calendar"),host.join("calendar/events.json"),marker.clone()] { regular(&path)?; }
    let scope:Value=serde_json::from_slice(&std::fs::read(marker).map_err(|e|e.to_string())?).map_err(|e|e.to_string())?;
    if scope["purpose"]!="NIGHT004_SYNTHETIC_EXTERNAL_OWNER" || scope["host_dir"]!=host.to_string_lossy().as_ref()
        || scope["event_id"]!=id || scope["fixture_request_id"]!=request_id {
        return Err("External write marker must bind this exact host, event and fixture request ID".into());
    }
    let mut input=String::new();io::stdin().read_to_string(&mut input).map_err(|e|e.to_string())?;
    let request:Value=serde_json::from_str(&input).map_err(|e|e.to_string())?;
    let args=request["args"].as_object().ok_or("Object arguments required")?;
    if request["owner"]!="os.calendar" || request["method"]!="update_event" || request["args"]["id"]!=id
        || request["args"]["expected"]["id"]!=id || request["args"]["expected"]["request_id"]!=request_id
        || args.keys().any(|k|!matches!(k.as_str(),"id"|"expected"|"title"|"start"|"end"|"timezone"|"location"|"notes")) {
        return Err("Only exact owner update_event with its original expected snapshot is allowed".into());
    }
    let current=gpt01_night004_calendar::owner_call(&host,"os.calendar","get_event",json!({"id":id}))?;
    if current["found"]!=true || current["event"]["id"]!=id || current["event"]["request_id"]!=request_id {
        return Err("Target is not the explicitly selected existing synthetic event".into());
    }
    if check { return Ok(json!({"read_only":true,"current_owner_result":current,"prepared_owner_request":request})); }
    // Do not substitute the fresh read for expected. The real service owns CAS.
    gpt01_night004_calendar::owner_call(&host,"os.calendar","update_event",request["args"].clone())
}

fn main() {
    let result=match run(){Ok(data)=>json!({"ok":true,"data":data}),Err(error)=>json!({"ok":false,"error":error})};
    println!("{}",json!({"fixture_authorization":true,"external_owner_process":true,"process_id":std::process::id(),"kernel":false,"result":result}));
}
