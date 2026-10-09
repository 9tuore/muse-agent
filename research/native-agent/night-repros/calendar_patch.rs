use calendar_core_repro::{handle,parse_time,APP,relay_catalog::Catalog};
use serde_json::{Value,json};
fn tools() -> Vec<Value> {
    serde_json::from_str::<Value>(include_str!("../../../.local-state/night-calendar-patched/tools.json")).unwrap()["tools"].as_array().unwrap().clone()
}
#[test]
fn shared_patch_keeps_grants_owner_boundary_and_destructive_confirmation() {
    let mut catalog=Catalog::default();let descriptors=tools();
    let delete=descriptors.iter().find(|t|t["name"]=="calendar.remove_event").unwrap();
    assert_eq!(delete["risk"],"destructive");assert_eq!(delete["confirm"],"host");
    catalog.tools.insert(APP.into(),descriptors);
    for name in ["calendar.get_event","calendar.update_event","calendar.remove_event"] {
        assert!(!catalog.may_call("muse-goals",APP,name,false));
        catalog.grant("muse-goals",APP,name);
        assert!(catalog.may_call("muse-goals",APP,name,false));
    }
    let now=parse_time("2026-10-09T09:00").unwrap();
    assert!(handle("muse-goals","get_event",&json!({"id":"any"}),&std::env::temp_dir(),now,None).is_err());
}
