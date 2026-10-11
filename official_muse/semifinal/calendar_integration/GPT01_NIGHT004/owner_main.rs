use serde_json::{json, Value};
use std::{io::{self,Read},path::PathBuf};
fn main() {
    let mut argv=std::env::args_os().skip(1);let first=argv.next().expect("isolated fixture root");
    let read_only=first=="--read-only";
    let root=PathBuf::from(if read_only{argv.next().expect("isolated fixture root")}else{first});
    let temporary=root.file_name().unwrap().to_string_lossy().starts_with("gpt01-night004-");
    let central_night=PathBuf::from("/Users/mima0000/.codex/worktrees/muse-semifinal-a-20261009/Agent APP黑客松/build/night-004");
    let central_fixture=read_only&&root.canonicalize().unwrap().starts_with(central_night.canonicalize().unwrap());
    assert!((temporary||central_fixture)&&root.join("FIXTURE_ONLY").is_file(),"Only explicitly marked synthetic fixture directories are accepted");
    let mut input=String::new();io::stdin().read_to_string(&mut input).unwrap();
    let request:Value=serde_json::from_str(&input).unwrap();
    if read_only{assert!(matches!(request["method"].as_str(),Some("events"|"get_event")),"Independent GUI helper is read-only");}
    let outcome=gpt01_night004_calendar::owner_call(&root,request["owner"].as_str().unwrap(),request["method"].as_str().unwrap(),request["args"].clone());
    let result=match outcome { Ok(data)=>json!({"ok":true,"data":data}), Err(error)=>json!({"ok":false,"error":error}) };
    println!("{}",json!({"fixture_authorization":true,"process_id":std::process::id(),"result":result}));
}
