#!/usr/bin/env python3
"""Read fixed SDK source and emit manual Mail request data; never call Host."""
import argparse
import hashlib
import json
from pathlib import Path
import re

PINS = {
    "apps/mail/host-service/src/lib.rs": "724c7d7faee03d1303b8caf20b33e6958f385a03f01bf29a92a704a477fcbf7c",
    "apps/mail/host-service/src/public_review.rs": "68b77eb1d9a0438f8e20e7ad333a7c8d3dcfb412733f99fc8fb2309418bdc292",
    "apps/mail/host-service/src/drafts.rs": "1b8dc404dd90a23e8ce59c4c5147dda9ca154a0900fa9f49cba70e852a039987",
    "apps/mail/host-service/src/vault.rs": "35d1fffc17d086dab55fdc87c2424ed3e42df5a5732eef5c0b18cc7509c6c91a",
    "apps/mail/host-service/src/network.rs": "c47bfbd7529a88fda95bd24912bbb2fb0932a18c6726f45526cb3b6ae781ddba",
    "crates/shell/src/connected_review.rs": "4ab475500052d01eaff30a9409c16c9d9ba594216580989440a94ccd14cd5726",
    "crates/shell/src/apps.rs": "a523dcaebee3ab84c7308a8f08327701926d75f7e07705e4535984574158090b",
    ".sources/makepad/platform/src/remote.rs": "05630f12ee87d8926d7cd90fb72987f9e2cac6b828965852ae7e0a28eca84d5b"
}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sdk', type=Path, required=True)
    p.add_argument('--account', help='ID returned by the SAME foreground app mail.accounts')
    p.add_argument('--to', default='owner@example.invalid', help='Replace with the authorized owner address before UI use')
    p.add_argument('--compose-id', help='Only the actual mail.compose response identity')
    p.add_argument('--revision', type=int, help='Only the actual mail.compose response revision')
    p.add_argument('--mail-dir', type=Path, help='Optional profile path; derive naming only, no contents read')
    a = p.parse_args()
    observed = {}
    for name, expected in PINS.items():
        actual = hashlib.sha256((a.sdk / name).read_bytes()).hexdigest()
        observed[name] = actual
        if actual != expected:
            p.error('Fixed SDK source drift: ' + name)
    if a.account is not None and not a.account.strip():
        p.error('account must be a nonempty ID from this app')
    if (a.compose_id is None) != (a.revision is None):
        p.error('compose-id and revision must be supplied together')
    if a.compose_id is not None:
        if not a.account or not re.fullmatch(r'compose-[A-Za-z0-9-]+', a.compose_id) or len(a.compose_id) > 96 or a.revision < 1:
            p.error('existing composer requires account, a valid compose-ID, and positive revision')
    if not a.to.isascii() or len(a.to) > 254 or a.to.count('@') != 1 or a.to.startswith('@') or a.to.endswith('@') or any(c.isspace() or ord(c) < 32 or ord(c) == 127 or c in '<>,;' for c in a.to):
        p.error('to must be one ASCII email address')
    result = {'status': 'SOURCE_VERIFIED_LIVE_NOT_EXECUTED', 'source_sha256': observed,
              'requests_executed': 0, 'accounts': {'method': 'mail.accounts', 'args': {}},
              'note': 'Data only. Central owns UI. Review must be manually cancelled; never activate Approve & Send.'}
    if a.account:
        fields = {'account': a.account, 'to': a.to,
                  'subject': 'MUSE-MAIL-PREFLIGHT-CANCEL-20261011',
                  'body': 'MUSE-MAIL-PREFLIGHT-CANCEL-20261011\n仅核对官方草稿与原生取消；本轮不发送。'}
        result['list'] = {'method': 'mail.list', 'args': {'account': a.account, 'folder': 'INBOX', 'offset': 0, 'limit': 1}}
        if a.compose_id is None:
            result['compose'] = {'method': 'mail.compose', 'args': fields}
            result['next'] = 'Bind actual compose_id/revision and exact text before generating status/review request.'
        else:
            result['compose_status'] = {'method': 'mail.compose_status', 'args': {'account': a.account, 'compose_id': a.compose_id}}
            result['review_cancel_only'] = {'method': 'mail.review_send', 'args': dict(fields, compose_id=a.compose_id, expected_revision=a.revision)}
            result['next'] = 'Use review only if these exact fields equal the stored draft; cancel using Back to editing, then reread compose_status.'
    if a.mail_dir:
        canonical = a.mail_dir.resolve()
        result['keychain_naming_only'] = {'service': 'OctoSense Mail ' + hashlib.sha256(str(canonical).encode()).hexdigest()[:12],
                                         'account': 'SHA256(host + newline + username)[:24]',
                                         'credential_accessed': False}
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
