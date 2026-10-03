use makepad_script::{ScriptHeap, tokenizer::{ScriptTokenizer, ScriptToken}};

fn tokens(path: &str, heap: &mut ScriptHeap) -> Vec<String> {
    let source = std::fs::read_to_string(path).unwrap();
    let mut tokenizer = ScriptTokenizer::default();
    tokenizer.tokenize(&source, heap);
    tokenizer.tokens.iter().map(|item| {
        let value = match item.token {
            ScriptToken::String(value) => {
                let mut text = String::new();
                heap.cast_to_string(value, &mut text);
                format!("String:{text:?}")
            },
            token => format!("{token:?}"),
        };
        format!("{}:{value}", item.preceded_by_newline)
    }).collect()
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let mut heap = ScriptHeap::default();
    let original = tokens(&args[1], &mut heap);
    let compact = tokens(&args[2], &mut heap);
    let same = original == compact;
    println!("{{\"tokens_equal\":{same},\"original_count\":{},\"artifact_count\":{}}}", original.len(), compact.len());
    if !same { std::process::exit(1); }
}
