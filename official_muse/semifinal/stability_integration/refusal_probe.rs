fn refusal_card(reason: &str) -> String {
    let mut out = String::from(
        "View{width: Fill height: Fill flow: Down padding: Inset{left: 24 right: 24 top: 28 bottom: 24} \
         spacing: 10 show_bg: true draw_bg.color: #xffffff\n\
         \x20   Label{width: Fill max_lines: 1 text: \"card-host refused this bundle\" \
         draw_text.color: #x1c1c1e draw_text.text_style: theme.font_bold{font_size: 16}}\n",
    );
    for line in wrap_script_text(reason, 52, 6) {
        out.push_str(&format!(
            "    Label{{width: Fill max_lines: 1 text: \"{}\" \
             draw_text.color: #x3a3a3c draw_text.text_style.font_size: 13}}\n",
            escape_script_text(&line)
        ));
    }
    out.push_str("}\n");
    out
}

/// `reason` broken into lines of at most `width` characters, at most `lines`
/// of them. A word that fits on a line moves to the next one whole; only a
/// token longer than `width` is broken rather than allowed to run off the
/// card, which is what a digest or a path is.
fn wrap_script_text(text: &str, width: usize, lines: usize) -> Vec<String> {
    let mut out: Vec<String> = Vec::new();
    let mut line = String::new();
    for word in text.split_whitespace() {
        let mut word = word;
        loop {
            let room = width.saturating_sub(if line.is_empty() { 0 } else { line.chars().count() + 1 });
            if word.chars().count() <= room {
                if !line.is_empty() {
                    line.push(' ');
                }
                line.push_str(word);
                break;
            }
            if room > 1 && word.chars().count() > width {
                let take: String = word.chars().take(room).collect();
                if !line.is_empty() {
                    line.push(' ');
                }
                line.push_str(&take);
                word = &word[take.len()..];
            }
            out.push(std::mem::take(&mut line));
            if out.len() == lines {
                // On a full line the ellipsis takes the last character's place.
                let last = out.last_mut().unwrap();
                if last.chars().count() >= width {
                    last.pop();
                }
                last.push('…');
                return out;
            }
        }
    }
    if !line.is_empty() {
        out.push(line);
    }
    if out.is_empty() {
        out.push("(no reason given)".to_string());
    }
    out.truncate(lines);
    out
}

/// A string as a Makepad script string literal: the two characters that would
/// end or corrupt it, escaped.
fn escape_script_text(text: &str) -> String {
    text.replace('\\', "\\\\").replace('"', "\\\"").replace('\n', " ").replace('\t', " ")
}


fn main() { let card=refusal_card("this host does not implement required APIs: mail.compose@1, mail.compose_status@1, mail.review_send@1"); println!("reason={} bytes={}", "this host does not implement required APIs: mail.compose@1, mail.compose_status@1, mail.review_send@1", card.len()); assert_eq!(card.len(),717); }
