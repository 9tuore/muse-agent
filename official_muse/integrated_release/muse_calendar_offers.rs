//! Signed synthetic catalog. Tests host configuration, not consent or Relay.
use octosense_app_hub::{sign_manifest, Catalog, Entry, HubKey, Source, Status, Store};
use octosense_app_policy::{digest_dir, AppManifest};
use octosense_appstore::{configure_muse_calendar_offers, host_store, set_muse_calendar_integration_enabled};
use serde_json::json;
use std::path::PathBuf;

const SIX: &[&str] = &["calendar.events", "calendar.get_event", "calendar.add_event",
    "calendar.update_event", "calendar.remove_event", "calendar.notify"];

struct Fixture {
    root: PathBuf,
    store: Store,
    catalog: Catalog,
    signer: HubKey,
    certificate: String,
    anchor: String,
}

impl Fixture {
    fn new(tools: &[&str]) -> Self {
        let root = std::env::temp_dir().join(format!("muse-host-offers-{}-{}",
            std::process::id(), std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_nanos()));
        std::fs::create_dir(&root).unwrap();
        let anchor = HubKey::generate();
        let signer = HubKey::generate();
        let certificate = anchor.certify(&signer.public_hex()).unwrap();
        let mut entries = Vec::new();
        for id in ["muse-goals", "another-app"] {
            let bundle = root.join(id);
            std::fs::create_dir(&bundle).unwrap();
            std::fs::write(bundle.join("main.splash"), "Label{text: \"Synthetic fixture\"}").unwrap();
            let mut manifest = AppManifest::parse(&json!({"schema":1, "id":id, "version":"1.0.0", "name":"Fixture",
                "integrity":{"bundle_blake3":digest_dir(&bundle).unwrap()},
                "agent":{"profile":"read-only", "tools":tools}}).to_string()).unwrap();
            let publisher = HubKey::generate();
            sign_manifest(&publisher, &mut manifest, id).unwrap();
            entries.push(Entry {manifest, listing:None, tools:vec![], artifact:id.into(),
                publisher:id.into(), publisher_key:publisher.public_hex(),
                source:Source {repository:String::new(), commit:String::new()},
                status:Status::Offered, admitted:"2026-10-11".into()});
        }
        let mut fixture = Self {root:root.clone(), store:host_store(&anchor.public_hex(), &root),
            catalog:Catalog::new(1, "2026-10-11", entries), signer, certificate, anchor:anchor.public_hex()};
        fixture.accept();
        fixture
    }

    fn accept(&mut self) {
        self.catalog.sequence += 1;
        self.signer.sign_catalog(&mut self.catalog, &self.certificate).unwrap();
        self.store.accept_catalog(&serde_json::to_string(&self.catalog).unwrap()).unwrap();
    }

    fn fresh(&self) -> Store {
        let mut store = host_store(&self.anchor, &self.root);
        store.accept_catalog(&serde_json::to_string(&self.catalog).unwrap()).unwrap();
        store
    }
}

impl Drop for Fixture {
    fn drop(&mut self) {
        set_muse_calendar_integration_enabled(false);
        configure_muse_calendar_offers(&mut self.store).unwrap();
        std::fs::remove_dir_all(&self.root).unwrap();
    }
}

#[test]
fn authenticated_muse_ceiling_is_exact_revocable_and_does_not_bypass_signatures() {
    // One test process owns the host's global integration configuration.
    set_muse_calendar_integration_enabled(false);
    {
        let mut f = Fixture::new(SIX);
        configure_muse_calendar_offers(&mut f.store).unwrap();
        assert!(f.store.resolve_offered_policy("muse-goals").unwrap_err().contains("does not offer"));
        set_muse_calendar_integration_enabled(true);
        configure_muse_calendar_offers(&mut f.store).unwrap();
        let expected = SIX.iter().map(|tool| (*tool).to_owned()).collect::<std::collections::BTreeSet<_>>();
        assert_eq!(f.store.resolve_offered_policy("muse-goals").unwrap().agent.unwrap().tools, expected);
        assert!(f.store.resolve_offered_policy("another-app").unwrap_err().contains("does not offer"));
        let clone = f.store.clone();
        let fresh = f.fresh();
        set_muse_calendar_integration_enabled(false);
        configure_muse_calendar_offers(&mut f.store).unwrap();
        for store in [&f.store, &clone, &fresh] {
            assert!(store.resolve_offered_policy("muse-goals").unwrap_err().contains("does not offer"));
        }
        set_muse_calendar_integration_enabled(true);
        configure_muse_calendar_offers(&mut f.store).unwrap();
        f.catalog.entries[0].status = Status::Withdrawn("synthetic withdrawal".into());
        f.accept();
        configure_muse_calendar_offers(&mut f.store).unwrap();
        assert!(f.store.resolve_offered_policy("muse-goals").unwrap_err().contains("withdrawn"));
        assert!(clone.resolve_offered_policy("muse-goals").unwrap_err().contains("does not offer"));
        f.catalog.entries[0].status = Status::Offered;
        f.catalog.entries[0].manifest.integrity.signature = None;
        f.accept();
        assert!(configure_muse_calendar_offers(&mut f.store).is_err());
        assert!(clone.resolve_offered_policy("muse-goals").unwrap_err().contains("does not offer"));
    }
    {
        let mut f = Fixture::new(&["calendar.events", "calendar.agenda", "calendar.delete_event"]);
        set_muse_calendar_integration_enabled(true);
        configure_muse_calendar_offers(&mut f.store).unwrap();
        let error = f.store.resolve_offered_policy("muse-goals").unwrap_err();
        assert!(error.contains("does not offer") && (error.contains("agenda") || error.contains("delete_event")));
    }
    {
        let mut f = Fixture::new(&[]);
        f.catalog.entries.remove(0);
        f.accept();
        set_muse_calendar_integration_enabled(true);
        configure_muse_calendar_offers(&mut f.store).unwrap();
        assert!(f.store.resolve_offered_policy("another-app").is_ok(), "No Muse must not block unrelated admission");
    }
}
