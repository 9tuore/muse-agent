use octosense_app_policy::{AppManifest,ToolManifest};
use serde_json::json;

#[test]
fn legal_hyphenated_app_id_has_no_own_tool_namespace_upgrade() {
    let raw=json!({"schema":1,"id":"muse-goals","version":"1.0.0","name":"Synthetic compatibility fixture",
        "integrity":{"bundle_blake3":"0".repeat(64)},"capabilities":["storage"]});
    let manifest=AppManifest::parse(&raw.to_string()).unwrap();
    let declaration=json!({"schema":1,"tools":[{"name":"muse-goals.memory.search","description":"Read synthetic state",
        "input_schema":{"type":"object","properties":{},"additionalProperties":false},
        "output_schema":{"type":"object"},"risk":"read","implemented_by":"app"}]});
    let tools=ToolManifest::parse(&declaration.to_string()).unwrap();
    let issues=tools.check(&manifest);
    assert!(issues.iter().any(|i|i.refusal && i.detail.contains("must be [a-z0-9_]")));
    // Records existing policy. Does not relax the Gate or prove native admission.
}
