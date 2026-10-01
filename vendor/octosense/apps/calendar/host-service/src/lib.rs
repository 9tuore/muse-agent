//! A bounded EventKit service for contained apps granted `calendar`.
//! The policy isolate checks the capability; EventKit checks macOS access.
//! Mutations have a durable host-side request journal so an uncertain result
//! is never silently retried after a crash or storage failure.

use chrono::{DateTime, FixedOffset};
use octosense_appstore::services::{HostService, Replier, ServiceCall, ServiceHost};
use serde_json::{json, Value};
use sha2::{Digest, Sha256};
use std::collections::BTreeMap;
use std::path::{Path, PathBuf};
use std::sync::Mutex;

static ACTION_LOCK: Mutex<()> = Mutex::new(());

pub fn register() {
    octosense_appstore::services::register_host_service(Box::new(CalendarService));
}

struct CalendarService;

impl HostService for CalendarService {
    fn family(&self) -> &'static str {
        "calendar"
    }

    fn call(&mut self, call: ServiceCall, reply: Replier, _host: &mut dyn ServiceHost) {
        // EventKit queries and the system permission prompt never block the UI.
        std::thread::spawn(move || reply.send(handle(call)));
    }
}

fn text<'a>(args: &'a Value, key: &str) -> Result<&'a str, String> {
    args.get(key)
        .and_then(Value::as_str)
        .map(str::trim)
        .filter(|s| !s.is_empty())
        .ok_or_else(|| format!("{key} is required"))
}

fn bounded_text(args: &Value, key: &str, max: usize) -> Result<(), String> {
    let value = text(args, key)?;
    if value.len() > max || value.contains(['\r', '\n']) {
        return Err(format!("{key} is too long or contains a line break"));
    }
    Ok(())
}

fn time(args: &Value, key: &str) -> Result<DateTime<FixedOffset>, String> {
    DateTime::parse_from_rfc3339(text(args, key)?).map_err(|_| format!("{key} must be RFC 3339 with a UTC offset"))
}

fn valid_range(args: &Value) -> Result<(), String> {
    let start = time(args, "start")?;
    let end = time(args, "end")?;
    let seconds = (end - start).num_seconds();
    if seconds <= 0 || seconds > 31 * 86_400 {
        return Err("The date range must be positive and at most 31 days".into());
    }
    Ok(())
}

fn valid_request(args: &Value) -> Result<(), String> {
    let id = text(args, "request_id")?;
    if id.len() > 100 || id.len() < 8 || !id.bytes().all(|b| b.is_ascii_alphanumeric() || b == b'_' || b == b'-') {
        return Err("request_id must be 8-100 ASCII letters, digits, _ or -".into());
    }
    Ok(())
}

fn validate(method: &str, args: &Value) -> Result<(), String> {
    match method {
        "status" | "request_access" => Ok(()),
        "list" => {
            bounded_text(args, "calendar_id", 512)?;
            valid_range(args)?;
            let limit = args.get("limit").and_then(Value::as_u64).unwrap_or(50);
            if limit == 0 || limit > 100 {
                return Err("limit must be 1-100".into());
            }
            Ok(())
        }
        "get" => {
            bounded_text(args, "calendar_id", 512)?;
            bounded_text(args, "event_id", 512)
        }
        "create" => {
            valid_request(args)?;
            bounded_text(args, "calendar_id", 512)?;
            bounded_text(args, "title", 200)?;
            bounded_text(args, "time_zone", 100)?;
            valid_range(args)?;
            if args.get("location").is_some() && !args["location"].is_null() {
                if args["location"].as_str().is_none_or(|s| s.len() > 500) {
                    return Err("location must be text of at most 500 bytes".into());
                }
            }
            Ok(())
        }
        "update" => {
            valid_request(args)?;
            bounded_text(args, "calendar_id", 512)?;
            bounded_text(args, "event_id", 512)?;
            bounded_text(args, "expected_version", 64)?;
            let changes = args.get("changes").and_then(Value::as_object).ok_or("changes must be an object")?;
            if changes.is_empty() || changes.keys().any(|key| !["title", "start", "end", "time_zone", "location"].contains(&key.as_str())) {
                return Err("changes must contain only title, start, end, time_zone or location".into());
            }
            for (key, value) in changes {
                if value.as_str().is_none_or(|s| s.len() > 500 || s.contains(['\r', '\n'])) {
                    return Err(format!("invalid {key} change"));
                }
            }
            Ok(())
        }
        "delete" => {
            valid_request(args)?;
            bounded_text(args, "calendar_id", 512)?;
            bounded_text(args, "event_id", 512)?;
            bounded_text(args, "expected_version", 64)
        }
        _ => Err(format!("calendar has no method {method:?}")),
    }
}

fn digest(data: &[u8]) -> String {
    format!("{:x}", Sha256::digest(data))
}

fn version(event: &Value) -> String {
    digest(event.to_string().as_bytes())
}

fn decorate(mut event: Value) -> Value {
    let v = version(&event);
    event["version"] = json!(v);
    event
}

fn native_request(method: &str, args: &Value) -> Result<Value, String> {
    native::call(&json!({"method": method, "args": args}))
}

fn journal_path(host_dir: &Path, app_id: &str) -> PathBuf {
    host_dir.join("calendar").join(format!("{}.json", digest(app_id.as_bytes())))
}

fn read_journal(path: &Path) -> Result<BTreeMap<String, Value>, String> {
    match std::fs::read(path) {
        Ok(bytes) => serde_json::from_slice(&bytes).map_err(|e| format!("calendar journal is damaged: {e}")),
        Err(e) if e.kind() == std::io::ErrorKind::NotFound => Ok(BTreeMap::new()),
        Err(e) => Err(format!("cannot read calendar journal: {e}")),
    }
}

fn write_journal(path: &Path, journal: &BTreeMap<String, Value>) -> Result<(), String> {
    let parent = path.parent().ok_or("invalid calendar journal path")?;
    std::fs::create_dir_all(parent).map_err(|e| e.to_string())?;
    let temp = path.with_extension(format!("{}.tmp", std::process::id()));
    let bytes = serde_json::to_vec(journal).map_err(|e| e.to_string())?;
    let mut file = std::fs::File::create(&temp).map_err(|e| e.to_string())?;
    use std::io::Write;
    file.write_all(&bytes).and_then(|_| file.sync_all()).map_err(|e| e.to_string())?;
    std::fs::rename(&temp, path).map_err(|e| e.to_string())?;
    std::fs::File::open(parent).and_then(|file| file.sync_all()).map_err(|e| e.to_string())?;
    Ok(())
}

fn handle(call: ServiceCall) -> Result<Value, String> {
    let method = call.method().to_string();
    validate(&method, &call.args)?;
    match method.as_str() {
        "status" | "request_access" => native_request(&method, &call.args),
        "list" => {
            let mut result = native_request(&method, &call.args)?;
            if let Some(events) = result["events"].as_array_mut() {
                for event in events {
                    *event = decorate(event.take());
                }
            }
            Ok(result)
        }
        "get" => {
            let mut result = native_request("get", &call.args)?;
            if result["found"] == true {
                let event = result["event"].take();
                result["event"] = decorate(event);
            }
            Ok(result)
        }
        "create" | "update" | "delete" => mutate(&call, &method),
        _ => Err("unknown calendar method".into()),
    }
}

fn mutate(call: &ServiceCall, method: &str) -> Result<Value, String> {
    let _lock = ACTION_LOCK.lock().map_err(|_| "calendar action lock poisoned")?;
    let path = journal_path(&call.host_dir, &call.app_id);
    let mut journal = read_journal(&path)?;
    let request_id = text(&call.args, "request_id")?;
    let fingerprint = digest(json!({"method": method, "args": call.args}).to_string().as_bytes());
    if let Some(previous) = journal.get(request_id) {
        if previous["fingerprint"] != fingerprint {
            return Err("request_id was already used with different calendar content".into());
        }
        return if previous["state"] == "done" {
            Ok(previous["result"].clone())
        } else {
            Err("Calendar action outcome is uncertain; check the system calendar before a new request".into())
        };
    }

    let mut args = call.args.clone();
    args["owner"] = json!(digest(call.app_id.as_bytes()));
    if method != "create" {
        let read = native_request("get", &args)?;
        if read["found"] != true {
            return Err("Calendar event no longer exists; review before acting".into());
        }
        let current = &read["event"];
        if version(&current) != text(&args, "expected_version")? {
            return Err("Calendar event changed; review it again before acting".into());
        }
        args["expected_last_modified"] = current["last_modified"].clone();
    }

    journal.insert(request_id.into(), json!({"fingerprint": fingerprint, "state": "pending"}));
    write_journal(&path, &journal)?;
    let raw = native_request(method, &args);
    let result = match raw {
        Ok(event) if method == "delete" => event,
        Ok(event) => {
            let event = decorate(event);
            json!({"event_id": event["id"], "version": event["version"]})
        }
        Err(e) => return Err(format!("Calendar action may have changed the system calendar; reconcile before retry: {e}")),
    };
    journal.insert(request_id.into(), json!({"fingerprint": fingerprint, "state": "done", "result": result}));
    write_journal(&path, &journal).map_err(|e| format!("Calendar changed, but saving its result failed; reconcile before retry: {e}"))?;
    Ok(result)
}

#[cfg(target_os = "macos")]
mod native {
    use serde_json::Value;
    use std::ffi::{c_char, CStr, CString};

    unsafe extern "C" {
        fn muse_calendar_call(request: *const c_char) -> *mut c_char;
        fn muse_calendar_free(result: *mut c_char);
    }

    pub fn call(request: &Value) -> Result<Value, String> {
        let json = CString::new(request.to_string()).map_err(|e| e.to_string())?;
        let pointer = unsafe { muse_calendar_call(json.as_ptr()) };
        if pointer.is_null() {
            return Err("EventKit bridge returned no response".into());
        }
        let answer = unsafe { CStr::from_ptr(pointer).to_string_lossy().into_owned() };
        unsafe { muse_calendar_free(pointer) };
        let value: Value = serde_json::from_str(&answer).map_err(|e| format!("invalid EventKit response: {e}"))?;
        if let Some(error) = value["error"].as_str() {
            Err(error.into())
        } else {
            value.get("result").cloned().ok_or_else(|| "EventKit response has no result".into())
        }
    }
}

#[cfg(not(target_os = "macos"))]
mod native {
    use serde_json::Value;
    pub fn call(_request: &Value) -> Result<Value, String> {
        Err("Calendar EventKit service is available only on macOS in this build".into())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn invalid_ranges_and_duplicate_ids_are_refused_before_eventkit() {
        assert!(validate("list", &json!({"calendar_id":"c","start":"2026-10-01T10:00:00+08:00","end":"2026-10-01T09:00:00+08:00"})).is_err());
        assert!(validate("create", &json!({"calendar_id":"c","title":"T","start":"2026-10-01T10:00:00+08:00","end":"2026-10-01T11:00:00+08:00","time_zone":"Asia/Shanghai","request_id":"bad/../id"})).is_err());
    }

    #[test]
    fn damaged_journal_fails_closed() {
        let path = std::env::temp_dir().join(format!("muse-calendar-journal-{}", std::process::id()));
        std::fs::write(&path, b"not-json").unwrap();
        assert!(read_journal(&path).unwrap_err().contains("damaged"));
        std::fs::remove_file(path).unwrap();
    }

    #[test]
    fn completed_request_is_replayed_only_for_identical_content() {
        let host_dir = std::env::temp_dir().join(format!("muse-calendar-actions-{}", std::process::id()));
        let args = json!({"calendar_id":"c","title":"Test","start":"2026-10-01T10:00:00+08:00",
            "end":"2026-10-01T11:00:00+08:00","time_zone":"Asia/Shanghai","request_id":"phase2-test-1"});
        let call = ServiceCall { app_id: "muse.test".into(), service: "calendar.create".into(),
            args: args.clone(), from_sheet: false, host_dir: host_dir.clone() };
        let path = journal_path(&host_dir, &call.app_id);
        let fingerprint = digest(json!({"method":"create","args":args}).to_string().as_bytes());
        let mut journal = BTreeMap::new();
        journal.insert("phase2-test-1".into(), json!({"fingerprint":fingerprint,"state":"done",
            "result":{"event_id":"event-1","version":"v1"}}));
        write_journal(&path, &journal).unwrap();
        assert_eq!(mutate(&call, "create").unwrap()["event_id"], "event-1");
        let mut changed = call.clone();
        changed.args["title"] = json!("Different");
        assert!(mutate(&changed, "create").unwrap_err().contains("different calendar content"));
        assert_ne!(journal_path(&host_dir, "other.app"), path);
        journal.get_mut("phase2-test-1").unwrap()["state"] = json!("pending");
        write_journal(&path, &journal).unwrap();
        assert!(mutate(&call, "create").unwrap_err().contains("uncertain"));
        std::fs::remove_dir_all(host_dir).unwrap();
    }
}
