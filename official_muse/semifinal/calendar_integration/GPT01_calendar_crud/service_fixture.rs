//! Compile adapter only. Production service dispatch, sheet and signal APIs are not exercised.
extern crate self as octosense_appstore;
pub mod services {
    use serde_json::Value;
    use std::path::PathBuf;
    pub struct ServiceCall { pub app_id: String, pub service: String, pub args: Value, pub host_dir: PathBuf }
    impl ServiceCall { pub fn method(&self) -> &str { self.service.split_once('.').map(|(_, m)| m).unwrap_or("") } }
    pub struct Replier;
    impl Replier { pub fn send(self, _result: Result<Value, String>) { panic!("Fixture must call the real owner handle directly") } }
    pub trait ServiceHost {}
    pub trait HostService: Send {
        fn family(&self) -> &'static str;
        fn call(&mut self, call: ServiceCall, reply: Replier, host: &mut dyn ServiceHost);
    }
    pub fn register_host_service(_service: Box<dyn HostService>) { panic!("Fixture never registers a production service") }
}
#[path="calendar/lib.rs"]
mod calendar;
