// Insert into the existing lib.rs cfg(test) tests module, which owns Host/ask.
    struct Batch;
    impl Transport for Batch {
        fn test(&self,_:&Value)->Result<(),String>{Ok(())}
        fn folders(&self,_:&Value)->Result<Vec<Value>,String>{Ok(inbox_only())}
        fn fetch(&self,_:&Value,_:&str,_:&Value)->Result<Value,String>{
            Ok(json!({"messages":[{"id":"fixture-1","uid":"fixture-1","historical":true,"time":0}],"state":{},"reset":true,"has_more":true}))
        }
        fn mark_seen(&self,_:&Value,_:&str,_:&Value)->Result<(),String>{Ok(())}
        fn send(&self,_:&Value,_:&Value)->Result<Value,String>{Err("fixture denies send".into())}
    }
    #[test]
    fn prelim_host_sync_forwards_completeness_reset_and_header_history() {
        let dir=std::env::temp_dir().join(format!("prelim-mail-host-{}",std::process::id()));
        std::fs::create_dir_all(dir.join("mail")).unwrap();
        let accounts=json!([{"id":"fixture","address":"fixture@example.invalid","apps":["os.fixture"]}]);
        std::fs::write(dir.join("mail/accounts.json"),accounts.to_string()).unwrap();
        vault::FileVault.put(&dir.join("mail"),"fixture","synthetic-test-only").unwrap();
        register_with_vault(Arc::new(Batch),Arc::new(vault::FileVault));
        let mut host=Host::default();
        let sync=ask(&dir,"os.fixture","mail.sync",json!({"account":"fixture"}),false,&mut host).unwrap();
        let list=ask(&dir,"os.fixture","mail.list",json!({"account":"fixture"}),false,&mut host).unwrap();
        std::fs::remove_dir_all(dir).unwrap();
        assert_eq!(sync["has_more"],true,"app must know history is incomplete");
        assert_eq!(sync["reset"],true);
        assert_eq!(list["messages"][0]["historical"],true,"cached history must stay distinguishable after UI sync");
    }
