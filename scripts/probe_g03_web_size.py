#!/usr/bin/env python3
"""Measure one approved public HTML response without logging its body."""

import argparse
import json
import sys
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
from muse_capabilities import _PinnedHTTPS, _public_address, _public_url


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    args = parser.parse_args()
    url, host, target = _public_url(args.url)
    connection = _PinnedHTTPS(host, _public_address(host))
    try:
        connection.request("GET", target, headers={"Host": host, "User-Agent": "MuseLocalAgent/0.1",
                                                   "Accept": "text/html,text/plain", "Accept-Encoding": "identity"})
        response = connection.getresponse()
        encoding = response.getheader("Content-Encoding", "")
        content_type = response.getheader("Content-Type", "")
        length_header = response.getheader("Content-Length", "")
        raw = response.read(1024 * 1024 + 1)
    finally:
        connection.close()
    decoded_size = None
    if len(raw) <= 1024 * 1024:
        if encoding == "gzip":
            decoder = zlib.decompressobj(zlib.MAX_WBITS + 16)
            decoded = decoder.decompress(raw, 4 * 1024 * 1024 + 1)
            decoded_size = len(decoded) if decoder.eof and not decoder.unconsumed_tail else "over_4MiB_or_incomplete"
        elif encoding in {"", "identity"}:
            decoded_size = len(raw)
    print(json.dumps({"url": url, "http_status": response.status, "content_type": content_type,
                      "content_encoding": encoding or "identity", "content_length_header": length_header,
                      "raw_bytes_capped_at_1MiB": len(raw), "decoded_bytes": decoded_size}, ensure_ascii=False))


if __name__ == "__main__":
    main()
