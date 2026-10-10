//! Verify the shipped artifact with the installed official tokenizer/parser.
//! Never executes app code or changes policy, budgets, storage or permissions.
use makepad_script::{heap::ScriptHeap, parser::ScriptParser, tokenizer::ScriptTokenizer};

fn parsed(source: &str) -> (Vec<String>, Vec<String>, usize) {
    let mut heap = ScriptHeap::empty();
    let mut tokenizer = ScriptTokenizer::default();
    tokenizer.tokenize(source, &mut heap);
    tokenizer.finish(&mut heap);
    let tokens = tokenizer.tokens.iter().map(|t| {
        format!("{:?}:{}", t.token, t.preceded_by_newline)
    }).collect();
    let mut parser = ScriptParser::default();
    parser.parse(&tokenizer, "muse-artifact-check", (0, 0), &[]);
    assert!(parser.parse_errors.is_empty(), "{:?}", parser.parse_errors);
    let opcodes = parser.opcodes.iter().map(|value| format!("{value:?}")).collect();
    (tokens, opcodes, tokenizer.docs.len())
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    assert_eq!(args.len(), 3);
    let source = std::fs::read_to_string(&args[1]).unwrap();
    let artifact = std::fs::read_to_string(&args[2]).unwrap();
    // The exact no-network prefix of the tested official Splash version.
    let prefix = "use mod.prelude.widgets.*\nlet fs = mod.fs\nlet host = mod.host\nView{height:Fit, ";
    let before = parsed(&format!("{prefix}{source}"));
    let after = parsed(&format!("{prefix}{artifact}"));
    assert_eq!(before, after, "Compaction changed official tokens or opcodes");
    assert_eq!(source.lines().count(), artifact.lines().count());
    println!("{{\"tokens_and_newline_boundaries_equal\":true,\"opcodes_equal\":true,\"parse_errors\":0,\"line_count_preserved\":true,\"tokens\":{},\"opcodes\":{},\"source_bytes\":{},\"artifact_bytes\":{}}}", before.0.len(), before.1.len(), source.len(), artifact.len());
}
