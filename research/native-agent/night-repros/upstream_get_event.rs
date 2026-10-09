/// Exact saved-record lookup; never turn unreadable/corrupt storage into absence.
fn get_event(host_dir: &Path, args: &Value) -> Result<Value, String> {
    let id = bounded(text(args, "id"), 64, "An event id")?;
    if id.is_empty() {
        return Err("Give the saved event id.".into());
    }
    let events: Vec<Event> = match std::fs::read(store_path(host_dir)) {
        Ok(bytes) => serde_json::from_slice(&bytes)
            .map_err(|e| format!("Calendar cannot read its saved events: {e}"))?,
        Err(e) if e.kind() == std::io::ErrorKind::NotFound => Vec::new(),
        Err(e) => return Err(format!("Calendar cannot read its saved events: {e}")),
    };
    Ok(match events.into_iter().find(|event| event.id == id) {
        Some(event) => json!({"found": true, "event": event}),
        None => json!({"found": false, "event": {}}),
    })
}
