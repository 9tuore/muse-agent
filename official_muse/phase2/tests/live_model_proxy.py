"""Observe synthetic LIVE model tests without recording headers or credentials.

This localhost relay forwards actual requests to the existing keyless local
model. It changes neither prompts nor replies. Evidence contains role order,
content hashes and synthetic-test text only; other content is redacted.
"""

import argparse
import hashlib
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen


QUESTIONS = {
    "请记住测试代号 MUSE-3147，不要解释。",
    "刚才的测试代号是什么？",
    "不要再重复完整代号，只告诉我其中有几位数字。",
    "记住代号 TEST-9082。",
    "记住验证码 MUSE-8427，只用于这次测试。",
    "刚才的验证码是什么？",
    "不要再重复验证码，告诉我它有几位数字。",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8081)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    args.evidence.parent.mkdir(parents=True, exist_ok=True)
    if args.evidence.exists():
        raise FileExistsError(args.evidence)

    class Relay(BaseHTTPRequestHandler):
        def log_message(self, *unused):
            pass

        def do_POST(self):
            if self.path != "/v1/chat/completions":
                self.send_error(404)
                return
            body = self.rfile.read(int(self.headers.get("Content-Length", "0")))
            payload = json.loads(body)
            turns = []
            for turn in payload.get("messages", []):
                content = str(turn.get("content", ""))
                visible = content if content in QUESTIONS else "[redacted]"
                turns.append({"role": turn.get("role"), "content": visible,
                              "characters": len(content),
                              "sha256": hashlib.sha256(content.encode()).hexdigest()})
            with args.evidence.open("a", encoding="utf-8") as evidence:
                evidence.write(json.dumps({"messages": turns}, ensure_ascii=False) + "\n")
            request = Request("http://127.0.0.1:8080" + self.path, data=body,
                              headers={"Content-Type": "application/json"})
            try:
                response = urlopen(request, timeout=125)
                status, answer = response.status, response.read()
            except HTTPError as error:
                status, answer = error.code, error.read()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(answer)))
            self.end_headers()
            self.wfile.write(answer)

    print(f"keyless synthetic-test relay on 127.0.0.1:{args.port}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", args.port), Relay).serve_forever()


if __name__ == "__main__":
    main()
