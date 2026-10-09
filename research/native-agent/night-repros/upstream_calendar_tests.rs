#[cfg(test)]
mod reconciliation_tests {
    use super::*;

    #[test]
    fn exact_readback_update_stale_refusal_delete_and_absence() {
        let dir = std::env::temp_dir().join(format!(
            "muse-calendar-patch-chain-{}",
            std::process::id()
        ));
        let _ = std::fs::remove_dir_all(&dir);
        let now = parse_time("2026-10-09T09:00").unwrap();
        let absent = handle(APP, "get_event", &json!({"id": "absent"}), &dir, now, None).unwrap();
        assert_eq!(absent["found"], false);

        let args = json!({
            "title": "Synthetic delivery",
            "start": "2026-10-10T09:00",
            "timezone": "Asia/Shanghai",
            "request_id": "synthetic-patch-one"
        });
        let added = handle(APP, "add_event", &args, &dir, now, None).unwrap();
        let id = added["id"].clone();
        let first = handle(APP, "get_event", &json!({"id": id}), &dir, now, None).unwrap();
        assert_eq!(first["found"], true);
        assert_eq!(first["event"]["request_id"], args["request_id"]);

        let update = json!({
            "id": id,
            "expected": first["event"],
            "title": "Synthetic moved",
            "start": "2026-10-10T10:00",
            "timezone": "Asia/Shanghai"
        });
        let saved = handle(APP, "update_event", &update, &dir, now, None).unwrap();
        assert_eq!(saved["event"]["id"], id);
        let stale = handle(APP, "update_event", &update, &dir, now, None).unwrap_err();
        assert!(stale.contains("changed elsewhere"));

        let read = handle(APP, "get_event", &json!({"id": id}), &dir, now, None).unwrap();
        assert_eq!(read["event"], saved["event"]);
        handle(
            APP,
            "remove_event",
            &json!({"id": id, "expected": read["event"]}),
            &dir,
            now,
            None,
        )
        .unwrap();
        let removed = handle(APP, "get_event", &json!({"id": id}), &dir, now, None).unwrap();
        assert_eq!(removed["found"], false);
        std::fs::remove_dir_all(dir).unwrap();
    }

    #[test]
    fn exact_query_beyond_list_cap_and_corrupt_store_never_absent() {
        let dir = std::env::temp_dir().join(format!(
            "muse-calendar-patch-bounds-{}",
            std::process::id()
        ));
        let _ = std::fs::remove_dir_all(&dir);
        std::fs::create_dir_all(dir.join("calendar")).unwrap();
        let events: Vec<Event> = (0..201)
            .map(|i| Event {
                id: format!("ev-{i:03}"),
                title: "Synthetic".into(),
                start: "2026-10-10T09:00".into(),
                end: None,
                location: String::new(),
                notes: String::new(),
                request_id: String::new(),
                timezone: String::new(),
            })
            .collect();
        let path = dir.join("calendar/events.json");
        std::fs::write(&path, serde_json::to_vec(&events).unwrap()).unwrap();
        let now = parse_time("2026-10-09T09:00").unwrap();

        let list = handle(APP, "events", &json!({"limit": 200}), &dir, now, None).unwrap();
        let rows = list["events"].as_array().unwrap();
        assert_eq!(rows.len(), 200);
        assert!(!rows.iter().any(|event| event["id"] == "ev-200"));
        let exact = handle(APP, "get_event", &json!({"id": "ev-200"}), &dir, now, None).unwrap();
        assert_eq!(exact["found"], true);

        std::fs::write(path, b"not json").unwrap();
        assert!(handle(APP, "get_event", &json!({"id": "absent"}), &dir, now, None).is_err());
        assert!(handle(APP, "get_event", &json!({"id": ""}), &dir, now, None).is_err());
        std::fs::remove_dir_all(dir).unwrap();
    }
}
