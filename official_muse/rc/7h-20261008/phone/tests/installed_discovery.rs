#[cfg(test)]
mod installed_discovery_tests {
    use super::*;
    use std::path::{Path, PathBuf};
    use std::sync::atomic::{AtomicU64, Ordering};

    struct Fixture(PathBuf);
    impl Fixture {
        fn new() -> Self {
            static NEXT: AtomicU64 = AtomicU64::new(0);
            let path = std::env::temp_dir().join(format!("app-discovery-{}-{}",
                std::process::id(), NEXT.fetch_add(1, Ordering::Relaxed)));
            std::fs::create_dir_all(path.join("apps")).unwrap();
            Self(path)
        }
        fn root(&self) -> PathBuf { self.0.join("apps") }
    }
    impl Drop for Fixture {
        fn drop(&mut self) { std::fs::remove_dir_all(&self.0).unwrap(); }
    }
    fn manifest(id: &str, name: &str) -> String {
        serde_json::json!({"schema":1,"id":id,"version":"1.0.0","name":name,
            "integrity":{"bundle_blake3":"0".repeat(64)}}).to_string()
    }
    fn install(root: &Path, directory: &str, id: &str, name: &str) -> PathBuf {
        let bundle = root.join(directory).join("bundle");
        std::fs::create_dir_all(&bundle).unwrap();
        std::fs::write(bundle.join("manifest.json"), manifest(id, name)).unwrap();
        bundle
    }

    #[test]
    fn normal_installed_apps_are_discovered_in_name_order() {
        let f = Fixture::new();
        install(&f.root(), "org.example.notes", "org.example.notes", "Notes");
        install(&f.root(), "org.example.mail", "org.example.mail", "Mail");
        let rows = installed_apps(&f.root());
        assert_eq!(rows.iter().map(|r| r.id.as_str()).collect::<Vec<_>>(),
            ["org.example.mail", "org.example.notes"]);
        assert!(rows.iter().all(|r| r.version == "1.0.0"));
    }

    #[test]
    fn a_manifest_cannot_impersonate_another_install_directory() {
        let f = Fixture::new();
        install(&f.root(), "org.example.notes", "org.example.mail", "Wrong directory");
        assert!(installed_apps(&f.root()).is_empty());
    }

    #[test]
    fn an_oversized_but_parseable_manifest_is_not_read_into_the_launcher() {
        let f = Fixture::new();
        let bundle = install(&f.root(), "org.example.notes", "org.example.notes", "Notes");
        std::fs::write(bundle.join("manifest.json"),
            manifest("org.example.notes", "Notes") + &" ".repeat(64 * 1024)).unwrap();
        assert!(installed_apps(&f.root()).is_empty());
    }

    #[test]
    fn damaged_or_missing_manifests_do_not_hide_other_apps() {
        let f = Fixture::new();
        install(&f.root(), "org.example.notes", "org.example.notes", "Notes");
        let bad = install(&f.root(), "org.example.bad", "org.example.bad", "Bad");
        std::fs::write(bad.join("manifest.json"), [0xff, 0xfe]).unwrap();
        std::fs::create_dir(f.root().join("missing")).unwrap();
        assert_eq!(installed_apps(&f.root()).len(), 1);
        assert!(installed_apps(&f.0.join("absent")).is_empty());
    }

    #[cfg(unix)]
    #[test]
    fn an_install_directory_cannot_escape_the_apps_root() {
        let f = Fixture::new();
        install(&f.0.join("outside"), "org.example.notes", "org.example.notes", "Outside");
        std::os::unix::fs::symlink(f.0.join("outside/org.example.notes"),
            f.root().join("org.example.notes")).unwrap();
        assert!(installed_apps(&f.root()).is_empty());
    }

    #[cfg(unix)]
    #[test]
    fn a_bundle_cannot_escape_its_own_install_directory() {
        let f = Fixture::new();
        let outside = install(&f.0.join("outside"), "org.example.notes", "org.example.notes", "Outside");
        std::fs::create_dir(f.root().join("org.example.notes")).unwrap();
        std::os::unix::fs::symlink(outside, f.root().join("org.example.notes/bundle")).unwrap();
        assert!(installed_apps(&f.root()).is_empty());
    }

    #[cfg(unix)]
    #[test]
    fn a_manifest_link_cannot_escape_its_bundle() {
        let f = Fixture::new();
        let bundle = install(&f.root(), "org.example.notes", "org.example.notes", "Notes");
        std::fs::write(f.0.join("outside.json"), manifest("org.example.notes", "Outside")).unwrap();
        std::fs::remove_file(bundle.join("manifest.json")).unwrap();
        std::os::unix::fs::symlink(f.0.join("outside.json"), bundle.join("manifest.json")).unwrap();
        assert!(installed_apps(&f.root()).is_empty());
    }

    #[cfg(unix)]
    #[test]
    fn an_explicit_symlink_to_the_apps_root_still_works() {
        let f = Fixture::new();
        install(&f.root(), "org.example.notes", "org.example.notes", "Notes");
        std::os::unix::fs::symlink(f.root(), f.0.join("root-alias")).unwrap();
        assert_eq!(installed_apps(&f.0.join("root-alias")).len(), 1);
    }
}
