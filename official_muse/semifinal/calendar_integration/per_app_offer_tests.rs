//! Signed fixture exercising the real Store. No shell/consent/Relay claim.
mod common;
use common::Fixture;
use octosense_app_hub::{sign_manifest, Catalog, Entry, HubKey, PublisherKeys, Status, Store};
use octosense_app_policy::{AppManifest, HostLimits};
use serde_json::json;

struct Harness {
    apps: Vec<Fixture>,
    store: Store,
    catalog: Catalog,
    signer: HubKey,
    certificate: String,
}

impl Harness {
    fn new(requests: &[(&str, &[&str])]) -> Self {
        let anchor = HubKey::generate();
        let signer = HubKey::generate();
        let certificate = anchor.certify(&signer.public_hex()).unwrap();
        let mut apps = Vec::new();
        let mut entries: Vec<Entry> = Vec::new();
        for (id, tools) in requests {
            let mut app = Fixture::new();
            app.manifest.id = (*id).into();
            app.sign();
            let mut entry = app.entry();
            let mut raw = serde_json::to_value(&app.manifest).unwrap();
            raw["agent"] = json!({"profile":"workspace-write-never-ask", "tools": tools,
                "background":false});
            app.manifest = AppManifest::parse(&raw.to_string()).unwrap();
            app.sign();
            // Fixture::sign/keys use publisher-one. Each independently
            // generated publisher needs its own catalog key identity.
            let key_id = format!("publisher-fixture-{id}");
            sign_manifest(&app.publisher, &mut app.manifest, &key_id).unwrap();
            app.write_manifest();
            entry.publisher = key_id;
            entry.manifest = app.manifest.clone();
            entries.push(entry); apps.push(app);
        }
        let store = Store::new(&anchor.public_hex(), &apps[0].root.join("installed"), HostLimits::default());
        let catalog = Catalog::new(1, "2026-09-25", entries);
        let mut h = Self { apps, store, catalog, signer, certificate };
        h.accept(); h
    }
    fn accept(&mut self) {
        self.catalog.sequence += 1;
        self.signer.sign_catalog(&mut self.catalog, &self.certificate).unwrap();
        self.store.accept_catalog(&serde_json::to_string(&self.catalog).unwrap()).unwrap();
    }
    fn install(&self, n: usize) -> Result<octosense_app_policy::AppPolicy, String> {
        let app = &self.apps[n];
        let key_id = format!("publisher-fixture-{}", app.manifest.id);
        let keys = PublisherKeys::new().with(&key_id, &app.publisher.public_hex());
        self.store.install_staged(&app.manifest.id, &app.bundle, &keys, "2026-09-25")
    }
}

#[test]
fn default_is_closed_and_one_app_offer_does_not_extend_another() {
    let mut h = Harness::new(&[("muse-goals", &["calendar.events"]), ("another-app", &["calendar.events"])]);
    assert_ne!(h.catalog.entries[0].publisher, h.catalog.entries[1].publisher);
    assert_ne!(h.catalog.entries[0].publisher_key, h.catalog.entries[1].publisher_key);
    let error = h.install(0).unwrap_err();
    eprintln!("default offer refusal: {error}");
    assert!(error.contains("does not offer"), "{error}");
    h.store.set_agent_tool_offer("muse-goals", Some("calendar.events")).unwrap();
    h.install(0).unwrap();
    h.store.may_run("muse-goals").unwrap();
    let error = h.install(1).unwrap_err();
    eprintln!("other app refusal: {error}");
    assert!(error.contains("does not offer"), "{error}");
}

#[test]
fn exact_offer_cannot_admit_a_second_requested_tool() {
    let mut h = Harness::new(&[("muse-goals", &["calendar.events", "calendar.remove_event"])]);
    h.store.set_agent_tool_offer("muse-goals", Some("calendar.events")).unwrap();
    let error = h.install(0).unwrap_err();
    assert!(error.contains("calendar.remove_event") && error.contains("does not offer"), "{error}");
}

#[test]
fn host_offer_does_not_grant_a_tool_absent_from_the_manifest() {
    let mut h = Harness::new(&[("muse-goals", &[])]);
    h.store.set_agent_tool_offer("muse-goals", Some("calendar.events")).unwrap();
    let policy = h.install(0).unwrap();
    assert!(policy.agent.unwrap().tools.is_empty());
}

#[test]
fn revoke_rechecks_installed_and_already_prepared_launches() {
    let mut h = Harness::new(&[("muse-goals", &["calendar.events"])]);
    h.store.set_agent_tool_offer("muse-goals", Some("calendar.events")).unwrap();
    h.install(0).unwrap();
    let prepared = h.store.prepare_launch("muse-goals").unwrap();
    h.store.set_agent_tool_offer("muse-goals", None).unwrap();
    assert!(h.store.may_run("muse-goals").unwrap_err().contains("does not offer"));
    assert!(h.store.validate_prepared_launch(&prepared).unwrap_err().contains("does not offer"));
    h.store.set_agent_tool_offer("muse-goals", Some("calendar.events")).unwrap();
    assert!(h.store.validate_prepared_launch(&prepared).is_ok());
}

#[test]
fn enabled_offer_does_not_bypass_bundle_digest() {
    let mut h = Harness::new(&[("muse-goals", &["calendar.events"])]);
    h.store.set_agent_tool_offer("muse-goals", Some("calendar.events")).unwrap();
    std::fs::write(h.apps[0].bundle.join("main.splash"), "changed").unwrap();
    assert!(h.install(0).unwrap_err().contains("hashes"));
}

#[test]
fn offer_refuses_unverified_publisher_and_unsigned_manifests() {
    let mut h = Harness::new(&[("muse-goals", &["calendar.events"])]);
    h.store.set_agent_tool_offer("muse-goals", Some("calendar.events")).unwrap();
    h.catalog.entries[0].publisher_key = HubKey::generate().public_hex(); h.accept();
    assert!(h.store.set_agent_tool_offer("muse-goals", Some("calendar.events")).is_err());
    assert!(h.install(0).is_err(), "retained offer must not bypass the catalog signing key");
    let mut h = Harness::new(&[("muse-goals", &["calendar.events"])]);
    h.store.set_agent_tool_offer("muse-goals", Some("calendar.events")).unwrap();
    h.apps[0].manifest.integrity.signature = None; h.apps[0].write_manifest();
    h.catalog.entries[0].manifest = h.apps[0].manifest.clone(); h.accept();
    assert!(h.store.set_agent_tool_offer("muse-goals", Some("calendar.events")).is_err());
    assert!(h.install(0).is_err(), "retained offer must not bypass required authentication");
}

#[test]
fn signed_catalog_withdrawal_still_blocks_installed_and_prepared_release() {
    let mut h = Harness::new(&[("muse-goals", &["calendar.events"])]);
    h.store.set_agent_tool_offer("muse-goals", Some("calendar.events")).unwrap(); h.install(0).unwrap();
    let prepared = h.store.prepare_launch("muse-goals").unwrap();
    h.catalog.entries[0].status = Status::Withdrawn("fixture withdrawal".into()); h.accept();
    assert!(h.store.may_run("muse-goals").unwrap_err().contains("withdraw"));
    assert!(h.store.validate_prepared_launch(&prepared).unwrap_err().contains("withdraw"));
}

#[test]
fn unknown_and_reserved_ids_never_receive_an_offer() {
    let mut h = Harness::new(&[("muse-goals", &["calendar.events"])]);
    assert!(h.store.set_agent_tool_offer("unknown-app", Some("calendar.events")).is_err());
    assert!(h.store.set_agent_tool_offer("os.calendar", Some("calendar.events")).is_err());
    assert!(h.install(0).is_err());
}
