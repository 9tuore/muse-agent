use serde_json::{json, Value};
use std::{io::{self,Read},path::PathBuf};
fn main() {
    let root=PathBuf::from(std::env::args_os().nth(1).expect("isolated fixture root"));
    assert!(root.file_name().unwrap().to_string_lossy().starts_with("gpt01-night004-") && root.join("FIXTURE_ONLY").is_file(),"Only synthetic fixture directories are accepted");
    let mut input=String::new();io::stdin().read_to_string(&mut input).unwrap();
    let request:Value=serde_json::from_str(&input).unwrap();
    let outcome=gpt01_night004_calendar::owner_call(&root,request["owner"].as_str().unwrap(),request["method"].as_str().unwrap(),request["args"].clone());
    let result=match outcome { Ok(data)=>json!({"ok":true,"data":data}), Err(error)=>json!({"ok":false,"error":error}) };
    println!("{}",json!({"fixture_authorization":true,"process_id":std::process::id(),"result":result}));
}
