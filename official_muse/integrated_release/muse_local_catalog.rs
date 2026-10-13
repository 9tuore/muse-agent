//! Local, fresh catalog for the paired host's exact Muse ceiling.
//! Uses the unchanged Hub gate, packer and signature verifier. No network.
use octosense_app_hub::*;
use octosense_app_policy::{AppManifest, HostLimits};
use std::path::PathBuf;

fn run() -> Result<(), String> {
    let argv: Vec<String> = std::env::args().skip(1).collect();
    if argv.len() != 6 {
        return Err("usage: muse_local_catalog BUNDLE NEW_MIRROR WORKING_KEY CERTIFICATE_FILE ANCHOR_PUBLIC_FILE SOURCE_COMMIT".into());
    }
    let bundle = PathBuf::from(&argv[0]);
    let output = PathBuf::from(&argv[1]);
    let commit = &argv[5];
    if commit.len() != 40 || !commit.bytes().all(|b| b.is_ascii_hexdigit()) {
        return Err("source commit must be a full Git SHA".into());
    }
    let manifest = AppManifest::parse(&std::fs::read_to_string(bundle.join("manifest.json")).map_err(|e| e.to_string())?)?;
    if manifest.id != "muse-goals" || manifest.version != "0.4.0-rc11" {
        return Err("this paired-host publisher accepts only muse-goals 0.4.0-rc11".into());
    }
    const PUBLISHER: &str = "muse-integrated-local";
    const PUBLIC: &str = "79a4c263acba7309593edc38ec1256d5e30f22cc059500c733877d4fbc6d066b";
    const SIX: &[&str] = &["calendar.events", "calendar.get_event", "calendar.add_event",
        "calendar.update_event", "calendar.remove_event", "calendar.notify"];
    let keys = PublisherKeys::new().with(PUBLISHER, PUBLIC);
    let mut limits = HostLimits::default().with_require_signature(true);
    // Mirrors the reviewed native configuration for this exact authenticated
    // app. Default ceilings and the validator remain unchanged for every other app.
    limits.offered_tools.extend(SIX.iter().map(|tool| (*tool).to_owned()));
    let report = check_bundle(&bundle, &limits, &keys, None)?;
    if !report.passed() { return Err(report.render()); }
    if report.app_id != "muse-goals" || report.version != "0.4.0-rc11" {
        return Err("bundle identity changed during admission".into());
    }
    let review = packet(&bundle, &report)?;
    let entry = entry_for(&bundle, &report, PUBLISHER, PUBLIC,
        "https://github.com/9tuore/muse-agent", commit, &today())?;
    let pack = pack_dir(&bundle)?;
    let key_text = std::fs::read_to_string(&argv[2]).map_err(|_| "working key is unavailable")?;
    let raw = hex::decode(key_text.trim()).map_err(|_| "invalid working key encoding")?;
    let bytes: [u8;32] = raw.try_into().map_err(|_| "invalid working key length")?;
    let working = HubKey::from_bytes(&bytes);
    let certificate = std::fs::read_to_string(&argv[3]).map_err(|_| "working certificate is unavailable")?;
    let anchor = std::fs::read_to_string(&argv[4]).map_err(|_| "anchor public key is unavailable")?;
    let mut catalog = Catalog::new(11, &today(), vec![entry]);
    working.sign_catalog(&mut catalog, certificate.trim())?;
    verify_catalog(&catalog, anchor.trim())?;
    std::fs::create_dir(&output).map_err(|e| e.to_string())?;
    let artifact = output.join(&catalog.entries[0].artifact);
    unpack(&pack, &artifact)?;
    let packed_manifest = AppManifest::parse(&std::fs::read_to_string(artifact.join("manifest.json")).map_err(|e| e.to_string())?)?;
    if serde_json::to_value(&packed_manifest).map_err(|e| e.to_string())?
        != serde_json::to_value(&catalog.entries[0].manifest).map_err(|e| e.to_string())?
    {
        return Err("packed manifest differs from the authenticated catalog entry".into());
    }
    if octosense_app_policy::digest_dir(&artifact)? != report.digest {
        return Err("packed bundle differs from the admitted bytes".into());
    }
    for (path, value) in [
        (output.join("catalog.json"), serde_json::to_value(&catalog).map_err(|e| e.to_string())?),
        (output.join("paired-host-gate.json"), report.json()),
        (output.join("review-packet.json"), serde_json::to_value(review).map_err(|e| e.to_string())?),
        (output.join(format!("{}.pack.json", catalog.entries[0].artifact)), serde_json::to_value(pack).map_err(|e| e.to_string())?),
    ] {
        std::fs::write(path, serde_json::to_vec_pretty(&value).map_err(|e| e.to_string())?).map_err(|e| e.to_string())?;
    }
    println!("ADMITTED_LOCAL_PAIRED_HOST_ONLY: {} {}", manifest.id, manifest.version);
    Ok(())
}

fn main() {
    if let Err(error) = run() {
        eprintln!("{error}");
        std::process::exit(1);
    }
}
