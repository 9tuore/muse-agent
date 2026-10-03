#[cfg(test)]
mod prelim_host_tests {
    use super::*;
    fn batch(uids: Vec<u64>, seen: &HashSet<String>, state: &Value) -> Value {
        let listener=std::net::TcpListener::bind("127.0.0.1:0").unwrap();
        let port=listener.local_addr().unwrap().port();
        let server=std::thread::spawn(move || {
            let (socket,_)=listener.accept().unwrap();
            let mut out=socket.try_clone().unwrap();
            let mut input=BufReader::new(socket);
            loop {
                let mut line=String::new();
                if input.read_line(&mut line).unwrap()==0 {break;}
                let command=line.trim_end();
                let reply=match command {
                    "STAT"=>format!("+OK {} 1000\r\n",uids.len()),
                    "UIDL"=>format!("+OK\r\n{}.\r\n",uids.iter().enumerate().map(|(i,u)|format!("{} uid-{u}\r\n",i+1)).collect::<String>()),
                    "LIST"=>format!("+OK\r\n{}.\r\n",uids.iter().enumerate().map(|(i,_)|format!("{} 100\r\n",i+1)).collect::<String>()),
                    "QUIT"=>"+OK goodbye\r\n".into(),
                    c if c.starts_with("RETR ")=>{
                        let index:usize=c[5..].parse().unwrap();
                        format!("+OK\r\nFrom: fixture@example.invalid\r\nSubject: uid-{}\r\n\r\nBody\r\n.\r\n",uids[index-1])
                    },
                    _=>panic!("unexpected fixture command {command}")
                };
                out.write_all(reply.as_bytes()).unwrap();
                if command=="QUIT" {break;}
            }
        });
        let fetched=fetch_connected(Wire::connect("127.0.0.1",port).unwrap(),&defaults(),seen,state).unwrap();
        server.join().unwrap();
        let adapted=crate::pop_batch(fetched.clone(),seen.iter().map(|uid|json!(uid)).collect());
        assert_eq!(adapted["has_more"],fetched["has_more"],"Network adapter must preserve POP completion");
        assert_eq!(adapted["state"]["baseline_uids"],fetched["baseline_uids"]);
        assert_eq!(adapted["state"]["seen"].as_array().unwrap().len(),seen.len()+fetched["messages"].as_array().unwrap().len());
        fetched
    }
    #[test]
    fn prelim_host_pop_historical_batches_and_arrivals_remain_distinct() {
        let first=batch((1..=30).collect(),&HashSet::new(),&json!({}));
        assert_eq!(first["has_more"],true);
        assert!(first["messages"].as_array().unwrap().iter().all(|m|m["historical"]==true));
        let mut seen:HashSet<String>=first["messages"].as_array().unwrap().iter().map(|m|text(m,"uid").to_string()).collect();
        let state=json!({"baseline_uids":first["baseline_uids"]});
        let second=batch((1..=31).collect(),&seen,&state);
        assert_eq!(second["messages"].as_array().unwrap().len(),6);
        assert_eq!(second["messages"][0]["uid"],"uid-31");
        assert_eq!(second["messages"][0]["historical"],false);
        assert!(second["messages"].as_array().unwrap()[1..].iter().all(|m|m["historical"]==true));
        assert_eq!(second["has_more"],false);
        seen.extend(second["messages"].as_array().unwrap().iter().map(|m|text(m,"uid").to_string()));
        let third=batch((1..=31).collect(),&seen,&state);
        assert_eq!(third["messages"],json!([]));
        assert_eq!(third["has_more"],false);
    }
}
