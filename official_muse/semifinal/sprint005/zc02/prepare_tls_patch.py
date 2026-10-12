#!/usr/bin/env python3
"""Propose scoped root trust; never apply/build shared SDK."""
import difflib,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent

HELPER='''// Explicit synthetic GUI profile only. No production trust or consent change.
fn sprint005_fixture_ca(host: &str) -> Result<Option<Vec<u8>>, String> {
    let Some(requested) = std::env::var_os("OCTOSENSE_MAIL_TLS_FIXTURE_ROOT") else { return Ok(None) };
    if host != "127.0.0.1" || std::env::var("OCTOSENSE_MAIL_VAULT").ok().as_deref() != Some("file") {
        return Err("SPRINT005 fixture requires loopback and file-only synthetic vault".into());
    }
    let requested = std::path::PathBuf::from(requested);
    let root = std::fs::canonicalize(&requested).map_err(|_| "Fixture root unavailable")?;
    if root != requested { return Err("Canonical fixture root required".into()) }
    let profile = std::env::var_os("MUSE_INTEGRATED_STATE").ok_or("Explicit fixture profile required")?;
    if std::fs::canonicalize(profile).map_err(|_| "Fixture profile unavailable")? != root {
        return Err("Fixture TLS root and active launcher profile differ".into());
    }
    for relative in ["FIXTURE_ONLY", "apps", "apps/.host", "apps/.host/FIXTURE_ONLY", "public", "public/mail-fixture-ca.der", "mail-fixture.json"] {
        if std::fs::symlink_metadata(root.join(relative)).map_err(|_| "Fixture component missing")?.file_type().is_symlink() {
            return Err("Fixture symlink refused".into());
        }
    }
    if std::fs::read(root.join("FIXTURE_ONLY")).ok().as_deref() != Some(b"SPRINT005 isolated SDK GUI fixture only\\n")
        || std::fs::read(root.join("apps/.host/FIXTURE_ONLY")).ok().as_deref() != Some(b"SPRINT005 synthetic Calendar/Mail owner fixture only\\n") {
        return Err("Exact SPRINT005 double fixture markers required".into());
    }
    let cert_path = root.join("public/mail-fixture-ca.der");
    if std::fs::metadata(&cert_path).map_err(|_| "Fixture CA unavailable")?.len() > 16384 {
        return Err("Fixture CA too large".into());
    }
    let cert = std::fs::read(cert_path).map_err(|_| "Fixture CA unavailable")?;
    let config: Value = serde_json::from_slice(&std::fs::read(root.join("mail-fixture.json")).map_err(|_| "Fixture configuration missing")?)
        .map_err(|_| "Fixture configuration invalid")?;
    let digest = format!("{:x}", Sha256::digest(&cert));
    if config["protocol"] != "SPRINT005_MAIL_TLS_FIXTURE_V1" || config["ca_sha256"] != digest {
        return Err("Fixture CA identity mismatch".into());
    }
    Ok(Some(cert))
}

'''

def main():
    record=json.loads((HERE/'source-identities.json').read_text())['mail/network.rs']
    src=Path(record['path']);before=src.read_text();assert hashlib.sha256(src.read_bytes()).hexdigest()==record['sha256']
    after=before.replace('pub(crate) enum Wire {',HELPER+'pub(crate) enum Wire {',1)
    after=after.replace('    pub(crate) fn connect(host: &str, port: u16) -> Result<Self, String> {\n','    pub(crate) fn connect(host: &str, port: u16) -> Result<Self, String> {\n        let _ = sprint005_fixture_ca(host)?; // Reject nonloopback before DNS/connect.\n',1)
    after=after.replace('        let roots = rustls::RootCertStore {','        let mut roots = rustls::RootCertStore {',1)
    old='''            roots: webpki_roots::TLS_SERVER_ROOTS.to_vec(),
        };
        let config'''
    new='''            roots: webpki_roots::TLS_SERVER_ROOTS.to_vec(),
        };
        if let Some(cert) = sprint005_fixture_ca(host)? {
            roots.add(rustls::pki_types::CertificateDer::from(cert)).map_err(|_| "Fixture CA rejected")?;
        }
        let config'''
    assert old in after;after=after.replace(old,new,1)
    rel='apps/mail/host-service/src/network.rs'
    (HERE/'tls-fixture.patch').write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel)))
    (HERE/'tls-patch-identity.json').write_text(json.dumps({'before_sha256':record['sha256'],'after_sha256':hashlib.sha256(after.encode()).hexdigest(),'scope':'proposal only; Root applies/builds isolated Host','tls_chain_name_verifier_unchanged':True,'compiled':False},indent=2)+'\n')
    return after

if __name__=='__main__':main()
