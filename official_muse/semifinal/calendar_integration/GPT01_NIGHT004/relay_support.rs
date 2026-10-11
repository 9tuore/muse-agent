//! Unused native/file/process surfaces are explicit fixture adapters, never successful executors.
pub mod ai_host {
    pub use octosense_app_peers as app_peers;
    pub mod contained { pub const PEER_PREFIX:&str="card."; }
}
pub mod app_chat { pub const INSTANCE:&str="shell-ask"; }
pub mod glance_chat { pub const INSTANCE:&str="card-chat"; }
pub mod native_apps {
    pub struct NativeApp {
        pub id:&'static str, pub tools_json:&'static str, pub own_tools:&'static [&'static str],
        pub grants:&'static [(&'static str,&'static str)], pub generic_tools:&'static [&'static str],
        pub calls_per_turn:Option<u32>,pub calls_per_day:Option<u32>,
    }
    pub const APPS:&[NativeApp]=&[];
    pub fn find(_id:&str)->Option<&'static NativeApp>{None}
}
pub mod approvals;
pub mod peer_link;
pub mod host_tools {
    pub mod relay;
    pub mod schema;
    pub mod files {
        pub const TOOLS:&[&str]=&["files.list","files.read","files.search"];
        pub fn declarations(_owner:&str)->Vec<serde_json::Value>{panic!("File tools excluded from Calendar fixture")}
    }
    pub mod dev_run {
        pub fn declaration(_owner:&str)->serde_json::Value{panic!("Developer commands excluded from fixture")}
    }
}
#[cfg(test)]
mod relay_tests;
