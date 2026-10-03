//! Pure format tests fed raw RFC822/MIME bytes; no transport or stored accounts.
use super::*;
use base64::{engine::general_purpose::STANDARD, Engine};

#[test]
fn empty_or_missing_sender_and_subject_use_host_fallbacks() {
    for headers in ["", "From:\r\nSubject: \t\r\n"] {
        let raw = format!("{headers}Content-Type: text/plain; charset=utf-8\r\n\r\n实际正文");
        let decoded = network::decode(raw.as_bytes(), "empty-headers").unwrap();
        let message = normalize(decoded);
        assert_eq!(message["sender"], "未知发件人");
        assert_eq!(message["address"], "");
        assert_eq!(message["subject"], "(No subject)");
        assert_eq!(message["body"], "实际正文");
    }
}

#[test]
fn sender_without_display_name_uses_parsed_address() {
    let raw = b"From: sender@example.invalid\r\nSubject: Bare address\r\nContent-Type: text/plain\r\n\r\nbody";
    let message = normalize(network::decode(raw, "bare-address").unwrap());
    assert_eq!(message["sender"], "sender@example.invalid");
    assert_eq!(message["address"], "sender@example.invalid");
}

#[test]
fn alternative_plain_body_wins_in_either_part_order() {
    let plain = "Content-Type: text/plain; charset=utf-8\r\nContent-Transfer-Encoding: quoted-printable\r\n\r\n=E7=BA=AF=E6=96=87=E6=9C=AC plain wins";
    let html = "Content-Type: text/html; charset=utf-8\r\n\r\n<p>HTML alternative must not replace plain</p>";
    for parts in [[plain, html], [html, plain]] {
        let raw = format!("MIME-Version: 1.0\r\nContent-Type: multipart/alternative; boundary=fmt\r\n\r\n--fmt\r\n{}\r\n--fmt\r\n{}\r\n--fmt--\r\n", parts[0], parts[1]);
        let decoded = network::decode(raw.as_bytes(), "plain-priority").unwrap();
        assert_eq!(decoded["body"], "纯文本 plain wins");
        let message = normalize(decoded);
        assert_eq!(message["body"], "纯文本 plain wins");
        assert!(text(&message, "html").contains("HTML alternative"));
    }
}

#[test]
fn html_only_utf8_base64_decodes_then_normalizes_to_readable_body() {
    let html = "<html><head><style>FORMAT_STYLE_SENTINEL</style></head><body><p>你好，世界 &amp; Muse</p><p>下一段</p></body></html>";
    let raw = format!("MIME-Version: 1.0\r\nContent-Type: text/html; charset=utf-8\r\nContent-Transfer-Encoding: base64\r\n\r\n{}", STANDARD.encode(html.as_bytes()));
    let decoded = network::decode(raw.as_bytes(), "html-utf8").unwrap();
    assert_eq!(decoded["html"], html);
    assert!(text(&decoded, "body").contains("你好，世界 & Muse"));
    assert!(text(&decoded, "body").contains("FORMAT_STYLE_SENTINEL"));
    let message = normalize(decoded);
    assert_eq!(message["body"], "你好，世界 & Muse\n\n下一段");
    assert_eq!(message["preview"], "你好，世界 & Muse 下一段");
    assert!(!text(&message, "html").contains("FORMAT_STYLE_SENTINEL"));
    assert!(!text(&message, "body").contains("FORMAT_STYLE_SENTINEL"));
}

#[test]
fn whitespace_plain_part_falls_back_to_html_utf8() {
    let raw = "MIME-Version: 1.0\r\nContent-Type: multipart/alternative; boundary=blank\r\n\r\n--blank\r\nContent-Type: text/plain; charset=utf-8\r\n\r\n \t\r\n--blank\r\nContent-Type: text/html; charset=utf-8\r\n\r\n<p>仅 HTML 可读正文</p>\r\n--blank--\r\n";
    let message = normalize(network::decode(raw.as_bytes(), "empty-plain").unwrap());
    assert_eq!(message["body"], "仅 HTML 可读正文");
}
