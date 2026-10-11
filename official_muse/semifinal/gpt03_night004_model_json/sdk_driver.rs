//! Test-only stdio gateway to the existing compiled SDK ModelService.
//! Provider bytes and grants are fixture inputs; parsing, retry, schema and
//! Refusal formatting are the actual linked SDK implementation.
use octosense_appstore::services::{dispatch, take_replies_for, ServiceCall, ServiceHost};
use octosense_llm_config::{ApiType, Provider};
use octosense_llm_service::complete::{self, Candidate, Providers, Transport};
use serde_json::{json, Value};
use std::io::{BufRead, Write};
use std::path::PathBuf;
use std::sync::{Arc, Mutex};
use std::time::{Duration, Instant};

const APP: &str = "night004.synthetic-model-json";
struct Surface;
impl ServiceHost for Surface {
    fn open_sheet(&mut self, _: String) { panic!("No real or synthetic consent sheet allowed"); }
    fn close_sheet(&mut self) {}
}
struct Fixed;
impl Providers for Fixed {
    fn candidates(&self) -> Result<Vec<Candidate>, String> {
        let mut provider = Provider::new("local", Some("night004-synthetic-model".into()));
        provider.base_url = Some("http://127.0.0.1:9/v1".into());
        provider.api_type = Some(ApiType::OpenAi);
        Ok(vec![Candidate { provider, key: None }])
    }
}
#[derive(Default)]
struct RawProvider {
    model_text: Mutex<String>,
    seen: Mutex<Vec<Value>>,
}
impl Transport for RawProvider {
    fn post(&self, url: &str, headers: &[(String, String)], request: &str) -> Result<(u16, Vec<u8>), String> {
        assert!(url.starts_with("http://127.0.0.1:9/"));
        assert!(!headers.iter().any(|(name, _)| name.eq_ignore_ascii_case("authorization") || name.eq_ignore_ascii_case("x-api-key")));
        let content = self.model_text.lock().unwrap().clone();
        let response = json!({"choices":[{"message":{"content":content}}],
            "usage":{"prompt_tokens":100,"completion_tokens":20}}).to_string().into_bytes();
        self.seen.lock().unwrap().push(json!({"http_status":200,"request":serde_json::from_str::<Value>(request).unwrap(),
            "raw_model_text":content,"raw_provider_response_utf8":String::from_utf8(response.clone()).unwrap()}));
        // No HTTP request is made. These exact bytes enter the SDK wire parser.
        Ok((200, response))
    }
}

fn main() {
    let root = PathBuf::from(std::env::args().nth(1).expect("owned marked model fixture root"));
    let base = PathBuf::from(std::env::var("NIGHT004_MODEL_ALLOWED_ROOT").unwrap()).canonicalize().unwrap();
    let root = root.canonicalize().unwrap();
    assert!(root.starts_with(&base) && root != base);
    assert_eq!(std::fs::read_to_string(root.join("FIXTURE_ONLY")).unwrap(), "NIGHT004 model JSON fixture only\n");
    let provider = Arc::new(RawProvider::default());
    let host = complete::register_with(complete::Options::default()
        .providers(Arc::new(Fixed)).transport(provider.clone())
        .grants(|app, _| app == APP).clock(|| 1_791_741_600_000));
    for (index, line) in std::io::stdin().lock().lines().enumerate() {
        let request: Value = serde_json::from_str(&line.unwrap()).unwrap();
        if request["method"] == "fixture.quit" {
            println!("{}", json!({"is_ok":true,"data":{"quit":true}}));
            std::io::stdout().flush().unwrap();
            break;
        }
        assert_eq!(request["method"], "model.complete");
        *provider.model_text.lock().unwrap() = request["raw_model_text"].as_str().unwrap().into();
        provider.seen.lock().unwrap().clear();
        let heap = 991_400 + index;
        dispatch(ServiceCall { app_id: APP.into(), service: "model.complete".into(),
            args: request["args"].clone(), from_sheet: false, may_prompt: true, host_dir: root.join(".host") },
            heap, 1, &mut Surface);
        let deadline = Instant::now() + Duration::from_secs(15);
        let result = loop {
            if let Some((_, _, result)) = take_replies_for(&[heap]).pop() { break result; }
            assert!(Instant::now() < deadline, "Actual SDK dispatch did not complete");
            std::thread::sleep(Duration::from_millis(5));
        };
        let reply = match &result {
            Ok(text) => json!({"is_ok":true,"data":serde_json::from_str::<Value>(text).unwrap()}),
            Err(error) => json!({"is_ok":false,"error":error}),
        };
        println!("{}", json!({"reply":reply,"actual_sdk_response":result,
            "provider_attempts":provider.seen.lock().unwrap().clone(),
            "budget":host.budget(APP).to_json(),"real_http_calls":0,
            "boundary":"Actual existing SDK dispatch/ModelHost/wire/accept/schema/Refusal; synthetic provider bytes and grant only"}));
        std::io::stdout().flush().unwrap();
    }
}
