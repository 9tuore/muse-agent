use std::io::{self,BufRead,Write};
use serde_json::json;
fn main(){
    let root=std::env::args_os().nth(1).expect("explicit marked fixture host root");
    let mut session=match gpt01_night004_relay::relay_jsonl::Session::new(std::path::Path::new(&root)){
        Ok(v)=>v,Err(e)=>{eprintln!("{e}");std::process::exit(2)}};
    for line in io::stdin().lock().lines(){
        let response=match line{
            Ok(line) if line.len()<=1024*1024=>match serde_json::from_str(&line){Ok(v)=>session.call(v),Err(e)=>json!({"is_ok":false,"error":{"kind":"bad_json","message":e.to_string()},"fixture":{"authorization":true,"kernel":false}})},
            _=>json!({"is_ok":false,"error":{"kind":"input_error","message":"Unreadable line or line exceeds 1 MiB"}})
        };
        println!("{response}");io::stdout().flush().unwrap();
    }
}
