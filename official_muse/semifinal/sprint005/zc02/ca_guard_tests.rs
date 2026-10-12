// Proposal only: append to patched network.rs for one focused isolated SDK test.
// No GUI, grant, account/draft store or production credential access.
#[cfg(test)]
mod sprint005_fixture_tests {
    use super::*;
    use std::{ffi::OsString, path::PathBuf};
    static ENV_LOCK: std::sync::Mutex<()> = std::sync::Mutex::new(());
    struct Restore(Vec<(&'static str, Option<OsString>)>);
    impl Drop for Restore {
        fn drop(&mut self) { for (key,value) in &self.0 { match value { Some(v)=>std::env::set_var(key,v),None=>std::env::remove_var(key) } } }
    }
    #[test]
    fn sprint005_ca_guard_matrix() {
        let _lock=ENV_LOCK.lock().unwrap();
        let keys=["OCTOSENSE_MAIL_TLS_FIXTURE_ROOT","OCTOSENSE_MAIL_VAULT","MUSE_INTEGRATED_STATE"];
        let _restore=Restore(keys.into_iter().map(|k|(k,std::env::var_os(k))).collect());
        std::env::remove_var(keys[0]);
        assert!(sprint005_fixture_ca("imap.example.invalid").unwrap().is_none());
        let ca=std::fs::read(PathBuf::from(std::env::var_os("SPRINT005_TEST_CA_DER").expect("Explicit generated fixture PUBLIC CA DER required"))).unwrap();
        let name=format!("sprint005-ca-{}-{}",std::process::id(),std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_nanos());
        let root=std::env::temp_dir().join(name);std::fs::create_dir_all(root.join("apps/.host")).unwrap();std::fs::create_dir(root.join("public")).unwrap();let root=root.canonicalize().unwrap();
        let primary=b"SPRINT005 isolated SDK GUI fixture only\n";
        let owner=b"SPRINT005 synthetic Calendar/Mail owner fixture only\n";
        std::fs::write(root.join("FIXTURE_ONLY"),primary).unwrap();std::fs::write(root.join("apps/.host/FIXTURE_ONLY"),owner).unwrap();
        std::fs::write(root.join("public/mail-fixture-ca.der"),&ca).unwrap();
        let good=json!({"protocol":"SPRINT005_MAIL_TLS_FIXTURE_V1","ca_sha256":format!("{:x}",Sha256::digest(&ca))});
        std::fs::write(root.join("mail-fixture.json"),good.to_string()).unwrap();
        std::env::set_var(keys[0],&root);std::env::set_var(keys[1],"file");std::env::set_var(keys[2],&root);
        assert_eq!(sprint005_fixture_ca("127.0.0.1").unwrap().unwrap(),ca);
        let mut roots=rustls::RootCertStore::empty();assert!(roots.add(rustls::pki_types::CertificateDer::from(ca.clone())).is_ok());
        for host in ["localhost","::1","127.1","smtp.example.invalid","127.0.0.1.example.invalid"] { assert!(sprint005_fixture_ca(host).is_err()); }
        std::env::set_var(keys[1],"keychain");assert!(sprint005_fixture_ca("127.0.0.1").is_err());std::env::set_var(keys[1],"file");
        std::env::set_var(keys[2],root.join("different-profile"));assert!(sprint005_fixture_ca("127.0.0.1").is_err());std::env::set_var(keys[2],&root);
        std::fs::remove_file(root.join("apps/.host/FIXTURE_ONLY")).unwrap();assert!(sprint005_fixture_ca("127.0.0.1").is_err());std::fs::write(root.join("apps/.host/FIXTURE_ONLY"),owner).unwrap();
        std::fs::write(root.join("FIXTURE_ONLY"),b"legacy fixture\n").unwrap();assert!(sprint005_fixture_ca("127.0.0.1").is_err());std::fs::write(root.join("FIXTURE_ONLY"),primary).unwrap();
        std::fs::write(root.join("mail-fixture.json"),b"{broken").unwrap();assert!(sprint005_fixture_ca("127.0.0.1").is_err());
        let mut bad=good.clone();bad["ca_sha256"]=json!("0".repeat(64));std::fs::write(root.join("mail-fixture.json"),bad.to_string()).unwrap();assert!(sprint005_fixture_ca("127.0.0.1").is_err());
        std::fs::write(root.join("mail-fixture.json"),good.to_string()).unwrap();std::fs::write(root.join("public/mail-fixture-ca.der"),vec![0;16385]).unwrap();assert!(sprint005_fixture_ca("127.0.0.1").is_err());
        std::fs::write(root.join("public/mail-fixture-ca.der"),&ca).unwrap();
        #[cfg(unix)] {
            let cert=root.join("public/mail-fixture-ca.der");std::fs::rename(&cert,root.join("public/ca-original.der")).unwrap();std::os::unix::fs::symlink(root.join("public/ca-original.der"),&cert).unwrap();assert!(sprint005_fixture_ca("127.0.0.1").is_err());std::fs::remove_file(cert).unwrap();
        }
        std::fs::remove_dir_all(root).unwrap();
    }
}
