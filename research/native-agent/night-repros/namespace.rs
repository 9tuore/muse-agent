use octosense_app_policy::{AppManifest, ToolManifest, ToolHost};

#[test]
fn legal_id_fails_its_own_tool_namespace() {
    let manifest = AppManifest::parse(include_str!("../../../bundle/manifest.json")).unwrap();
    assert_eq!(manifest.id, "muse-goals");
    let tools = ToolManifest::parse(include_str!("../prototype/tools.json")).unwrap();
    let issues = tools.check(&manifest);
    let refusal = issues.iter().find(|i| i.refusal && i.detail.contains("must be [a-z0-9_]")).unwrap();
    eprintln!("BASE_ID_PARSE=PASS id={}\nOWN_TOOLS_REFUSAL={}", manifest.id, refusal.detail);
    // Native policy method, not an installed/native hub Gate invocation.
    assert!(tools.validate("muse", ToolHost::Contained, false).iter()
        .all(|i| !i.detail.contains("must be [a-z0-9_]")), "legal namespace control");
}
