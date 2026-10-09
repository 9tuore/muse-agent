use calendar_core_repro::{handle,parse_time,APP,relay_catalog::Catalog};
use serde_json::{Value,json};

fn descriptors() -> Vec<Value> {
    serde_json::from_str::<Value>(include_str!("../../../.local-state/native-agent-upstream/OctoSense/apps/calendar/bundle/tools.json"))
        .unwrap()["tools"].as_array().unwrap().clone()
}
#[test]
fn explicit_grants_cannot_share_owner_only_update_or_delete() {
    let mut catalog = Catalog::default();
    catalog.tools.insert(APP.into(), descriptors());
    for name in ["calendar.events","calendar.add_event","calendar.notify","calendar.update_event","calendar.remove_event"] {
        catalog.grant("muse-goals", APP, name);
    }
    assert!(catalog.may_call("muse-goals",APP,"calendar.events",false));
    for name in ["calendar.update_event","calendar.remove_event"] {
        assert!(!catalog.may_call("muse-goals",APP,name,false));
        assert!(!catalog.may_call("muse-goals",APP,name,true), "developer mode still cannot invent shareable");
        assert!(catalog.may_call(APP,APP,name,false), "owner positive control");
        eprintln!("EXPLICIT_GRANT_STILL_BLOCKED={name}");
    }
    assert!(!catalog.may_call("ungranted-app",APP,"calendar.events",false));
    assert!(!catalog.may_call("muse-goals",APP,"calendar.get",false));
}
#[test]
fn owner_service_and_precise_missing_query_boundaries() {
    let dir=std::env::temp_dir().join(format!("muse-calendar-boundary-{}",std::process::id()));
    let _=std::fs::remove_dir_all(&dir);
    let at=parse_time("2026-10-09T10:00").unwrap();
    assert!(handle("muse-goals","events",&json!({}),&dir,at,None).unwrap_err().contains("own service"));
    let missing=handle(APP,"get",&json!({"id":"absent"}),&dir,at,None);
    assert!(missing.is_err(), "there is no get handler, not a successful not-found answer");
    // Actual service list defaults/caps: a filtered empty list is not an exact-id lookup.
    let added=handle(APP,"add_event",&json!({"title":"Synthetic","start":"2026-10-10T09:00","request_id":"synthetic-one"}),&dir,at,None).unwrap();
    let filtered=handle(APP,"events",&json!({"from":"2026-10-11T00:00"}),&dir,at,None).unwrap();
    assert!(filtered["events"].as_array().unwrap().is_empty());
    let all=handle(APP,"events",&json!({}),&dir,at,None).unwrap();
    assert_eq!(all["events"][0]["id"],added["id"]);
    assert!(handle(APP,"update_event",&json!({"id":added["id"],"expected":{},"title":"Moved","start":"2026-10-10T10:00"}),&dir,at,None).is_err());
    eprintln!("DIRECT_MUSE_SERVICE=REFUSED; GET_METHOD=UNAVAILABLE; FILTERED_ABSENCE_NOT_DELETION=CONFIRMED");
    std::fs::remove_dir_all(dir).unwrap();
}
