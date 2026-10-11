
#[cfg(any(feature = "app-hub", native_mobile))]
#[test]
fn mail_device_lifecycle_claim_uses_resumed_device_and_keeps_account_selection() {
    let home = Scratch::new("mail-device-lifecycle-claim");
    let host = storage(&home.0);
    let app = "sample.device-mail";
    host.set_spec(app, StorageSpec::default());
    let dir = host.layout().apps_root().join(".host");
    write_json(&dir.join("mail/accounts.json"), &json!([
        {"id":"one","address":"one@example.invalid","apps":[app],"signed_in":1}
    ]));
    // Synthetic uninstall state, never the person's metadata or grants.
    host.state().uninstalled.insert(app.into(), std::collections::HashSet::new());
    assert!(mail_account_claim_allowed(&host, &dir, app, "one").unwrap_err().contains("signed out"));
    host.installed(app);
    assert!(!host.is_signed_out(app, None));
    assert!(host.is_signed_out(app, Some("one")));
    assert!(mail_account_claim_allowed(&host, &dir, app, "one").is_ok());
    host.sign_out(app, None);
    assert!(mail_account_claim_allowed(&host, &dir, app, "one").unwrap_err().contains("signed out"));
    host.sign_in(app, None);
    assert!(mail_account_claim_allowed(&host, &dir, app, "other").unwrap_err().contains("selected Mail account changed"));
    // Admission and exact host-dir checks still reject this unadmitted fixture.
    assert!(mail_claim_allowed(&host, &dir, app, "one").is_err());
    assert!(mail_claim_allowed(&host, &dir.join("wrong"), app, "one").is_err());
}
