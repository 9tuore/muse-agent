pub mod agents { pub fn strip_note(text: &str) -> &str {
    match text.strip_prefix("[OctoSense: apps with an agent:") {
        Some(rest) => match rest.find("]\n") { Some(end) => rest[end + 2..].trim_start(), None => text },
        None => text,
    }
} }
