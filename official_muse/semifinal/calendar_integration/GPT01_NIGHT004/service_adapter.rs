//! Fixture transport only; CalendarService::call and event persistence are real SDK source.
extern crate self as octosense_appstore;
pub mod services {
    use serde_json::Value;
    use std::{path::PathBuf, sync::{Arc, Mutex}};
    pub struct ServiceCall { pub app_id: String, pub service: String, pub args: Value, pub host_dir: PathBuf }
    impl ServiceCall { pub fn method(&self) -> &str { self.service.split_once('.').map(|(_, m)| m).unwrap_or("") } }
    pub struct Replier(pub Arc<Mutex<Option<Result<Value,String>>>>);
    impl Replier { pub fn send(self, result: Result<Value, String>) { let mut r=self.0.lock().unwrap(); assert!(r.is_none()); *r=Some(result); } }
    pub trait ServiceHost { fn open_sheet(&mut self, body:String); fn close_sheet(&mut self); }
    pub trait HostService: Send {
        fn family(&self) -> &'static str;
        fn call(&mut self, call: ServiceCall, reply: Replier, host: &mut dyn ServiceHost);
    }
    pub fn register_host_service(_service: Box<dyn HostService>) { panic!("Fixture never registers into a production Host") }
}
#[path="calendar/lib.rs"]
pub mod calendar;

pub fn owner_call(root: &std::path::Path, owner: &str, method: &str, args: serde_json::Value) -> Result<serde_json::Value,String> {
    use services::HostService;
    struct FixtureHost;
    impl services::ServiceHost for FixtureHost {
        fn open_sheet(&mut self, _body:String) { panic!("No GUI in this fixture") }
        fn close_sheet(&mut self) { panic!("No GUI in this fixture") }
    }
    let result=std::sync::Arc::new(std::sync::Mutex::new(None));
    calendar::CalendarService.call(services::ServiceCall {app_id:owner.into(), service:format!("calendar.{method}"), args, host_dir:root.into()}, services::Replier(result.clone()), &mut FixtureHost);
    let result=result.lock().unwrap().take().expect("real synchronous CalendarService replied");
    result
}
