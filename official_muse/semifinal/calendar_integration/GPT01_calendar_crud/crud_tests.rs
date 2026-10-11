//! Synthetic owner-service checks. This does not exercise a GUI approval sheet.
use super::*;

struct Fixture(std::path::PathBuf);
impl Fixture {
    fn new() -> Self {
        let dir = std::env::temp_dir().join(format!("gpt01-calendar-crud-{}-{}",
            std::process::id(), std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_nanos()));
        std::fs::create_dir(&dir).unwrap();
        Self(dir)
    }
    fn call(&self, method: &str, args: Value) -> Result<Value, String> {
        handle(APP, method, &args, &self.0, parse_time("2026-10-11T09:00").unwrap(), None)
    }
    fn create(&self) -> Value {
        let result = self.call("add_event", json!({"title":"Synthetic CRUD", "start":"2026-10-12T15:00",
            "timezone":"Asia/Shanghai", "request_id":"fixture-crud-1", "notes":"Synthetic only"})).unwrap();
        self.call("get_event", json!({"id":result["id"]})).unwrap()["event"].clone()
    }
}
impl Drop for Fixture {
    fn drop(&mut self) { std::fs::remove_dir_all(&self.0).unwrap(); }
}

#[test]
fn gpt01_crud_create_retry_update_delete_and_exact_absence() {
    let f = Fixture::new();
    let old = f.create();
    let retry = f.call("add_event", json!({"title":"Synthetic CRUD", "start":"2026-10-12T15:00",
        "timezone":"Asia/Shanghai", "request_id":"fixture-crud-1", "notes":"Synthetic only"})).unwrap();
    assert_eq!(retry["id"], old["id"]);
    assert_eq!(retry["reused"], true);
    let edited = f.call("update_event", json!({"id":old["id"],"expected":old,
        "title":"Synthetic revised", "start":"2026-10-12T16:00", "timezone":"Asia/Shanghai",
        "notes":"Synthetic revised notes"})).unwrap()["event"].clone();
    assert_eq!(edited["id"], old["id"]);
    assert_eq!(edited["request_id"], old["request_id"]);
    assert_eq!(f.call("get_event", json!({"id":old["id"]})).unwrap()["event"], edited);
    assert_eq!(f.call("view", json!({"day":"2026-10-12"})).unwrap()["events"][0]["id"], edited["id"]);
    assert_eq!(f.call("remove_event", json!({"id":edited["id"],"expected":edited})).unwrap()["removed"], true);
    assert_eq!(f.call("get_event", json!({"id":edited["id"]})).unwrap(), json!({"found":false,"event":null}));
    assert_eq!(f.call("view", json!({"day":"2026-10-12"})).unwrap()["events"], json!([]));
    assert!(f.call("remove_event", json!({"id":edited["id"],"expected":edited})).is_err(),
        "A repeated stale mutation is not another successful deletion; reconcile with get_event");
}

#[test]
fn gpt01_crud_stale_or_wrong_event_snapshot_never_deletes() {
    let f = Fixture::new();
    let old = f.create();
    let current = f.call("update_event", json!({"id":old["id"],"expected":old,
        "title":"Synthetic changed", "start":"2026-10-12T15:00", "timezone":"Asia/Shanghai"})).unwrap()["event"].clone();
    let bytes = std::fs::read(store_path(&f.0)).unwrap();
    for expected in [old, json!({"id":"wrong","title":"Synthetic changed","start":"2026-10-12T15:00"})] {
        assert!(f.call("remove_event", json!({"id":current["id"],"expected":expected})).is_err());
        assert_eq!(std::fs::read(store_path(&f.0)).unwrap(), bytes);
    }
    assert_eq!(f.call("get_event", json!({"id":current["id"]})).unwrap()["event"], current);
}

#[test]
fn gpt01_crud_mutation_rejects_foreign_owner_and_invalid_replacement() {
    let f = Fixture::new();
    let event = f.create();
    let bytes = std::fs::read(store_path(&f.0)).unwrap();
    let args = json!({"id":event["id"],"expected":event});
    assert!(handle("muse-goals", "remove_event", &args, &f.0, parse_time("2026-10-11").unwrap(), None).is_err());
    assert!(f.call("update_event", json!({"id":event["id"],"title":"No snapshot","start":"2026-10-12T15:00"})).is_err());
    assert!(f.call("update_event", json!({"id":event["id"],"expected":event,
        "title":"Bad range","start":"2026-10-12T17:00","end":"2026-10-12T16:00","timezone":"Asia/Shanghai"})).is_err());
    assert_eq!(std::fs::read(store_path(&f.0)).unwrap(), bytes);
}

#[test]
fn gpt01_crud_broken_projection_is_warning_after_authoritative_delete() {
    let f = Fixture::new();
    let event = f.create();
    std::fs::write(f.0.join("calendar/cards.json"), b"{broken synthetic projection").unwrap();
    let result = f.call("remove_event", json!({"id":event["id"],"expected":event})).unwrap();
    assert_eq!(result["removed"], true);
    assert!(result["card_warning"].as_str().unwrap().contains("Cannot read Calendar cards"));
    assert_eq!(f.call("get_event", json!({"id":event["id"]})).unwrap(), json!({"found":false,"event":null}));
}
