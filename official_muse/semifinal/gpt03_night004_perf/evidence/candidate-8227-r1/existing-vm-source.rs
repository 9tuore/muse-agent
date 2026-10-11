use makepad_script::*;
use std::io::Write;
use sha2::{Digest, Sha256};
fn main() {
    let path = std::env::args().nth(1).expect("Splash source path required");
    let code = std::fs::read_to_string(&path).expect("read source");
    let host = Box::leak(Box::new(ScriptVmHost::new((), ())));
    let mut vm = ScriptVm { host, bx: Box::new(ScriptVmBase::new()) };
    let module = vm.new_module(id!(fixture));
    vm.add_method(module, id_lut!(sha256), script_args_def!(text = NIL), |vm, args| {
        let text = script_value!(vm, args.text);
        let text = vm.bx.heap.string_with(text, |_, s| s.to_owned()).expect("SHA256 string");
        let digest = format!("{:x}", Sha256::digest(text.as_bytes()));
        vm.new_string_with(|_, value| value.push_str(&digest))
    });
    vm.add_method(module, id_lut!(rpc), script_args_def!(request = NIL), |vm, args| {
        let request = script_value!(vm, args.request);
        let text = vm.bx.heap.string_with(request, |_, s| s.to_owned()).expect("RPC JSON string");
        assert!(text.len() <= 1_000_000, "RPC request exceeds fixture bound");
        println!("MUSE_VM_REQUEST {text}");
        std::io::stdout().flush().expect("flush RPC request");
        let mut reply = String::new();
        std::io::stdin().read_line(&mut reply).expect("read RPC reply");
        assert!(!reply.is_empty() && reply.len() <= 1_000_000, "RPC reply missing or exceeds fixture bound");
        vm.new_string_with(|_, value| value.push_str(reply.trim_end()))
    });
    vm.bx.captured_errors = Some(Vec::new());
    let value = vm.with_instruction_limit(50_000_000, |vm| vm.eval(ScriptMod {
        file: path, code, ..Default::default()
    }));
    let errors = ScriptVm::take_errors(&mut vm);
    for error in &errors { eprintln!("VM_ERROR: {error}"); }
    if !errors.is_empty() { std::process::exit(1); }
    let rpc = std::env::args().any(|arg| arg == "--rpc");
    vm.string_with(value, |_vm, result| {
        if rpc { println!("MUSE_VM_RESULT {result}"); } else { println!("{result}"); }
    });
}
