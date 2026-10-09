use octosense_app_policy::{ToolManifest,ToolHost};
#[test]
fn proposed_descriptors_pass_original_tool_policy_without_gate_changes() {
    let tools=ToolManifest::parse(include_str!("../../../.local-state/night-calendar-patched/tools.json")).unwrap();
    let issues=tools.validate("calendar",ToolHost::Contained,false);
    let refusals:Vec<_>=issues.iter().filter(|i|i.refusal).collect();
    assert!(refusals.is_empty(),"{refusals:?}");
    assert_eq!(tools.tools.len(),7);
}
