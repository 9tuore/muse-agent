fn main() {
    #[cfg(target_os = "macos")]
    {
        println!("cargo:rerun-if-changed=src/eventkit.m");
        cc::Build::new()
            .file("src/eventkit.m")
            .flag("-fobjc-arc")
            .warnings(true)
            .compile("octosense_calendar_eventkit");
        println!("cargo:rustc-link-lib=framework=Foundation");
        println!("cargo:rustc-link-lib=framework=EventKit");
    }
}
