use std::path::{Path, PathBuf};

fn directory(name: &str) -> PathBuf {
    let root = PathBuf::from(std::env::var("MUSE_PATH_TEST_ROOT").unwrap());
    let path = root.join(name);
    std::fs::create_dir_all(&path).unwrap();
    path
}

fn check_path(name: &str, prefix: &str, suffix: &str) {
    let path = directory(name);
    let line = format!("├── octosense-shell v0.1.0 {prefix}({}){suffix}", path.display());
    assert_eq!(extract_dependency_paths(&line), Some(("octosense-shell".into(), Some(path))));
}

#[test]
fn space_and_unicode_source_path() { check_path("Agent APP黑客松/shell", "", ""); }

#[test]
fn parentheses_inside_source_path() { check_path("build (candidate)/shell", "", ""); }

#[test]
fn normal_source_path() { check_path("plain/shell", "", ""); }

#[test]
fn duplicate_with_proc_macro_marker() { check_path("macro source/shell", "(proc-macro) ", " (*)"); }

#[test]
fn nonexistent_source_stays_unresolved() {
    let root = PathBuf::from(std::env::var("MUSE_PATH_TEST_ROOT").unwrap());
    let line = format!("└── absent-crate v1.0.0 ({}/never-created)", root.display());
    assert_eq!(extract_dependency_paths(&line), Some(("absent-crate".into(), None)));
}

#[test]
fn registry_crate_stays_unresolved() {
    assert_eq!(extract_dependency_paths("│ └── serde v1.0.0 (*)"), Some(("serde".into(), None)));
}
