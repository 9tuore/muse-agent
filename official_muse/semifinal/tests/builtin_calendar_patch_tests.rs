use super::*;

fn fixture(tag: &str) -> std::path::PathBuf {
    let root = std::env::temp_dir().join(format!("muse-calendar-review-{tag}-{}", std::process::id()));
    let _ = std::fs::remove_dir_all(&root);
    root
}

#[test]
fn exact_readback_reconciles_create_update_and_delete() {
    let root = fixture("lifecycle");
    let now = parse_time("2026-10-10T18:00").unwrap();
    let created = handle(APP, "add_event", &json!({"title":"Synthetic review", "start":"2026-10-11T15:00", "request_id":"synthetic-review"}), &root, now, None).unwrap();
    let by_request = handle(APP, "get_event", &json!({"request_id":"synthetic-review"}), &root, now, None).unwrap();
    assert_eq!(by_request["event"]["id"], created["id"]);
    let snapshot = by_request["event"].clone();
    let edit = json!({"id":created["id"],"expected":snapshot,"title":"Synthetic review", "start":"2026-10-11T16:00"});
    handle(APP, "update_event", &edit, &root, now, None).unwrap();
    assert!(handle(APP, "update_event", &edit, &root, now, None).is_err());
    let current = handle(APP, "get_event", &json!({"id":created["id"]}), &root, now, None).unwrap();
    assert_eq!(current["event"]["start"], "2026-10-11T16:00");
    assert_eq!(current["event"]["request_id"], "synthetic-review");
    handle(APP, "remove_event", &json!({"id":created["id"],"expected":current["event"]}), &root, now, None).unwrap();
    let absent = handle(APP, "get_event", &json!({"id":created["id"]}), &root, now, None).unwrap();
    assert_eq!(absent, json!({"found":false,"event":null}));
    assert!(handle("muse-goals", "get_event", &json!({"id":created["id"]}), &root, now, None).is_err());
    std::fs::remove_dir_all(root).unwrap();
}

#[test]
fn unreadable_store_never_becomes_empty_or_overwritten() {
    let root = fixture("corrupt");
    std::fs::create_dir_all(root.join("calendar")).unwrap();
    let original = b"{unfinished calendar records";
    std::fs::write(store_path(&root), original).unwrap();
    let now = parse_time("2026-10-10T18:00").unwrap();
    for (method,args) in [
        ("events",json!({})), ("view",json!({})), ("get_event",json!({"id":"synthetic"})),
        ("add_event",json!({"title":"Synthetic", "start":"2026-10-11T15:00"})),
        ("update_event",json!({"id":"synthetic"})), ("remove_event",json!({"id":"synthetic"}))
    ] {
        assert!(handle(APP,method,&args,&root,now,None).is_err(), "{method}");
        assert_eq!(std::fs::read(store_path(&root)).unwrap(),original);
    }
    std::fs::remove_dir_all(root).unwrap();
}

#[test]
fn exact_lookup_is_independent_of_list_cap_and_rejects_ambiguity() {
    let root = fixture("cap");
    let now = parse_time("2026-10-10T18:00").unwrap();
    let events: Vec<Event> = (0..201).map(|n| Event { id:format!("synthetic-{n:04}"),title:"Synthetic".into(),
        start:"2026-10-11T15:00".into(),end:None,location:String::new(),notes:String::new(),request_id:format!("request-{n:04}"),timezone:String::new() }).collect();
    save(&root,&events).unwrap();
    assert_eq!(handle(APP,"events",&json!({"limit":200}),&root,now,None).unwrap()["events"].as_array().unwrap().len(),200);
    assert_eq!(handle(APP,"get_event",&json!({"id":"synthetic-0200"}),&root,now,None).unwrap()["event"]["id"],"synthetic-0200");
    let mut duplicate = events.clone(); duplicate.push(events[0].clone()); save(&root,&duplicate).unwrap();
    assert!(handle(APP,"get_event",&json!({"request_id":"request-0000"}),&root,now,None).unwrap_err().contains("ambiguous"));
    assert!(handle(APP,"get_event",&json!({}),&root,now,None).is_err());
    std::fs::remove_dir_all(root).unwrap();
}
