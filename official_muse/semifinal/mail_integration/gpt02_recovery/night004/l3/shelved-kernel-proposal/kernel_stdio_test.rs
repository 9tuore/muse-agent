
/// Test-only actual Kernel/Broker/Relay/Calendar stdio bridge for the production VM.
/// Model, fixture admission and gestures are synthetic; history is returned only by the real Broker.
#[test]
#[ignore="central owned L3 orchestration only; requires pinned actual Kernel and marked state"]
fn night004_l3_kernel_stdio_bridge(){
    use octosense_app_hub::{Catalog, Entry, HubKey, Source, Status};
    use crate::approvals::Caller;
    use crate::approvals::sheet::Answer;
    use std::io::Write;
    use sha2::Digest;
    let program=kernel().expect("actual pinned Kernel required; no skip/pass fallback");
    assert_eq!(format!("{:x}",sha2::Sha256::digest(std::fs::read(&program).unwrap())),
        "56761a9f24dd2b8dea0cd3fd2df85be877e9ee466aa6b88a5f2c0e2ee3948270");
    // Process-local catalog settings: no production profile, credential or remote model.
    std::env::set_var("OCTOSENSE_HUB_CATALOG", "legacy");
    let dir=PathBuf::from(std::env::var_os("NIGHT004_L3_KERNEL_ROOT").expect("explicit owned fixture root")).canonicalize().unwrap();
    let allowed=Path::new("/Users/mima0000/.codex/worktrees/muse-semifinal-a-20261009/Agent APP黑客松/build/night-004").canonicalize().unwrap();
    assert!(dir.starts_with(&allowed)&&dir!=allowed&&dir.join("FIXTURE_ONLY").is_file(),"marked central NIGHT-004 fixture root required");
    let apps_root = dir.join("apps");
    octosense_appstore::set_data_root(apps_root.clone());
    octosense_appstore::set_muse_calendar_integration_enabled(true);
    let bundle = octosense_app_hub::installed_bundle_dir(&apps_root, "muse-goals");
    std::fs::create_dir_all(&bundle).unwrap();
    std::fs::write(bundle.join("main.splash"), "Label{text: \"NIGHT-004 synthetic Muse fixture\"}").unwrap();
    let six = ["calendar.events", "calendar.get_event", "calendar.add_event",
        "calendar.update_event", "calendar.remove_event", "calendar.notify"];
    let mut manifest = octosense_app_contract::AppManifest::parse(&json!({
        "schema":1,"id":"muse-goals","version":"1.0.0","name":"Synthetic Muse",
        "integrity":{"bundle_blake3":octosense_app_contract::digest_dir(&bundle).unwrap()},
        "agent":{"profile":"read-only","tools":six}
    }).to_string()).unwrap();
    let publisher = HubKey::generate();
    octosense_app_hub::sign_manifest(&publisher, &mut manifest, "night004-fixture").unwrap();
    std::fs::write(bundle.join("manifest.json"), serde_json::to_vec(&manifest).unwrap()).unwrap();
    let anchor = HubKey::generate();
    let signer = HubKey::generate();
    let certificate = anchor.certify(&signer.public_hex()).unwrap();
    std::env::set_var("OCTOSENSE_HUB_ANCHOR", anchor.public_hex());
    let mut catalog = Catalog::new(1, "2026-10-12", vec![Entry {
        manifest,listing:None,tools:vec![],artifact:"night004-fixture".into(),
        publisher:"night004-fixture".into(),publisher_key:publisher.public_hex(),
        source:Source{repository:String::new(),commit:String::new()},
        status:Status::Offered,admitted:"2026-10-12".into()
    }]);
    signer.sign_catalog(&mut catalog, &certificate).unwrap();
    std::fs::write(apps_root.join("catalog.json"), serde_json::to_vec(&catalog).unwrap()).unwrap();
    let home = dir.join("home");
    std::fs::create_dir_all(&home).unwrap();
    crate::approvals::init(&home);
    super::init();
    assert!(!crate::dev_mode::grants_all("muse-goals"), "no developer blanket grant");
    crate::approvals::with(|a| a.consent.set(
        &crate::approvals::rules::ApprovalGesture::sheet_tap(), "muse-goals", true, crate::approvals::now())).unwrap();
    let host_dir = apps_root.join(".host");
    std::fs::create_dir(&host_dir).unwrap();
    std::fs::write(host_dir.join("FIXTURE_ONLY"), "Synthetic fixture only\n").unwrap();
    // Match prepare_news/production App Hub: first use registers the compiled
    // system packs. Registering CalendarService alone does not register its bundle.
    let calendar_system=octosense_app_hub_app::system_apps().into_iter()
        .find(|app|app.id=="os.calendar").expect("the actual build ships Calendar's official system pack");
    let (calendar_bundle,_)=octosense_appstore::system::prepare(&apps_root,&calendar_system)
        .expect("Calendar's compiled pack must pass real digest/policy admission");
    assert!(calendar_bundle.join("manifest.json").is_file());
    octosense_calendar_service::register();
    // Fail at initialization rather than letting ensure_loaded's logged failure
    // produce an empty model offer later. This uses the actual admitted owner.
    super::script_apps::load("os.calendar").expect("official Calendar owner tools/executor loaded");
    super::script_apps::load("muse-goals").expect("signed fixture and real system Calendar owner admitted");
    assert_eq!(super::owner_of("calendar.add_event").as_deref(), Some("os.calendar"));
    let preflight=super::ShellToolHost.declarations("card.muse-goals",crate::ai_host::contained::ACCOUNT)
        .expect("real signed Muse admission and owner declarations");
    for tool in six {assert!(preflight.iter().any(|d|d["app"]=="os.calendar"&&d["name"]==tool),
        "real owner must offer {tool} before starting the model: {preflight}");}
    eprintln!("NIGHT004_OWNER_INITIALIZED {}",json!({"owner":"os.calendar","bundle":calendar_bundle,"declarations":preflight}));
    let offered_log = dir.join("offered.jsonl");
    let model_script=PathBuf::from(std::env::var_os("NIGHT004_L3_MODEL_SCRIPT").expect("explicit scripted model fixture"));
    let official_model_script=Path::new(env!("CARGO_MANIFEST_DIR")).join("../app-peers/tests/fixtures/mock_agent_llm.py");
    let mut model_child=std::process::Command::new("python3").arg(&model_script).arg(&official_model_script)
        .env("MOCK_LLM_TOOLS_LOG",&offered_log).stdout(std::process::Stdio::piped()).stderr(std::process::Stdio::inherit()).spawn().unwrap();
    let mut model_port=String::new();std::io::BufReader::new(model_child.stdout.take().unwrap()).read_line(&mut model_port).unwrap();
    let model=Model(model_child,model_port.trim().parse().unwrap());
    let core_dir = dir.join("octos-home/.octos");
    write_profile(&core_dir, model.1);
    let core = Core::new(Options::default().core_dir(&core_dir).program(&program));
    let mut cfg = BrokerConfig::new(Deployment::Hosted, "_main", "_main:api:octosense#system",
        "card.muse-goals", "Synthetic Muse", OCTOS_SERVICES.iter().map(|s|s.to_string()).collect());
    cfg.state_dir = Some(dir.join("host-state"));
    cfg.tool_host = Some(ToolHostHandle(Arc::new(super::ShellToolHost) as Arc<dyn ToolHost>));
    let muse = Broker::new(cfg, Arc::new(CoreConnector::shared(core.clone())));
    muse.set_account(Some(crate::ai_host::contained::ACCOUNT));
    let ctx = muse.open_context(ContextSpec {account:crate::ai_host::contained::ACCOUNT.into(),
        instance:"card.muse-goals-night004-l3".into(),services:OCTOS_SERVICES.iter().map(|s|s.to_string()).collect()}).unwrap();

    let _cleanup=Cleanup{core:core.clone(),model:Some(model),dirs:vec![],broker:Some(muse.clone()),links:None};
    for line in std::io::stdin().lock().lines(){
        let line=line.unwrap();assert!(line.len()<=1_000_000);
        let request:Value=serde_json::from_str(&line).unwrap();let id=request["id"].clone();
        let method=request["method"].as_str().unwrap();let payload=&request["payload"];
        if method=="fixture.quit"{println!("MUSE_KERNEL_REPLY {}",json!({"id":id,"is_ok":true,"data":{"quit":true}}));std::io::stdout().flush().unwrap();break;}
        let plan=request["tool_plan"].as_array().cloned().unwrap_or_default();
        let operation=match method{
            "octos.session.open"=>ContextOp::Open,
            "octos.session.history"=>ContextOp::History,
            "octos.turn.start"=>{
                assert!(!plan.is_empty()&&plan.len()<=5,"explicit bounded fixture tool selection required");
                for step in &plan{assert!(six.contains(&step["tool"].as_str().unwrap())&&step["args"].is_object());}
                let text=payload["text"].as_str().unwrap();
                ContextOp::Turn{text:format!("{}\nMUSE_L3_TOOL_PLAN:{}",text,Value::Array(plan.clone()))}
            },
            _=>{println!("MUSE_KERNEL_REPLY {}",json!({"id":id,"is_ok":false,"error":"unsupported actual Kernel bridge method"}));std::io::stdout().flush().unwrap();continue;}
        };
        let approvals=Arc::new(Mutex::new(Vec::<Value>::new()));
        let (tx,rx)=std::sync::mpsc::channel();let tx=Mutex::new(tx);
        let started=ctx.call(operation,Arc::new(move|event|{let _=tx.lock().unwrap().send(event);}));
        let result=if let Err(error)=started{Err(error)}else{
            let deadline=Instant::now()+Duration::from_secs(120);
            loop{
                super::pump();
                crate::approvals::with(|a|{
                    let Some(sheet)=a.router.front_sheet().cloned()else{return};
                    for line in sheet.lines{
                        let pending=a.router.pending_request(&line.request).cloned().unwrap();
                        assert_eq!(pending.app,"os.calendar");assert_eq!(pending.caller,Caller::AppAgent{app:"muse-goals".into()});
                        assert!(plan.iter().any(|step|step["tool"]==pending.tool.name&&step["args"]==pending.args),"approval differs from explicit fixture tool plan");
                        let answer=match request["fixture_approval"].as_str(){Some("once")=>Answer::Once,Some("deny")=>Answer::Deny,_=>panic!("explicit synthetic approval decision required")};
                        approvals.lock().unwrap().push(json!({"fixture_gesture":true,"owner":pending.app,"tool":pending.tool.name,"args":pending.args,"caller":"muse-goals","approved":answer==Answer::Once}));
                        a.router.answer(sheet.id,&line.request,answer,&crate::approvals::rules::ApprovalGesture::sheet_tap(),crate::approvals::now()).unwrap();
                    }
                });
                match rx.recv_timeout(Duration::from_millis(20)){
                    Ok(ContextEvent::Complete(result))=>break result,
                    Ok(ContextEvent::Data(_))|Err(std::sync::mpsc::RecvTimeoutError::Timeout)=>{},
                    Err(std::sync::mpsc::RecvTimeoutError::Disconnected)=>break Err("actual Kernel callback disconnected".into())
                }
                if Instant::now()>=deadline{break Err("actual Kernel fixture turn timed out".into());}
            }
        };
        let mut response=match result{Ok(data)=>json!({"id":id,"is_ok":true,"data":data}),Err(error)=>json!({"id":id,"is_ok":false,"error":error})};
        response["fixture"]=json!({"model":"scripted localhost","admission":"signed synthetic Muse catalog","approval_gestures":"synthetic","kernel_process":true,"history":"unmodified actual Broker response"});
        response["approval_trace"]=json!(approvals.lock().unwrap().clone());
        println!("MUSE_KERNEL_REPLY {response}");std::io::stdout().flush().unwrap();
    }
}
