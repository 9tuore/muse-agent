"""Generate review patches only; never modify either upstream checkout."""
import argparse
import difflib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def generate(sdk, hub, output):
    evidence = {}
    contents = {}
    patches = {"desktop": "", "hub": ""}

    def change(tree, relative, old, new):
        root = sdk if tree == "desktop" else hub
        key = (tree, relative)
        before = contents.get(key, (root / relative).read_text())
        assert before.count(old) == 1, f"Baseline mismatch: {relative}"
        contents[key] = before.replace(old, new)
        evidence[f"{tree}/{relative}"] = hashlib.sha256((root / relative).read_bytes()).hexdigest()

    change("hub", "crates/appstore/src/lib.rs", "pub mod system;", """pub mod system;
mod store_agent_offer;
static STORE_AGENT_OFFER: store_agent_offer::StoreAgentOffer = store_agent_offer::StoreAgentOffer::new();

/// Host startup opt-in; not consent, not a grant, not raw Calendar access.
pub fn set_store_calendar_agent_offer(enabled: bool) {
    STORE_AGENT_OFFER.enable_calendar(enabled);
}
pub fn store_host_limits() -> HostLimits {
    let mut limits = HostLimits::default();
    STORE_AGENT_OFFER.extend(&mut limits.offered_tools);
    limits
}""")
    change("hub", "crates/appstore/src/lib.rs",
        "Store::new(&anchor, &self.app_data_root, HostLimits::default())",
        "Store::new(&anchor, &self.app_data_root, store_host_limits())")
    change("hub", "crates/appstore/src/cardapp.rs", "Store::new(&anchor, &root, HostLimits::default())", "Store::new(&anchor, &root, crate::store_host_limits())")
    change("hub", "crates/appstore/src/cardapp.rs", "use octosense_app_policy::HostLimits;", "// Store ceilings come from the host-owned offer.")
    module = (HERE / "store_agent_offer.rs").read_text()
    patches["hub"] += "".join(difflib.unified_diff([],module.splitlines(True),fromfile="/dev/null",tofile="b/crates/appstore/src/store_agent_offer.rs"))
    change("desktop", "crates/shell/src/host_tools/admission.rs", "octosense_app_contract::HostLimits::default()", "octosense_appstore::store_host_limits()")
    change("desktop", "crates/shell/src/glance_card.rs", "octosense_app_contract::HostLimits::default()", "octosense_appstore::store_host_limits()")
    change("desktop", "crates/shell/src/apps.rs", '    octosense_appstore::system::set_agent_tool_offer("os.mail", &["calendar.events", "calendar.add_event", "calendar.notify"]);\n    register_calendar_services();', '    octosense_appstore::system::set_agent_tool_offer("os.mail", &["calendar.events", "calendar.add_event", "calendar.notify"]);\n    register_calendar_services();\n    octosense_appstore::set_store_calendar_agent_offer(true);')
    for (tree, relative), after in contents.items():
        root = sdk if tree == "desktop" else hub
        before = (root / relative).read_text()
        patches[tree] += "".join(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
            fromfile="a/"+relative, tofile="b/"+relative))
    output.mkdir(parents=True, exist_ok=True)
    for tree, patch in patches.items():
        (output / f"{tree}-store-calendar-offer.patch").write_text(patch)
    (output / "baseline-sha256.json").write_text(json.dumps(evidence, indent=2)+"\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sdk", type=Path, required=True)
    parser.add_argument("--hub", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    generate(args.sdk, args.hub, args.out)
