
#[test]
fn shared_offer_revocation_reaches_clone_staging_independent_and_fresh_store() {
    let mut h = Harness::new(&[("muse-goals", &["calendar.events"])]);
    let config = octosense_app_hub::AgentToolOffers::default();
    h.store = h.store.with_agent_tool_offers(config.clone());
    let clone = h.store.clone();
    let staging = h.store.for_install_root(&h.apps[0].root.join("staging"));
    let mut independent = Store::new(&h.anchor_public_hex, &h.apps[0].root.join("installed"), HostLimits::default())
        .with_agent_tool_offers(config.clone());
    independent.accept_catalog(&serde_json::to_string(&h.catalog).unwrap()).unwrap();
    h.store.set_agent_tool_offers("muse-goals", &["calendar.events"]).unwrap();
    h.install(0).unwrap();
    clone.may_run("muse-goals").unwrap();
    independent.may_run("muse-goals").unwrap();
    let prepared = clone.prepare_launch("muse-goals").unwrap();
    independent.set_agent_tool_offers("muse-goals", &[]).unwrap();
    for store in [&h.store, &clone, &independent] {
        let error = store.may_run("muse-goals").unwrap_err();
        assert!(error.contains("does not offer"), "{error}");
        assert!(store.validate_prepared_launch(&prepared).unwrap_err().contains("does not offer"));
    }
    let app = &h.apps[0];
    let keys = PublisherKeys::new().with("publisher-fixture-muse-goals", &app.publisher.public_hex());
    assert!(staging.install_staged("muse-goals", &app.bundle, &keys, "2026-09-25")
        .unwrap_err().contains("does not offer"));
    let mut fresh = Store::new(&h.anchor_public_hex, &h.apps[0].root.join("installed"), HostLimits::default())
        .with_agent_tool_offers(config);
    fresh.accept_catalog(&serde_json::to_string(&h.catalog).unwrap()).unwrap();
    assert!(fresh.may_run("muse-goals").unwrap_err().contains("does not offer"));
}

#[test]
fn exact_shared_set_replacement_does_not_leak_or_accumulate_tools() {
    let mut h = Harness::new(&[("muse-goals", &["calendar.events", "calendar.notify"]),
        ("another-app", &["calendar.events"])]);
    h.store = h.store.with_agent_tool_offers(octosense_app_hub::AgentToolOffers::default());
    h.store.set_agent_tool_offers("muse-goals", &["calendar.events", "calendar.notify"]).unwrap();
    h.install(0).unwrap();
    assert!(h.install(1).unwrap_err().contains("does not offer"));
    h.store.set_agent_tool_offers("muse-goals", &["calendar.events"]).unwrap();
    let error = h.store.may_run("muse-goals").unwrap_err();
    assert!(error.contains("calendar.notify") && error.contains("does not offer"), "{error}");
}
