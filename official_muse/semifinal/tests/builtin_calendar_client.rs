//! An independent-process client of the original service, no fake transport.
use serde_json::{json, Value};
use std::path::Path;
fn main() {
    let args: Vec<String> = std::env::args().collect();
    assert_eq!(args.len(), 5);
    let root = Path::new(&args[1]);
    let payload: Value = serde_json::from_str(&args[4]).unwrap();
    if args[3] == "admission-check" {
        use octosense_app_policy::{admit_and_resolve, bundle_digest, HostLimits, RefuseAllSignatures};
        let bytes = b"Synthetic reviewed Calendar grant fixture";
        let mut manifest = json!({"schema":1,"id":"muse-goals","version":"0.0.1","name":"Muse synthetic grant",
            "integrity":{"bundle_blake3":bundle_digest(bytes)},"capabilities":["storage","calendar"],
            "agent":{"profile":"read-only","tools":["calendar.events"]}});
        // Explicit unsigned developer fixture; shipping signature policy is
        // tested separately and never changed in an installed host.
        let baseline = HostLimits::default().with_require_signature(false);
        let default_result = admit_and_resolve(&manifest.to_string(),bytes,&baseline,&RefuseAllSignatures);
        let offer = baseline.clone().with_offered_tools(["calendar.events"]);
        let scoped = admit_and_resolve(&manifest.to_string(),bytes,&offer,&RefuseAllSignatures);
        let strict = admit_and_resolve(&manifest.to_string(),bytes,&offer.clone().with_require_signature(true),&RefuseAllSignatures);
        manifest["agent"]["tools"] = json!(["calendar.remove_event"]);
        let extra = admit_and_resolve(&manifest.to_string(),bytes,&offer,&RefuseAllSignatures);
        manifest["agent"]["tools"] = json!(["calendar.events"]);
        let tamper = admit_and_resolve(&manifest.to_string(),b"changed bytes",&offer,&RefuseAllSignatures);
        println!("{}",json!({"ok":true,"value":{
            "default_calendar_offer_denied":default_result.is_err(),
            "trusted_host_scoped_offer_resolves":scoped.is_ok(),
            "identity_preserved":scoped.as_ref().map(|p|p.app.app_id.as_str())==Ok("muse-goals"),
            "unoffered_delete_still_denied":extra.is_err(),"digest_tamper_still_denied":tamper.is_err(),
            "shipping_signature_requirement_preserved":strict.is_err(),
            "budgets_unchanged":offer.max_instruction_budget==baseline.max_instruction_budget && offer.max_memory_bytes==baseline.max_memory_bytes,
            "boundary":"Official policy/digest component only; no installed publisher signature, catalog admission, Shell grant or native confirmation."}}));
        return;
    }
    if args[3] == "tools-check" {
        use octosense_app_policy::{ToolManifest, ToolHost};
        let source = std::fs::read_to_string(payload["path"].as_str().unwrap()).unwrap();
        let result = ToolManifest::load(&source,"calendar",ToolHost::Contained,false);
        println!("{}", match result {
            Ok((tools,issues)) => json!({"ok":!issues.iter().any(|i| i.refusal),"value":tools.tools.iter().map(|t|json!({"name":t.name,"shareable":t.shareable,"needs_person":t.supervision().needs_person(),"auto_approvable":t.auto_approvable})).collect::<Vec<_>>(),"issues":issues.iter().map(|i|i.detail.clone()).collect::<Vec<_>>()}),
            Err(error)=>json!({"ok":false,"error":error})
        });
        return;
    }
    let result = if args[3] == "raw-read" {
        // Independent durable read; this is a test oracle, not an app tool.
        std::fs::read(root.join("calendar/events.json"))
            .map_err(|e| e.to_string()).and_then(|bytes| serde_json::from_slice(&bytes).map_err(|e| e.to_string()))
    } else {
        octosense_calendar_service::handle(&args[2], &args[3], &payload, root,
            octosense_calendar_service::parse_time("2026-10-10T18:30").unwrap(), None)
    };
    println!("{}", match result { Ok(value) => json!({"ok":true,"value":value}), Err(error) => json!({"ok":false,"error":error}) });
}
