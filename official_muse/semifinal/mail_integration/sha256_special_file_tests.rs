// Proposed append-only test module for the centrally patched splash_storage.rs.
// Component helper only: the production VM registration/jail still needs tests.
#[cfg(test)]
mod digest_special_file_tests {
    use super::*;

    #[test]
    fn special_file_child() {
        let Some(path) = std::env::var_os("MUSE_DIGEST_SPECIAL_PATH") else { return; };
        assert!(file_sha256(Path::new(&path)).is_err(), "special file must be rejected");
    }
}
