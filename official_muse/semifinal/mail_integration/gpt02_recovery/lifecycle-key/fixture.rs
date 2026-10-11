// Dependency adapters for the source-extracted guards; no Shell, disk profile, or secrets.
use std::{collections::{HashMap,HashSet},sync::{Mutex,MutexGuard},path::{Path,PathBuf},cell::RefCell};
const DEVICE: &str = "device";
fn account_hash(a: &str)->String { format!("fixture-account:{a}") }
#[derive(Clone,Default)] struct StorageSpec { accounts: bool }
#[derive(Default)] struct State { signed_out:HashSet<(String,String)>,uninstalled:HashMap<String,HashSet<String>>,erased:HashSet<(String,String)> }
struct Layout { root:PathBuf }
impl Layout { fn apps_root(&self)->&Path { &self.root } }
struct Storage { state:Mutex<State>,spec:StorageSpec,layout:Layout }
impl Storage {
    fn new(accounts:bool)->Self { Self{state:Mutex::default(),spec:StorageSpec{accounts},layout:Layout{root:PathBuf::from("fixture-apps")}} }
    fn state(&self)->MutexGuard<'_,State> {self.state.lock().unwrap()}
    fn spec(&self,_:&str)->StorageSpec {self.spec.clone()}
    fn layout(&self)->&Layout {&self.layout}
    fn save_suspended(&self,_:&State) {} // Persistence boundary omitted in this unit fixture.
    // INSERT_SOURCE_METHODS
}
thread_local! { static ACTIVE:RefCell<Option<String>>=const{RefCell::new(None)}; static ADMITTED:RefCell<bool>=const{RefCell::new(true)}; static GRANTED:RefCell<bool>=const{RefCell::new(true)}; }
mod octosense_mail_service { use super::*; pub fn active_account(_:&Path,_:&str)->Option<String>{ACTIVE.with(|v|v.borrow().clone())} }
mod host_tools {
    pub mod admission { pub fn check(_:&str)->Result<(),String>{super::super::ADMITTED.with(|v|if *v.borrow(){Ok(())}else{Err("fixture admission refused".into())})} }
    pub mod script_apps {pub fn grants(_:&str,_:&str)->bool{super::super::GRANTED.with(|v|*v.borrow())}}
}
// INSERT_SOURCE_GUARDS
#[cfg(test)] mod tests {
    use super::*;
    fn setup(accounts:bool)->Storage {ACTIVE.with(|v|*v.borrow_mut()=Some("one".into()));ADMITTED.with(|v|*v.borrow_mut()=true);GRANTED.with(|v|*v.borrow_mut()=true);Storage::new(accounts)}
    fn check(s:&Storage)->Result<(),String>{mail_claim_allowed(s,&s.layout.apps_root().join(".host"),"sample.mail","one")}
    #[test] fn device_reinstall_resumes_device_even_with_unresumed_mail_key(){let s=setup(false);s.state().uninstalled.insert("sample.mail".into(),HashSet::new());assert!(check(&s).unwrap_err().contains("signed out"));s.installed("sample.mail");assert!(!s.is_signed_out("sample.mail",None));assert!(s.is_signed_out("sample.mail",Some("one")));assert!(check(&s).is_ok());}
    #[test] fn device_signed_out_still_refused(){let s=setup(false);s.sign_out("sample.mail",None);assert!(check(&s).unwrap_err().contains("signed out"));s.sign_in("sample.mail",None);assert!(check(&s).is_ok());}
    #[test] fn account_mode_uses_mail_key_even_when_device_is_suspended(){let s=setup(true);s.sign_out("sample.mail",None);assert!(check(&s).is_ok());s.sign_out("sample.mail",Some("one"));assert!(check(&s).unwrap_err().contains("signed out"));s.sign_in("sample.mail",Some("one"));assert!(check(&s).is_ok());}
    #[test] fn account_reinstall_requires_account_sign_in(){let s=setup(true);s.state().uninstalled.insert("sample.mail".into(),HashSet::new());s.installed("sample.mail");assert!(check(&s).unwrap_err().contains("signed out"));s.sign_in("sample.mail",Some("one"));assert!(check(&s).is_ok());assert!(s.is_signed_out("sample.mail",Some("other")));}
    #[test] fn selection_changed_or_removed_refused_in_both_modes(){for accounts in [false,true]{let s=setup(accounts);ACTIVE.with(|v|*v.borrow_mut()=Some("other".into()));assert!(check(&s).unwrap_err().contains("selected Mail account changed"));ACTIVE.with(|v|*v.borrow_mut()=None);assert!(check(&s).is_err());}}
    #[test] fn host_admission_and_capability_guards_unchanged(){for accounts in [false,true]{let s=setup(accounts);assert!(mail_claim_allowed(&s,Path::new("wrong"),"sample.mail","one").unwrap_err().contains("does not belong"));ADMITTED.with(|v|*v.borrow_mut()=false);assert!(check(&s).unwrap_err().contains("admission"));ADMITTED.with(|v|*v.borrow_mut()=true);GRANTED.with(|v|*v.borrow_mut()=false);assert!(check(&s).unwrap_err().contains("Mail capability"));}}
}
