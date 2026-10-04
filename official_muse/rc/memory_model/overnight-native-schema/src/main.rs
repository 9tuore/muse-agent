// Test driver invoking the exact source-bound SDK module; no model/runtime/services.
#[path = "../../../../../vendor/octosense/apps/ai-providers/host-service/src/complete/schema.rs"]
mod production_schema;
use serde_json::{json,Value};
fn main(){
    let args:Vec<String>=std::env::args().collect();
    assert_eq!(args.len(),3,"case JSON path and result JSON path required");
    let cases:Vec<Value>=serde_json::from_str(&std::fs::read_to_string(&args[1]).expect("cases")).expect("case JSON");
    let mut results=Vec::new();
    for case in &cases {
        let (actual,error)=match production_schema::Schema::compile(&case["schema"]){
            Err(error)=>("SCHEMA_COMPILE_ERROR",Some(error)),
            Ok(schema)=>match serde_json::from_str::<Value>(case["raw"].as_str().expect("raw text")){
                Err(error)=>("JSON_ERROR",Some(error.to_string())),
                Ok(value)=>match schema.validate(&value){Ok(())=>("VALID",None),Err(error)=>("SCHEMA_ERROR",Some(error))},
            },
        };
        results.push(json!({"id":case["id"],"category":case["category"],"input_sha256":case["input_sha256"],"expected":case["expected"],"actual":actual,"passed":case["expected"]==actual,"error":error}));
    }
    let failed=results.iter().filter(|r|r["passed"]!=true).count();
    let report=json!({"kind":"ACTUAL_RUST_SDK_SCHEMA_UNIT_TEST","total":results.len(),"passed":results.len()-failed,"failed":failed,"real_model":false,"host_retry_tested":false,"results":results});
    std::fs::write(&args[2],serde_json::to_string_pretty(&report).expect("report JSON")).expect("report write");
    println!("schema cases={}, passed={}, failed={}",results.len(),results.len()-failed,failed);
    if failed>0 {std::process::exit(1)}
}
