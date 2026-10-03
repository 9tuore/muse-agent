#[cfg(test)]
mod prelim_host_tests {
    use super::*;
    use std::io::{BufRead, BufReader, Write};

    fn server(validity: u64, mut uids: Vec<u64>, omit_meta: bool, late_uid: Option<u64>) -> (Imap, std::thread::JoinHandle<()>) {
        let listener = std::net::TcpListener::bind("127.0.0.1:0").unwrap();
        let port = listener.local_addr().unwrap().port();
        let thread = std::thread::spawn(move || {
            let (socket, _) = listener.accept().unwrap();
            let mut out = socket.try_clone().unwrap();
            let mut input = BufReader::new(socket);
            out.write_all(b"* OK fixture\r\n").unwrap();
            let mut examines=0;
            loop {
                let mut line = String::new();
                if input.read_line(&mut line).unwrap()==0 { break; }
                let (tag, command) = line.trim_end().split_once(' ').unwrap();
                let mut response = String::new();
                if command.starts_with("EXAMINE") {
                    examines+=1;
                    if examines==2 { if let Some(uid)=late_uid { uids.push(uid); } }
                    response = format!("* {} EXISTS\r\n* OK [UIDVALIDITY {validity}] fixture\r\n", uids.len());
                } else if let Some(range) = command.strip_prefix("UID SEARCH UID ") {
                    let from: u64 = range.trim_end_matches(":*").parse().unwrap();
                    response = format!("* SEARCH {}\r\n", uids.iter().filter(|u| **u>=from).map(u64::to_string).collect::<Vec<_>>().join(" "));
                } else if let Some(fetch) = command.strip_prefix("UID FETCH ") {
                    let (set, items) = fetch.split_once(' ').unwrap();
                    if items=="(UID FLAGS RFC822.SIZE)" {
                        if !omit_meta {
                            for uid in set.split(',') { response.push_str(&format!("* 1 FETCH (UID {uid} FLAGS () RFC822.SIZE 100)\r\n")); }
                        }
                    } else {
                        let raw = format!("From: fixture@example.invalid\r\nSubject: uid-{set}\r\n\r\nfixture-{set}\r\n");
                        response = format!("* 1 FETCH (UID {set} BODY[] {{{}}}\r\n{raw})\r\n", raw.len());
                    }
                } else if command=="LOGOUT" {
                    response = "* BYE\r\n".into();
                } else { panic!("Unexpected fixture command {command}"); }
                out.write_all(format!("{response}{tag} OK done\r\n").as_bytes()).unwrap();
                if command=="LOGOUT" { break; }
            }
        });
        (Imap::greeted(Wire::connect("127.0.0.1", port).unwrap()).unwrap(), thread)
    }

    #[test]
    fn prelim_host_imap_contiguous_cursor_covers_all_offline_uids() {
        let (mut imap, server) = server(42, (101..=130).collect(), false, None);
        let first = imap.fetch("INBOX", &json!({"uidvalidity":42,"last_uid":100}),25).unwrap();
        let second = imap.fetch("INBOX", &first["state"],25).unwrap();
        let third = imap.fetch("INBOX", &second["state"],25).unwrap();
        imap.logout(); server.join().unwrap();
        let mut downloaded: Vec<u64> = first["messages"].as_array().unwrap().iter()
            .chain(second["messages"].as_array().unwrap()).map(|m| m["imap_uid"].as_u64().unwrap()).collect();
        downloaded.sort_unstable();
        assert_eq!(downloaded,(101..=130).collect::<Vec<_>>(),"must not skip undownloaded UIDs");
        assert_eq!(first["state"]["last_uid"],125);
        assert_eq!(first["has_more"],true);
        assert_eq!(second["has_more"],false);
        assert_eq!(third["messages"],json!([]));
    }

    #[test]
    fn prelim_host_imap_missing_metadata_does_not_advance_cursor() {
        let (mut imap, server) = server(42, vec![101], true, None);
        let result = imap.fetch("INBOX", &json!({"uidvalidity":42,"last_uid":100}),25);
        imap.logout(); server.join().unwrap();
        assert!(result.is_err(),"incomplete metadata cannot be committed as a completed fetch");
    }
    #[test]
    fn prelim_host_imap_snapshot_history_stays_silent_but_later_uid_is_new() {
        let (mut imap, server)=server(7,(1..=30).collect(),false,Some(31));
        let first=imap.fetch("INBOX",&json!({}),25).unwrap();
        let second=imap.fetch("INBOX",&first["state"],25).unwrap();
        imap.logout(); server.join().unwrap();
        assert_eq!(first["reset"],true);
        assert!(first["messages"].as_array().unwrap().iter().all(|m|m["historical"]==true));
        assert_eq!(second["messages"].as_array().unwrap().len(),6);
        assert_eq!(second["messages"][0]["imap_uid"],31);
        assert_eq!(second["messages"][0]["historical"],false);
        assert!(second["messages"].as_array().unwrap()[1..].iter().all(|m|m["historical"]==true));
        assert_eq!(second["has_more"],false);
    }

}
