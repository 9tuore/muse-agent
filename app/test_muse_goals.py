import copy
import hashlib
import json
import sqlite3
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from memory_store import MemoryStore
from muse_capabilities import CapabilityExecutor
from muse_goals import GoalService, GoalValidationError, _comparison_hash, _page_excerpt, parse_plan, validate_plan
from muse_search_policy import page_relevance, select_results, topic_terms


def spec_for(text):
    return {
        "schema_version": "muse.goal/0.1", "goal_id": "model-id", "revision": 1,
        "title": "准备" + text[:30], "objective": text, "priority": "normal",
        "deadline": None, "timezone": "Asia/Shanghai",
        "triggers": [{"kind": "interval", "every_seconds": 60},
                     {"kind": "event", "topic": "file.changed", "source_ref": "resource:test-notes"}],
        "context_refs": [{"ref": "resource:test-notes", "purpose": "隔离测试资料"}],
        "steps": [
            {"id": "compose", "capability": "model.compose", "args": {"instruction": "给出有提纲标题的短文"}},
            {"id": "save", "capability": "workspace.write_artifact",
             "args": {"relative_path": "notes/speech.md", "content_from_step": "compose"},
             "input_refs": ["step:compose"]},
        ],
        "permissions": {"capabilities": ["model.compose", "workspace.write_artifact"],
                        "resource_refs": ["resource:test-notes", "resource:workspace/notes/speech.md"], "send_message": "deny",
                        "send_rule_ref": None, "cloud_context": "none"},
        "budget": {"period": "goal", "money": {"mode": "capped", "currency": "CNY", "amount": 0},
                   "max_model_tokens": 2000, "max_searches": 0, "max_run_seconds": 180},
        "verification": [{"type": "file_content", "target_ref": "step:save",
                          "expected": {"nonempty": True, "sections": ["提纲"]}}],
        "notify": {"on_major_update": True, "on_need_decision": True, "on_complete": True},
        "failure_policy": {"max_retries": 2, "escalate": True},
    }


def _reviewed_decision(service, event):
    digest = service.store.get(event["goal_id"])["digest"]
    return service.handle({**event, "plan_digest": digest})


class _FixtureModel:
    def __init__(self):
        self.calls = []

    def generate(self, prompt, *, purpose, require_json=False, max_tokens=512, goal_id=None):
        self.calls.append({"purpose": purpose, "goal_id": goal_id, "prompt": prompt})
        if purpose == "goal_plan":
            text = prompt.split("用户目标：", 1)[1]
            spec = spec_for(text)
            if "准备" in text:
                spec["triggers"] = spec["triggers"][:1]
            output = json.dumps(spec, ensure_ascii=False)
        else:
            output = "提纲\n1. 来自隔离测试的演讲内容"
        return {"ok": True, "status": "COMPLETED", "text": output, "provider": "fixture-model",
                "model": "fixture", "usage": {"total_tokens": 12, "cost": "unknown"}}


class _CompactEventModel:
    def generate(self, prompt, *, purpose, require_json=False, max_tokens=512, goal_id=None):
        if purpose == "goal_plan":
            output = json.dumps({"title": "测试资料更新", "objective": "跟踪合成文件变化", "kind": "file_monitor",
                                 "artifact": "notes/update.md", "content": "初稿", "interval_seconds": 60}, ensure_ascii=False)
        else:
            marker = "first.txt" if "first.txt" in prompt else "second.txt" if "second.txt" in prompt else "无事件"
            output = "提纲\n获授权目录事件：" + marker + "，仅根据事件元数据整理。"
        return {"ok": True, "status": "COMPLETED", "text": output, "provider": "fixture-model",
                "model": "fixture", "usage": {"total_tokens": 20, "cost": "unknown"}}


class _GenericArtifactModel(_CompactEventModel):
    def generate(self, prompt, *, purpose, require_json=False, max_tokens=512, goal_id=None):
        if purpose == "goal_plan":
            return {"ok": True, "status": "COMPLETED", "text": json.dumps({
                "title": "AI 任务验证演讲", "objective": "准备演讲提纲", "kind": "speech",
                "artifact": "md.md", "content": "提纲：第一点解释目标与任务范围；第二点解释验证方法、证据记录和来源标注，作为合成演讲初稿，后续仍需人工核对每个论点。",
                "interval_seconds": 60}, ensure_ascii=False),
                "provider": "fixture-model", "model": "fixture", "usage": {"total_tokens": 20, "cost": "unknown"}}
        return super().generate(prompt, purpose=purpose, require_json=require_json,
                                max_tokens=max_tokens, goal_id=goal_id)


class _TransientEventModel(_CompactEventModel):
    def __init__(self):
        self.step_calls = 0

    def generate(self, prompt, *, purpose, require_json=False, max_tokens=512, goal_id=None):
        if purpose == "goal_step":
            self.step_calls += 1
            if self.step_calls == 1:
                return {"ok": False, "status": "UNAVAILABLE", "error": "timeout", "route": "local",
                        "usage": {"total_tokens": 25}}
        return super().generate(prompt, purpose=purpose, require_json=require_json,
                                max_tokens=max_tokens, goal_id=goal_id)


class _RemoteLocalSlotModel(_CompactEventModel):
    def get_settings(self):
        return {"mode": "local", "profiles": {"local-profile": {"endpoint": "https://model.example.test/v1/chat/completions"}},
                "active_local": "local-profile", "active_high": "local-profile", "purpose_routes": {}}


class _RemoteMoneyModel(_FixtureModel):
    def get_settings(self):
        return {"mode": "high", "profiles": {"remote-profile": {
            "endpoint": "https://model.example.test/v1/chat/completions"}},
            "active_local": "remote-profile", "active_high": "remote-profile", "purpose_routes": {}}


class _TightBudgetModel(_FixtureModel):
    def generate(self, prompt, *, purpose, require_json=False, max_tokens=512, goal_id=None):
        result = super().generate(prompt, purpose=purpose, require_json=require_json,
                                  max_tokens=max_tokens, goal_id=goal_id)
        if purpose == "goal_plan":
            spec = json.loads(result["text"])
            spec["budget"]["max_model_tokens"] = 12
            result["text"] = json.dumps(spec, ensure_ascii=False)
        return result


class _ShortContentModel:
    def generate(self, prompt, *, purpose, require_json=False, max_tokens=512, goal_id=None):
        if purpose == "goal_plan":
            content = json.dumps({"title": "演讲资料", "objective": "准备演讲资料提纲", "kind": "speech",
                                  "artifact": "notes/speech.md", "content": "先写提纲", "interval_seconds": 60},
                                 ensure_ascii=False)
        else:
            content = "简短草稿"
        return {"ok": True, "status": "COMPLETED", "text": content, "provider": "fixture",
                "model": "fixture", "usage": {"total_tokens": 12}}


class _FailedRemoteModel(_FixtureModel):
    def __init__(self):
        super().__init__()
        self.step_calls = 0

    def generate(self, prompt, *, purpose, require_json=False, max_tokens=512, goal_id=None):
        if purpose == "goal_step":
            self.step_calls += 1
            return {"ok": False, "status": "UNAVAILABLE", "error": "timeout", "route": "high",
                    "usage": {"total_tokens": 20}}
        return super().generate(prompt, purpose=purpose, require_json=require_json,
                                max_tokens=max_tokens, goal_id=goal_id)


class _ResearchModel:
    def __init__(self, fail_step=False, kind="research", english_step=False):
        self.fail_step = fail_step
        self.kind = kind
        self.english_step = english_step
        self.step_calls = 0
        self.step_prompt = ""

    def generate(self, prompt, *, purpose, require_json=False, max_tokens=512, goal_id=None):
        if purpose == "goal_plan":
            return {"ok": True, "text": json.dumps({
                "title": "公开资料追踪", "objective": "整理获授权网址的变化", "kind": self.kind,
                "artifact": "notes/research.md", "content": "初稿", "interval_seconds": 60}, ensure_ascii=False),
                "provider": "fixture", "model": "fixture", "usage": {"total_tokens": 20}}
        self.step_calls += 1
        self.step_prompt = prompt
        if self.fail_step:
            return {"ok": False, "status": "UNAVAILABLE", "error": "timeout", "route": "local",
                    "usage": {"total_tokens": 20}}
        content = ("提纲：1. Python is a language. 2. Documentation is available." if self.english_step else
                   "提纲：第一，概括公开资料的主要内容；第二，核对来源网址和变更信息。")
        return {"ok": True, "status": "COMPLETED", "text": content, "route": "local",
                "provider": "fixture", "model": "fixture", "usage": {"total_tokens": 20}}


class _TemporalResearchModel(_ResearchModel):
    def generate(self, prompt, *, purpose, require_json=False, max_tokens=512, goal_id=None):
        result = super().generate(prompt, purpose=purpose, require_json=require_json,
                                  max_tokens=max_tokens, goal_id=goal_id)
        if purpose == "goal_step" and result.get("ok"):
            result["text"] = "提纲：Python 3.13.0 是最新主要版本；后续资料请核对原始公告。"
        return result


class _TextEditRecipeExecutor:
    def __init__(self, workspace, *, bad_receipt=False):
        self.workspace = workspace
        self.bad_receipt = bad_receipt
        self.enabled_approval_id = None
        self.calls = 0

    def execute(self, call, *, approved, context=None):
        self.calls += 1
        if (not approved or self.enabled_approval_id != context.get("approval_id") or
            call["capability"] != "app.recipe" or
            not call["action_id"].startswith(context.get("run_id", "missing-run") + ":")):
            return {"ok": False, "status": "BLOCKED", "error": "recipe_not_enabled"}
        args = call["args"]
        data = args["content"].encode("utf-8")
        (self.workspace / args["relative_path"]).write_bytes(data)
        return {"ok": True, "status": "COMPLETED", "capability": "app.recipe", "output": {
            "recipe_id": args["recipe_id"], "revision": args["revision"],
            "relative_path": args["relative_path"], "window_title": args["window_title"],
            "bytes": len(data), "sha256": "0" * 64 if self.bad_receipt else hashlib.sha256(data).hexdigest(),
        }, "verification": {"ax_value_matches": True, "disk_readback_matches": True,
                             "helper_trusted": True}}


class _AppHealthExecutor:
    def __init__(self, *, trusted=True):
        self.trusted = trusted
        self.calls = 0

    def execute(self, call, *, approved, context=None):
        self.calls += 1
        if not approved or context["permissions"]["resource_refs"] != ["app:com.apple.TextEdit"]:
            return {"ok": False, "status": "BLOCKED", "error": "app_outside_approved_scope"}
        return {"ok": True, "status": "COMPLETED", "capability": "system.app_health",
                "output": {"bundle_id": call["args"]["bundle_id"], "running": True,
                           "pids": [1234], "observed_at": datetime.now(timezone.utc).isoformat()},
                "verification": {"source": "NSRunningApplication" if self.trusted else "unknown",
                                 "read_only": True, "shell_used": False}}


class _ResearchExecutor:
    def __init__(self, workspace):
        self.real = CapabilityExecutor(workspace)
        self.body = "第一版"
        self.reads = 0

    def execute(self, call, *, approved, context=None):
        if call["capability"] == "web.read":
            self.reads += 1
            return {"ok": True, "status": "COMPLETED", "capability": "web.read",
                    "output": {"title": "合成公开页", "text": self.body,
                               "source_url": "https://example.test/brief",
                               "retrieved_at": datetime.now(timezone.utc).isoformat(),
                               "content_sha256": hashlib.sha256(self.body.encode()).hexdigest()}}
        return self.real.execute(call, approved=approved, context=context)


class _MultiResearchExecutor(_ResearchExecutor):
    def __init__(self, workspace):
        super().__init__(workspace)
        self.bodies = {
            "https://example.test/one": "第一份资料正文\nLast updated: 2026-09-28 12:00",
            "https://example.test/two": "第二份资料正文",
            "https://example.test/three": "第三份资料正文",
        }

    def execute(self, call, *, approved, context=None):
        if call["capability"] == "web.read":
            self.reads += 1
            url = call["args"]["url"]
            body = self.bodies[url]
            return {"ok": True, "status": "COMPLETED", "capability": "web.read",
                    "output": {"title": "合成公开页", "text": body, "source_url": url,
                               "retrieved_at": datetime.now(timezone.utc).isoformat(),
                               "content_sha256": hashlib.sha256(body.encode()).hexdigest()}}
        return self.real.execute(call, approved=approved, context=context)


class _UncertainWriteExecutor(_ResearchExecutor):
    def execute(self, call, *, approved, context=None):
        if call["capability"] == "workspace.write_artifact":
            return {"ok": False, "status": "RESULT_UNKNOWN", "capability": call["capability"]}
        return super().execute(call, approved=approved, context=context)


class _BlockedReadExecutor(_ResearchExecutor):
    def execute(self, call, *, approved, context=None):
        if call["capability"] == "web.read":
            return {"ok": False, "status": "BLOCKED", "error": "http_status_403",
                    "capability": "web.read", "output": {}}
        return super().execute(call, approved=approved, context=context)


class _SearchResearchModel(_ResearchModel):
    def generate(self, prompt, *, purpose, require_json=False, max_tokens=512, goal_id=None):
        if purpose == "goal_plan":
            return {"ok": True, "text": json.dumps({
                "title": "Python asyncio 资料", "objective": "持续整理 Python asyncio 的公开资料",
                "kind": "research", "search_query": "Python asyncio", "artifact": "notes/research.md",
                "content": "初稿", "interval_seconds": 60}, ensure_ascii=False),
                "provider": "fixture", "model": "fixture", "usage": {"total_tokens": 20}}
        return super().generate(prompt, purpose=purpose, require_json=require_json,
                                max_tokens=max_tokens, goal_id=goal_id)


class _GenericSuffixSearchModel(_SearchResearchModel):
    def generate(self, prompt, *, purpose, require_json=False, max_tokens=512, goal_id=None):
        result = super().generate(prompt, purpose=purpose, require_json=require_json,
                                  max_tokens=max_tokens, goal_id=goal_id)
        if purpose == "goal_plan":
            plan = json.loads(result["text"])
            plan.update(title="Python 3.13 公开资料", objective="持续整理 Python 3.13 的公开资料",
                        search_query="Python 3.13 公开资料")
            result["text"] = json.dumps(plan, ensure_ascii=False)
        return result


class _SearchResearchExecutor(_ResearchExecutor):
    def __init__(self, workspace, *, insufficient=False, historical=False,
                 blocked_urls=(), irrelevant_urls=(), truncated_urls=()):
        super().__init__(workspace)
        self.insufficient = insufficient
        self.historical = historical
        self.blocked_urls = set(blocked_urls)
        self.irrelevant_urls = set(irrelevant_urls)
        self.truncated_urls = set(truncated_urls)
        self.searches = 0
        self.read_urls = []
        self.candidates = [
            {"rank": 1, "title": "Python asyncio jobs", "url": "https://jobs.example.test/one",
             "snippet": "Hiring now", "source_id": "web:jobs"},
            {"rank": 2, "title": "Python asyncio official guide", "url": "https://docs.example.test/one",
             "snippet": "Python asyncio documentation", "source_id": "web:one"},
            {"rank": 3, "title": "Python asyncio reference", "url": "https://docs.example.test/two",
             "snippet": "Python asyncio APIs", "source_id": "web:two"},
            {"rank": 4, "title": "Python asyncio tutorial", "url": "https://docs.example.test/three",
             "snippet": "Python asyncio examples", "source_id": "web:three"},
            {"rank": 5, "title": "Python asyncio notes", "url": "https://docs.example.test/four",
             "snippet": "Python asyncio details", "source_id": "web:four"},
            {"rank": 6, "title": "Python asyncio overview", "url": "https://docs.example.test/five",
             "snippet": "Python asyncio concepts", "source_id": "web:five"},
        ]

    def execute(self, call, *, approved, context=None):
        if call["capability"] == "web.search":
            self.searches += 1
            results = self.candidates[:3] if self.insufficient else self.candidates
            return {"ok": True, "status": "COMPLETED", "capability": "web.search",
                    "output": {"query": call["args"]["query"], "search_page": "https://cn.bing.com/search?q=Python",
                               "retrieved_at": datetime.now(timezone.utc).isoformat(),
                               "content_sha256": "a" * 64, "results": results,
                               "candidate_count": len(results), "untrusted_source": True}}
        if call["capability"] == "web.read":
            url = call["args"]["url"]
            self.read_urls.append(url)
            if url.rsplit("/", 1)[-1] in self.blocked_urls:
                return {"ok": False, "status": "BLOCKED", "error": "page_too_large",
                        "capability": "web.read", "output": {}}
            body = ("Python asyncio guide is retired and unmaintained" if self.historical and
                    url.rsplit("/", 1)[-1] in {"one", "two", "three"} else
                    "Unrelated gardening notes about roses" if url.rsplit("/", 1)[-1] in self.irrelevant_urls else
                    "Python asyncio documentation explains cooperative tasks and event loops.")
            truncated = url.rsplit("/", 1)[-1] in self.truncated_urls
            return {"ok": True, "status": "COMPLETED", "capability": "web.read",
                    "output": {"title": "Python asyncio guide", "text": body, "source_url": url,
                               "retrieved_at": datetime.now(timezone.utc).isoformat(),
                               "content_sha256": hashlib.sha256(body.encode()).hexdigest(),
                               "text_truncated": truncated,
                               "extracted_text_chars": 67361 if truncated else len(body)}}
        return self.real.execute(call, approved=approved, context=context)


class _BrowserResearchModel(_ResearchModel):
    def generate(self, prompt, *, purpose, require_json=False, max_tokens=512, goal_id=None):
        if purpose == "goal_plan":
            return {"ok": True, "text": json.dumps({
                "title": "Python packaging 浏览器资料", "objective": "用 Edge 浏览器在 Python.org 搜索 packaging 并整理资料",
                "kind": "browser_research", "search_query": "packaging",
                "artifact": "notes/browser-research.md", "content": "初稿", "interval_seconds": 60}, ensure_ascii=False),
                "provider": "fixture", "model": "fixture", "usage": {"total_tokens": 20}}
        return super().generate(prompt, purpose=purpose, require_json=require_json,
                                max_tokens=max_tokens, goal_id=goal_id)


class _BrowserResearchExecutor(_ResearchExecutor):
    def __init__(self, workspace, *, blocked=False):
        super().__init__(workspace)
        self.blocked = blocked
        self.browser_calls = 0

    def execute(self, call, *, approved, context=None):
        if call["capability"] == "browser.research":
            self.browser_calls += 1
            if self.blocked:
                return {"ok": False, "status": "WAITING_USER", "error": "gui_control_not_granted",
                        "capability": "browser.research", "output": {}}
            sources = []
            for number in range(1, 4):
                body = "Python packaging guide explains current packages and distribution."
                sources.append({"rank": number, "title": f"Python packaging guide {number}",
                                "source_url": f"https://www.python.org/doc/packaging/{number}",
                                "text": body, "retrieved_at": datetime.now(timezone.utc).isoformat(),
                                "content_sha256": hashlib.sha256(body.encode()).hexdigest(),
                                "click_transport": "cdp_mouse", "untrusted_source": True})
            return {"ok": True, "status": "COMPLETED", "capability": "browser.research",
                    "output": {"query": "packaging", "engine": "python.org", "sources": sources,
                               "quality": "UNREVIEWED"},
                    "verification": {"clicked_pages": 3, "readback_pages": 3}}
        return super().execute(call, approved=approved, context=context)


class MuseGoalTests(unittest.TestCase):
    def test_no_url_search_drops_generic_suffix_before_approval(self):
        generic_results = [
            {"url": "https://www.python.org/", "title": "Welcome to Python.org",
             "snippet": "The mission of the Python Software Foundation"},
            {"url": "https://www.runoob.com/python/python-tutorial.html",
             "title": "Python 基础教程", "snippet": "Python 是一种编程语言"},
        ]
        self.assertEqual(select_results("Python 3.13 公开资料", generic_results, limit=5), [])
        with tempfile.TemporaryDirectory() as tmp:
            service = GoalService(Path(tmp), _GenericSuffixSearchModel(), _ResearchExecutor(Path(tmp)))
            draft = service.handle({"type": "goal_propose", "request_id": "generic-suffix",
                                    "text": "持续整理 Python 3.13 公开资料"})
            self.assertEqual(draft["status"], "DRAFT", draft)
            search = next(step for step in draft["plan"]["steps"]
                          if step["capability"] == "web.search")
            self.assertEqual(search["args"]["query"], "Python 3.13")
            expected_ref = "resource:public-search-" + hashlib.sha256(b"Python 3.13").hexdigest()[:16]
            self.assertIn(expected_ref, draft["plan"]["permissions"]["resource_refs"])
            self.assertNotIn("公开资料", search["args"]["query"])

    def test_textedit_app_health_is_approved_one_shot_read_only_goal(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            model = _FixtureModel()
            executor = _AppHealthExecutor()
            service = GoalService(workspace, model, executor)
            draft = service.handle({"type": "goal_propose", "request_id": "textedit-health",
                                    "text": "检查 TextEdit 是否正在运行"})
            self.assertEqual(draft["status"], "DRAFT", draft)
            self.assertEqual(model.calls, [])
            self.assertEqual(executor.calls, 0)
            self.assertEqual(draft["plan"]["permissions"]["capabilities"], ["system.app_health"])
            self.assertEqual(draft["plan"]["steps"], [{"id": "check_textedit",
                "capability": "system.app_health", "args": {"bundle_id": "com.apple.TextEdit"}}])
            bad = copy.deepcopy(draft["plan"])
            bad["steps"][0]["args"]["bundle_id"] = "com.apple.Finder"
            with self.assertRaises(GoalValidationError):
                validate_plan(bad)
            self.assertEqual(service.tick(), [])
            approved = service.handle({"type": "goal_decide", "goal_id": draft["goal_id"],
                                       "revision": 1, "decision": "approve",
                                       "plan_digest": draft["plan_digest"]})
            self.assertEqual(approved["status"], "ACTIVE")
            result = service.tick()[0]
            self.assertEqual(result["status"], "COMPLETED", result)
            self.assertEqual(result["app_health"]["pids"], [1234])
            self.assertEqual(result["result_card"]["next_step"], "TextEdit 正在运行")
            self.assertEqual(executor.calls, 1)
            self.assertEqual(service.tick(), [])

    def test_all_goal_approvals_require_exact_reviewed_digest(self):
        with tempfile.TemporaryDirectory() as tmp:
            service = GoalService(Path(tmp), _FixtureModel(), _AppHealthExecutor())
            draft = service.handle({"type": "goal_propose", "request_id": "health-digest",
                                    "text": "检查 TextEdit 运行状态"})
            for digest in (None, "0" * 64):
                event = {"type": "goal_decide", "goal_id": draft["goal_id"],
                         "revision": 1, "decision": "approve"}
                if digest is not None:
                    event["plan_digest"] = digest
                rejected = service.handle(event)
                self.assertEqual(rejected["error"], "plan_digest_required_or_changed")
                self.assertIsNone(service.store.decide(draft["goal_id"], 1, "approve",
                                                        reviewed_digest=digest))
                self.assertEqual(service.store.get(draft["goal_id"])["status"], "draft")
            with sqlite3.connect(Path(tmp) / "memory.sqlite3") as db:
                self.assertEqual(db.execute("SELECT COUNT(*) FROM muse_goal_approvals").fetchone()[0], 0)
            approved = service.handle({"type": "goal_decide", "goal_id": draft["goal_id"],
                                       "revision": 1, "decision": "approve",
                                       "plan_digest": draft["plan_digest"]})
            self.assertEqual(approved["status"], "ACTIVE")

    def test_textedit_app_health_rejects_untrusted_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            service = GoalService(Path(tmp), _FixtureModel(), _AppHealthExecutor(trusted=False))
            draft = service.handle({"type": "goal_propose", "request_id": "health-unknown-source",
                                    "text": "检查 TextEdit 运行状态"})
            _reviewed_decision(service, {"type": "goal_decide", "goal_id": draft["goal_id"],
                            "revision": 1, "decision": "approve"})
            result = service.tick()[0]
            self.assertEqual(result["status"], "WAITING_USER")
            self.assertEqual(result["error"], "verification_failed")
            self.assertEqual(service.handle({"type": "goal_control", "goal_id": draft["goal_id"],
                                             "action": "retry"})["status"], "REJECTED")

    def test_textedit_recipe_requires_goal_approval_and_independent_readback(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            (workspace / "notes").mkdir()
            target = workspace / "notes/Muse-Test-Alpha.txt"
            target.write_text("before\n", encoding="utf-8")
            recipe = {"recipe_id": "textedit.synthetic_save.fixture", "revision": 1,
                      "digest": "a" * 64, "target_bundle_id": "com.apple.TextEdit",
                      "window_title": target.name, "relative_path": "notes/Muse-Test-Alpha.txt",
                      "content": "Muse synthetic Goal-bound output A.\n"}
            model = _FixtureModel()
            executor = _TextEditRecipeExecutor(workspace)
            service = GoalService(workspace, model, executor)
            event = {"type": "goal_propose", "request_id": "textedit-recipe-a",
                     "text": "用 TextEdit 保存合成测试文件", "recipe": recipe}
            draft = service.handle(event)
            self.assertEqual(draft["status"], "DRAFT", draft)
            self.assertEqual(model.calls, [])
            self.assertEqual(executor.calls, 0)
            self.assertEqual(target.read_text(encoding="utf-8"), "before\n")
            self.assertEqual(draft["plan"]["steps"], [
                {"id": "save_textedit", "capability": "app.recipe", "args": recipe}])
            self.assertEqual(service.tick(), [])
            approved = _reviewed_decision(service, {"type": "goal_decide", "goal_id": draft["goal_id"],
                                       "revision": 1, "decision": "approve"})
            self.assertEqual(approved["status"], "ACTIVE")
            self.assertEqual(executor.calls, 0)
            executor.enabled_approval_id = approved["approval_id"]
            result = service.tick()[0]
            self.assertEqual(result["status"], "COMPLETED", result)
            self.assertEqual(result["verification"], "CHECKS_PASSED")
            self.assertEqual(target.read_text(encoding="utf-8"), recipe["content"])
            self.assertEqual(executor.calls, 1)
            self.assertEqual(service.tick(), [])

    def test_textedit_recipe_fails_closed_on_invalid_scope_or_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            (workspace / "notes").mkdir()
            target = workspace / "notes/Muse-Test-Alpha.txt"
            target.write_text("before\n", encoding="utf-8")
            recipe = {"recipe_id": "textedit.synthetic_save.fixture", "revision": 1,
                      "digest": "a" * 64, "target_bundle_id": "com.apple.TextEdit",
                      "window_title": target.name, "relative_path": "notes/Muse-Test-Alpha.txt",
                      "content": "Muse synthetic Goal-bound output A.\n"}
            executor = _TextEditRecipeExecutor(workspace, bad_receipt=True)
            service = GoalService(workspace, _FixtureModel(), executor)
            text = "用 TextEdit 保存合成测试文件"
            self.assertEqual(service.handle({"type": "goal_propose", "request_id": "no-recipe",
                                             "text": text})["status"], "NEEDS_SCOPE")
            for index, (field, value) in enumerate((
                ("digest", "wrong"), ("target_bundle_id", "com.apple.Finder"),
                ("window_title", "Another.txt"), ("relative_path", "notes/missing.txt"),
            )):
                bad = dict(recipe, **{field: value})
                response = service.handle({"type": "goal_propose", "request_id": f"bad-recipe-{index}",
                                           "text": text, "recipe": bad})
                self.assertEqual(response["status"], "INVALID_PLAN", response)
            linked = workspace / "notes/linked.txt"
            linked.symlink_to(target)
            response = service.handle({"type": "goal_propose", "request_id": "symlink-recipe",
                                       "text": text, "recipe": dict(recipe, relative_path="notes/linked.txt",
                                                                 window_title="linked.txt")})
            self.assertEqual(response["status"], "INVALID_PLAN")
            arbitrary = workspace / "notes/arbitrary.txt"
            arbitrary.write_text("before\n", encoding="utf-8")
            response = service.handle({"type": "goal_propose", "request_id": "arbitrary-target",
                                       "text": text, "recipe": dict(recipe, relative_path="notes/arbitrary.txt",
                                                                 window_title="arbitrary.txt")})
            self.assertEqual(response["status"], "INVALID_PLAN")
            draft = service.handle({"type": "goal_propose", "request_id": "bad-output",
                                    "text": text, "recipe": recipe})
            approved = _reviewed_decision(service, {"type": "goal_decide", "goal_id": draft["goal_id"],
                                       "revision": 1, "decision": "approve"})
            executor.enabled_approval_id = approved["approval_id"]
            result = service.tick()[0]
            self.assertEqual(result["status"], "WAITING_USER")
            self.assertEqual(result["error"], "recipe_result_mismatch")
            self.assertEqual(service.handle({"type": "goal_control", "goal_id": draft["goal_id"],
                                             "action": "retry"})["status"], "REJECTED")
            self.assertEqual(executor.calls, 1)

    def test_research_report_flags_unverified_temporal_comparisons(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            service = GoalService(workspace, _TemporalResearchModel(), _ResearchExecutor(workspace))
            draft = service.handle({"type": "goal_propose", "request_id": "temporal-claim",
                                    "text": "持续整理 https://example.org/ 的公开资料"})
            _reviewed_decision(service, {"type": "goal_decide", "goal_id": draft["goal_id"],
                            "revision": 1, "decision": "approve"})
            result = service.tick()[0]
            self.assertEqual(result["status"], "COMPLETED")
            self.assertEqual(result["fact_verification"], "NOT_VERIFIED")
            report = (workspace / "notes/research-v1.md").read_text(encoding="utf-8")
            self.assertIn("模型草稿含时效或比较用语（最新）", report)
            self.assertIn("未核验前勿对外引用", report)

    def test_browser_research_is_approved_goal_step_with_three_source_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            executor = _BrowserResearchExecutor(workspace)
            service = GoalService(workspace, _BrowserResearchModel(), executor)
            draft = service.handle({"type": "goal_propose", "request_id": "browser-goal",
                                    "text": "用 Edge 浏览器在 Python.org 搜索 packaging、点击并阅读三篇页面"})
            self.assertEqual(draft["status"], "DRAFT", draft)
            spec = draft["plan"]
            self.assertEqual(spec["steps"][0]["capability"], "browser.research")
            self.assertEqual(spec["steps"][0]["args"], {
                "query": "packaging", "engine": "python.org", "max_pages": 3})
            self.assertTrue({"app:com.microsoft.edgemac", "site:python.org"} <=
                            set(spec["permissions"]["resource_refs"]))
            self.assertEqual(executor.browser_calls, 0)
            _reviewed_decision(service, {"type": "goal_decide", "goal_id": draft["goal_id"],
                            "revision": 1, "decision": "approve"})
            run = service.tick()[0]
            self.assertEqual(run["status"], "COMPLETED", run.get("error"))
            self.assertEqual(executor.browser_calls, 1)
            self.assertEqual(len(run["receipts"][-1]["output"]["sources"]), 3)
            report = (workspace / "notes/browser-research-v1.md").read_text(encoding="utf-8")
            self.assertIn("## 来源清单", report)
            self.assertIn("https://www.python.org/doc/packaging/3", report)
            self.assertIn("事实待核验", report)
            self.assertEqual(service.handle({"type": "goal_tick"})["results"], [])

    def test_browser_research_requires_explicit_scope_and_fails_closed_without_gui_lease(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            service = GoalService(workspace, _BrowserResearchModel(), _BrowserResearchExecutor(workspace))
            draft = service.handle({"type": "goal_propose", "request_id": "browser-missing-scope",
                                    "text": "整理 packaging 资料"})
            self.assertEqual(draft["status"], "INVALID_PLAN")
            draft = service.handle({"type": "goal_propose", "request_id": "browser-blocked",
                                    "text": "用 Edge 浏览器在 Python.org 搜索 packaging"})
            spec = copy.deepcopy(draft["plan"])
            spec["steps"][0]["args"]["engine"] = "bing"
            with self.assertRaises(GoalValidationError):
                validate_plan(spec)
            spec = copy.deepcopy(draft["plan"])
            spec["permissions"]["resource_refs"].remove("site:python.org")
            with self.assertRaises(GoalValidationError):
                validate_plan(spec)

        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            executor = _BrowserResearchExecutor(workspace, blocked=True)
            service = GoalService(workspace, _BrowserResearchModel(), executor)
            draft = service.handle({"type": "goal_propose", "request_id": "browser-no-lease",
                                    "text": "用 Edge 浏览器在 Python.org 搜索 packaging"})
            _reviewed_decision(service, {"type": "goal_decide", "goal_id": draft["goal_id"],
                            "revision": 1, "decision": "approve"})
            run = service.tick()[0]
            self.assertEqual(run["status"], "WAITING_USER")
            self.assertEqual(run["failure"]["error_code"], "gui_control_not_granted")
            self.assertFalse((workspace / "notes/browser-research-v1.md").exists())

    def test_page_excerpt_prefers_relevant_body_over_navigation_and_examples(self):
        page = ("This page displays a fallback because interactive scripts did not run.\n"
                "Search This Site and navigate through the menu to explore the website.\n"
                "Calculations are simple with Python, and expression syntax is straightforward.\n"
                "Python is a programming language that lets you work quickly.\n"
                "Python source code and installers are available for download.\n"
                "Documentation for Python, including tutorials and guides, is available online.\n"
                "Privacy policy and all rights reserved by the website operator.")
        excerpt = _page_excerpt(page, "Welcome to Python.org", "整理 Python 官方首页资料")
        self.assertTrue(excerpt.startswith("Python is a programming language"))
        self.assertIn("download", excerpt)
        self.assertIn("Documentation", excerpt)
        self.assertNotIn("fallback", excerpt)

    def test_comparison_hash_ignores_only_standalone_fetch_clock(self):
        first = {"title": "Release notes", "text": "Important release: version 2.\nLast updated: 2026-09-28 12:00"}
        second = {"title": "Release notes", "text": "Important release: version 2.\nLast updated: 2026-09-28 13:00"}
        self.assertEqual(_comparison_hash(first), _comparison_hash(second))
        second["text"] = "Important release: version 3.\nLast updated: 2026-09-28 13:00"
        self.assertNotEqual(_comparison_hash(first), _comparison_hash(second))
        first.update(text_truncated=True, content_sha256="a" * 64)
        second = dict(first, content_sha256="b" * 64)
        self.assertNotEqual(_comparison_hash(first), _comparison_hash(second))

    def test_search_policy_skips_unrelated_and_job_candidates(self):
        with tempfile.TemporaryDirectory() as tmp:
            candidates = _SearchResearchExecutor(Path(tmp)).candidates
            selected = select_results("Python asyncio", candidates, limit=3)
            self.assertEqual([item["original_index"] for item in selected], [1, 2, 3])

    def test_search_policy_requires_each_topic_term_and_preserves_search_rank(self):
        self.assertEqual(topic_terms("持续关注 GOSIM Muse 官方资料变化"), ["gosim", "muse"])
        self.assertEqual(topic_terms("Python 异步编程 最新进展"), ["python", "异步编程"])
        self.assertEqual(topic_terms("Python 3.13 发布资料"), ["python", "3.13"])
        self.assertEqual(topic_terms("2026"), [])
        self.assertFalse(page_relevance("Python 3.13", {
            "title": "Python Release 3.12", "text": "Python 3.12 release notes"})[0])
        unrelated = [{"title": "GOSIM conference", "url": "https://gosim.example.org/",
                      "snippet": "Open source community"},
                     {"title": "GOSIM Shenzhen", "url": "https://shenzhen.example.org/",
                      "snippet": "2026 event"},
                     {"title": "GOSIM global", "url": "https://global.example.org/",
                      "snippet": "Innovation meetup"}]
        self.assertEqual(select_results("GOSIM Muse", unrelated), [])
        self.assertEqual(page_relevance("GOSIM Muse", {
            "title": "GOSIM conference", "text": "GOSIM open source event"})[0], False)
        self.assertEqual(page_relevance("GOSIM Muse", {
            "title": "GOSIM Muse", "text": "GOSIM Muse is the product discussed here"})[0], True)

        ranked = [{"title": "Python asyncio guide", "url": "https://blog.example.org/asyncio",
                   "snippet": "Python asyncio tutorial and examples"},
                  {"title": "Python asyncio official guide", "url": "https://www.python.org/doc/asyncio/",
                   "snippet": "Python asyncio tutorial"},
                  {"title": "Python asyncio documentation",
                   "url": "https://docs.python.org/3/library/asyncio.html", "snippet": "asyncio APIs"}]
        self.assertEqual([item["original_index"] for item in select_results("Python asyncio", ranked)],
                         [2, 1, 0])

    def test_failed_source_reports_read_error_and_source_without_query(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            service = GoalService(workspace, _ResearchModel(), _BlockedReadExecutor(workspace))
            source = "https://example.org/guide?private=value"
            draft = service.handle({"type": "goal_propose", "request_id": "blocked-source",
                                    "text": "持续整理 " + source + " 的公开资料"})
            self.assertEqual(draft["status"], "DRAFT")
            _reviewed_decision(service, {"type": "goal_decide", "goal_id": draft["goal_id"],
                            "revision": 1, "decision": "approve"})
            result = service.tick()[0]
            self.assertEqual(result["status"], "WAITING_USER")
            self.assertEqual(result["failure"], {
                "capability": "web.read", "status": "BLOCKED", "error_code": "http_status_403",
                "source_url": "https://example.org/guide"})
            self.assertIn("http_status_403", result["error"])
            self.assertNotIn("private=value", json.dumps(result.get("failure")))
            self.assertFalse((workspace / "notes/research-v1.md").exists())

    def test_search_research_uses_selected_three_and_rejects_insufficient_or_historical(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            model, executor = _SearchResearchModel(), _SearchResearchExecutor(workspace)
            service = GoalService(workspace, model, executor)
            draft = service.handle({"type": "goal_propose", "request_id": "search-research",
                                    "text": "持续搜索并整理 Python asyncio 公开资料"})
            self.assertEqual(draft["status"], "DRAFT")
            search_step = draft["plan"]["steps"][0]
            self.assertEqual(search_step["args"], {"query": "Python asyncio", "max_results": 10})
            self.assertEqual(draft["plan"]["steps"][1]["args"],
                             {"url_from_step": "search", "selected_rank": 0})
            self.assertEqual([step["args"]["selected_rank"] for step in draft["plan"]["steps"]
                              if step["capability"] == "web.read"], list(range(5)))
            changed = copy.deepcopy(draft["plan"])
            changed["steps"][1]["args"]["selected_rank"] = 5
            with self.assertRaises(GoalValidationError):
                validate_plan(changed)
            _reviewed_decision(service, {"type": "goal_decide", "goal_id": draft["goal_id"],
                            "revision": 1, "decision": "approve"})
            result = service.tick()[0]
            self.assertEqual(result["status"], "COMPLETED")
            self.assertEqual(result["fact_verification"], "NOT_VERIFIED")
            self.assertEqual(executor.read_urls,
                             ["https://docs.example.test/one", "https://docs.example.test/two",
                              "https://docs.example.test/three"])
            self.assertEqual(len(result["receipts"][-1]["output"]["sources"]), 3)
            self.assertEqual([item["reason"] for item in result["source_skips"]],
                             ["three_sources_ready", "three_sources_ready"])
            self.assertEqual(model.step_calls, 1)
            report = (workspace / "notes/research-v1.md").read_text(encoding="utf-8")
            self.assertIn("## 变化摘要", report)
            self.assertIn("## 来源清单", report)
            self.assertIn("## 待用户决策", report)
            self.assertIn("## 建议下一步", report)
            self.assertIn("未逐字审阅网页全文", report)
            self.assertIn("https://docs.example.test/three", report)

        for reason in ("insufficient", "historical"):
            with self.subTest(reason=reason), tempfile.TemporaryDirectory() as tmp:
                workspace = Path(tmp)
                model = _SearchResearchModel()
                executor = _SearchResearchExecutor(workspace, insufficient=reason == "insufficient",
                                                   historical=reason == "historical")
                service = GoalService(workspace, model, executor)
                draft = service.handle({"type": "goal_propose", "request_id": reason,
                                        "text": "持续搜索并整理 Python asyncio 公开资料"})
                _reviewed_decision(service, {"type": "goal_decide", "goal_id": draft["goal_id"],
                                "revision": 1, "decision": "approve"})
                result = service.tick()[0]
                self.assertEqual(result["status"], "WAITING_USER")
                self.assertIn("source_relevance_failed", result["error"])
                self.assertEqual(model.step_calls, 0)
                self.assertFalse((workspace / "notes/research-v1.md").exists())

    def test_search_research_uses_approved_later_candidates_after_failed_reads(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            model = _SearchResearchModel()
            executor = _SearchResearchExecutor(workspace, blocked_urls={"one"},
                                               irrelevant_urls={"two"}, truncated_urls={"four"})
            service = GoalService(workspace, model, executor)
            draft = service.handle({"type": "goal_propose", "request_id": "search-fallback",
                                    "text": "持续搜索并整理 Python asyncio 公开资料"})
            _reviewed_decision(service, {"type": "goal_decide", "goal_id": draft["goal_id"],
                            "revision": 1, "decision": "approve"})
            run = service.tick()[0]
            self.assertEqual(run["status"], "COMPLETED", run.get("error"))
            self.assertEqual(len(executor.read_urls), 5)
            self.assertEqual([item["error_code"] for item in run["source_failures"]],
                             ["page_too_large", "topic_not_found_in_body"])
            self.assertEqual(len([item for item in run["receipts"]
                                  if item["capability"] == "web.read" and item.get("accepted_source")]), 3)
            self.assertEqual(len(run["receipts"][-1]["output"]["sources"]), 3)
            self.assertEqual(model.step_calls, 1)
            report = (workspace / "notes/research-v1.md").read_text(encoding="utf-8")
            self.assertIn("https://docs.example.test/five", report)
            self.assertIn("以下候选未纳入本次报告", report)
            self.assertIn("网页正文较长，仅提取前段（总计 67361 字符）", report)
            source_section = report.split("## 来源清单\n", 1)[1].split("## 提纲", 1)[0]
            self.assertNotIn("https://docs.example.test/one", source_section)
            self.assertNotIn("https://docs.example.test/two", source_section)
            memory = MemoryStore(workspace)
            scope = {"project": "gosim-muse", "account": "local", "visibility": "personal"}
            claims = memory.find_claims(scope, predicate="page_excerpt")
            self.assertEqual(len(claims), 3)
            locators = [source["locator"] for claim in claims
                        for source in memory.explain_claim(claim["id"], scope)["sources"]]
            self.assertNotIn("https://docs.example.test/one", locators)
            self.assertNotIn("https://docs.example.test/two", locators)
            second = service.tick(datetime.now(timezone.utc) + timedelta(seconds=61))[0]
            self.assertEqual(second["status"], "NO_CHANGE")
            self.assertEqual(model.step_calls, 1)
            self.assertFalse((workspace / "notes/research-v2.md").exists())

    def test_search_research_waits_if_five_candidates_yield_only_two_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            model = _SearchResearchModel()
            executor = _SearchResearchExecutor(workspace, blocked_urls={"one", "two", "three"})
            service = GoalService(workspace, model, executor)
            draft = service.handle({"type": "goal_propose", "request_id": "search-not-enough",
                                    "text": "持续搜索并整理 Python asyncio 公开资料"})
            _reviewed_decision(service, {"type": "goal_decide", "goal_id": draft["goal_id"],
                            "revision": 1, "decision": "approve"})
            run = service.tick()[0]
            self.assertEqual(run["status"], "WAITING_USER")
            self.assertIn("insufficient_approved_readable_sources", run["error"])
            self.assertEqual(len(run["source_failures"]), 3)
            self.assertEqual(model.step_calls, 0)
            self.assertFalse((workspace / "notes/research-v1.md").exists())

    def test_model_draft_needs_revision_bound_approval_then_real_artifact(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            MemoryStore(workspace).remember("chat_user", "local_user", "旧记忆保留")
            model = _FixtureModel()
            service = GoalService(workspace, model, CapabilityExecutor(workspace))
            proposed = service.handle({"type": "goal_propose", "request_id": "fixture-request-1",
                                       "text": "准备一份演讲资料"})
            self.assertEqual(proposed["status"], "DRAFT")
            self.assertEqual(proposed["revision"], 1)
            self.assertFalse((workspace / "notes/speech.md").exists())
            self.assertEqual(_reviewed_decision(service, {"type": "goal_decide", "goal_id": proposed["goal_id"],
                                             "revision": 2, "decision": "approve"})["status"], "REJECTED")
            approved = _reviewed_decision(service, {"type": "goal_decide", "goal_id": proposed["goal_id"],
                                       "revision": 1, "decision": "approve"})
            self.assertEqual(approved["status"], "ACTIVE")
            self.assertTrue(approved["approval_id"].startswith("approval:"))
            run = service.tick(datetime.now(timezone.utc) + timedelta(seconds=1))[0]
            self.assertEqual(run["status"], "COMPLETED")
            self.assertEqual(run["approval_id"], approved["approval_id"])
            self.assertIn("提纲", (workspace / "notes/speech.md").read_text(encoding="utf-8"))
            self.assertEqual(run["receipts"][-1]["verification"]["readback_matches"], True)
            self.assertEqual(MemoryStore(workspace).search("旧记忆")[0]["kind"], "chat_user")
            self.assertEqual(run["memory_status"], "RECORDED")
            from agent_app import LocalAgent
            matches = LocalAgent(workspace).handle({"type": "memory_search", "query": "演讲资料"})["memory_matches"]
            self.assertTrue(any(proposed["goal_id"] in item["content"] and "notes/speech.md" in item["content"]
                                and "已验证完成" in item["content"] for item in matches))
            records = MemoryStore(workspace).list_records()
            goal_record = next(item for item in records if item["kind"] == "goal_result")
            self.assertEqual((goal_record["record_type"], goal_record["confirmed"]), ("fact", 1))
            claims = MemoryStore(workspace).find_claims(
                {"project": "gosim-muse", "account": "local", "visibility": "personal"},
                subject_id=proposed["goal_id"])
            self.assertEqual(len(claims), 1)
            self.assertEqual(claims[0]["payload"]["epistemic_type"], "fact")
            self.assertTrue(MemoryStore(workspace).explain_claim(
                claims[0]["id"], claims[0]["scope"])["sources"])
            restarted = GoalService(workspace, model, CapabilityExecutor(workspace))
            self.assertEqual(restarted.handle({"type": "goal_get", "goal_id": proposed["goal_id"]})["status"], "COMPLETED")
            self.assertTrue(restarted.handle({"type": "goal_propose", "request_id": "fixture-request-1",
                                              "text": "准备一份演讲资料"})["deduplicated"])

    def test_event_dedup_pause_resume_cancel(self):
        with tempfile.TemporaryDirectory() as tmp:
            service = GoalService(Path(tmp), _CompactEventModel(), CapabilityExecutor(Path(tmp)))
            proposed = service.handle({"type": "goal_propose", "request_id": "fixture-request-2",
                                       "text": "关注测试资料变化",
                                       "context_refs": [{"ref": "resource:test-notes", "purpose": "合成目录"}]})
            goal_id = proposed["goal_id"]
            _reviewed_decision(service, {"type": "goal_decide", "goal_id": goal_id, "revision": 1, "decision": "approve"})
            event = {"event_id": "file-event-1", "source": "fixture", "observed_at": datetime.now(timezone.utc).isoformat(),
                     "topic": "file.changed", "payload_ref": "resource:test-notes", "subject": "first.txt"}
            self.assertEqual(len(service.on_event(event)), 1)
            self.assertEqual(service.on_event(event), [])
            service.handle({"type": "goal_control", "goal_id": goal_id, "action": "pause"})
            self.assertEqual(service.on_event(dict(event, event_id="file-event-2")), [])
            service.handle({"type": "goal_control", "goal_id": goal_id, "action": "resume"})
            service.handle({"type": "goal_control", "goal_id": goal_id, "action": "cancel"})
            self.assertEqual(service.on_event(dict(event, event_id="file-event-3")), [])

    def test_late_out_of_order_workspace_event_does_not_replace_newer_result(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            model = _CompactEventModel()
            service = GoalService(workspace, model, CapabilityExecutor(workspace))
            draft = service.handle({"type": "goal_propose", "request_id": "file-event-order",
                                    "text": "持续整理合成目录变化",
                                    "context_refs": [{"ref": "resource:test-notes", "purpose": "合成目录"}]})
            _reviewed_decision(service, {"type": "goal_decide", "goal_id": draft["goal_id"],
                                        "revision": 1, "decision": "approve"})
            instant = datetime.now(timezone.utc)
            newer = {"event_id": "newer", "source": "workspace_watcher",
                     "observed_at": (instant + timedelta(microseconds=2)).isoformat(),
                     "topic": "file.changed", "payload_ref": "resource:test-notes",
                     "subject": "newer.txt"}
            older = dict(newer, event_id="older",
                         observed_at=(instant + timedelta(microseconds=1)).astimezone(
                             timezone(timedelta(hours=8))).isoformat(),
                         subject="older.txt")
            self.assertEqual(service.on_event(newer)[0]["status"], "COMPLETED")
            self.assertEqual(service.on_event(newer), [])
            self.assertEqual(service.on_event(older), [])
            restarted = GoalService(workspace, model, CapabilityExecutor(workspace))
            self.assertEqual(restarted.on_event(older), [])
            same_poll = dict(newer, event_id="same-poll", subject="peer.txt")
            self.assertEqual(restarted.on_event(same_poll)[0]["status"], "COMPLETED")
            self.assertEqual(restarted.handle({"type": "goal_get", "goal_id": draft["goal_id"]})["run_count"], 2)
            with sqlite3.connect(str(workspace / "memory.sqlite3")) as db:
                self.assertEqual({row[0] for row in db.execute(
                    "SELECT event_id FROM muse_goal_events WHERE goal_id=?", (draft["goal_id"],))},
                    {"newer", "same-poll"})

    def test_cancel_clears_scheduled_due_time(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            service = GoalService(workspace, _FixtureModel(), CapabilityExecutor(workspace))
            draft = service.handle({"type": "goal_propose", "request_id": "cancel-scheduled",
                                    "text": "关注合成目录变化",
                                    "context_refs": [{"ref": "resource:test-notes", "purpose": "合成目录"}]})
            approved = _reviewed_decision(service, {"type": "goal_decide", "goal_id": draft["goal_id"],
                                       "revision": 1, "decision": "approve"})
            self.assertIsNotNone(approved["next_due"])
            cancelled = service.handle({"type": "goal_control", "goal_id": draft["goal_id"],
                                        "action": "cancel"})
            self.assertEqual(cancelled["status"], "CANCELLED")
            self.assertIsNone(cancelled["next_due"])
            self.assertEqual(service.tick(), [])

    def test_event_observed_before_current_approval_cannot_trigger_after_restart(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            model = _CompactEventModel()
            service = GoalService(workspace, model, CapabilityExecutor(workspace))
            draft = service.handle({"type": "goal_propose", "request_id": "old-event-replay",
                                    "text": "持续整理文件变化",
                                    "context_refs": [{"ref": "resource:test-notes", "purpose": "合成目录"}]})
            old_event = {"event_id": "mail-before-approval", "source": "workspace_watcher",
                         "observed_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                         "topic": "file.changed", "subject": "old.txt", "sensitivity": "personal",
                         "payload_ref": "resource:test-notes"}
            _reviewed_decision(service, {"type": "goal_decide", "goal_id": draft["goal_id"],
                            "revision": 1, "decision": "approve"})
            restarted = GoalService(workspace, model, CapabilityExecutor(workspace))
            self.assertEqual(restarted.on_event(old_event), [])
            self.assertFalse((workspace / "notes/update-v1.md").exists())
            current = dict(old_event, event_id="file-after-approval",
                           observed_at=(datetime.now(timezone.utc) + timedelta(seconds=1)).isoformat(),
                           subject="new.txt")
            self.assertEqual(restarted.on_event(current)[0]["status"], "COMPLETED")

    def test_invalid_plans_fail_closed(self):
        valid = spec_for("准备演讲")
        validate_plan(valid)
        for mutation in (
            lambda item: item.update(approved=True),
            lambda item: item["steps"][0].update(capability="shell.exec"),
            lambda item: item["permissions"].update(send_message="approved_rule"),
            lambda item: item["steps"][1]["args"].update(relative_path="../escape.txt"),
            lambda item: item["budget"].update(max_run_seconds=0),
        ):
            invalid = copy.deepcopy(valid)
            mutation(invalid)
            with self.assertRaises(GoalValidationError):
                validate_plan(invalid)
        with self.assertRaisesRegex(GoalValidationError, "duplicate_json_key"):
            parse_plan('{"title":"one","title":"two"}')

    def test_utc_z_deadline_can_be_approved(self):
        with tempfile.TemporaryDirectory() as tmp:
            class DeadlineModel(_FixtureModel):
                def generate(self, prompt, *, purpose, require_json=False, max_tokens=512, goal_id=None):
                    result = super().generate(prompt, purpose=purpose, require_json=require_json,
                                              max_tokens=max_tokens, goal_id=goal_id)
                    if purpose == "goal_plan":
                        spec = json.loads(result["text"])
                        spec["deadline"] = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat().replace(
                            "+00:00", "Z")
                        result["text"] = json.dumps(spec, ensure_ascii=False)
                    return result

            service = GoalService(Path(tmp), DeadlineModel(), CapabilityExecutor(Path(tmp)))
            draft = service.handle({"type": "goal_propose", "request_id": "deadline-z",
                                    "text": "准备演讲资料"})
            self.assertEqual(draft["status"], "DRAFT")
            approved = _reviewed_decision(service, {"type": "goal_decide", "goal_id": draft["goal_id"],
                                       "revision": 1, "decision": "approve"})
            self.assertEqual(approved["status"], "ACTIVE")

    def test_explicit_deadline_keeps_dynamic_goal_active_then_expires(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            service = GoalService(workspace, _CompactEventModel(), CapabilityExecutor(workspace))
            local_deadline = (datetime.now(timezone(timedelta(hours=8))) + timedelta(days=1)).replace(
                hour=18, minute=0, second=0, microsecond=0)
            draft = service.handle({"type": "goal_propose", "request_id": "explicit-deadline",
                                    "text": "持续整理文件变化，截止 " + local_deadline.strftime("%Y-%m-%d %H:%M"),
                                    "context_refs": [{"ref": "resource:test-notes", "purpose": "合成目录"}]})
            self.assertEqual(draft["status"], "DRAFT")
            self.assertEqual(draft["plan"]["deadline"], local_deadline.isoformat())
            goal_id = draft["goal_id"]
            _reviewed_decision(service, {"type": "goal_decide", "goal_id": goal_id,
                            "revision": 1, "decision": "approve"})
            event = {"event_id": "before-deadline", "source": "workspace_watcher",
                     "observed_at": (datetime.now(timezone.utc) + timedelta(seconds=1)).isoformat(),
                     "topic": "file.changed", "subject": "timely.md", "sensitivity": "personal",
                     "payload_ref": "resource:test-notes"}
            self.assertEqual(service.on_event(event)[0]["status"], "COMPLETED")
            self.assertEqual(service.handle({"type": "goal_get", "goal_id": goal_id})["status"], "ACTIVE")
            after_deadline = dict(event, event_id="future-after-deadline",
                                  observed_at=(local_deadline + timedelta(seconds=2)).isoformat())
            self.assertEqual(service.on_event(after_deadline), [])
            self.assertEqual(service.tick(local_deadline.astimezone(timezone.utc) + timedelta(seconds=1)), [])
            self.assertEqual(service.handle({"type": "goal_get", "goal_id": goal_id})["status"], "EXPIRED")
            self.assertEqual(service.on_event(dict(after_deadline, event_id="after-deadline")), [])

    def test_ambiguous_or_past_deadline_is_not_silently_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            model = _FixtureModel()
            service = GoalService(Path(tmp), model, CapabilityExecutor(Path(tmp)))
            for index, text in enumerate(("下周五之前准备演讲资料", "2026-10-01前准备演讲资料",
                                          "明天下午6点完成演讲资料", "2026年10月1日完成演讲资料",
                                          "截止 2020-01-01 18:00 准备演讲资料")):
                response = service.handle({"type": "goal_propose", "request_id": f"unclear-{index}",
                                           "text": text})
                self.assertEqual(response["status"], "NEEDS_DEADLINE")
                self.assertTrue(response["next_step"])
            self.assertEqual(model.calls, [])

    def test_utc_deadline_is_parsed_and_unknown_timezone_requires_clarification(self):
        with tempfile.TemporaryDirectory() as tmp:
            service = GoalService(Path(tmp), _FixtureModel(), CapabilityExecutor(Path(tmp)))
            future = (datetime.now(timezone.utc) + timedelta(days=2)).strftime("%Y-%m-%d %H:%M")
            draft = service.handle({"type": "goal_propose", "request_id": "deadline-utc",
                                    "text": "准备演讲资料，截止 " + future + " UTC"})
            self.assertEqual(draft["status"], "DRAFT")
            self.assertTrue(draft["plan"]["deadline"].endswith("+00:00"))
            unclear = service.handle({"type": "goal_propose", "request_id": "deadline-pst",
                                      "text": "准备演讲资料，截止 " + future + " PST"})
            self.assertEqual(unclear["status"], "NEEDS_DEADLINE")

    def test_revision_preserves_deadline_until_explicitly_cleared(self):
        with tempfile.TemporaryDirectory() as tmp:
            service = GoalService(Path(tmp), _CompactEventModel(), CapabilityExecutor(Path(tmp)))
            future = (datetime.now(timezone(timedelta(hours=8))) + timedelta(days=2)).strftime("%Y-%m-%d %H:%M")
            draft = service.handle({"type": "goal_propose", "request_id": "deadline-revision",
                                    "text": "持续整理目录变化，截止 " + future,
                                    "context_refs": [{"ref": "resource:test-notes", "purpose": "合成目录"}]})
            self.assertEqual(draft["status"], "DRAFT")
            original = draft["plan"]["deadline"]
            _reviewed_decision(service, {"type": "goal_decide", "goal_id": draft["goal_id"],
                            "revision": 1, "decision": "approve"})
            revised = service.handle({"type": "goal_revise", "goal_id": draft["goal_id"],
                                      "text": "增加一条来源说明"})
            self.assertEqual(revised["plan"]["deadline"], original)
            self.assertIsNone(revised["approval_id"])
            cleared = service.handle({"type": "goal_revise", "goal_id": draft["goal_id"],
                                      "text": "不设截止日期"})
            self.assertEqual(cleared["status"], "DRAFT")
            self.assertIsNone(cleared["plan"]["deadline"])

    def test_file_event_changes_versioned_artifact_and_untrusted_source_does_not_trigger(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            service = GoalService(workspace, _CompactEventModel(), CapabilityExecutor(workspace))
            proposed = service.handle({"type": "goal_propose", "request_id": "event-plan",
                                       "text": "持续整理测试文件夹更新",
                                       "context_refs": [{"ref": "resource:test-notes", "purpose": "已批准合成目录"}]})
            self.assertEqual(proposed["status"], "DRAFT")
            goal_id = proposed["goal_id"]
            _reviewed_decision(service, {"type": "goal_decide", "goal_id": goal_id, "revision": 1, "decision": "approve"})
            self.assertEqual(service.tick(), [])
            common = {"source": "workspace_watcher", "topic": "file.changed", "sensitivity": "personal",
                      "observed_at": datetime.now(timezone.utc).isoformat(), "account_scope": "local-workspace"}
            self.assertEqual(service.on_event(dict(common, event_id="fake", subject="first.txt")), [])
            first = service.on_event(dict(common, event_id="e1", subject="first.txt",
                                          payload_ref="resource:test-notes", payload={"change": "created"}))[0]
            self.assertEqual(first["status"], "COMPLETED")
            self.assertIn("first.txt", (workspace / "notes/update-v1.md").read_text(encoding="utf-8"))
            scoped_results = MemoryStore(workspace).search_goal_results("测试资料更新", ["local-workspace"])
            self.assertEqual(scoped_results[0]["account_scope"], "local-workspace")
            self.assertEqual(scoped_results[0]["confirmed"], 1)
            self.assertEqual(service.on_event(dict(common, event_id="e1", subject="first.txt",
                                                   payload_ref="resource:test-notes")), [])
            second = service.on_event(dict(common, event_id="e2", subject="second.txt",
                                           payload_ref="resource:test-notes", payload={"change": "modified"}))[0]
            self.assertEqual(second["status"], "COMPLETED")
            self.assertIn("second.txt", (workspace / "notes/update-v2.md").read_text(encoding="utf-8"))

    def test_revision_invalidates_old_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            service = GoalService(Path(tmp), _FixtureModel(), CapabilityExecutor(Path(tmp)))
            first = service.handle({"type": "goal_propose", "request_id": "revision-plan",
                                    "text": "准备初稿"})
            goal_id = first["goal_id"]
            approved = _reviewed_decision(service, {"type": "goal_decide", "goal_id": goal_id,
                                       "revision": 1, "decision": "approve"})
            self.assertTrue(approved["approval_id"])
            revised = service.handle({"type": "goal_revise", "goal_id": goal_id,
                                      "text": "增加一个新的核验要点"})
            self.assertEqual(revised["status"], "DRAFT")
            self.assertEqual(revised["revision"], 2)
            self.assertIsNone(revised["approval_id"])
            self.assertEqual(service.tick(), [])
            stale = _reviewed_decision(service, {"type": "goal_decide", "goal_id": goal_id,
                                    "revision": 1, "decision": "approve"})
            self.assertEqual(stale["status"], "REJECTED")
            second = _reviewed_decision(service, {"type": "goal_decide", "goal_id": goal_id,
                                     "revision": 2, "decision": "approve"})
            self.assertNotEqual(second["approval_id"], approved["approval_id"])

    def test_read_only_model_step_retries_within_policy(self):
        with tempfile.TemporaryDirectory() as tmp:
            model = _TransientEventModel()
            service = GoalService(Path(tmp), model, CapabilityExecutor(Path(tmp)))
            draft = service.handle({"type": "goal_propose", "request_id": "retry-plan",
                                    "text": "持续整理测试文件夹更新",
                                    "context_refs": [{"ref": "resource:test-notes", "purpose": "合成目录"}]})
            _reviewed_decision(service, {"type": "goal_decide", "goal_id": draft["goal_id"],
                            "revision": 1, "decision": "approve"})
            run = service.on_event({"event_id": "retry-event", "source": "workspace_watcher",
                                    "observed_at": datetime.now(timezone.utc).isoformat(),
                                    "topic": "file.changed", "subject": "first.txt",
                                    "sensitivity": "personal", "payload_ref": "resource:test-notes"})[0]
            self.assertEqual(run["status"], "COMPLETED")
            self.assertEqual(model.step_calls, 2)
            self.assertTrue((Path(tmp) / "notes/update-v1.md").exists())

    def test_remote_model_failure_is_not_retried(self):
        with tempfile.TemporaryDirectory() as tmp:
            model = _FailedRemoteModel()
            service = GoalService(Path(tmp), model, CapabilityExecutor(Path(tmp)))
            draft = service.handle({"type": "goal_propose", "request_id": "remote-retry",
                                    "text": "准备演讲资料"})
            self.assertEqual(draft["status"], "DRAFT")
            _reviewed_decision(service, {"type": "goal_decide", "goal_id": draft["goal_id"],
                            "revision": 1, "decision": "approve"})
            run = service.tick()[0]
            self.assertEqual(run["status"], "WAITING_USER")
            self.assertEqual(model.step_calls, 1)
            self.assertEqual(run["model_tokens"], 20)

    def test_zero_money_plan_blocks_remote_model_before_request(self):
        with tempfile.TemporaryDirectory() as tmp:
            model = _RemoteMoneyModel()
            service = GoalService(Path(tmp), model, CapabilityExecutor(Path(tmp)))
            draft = service.handle({"type": "goal_propose", "request_id": "zero-money-remote",
                                    "text": "准备演讲资料"})
            _reviewed_decision(service, {"type": "goal_decide", "goal_id": draft["goal_id"],
                            "revision": 1, "decision": "approve"})
            run = service.tick()[0]
            self.assertEqual(run["error"], "model_money_budget_requires_local")
            self.assertEqual([call["purpose"] for call in model.calls], ["goal_plan"])

    def test_goal_period_token_budget_stops_second_cycle(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            model = _TightBudgetModel()
            service = GoalService(workspace, model, CapabilityExecutor(workspace))
            draft = service.handle({"type": "goal_propose", "request_id": "period-budget",
                                    "text": "关注资料变化"})
            self.assertEqual(draft["status"], "DRAFT")
            _reviewed_decision(service, {"type": "goal_decide", "goal_id": draft["goal_id"],
                            "revision": 1, "decision": "approve"})
            self.assertEqual(service.tick()[0]["status"], "COMPLETED")
            second = service.tick(datetime.now(timezone.utc) + timedelta(seconds=61))[0]
            self.assertEqual(second["error"], "model_token_budget_exceeded")
            self.assertEqual([call["purpose"] for call in model.calls], ["goal_plan", "goal_step"])

    def test_short_model_draft_remains_reviewable(self):
        with tempfile.TemporaryDirectory() as tmp:
            service = GoalService(Path(tmp), _ShortContentModel(), CapabilityExecutor(Path(tmp)))
            draft = service.handle({"type": "goal_propose", "request_id": "short-draft",
                                    "text": "准备一份演讲资料"})
            self.assertEqual(draft["status"], "DRAFT")
            content = draft["plan"]["steps"][0]["args"]["content"]
            self.assertIn("待补充", content)
            self.assertIn("准备演讲资料提纲", content)

    def test_research_skips_unchanged_source_then_writes_next_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            model, executor = _ResearchModel(), _ResearchExecutor(workspace)
            service = GoalService(workspace, model, executor)
            draft = service.handle({"type": "goal_propose", "request_id": "research-versions",
                                    "text": "持续整理公开网址 https://example.test/brief"})
            self.assertEqual(draft["status"], "DRAFT")
            goal_id = draft["goal_id"]
            _reviewed_decision(service, {"type": "goal_decide", "goal_id": goal_id,
                            "revision": 1, "decision": "approve"})
            self.assertEqual(service.tick()[0]["status"], "COMPLETED")
            self.assertTrue((workspace / "notes/research-v1.md").exists())
            second = service.tick(datetime.now(timezone.utc) + timedelta(seconds=61))[0]
            self.assertEqual(second["status"], "NO_CHANGE")
            self.assertEqual(model.step_calls, 1)
            self.assertFalse((workspace / "notes/research-v2.md").exists())
            executor.body = "第二版"
            third = service.tick(datetime.now(timezone.utc) + timedelta(seconds=122))[0]
            self.assertEqual(third["status"], "COMPLETED")
            self.assertTrue((workspace / "notes/research-v2.md").exists())
            self.assertEqual(model.step_calls, 2)
            self.assertEqual(executor.reads, 3)
            self.assertIn("https://example.test/brief", model.step_prompt)
            self.assertLess(len(model.step_prompt), 2000)

    def test_three_sources_are_read_before_filtering_and_written_to_one_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            model, executor = _ResearchModel(), _MultiResearchExecutor(workspace)
            service = GoalService(workspace, model, executor)
            urls = list(executor.bodies)
            draft = service.handle({"type": "goal_propose", "request_id": "three-sources",
                                    "text": "持续整理 " + " ".join(urls)})
            self.assertEqual(draft["status"], "DRAFT")
            self.assertEqual(len([step for step in draft["plan"]["steps"]
                                  if step["capability"] == "web.read"]), 3)
            _reviewed_decision(service, {"type": "goal_decide", "goal_id": draft["goal_id"],
                            "revision": 1, "decision": "approve"})
            first = service.tick()[0]
            self.assertEqual(first["status"], "COMPLETED")
            self.assertEqual(len(first["receipts"][-1]["output"]["sources"]), 3)
            self.assertTrue(all(url in model.step_prompt for url in urls))
            scope = {"project": "gosim-muse", "account": "local", "visibility": "personal"}
            run_claim = MemoryStore(workspace).find_claims(scope, subject_id=draft["goal_id"])[0]
            explained = MemoryStore(workspace).explain_claim(run_claim["id"], scope)
            self.assertEqual(len(explained["sources"]), 4)  # runtime receipt plus three pages
            self.assertEqual(len([item for item in MemoryStore(workspace).find_claims(scope)
                                  if item["payload"]["epistemic_type"] == "external_claim"]), 3)
            executor.bodies[urls[0]] = "第一份资料正文\nLast updated: 2026-09-28 13:00"
            second = service.tick(datetime.now(timezone.utc) + timedelta(seconds=61))[0]
            self.assertEqual(second["status"], "NO_CHANGE")
            self.assertFalse(second["notify"])
            self.assertEqual(model.step_calls, 1)
            self.assertEqual(len(second["source_changes"]), 3)
            executor.bodies[urls[2]] = "第三份资料正文，新增重要更新"
            third = service.tick(datetime.now(timezone.utc) + timedelta(seconds=122))[0]
            self.assertEqual(third["status"], "COMPLETED")
            self.assertTrue(third["notify"])
            self.assertEqual(model.step_calls, 2)
            self.assertTrue((workspace / "notes/research-v2.md").exists())

    def test_revising_multi_source_goal_keeps_sources_and_invalidates_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            service = GoalService(Path(tmp), _ResearchModel(), _MultiResearchExecutor(Path(tmp)))
            first = service.handle({"type": "goal_propose", "request_id": "multi-revise",
                                    "text": "持续整理 https://example.test/one https://example.test/two"})
            self.assertEqual(first["status"], "DRAFT")
            _reviewed_decision(service, {"type": "goal_decide", "goal_id": first["goal_id"],
                            "revision": 1, "decision": "approve"})
            revised = service.handle({"type": "goal_revise", "goal_id": first["goal_id"],
                                      "text": "增加 https://example.test/three 作为第三份来源"})
            self.assertEqual(revised["status"], "DRAFT")
            self.assertIsNone(revised["approval_id"])
            self.assertEqual(len([step for step in revised["plan"]["steps"]
                                  if step["capability"] == "web.read"]), 3)
            self.assertEqual(_reviewed_decision(service, {"type": "goal_decide", "goal_id": first["goal_id"],
                                             "revision": 1, "decision": "approve"})["status"], "REJECTED")

    def test_research_goal_uses_folder_event_for_second_version_even_when_web_is_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            model, executor = _ResearchModel(kind="file_monitor"), _ResearchExecutor(workspace)
            service = GoalService(workspace, model, executor)
            draft = service.handle({"type": "goal_propose", "request_id": "research-folder-combined",
                                    "text": "根据 https://example.test/brief 整理资料并持续关注目录变化",
                                    "context_refs": [{"ref": "resource:folder-selected", "purpose": "已批准目录"}]})
            self.assertEqual(draft["status"], "DRAFT")
            self.assertEqual({item["kind"] for item in draft["plan"]["triggers"]}, {"interval", "event"})
            self.assertEqual(len(draft["plan"]["context_refs"]), 2)
            self.assertEqual(draft["plan"]["triggers"][1]["source_ref"], "resource:folder-selected")
            _reviewed_decision(service, {"type": "goal_decide", "goal_id": draft["goal_id"],
                            "revision": 1, "decision": "approve"})
            self.assertEqual(service.tick()[0]["status"], "COMPLETED")
            event = {"event_id": "folder-update-1", "source": "workspace_watcher",
                     "observed_at": (datetime.now(timezone.utc) + timedelta(seconds=1)).isoformat(),
                     "topic": "file.changed", "subject": "changes.md", "sensitivity": "personal",
                     "payload_ref": "resource:folder-selected", "account_scope": "local-workspace",
                     "payload": {"relative_path": "changes.md", "change": "modified"}}
            second = service.on_event(event)[0]
            self.assertEqual(second["status"], "COMPLETED")
            self.assertTrue((workspace / "notes/research-v2.md").exists())
            content = (workspace / "notes/research-v2.md").read_text(encoding="utf-8")
            self.assertIn("changes.md", content)
            self.assertIn("变动类型：modified", content)
            self.assertNotIn("changes.md", model.step_prompt)
            self.assertEqual(service.tick(datetime.now(timezone.utc) + timedelta(seconds=61))[0]["status"],
                             "NO_CHANGE")
            self.assertEqual(model.step_calls, 2)

    def test_local_model_failure_after_web_read_is_not_retried(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            model = _ResearchModel(fail_step=True)
            service = GoalService(workspace, model, _ResearchExecutor(workspace))
            draft = service.handle({"type": "goal_propose", "request_id": "research-retry",
                                    "text": "整理公开网址 https://example.test/brief"})
            self.assertEqual(draft["status"], "DRAFT")
            _reviewed_decision(service, {"type": "goal_decide", "goal_id": draft["goal_id"],
                            "revision": 1, "decision": "approve"})
            self.assertEqual(service.tick()[0]["status"], "WAITING_USER")
            self.assertEqual(model.step_calls, 1)
            record = MemoryStore(workspace).list_records()[0]
            self.assertEqual((record["record_type"], record["confirmed"]), ("inference", 0))
            self.assertIn("待核验", record["content"])

    def test_explicit_retry_recovers_read_only_failure_with_same_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            model = _ResearchModel(fail_step=True)
            service = GoalService(workspace, model, _ResearchExecutor(workspace))
            draft = service.handle({"type": "goal_propose", "request_id": "safe-retry",
                                    "text": "整理公开网址 https://example.test/brief"})
            approved = _reviewed_decision(service, {"type": "goal_decide", "goal_id": draft["goal_id"],
                                       "revision": 1, "decision": "approve"})
            first = service.tick()[0]
            self.assertEqual(first["status"], "WAITING_USER")
            self.assertEqual(first["failed_capability"], "model.compose")
            model.fail_step = False
            resumed = service.handle({"type": "goal_control", "goal_id": draft["goal_id"],
                                      "action": "retry"})
            self.assertEqual(resumed["status"], "ACTIVE")
            self.assertEqual(resumed["approval_id"], approved["approval_id"])
            self.assertEqual(service.tick()[0]["status"], "COMPLETED")
            self.assertTrue((workspace / "notes/research-v1.md").exists())

    def test_uncertain_write_is_not_retried_and_safe_retries_are_bounded(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            service = GoalService(workspace, _ResearchModel(), _UncertainWriteExecutor(workspace))
            draft = service.handle({"type": "goal_propose", "request_id": "uncertain-write",
                                    "text": "整理公开网址 https://example.test/brief"})
            _reviewed_decision(service, {"type": "goal_decide", "goal_id": draft["goal_id"],
                            "revision": 1, "decision": "approve"})
            result = service.tick()[0]
            self.assertEqual(result["failed_capability"], "workspace.write_artifact")
            self.assertEqual(service.handle({"type": "goal_control", "goal_id": draft["goal_id"],
                                             "action": "retry"})["status"], "REJECTED")

        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            service = GoalService(workspace, _ResearchModel(fail_step=True), _ResearchExecutor(workspace))
            draft = service.handle({"type": "goal_propose", "request_id": "bounded-retry",
                                    "text": "整理公开网址 https://example.test/brief"})
            _reviewed_decision(service, {"type": "goal_decide", "goal_id": draft["goal_id"],
                            "revision": 1, "decision": "approve"})
            for attempt in range(3):
                self.assertEqual(service.tick()[0]["status"], "WAITING_USER")
                status = service.handle({"type": "goal_control", "goal_id": draft["goal_id"],
                                         "action": "retry"})["status"]
                self.assertEqual(status, "ACTIVE" if attempt < 2 else "REJECTED")

    def test_english_research_body_fails_before_artifact_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            model = _ResearchModel(english_step=True)
            service = GoalService(workspace, model, _ResearchExecutor(workspace))
            draft = service.handle({"type": "goal_propose", "request_id": "english-research",
                                    "text": "根据 https://example.test/brief 整理中文资料提纲"})
            _reviewed_decision(service, {"type": "goal_decide", "goal_id": draft["goal_id"],
                            "revision": 1, "decision": "approve"})
            run = service.tick()[0]
            self.assertEqual(run["status"], "WAITING_USER")
            self.assertEqual(run["error"], "model_language_insufficient")
            self.assertEqual([item["capability"] for item in run["receipts"]], ["web.read"])
            self.assertEqual(list(workspace.rglob("*.md")), [])

    def test_generic_model_artifact_name_gets_stable_safe_title_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            service = GoalService(Path(tmp), _GenericArtifactModel(), CapabilityExecutor(Path(tmp)))
            draft = service.handle({"type": "goal_propose", "request_id": "generic-artifact",
                                    "text": "准备 AI 任务验证演讲"})
            self.assertEqual(draft["status"], "DRAFT")
            path = draft["plan"]["steps"][0]["args"]["relative_path"]
            self.assertTrue(path.startswith("notes/AI-任务验证演讲-"))
            self.assertTrue(path.endswith(".md"))
            self.assertIn("resource:workspace/" + path, draft["plan"]["permissions"]["resource_refs"])

    def test_queued_event_survives_restart_with_bounded_context(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            service = GoalService(workspace, _CompactEventModel(), CapabilityExecutor(workspace))
            draft = service.handle({"type": "goal_propose", "request_id": "persisted-event",
                                    "text": "持续整理合成目录变化",
                                    "context_refs": [{"ref": "resource:test-notes", "purpose": "合成目录"}]})
            goal_id = draft["goal_id"]
            _reviewed_decision(service, {"type": "goal_decide", "goal_id": goal_id,
                            "revision": 1, "decision": "approve"})
            instant = datetime.now(timezone.utc)
            safe_event = {"event_id": "queued-1", "source": "workspace_watcher", "observed_at": instant.isoformat(),
                          "topic": "file.changed", "subject": "first.txt", "sensitivity": "personal",
                          "payload_ref": "resource:test-notes", "payload": {"change": "created"}}
            self.assertTrue(service.store.schedule_event(goal_id, safe_event, instant))
            del service
            restarted = GoalService(workspace, _CompactEventModel(), CapabilityExecutor(workspace))
            run = restarted.tick(instant + timedelta(seconds=1))[0]
            self.assertEqual(run["event_id"], "queued-1")
            self.assertEqual(run["status"], "COMPLETED")
            self.assertIn("first.txt", (workspace / "notes/update-v1.md").read_text(encoding="utf-8"))

    def test_wake_after_many_missed_intervals_runs_once_then_reschedules(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            model, executor = _ResearchModel(), _ResearchExecutor(workspace)
            service = GoalService(workspace, model, executor)
            draft = service.handle({"type": "goal_propose", "request_id": "wake-coalesce",
                                    "text": "持续整理 https://example.test/brief"})
            _reviewed_decision(service, {"type": "goal_decide", "goal_id": draft["goal_id"],
                            "revision": 1, "decision": "approve"})
            self.assertEqual(service.tick()[0]["status"], "COMPLETED")
            woke_at = datetime.now(timezone.utc) + timedelta(hours=3)
            resumed = GoalService(workspace, model, executor)
            self.assertEqual([item["status"] for item in resumed.tick(woke_at)], ["NO_CHANGE"])
            self.assertEqual(resumed.tick(woke_at), [])
            state = resumed.handle({"type": "goal_get", "goal_id": draft["goal_id"]})
            self.assertEqual(state["run_count"], 2)
            self.assertGreater(datetime.fromisoformat(state["next_due"]), woke_at)

    def test_new_service_does_not_interrupt_active_run_but_reviews_stale_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            model = _FixtureModel()
            service = GoalService(workspace, model, CapabilityExecutor(workspace))
            draft = service.handle({"type": "goal_propose", "request_id": "inflight-run",
                                    "text": "准备演讲资料"})
            goal_id = draft["goal_id"]
            _reviewed_decision(service, {"type": "goal_decide", "goal_id": goal_id,
                            "revision": 1, "decision": "approve"})
            claimed = service.store.claim(goal_id, datetime.now(timezone.utc) + timedelta(seconds=1),
                                          "interval", None)
            self.assertIsNotNone(claimed)
            second = GoalService(workspace, model, CapabilityExecutor(workspace))
            self.assertEqual(second.handle({"type": "goal_get", "goal_id": goal_id})["status"], "RUNNING")
            with sqlite3.connect(str(workspace / "memory.sqlite3")) as db:
                db.execute("UPDATE muse_goal_runs SET started_at=? WHERE run_id=?",
                           ((datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(), claimed["run_id"]))
            self.assertEqual(second.tick(), [])
            self.assertEqual(second.handle({"type": "goal_get", "goal_id": goal_id})["status"], "WAITING_USER")
            self.assertEqual(second.handle({"type": "goal_control", "goal_id": goal_id,
                                            "action": "retry"})["status"], "REJECTED")

    def test_personal_event_blocks_remote_endpoint_even_when_named_local(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            service = GoalService(workspace, _RemoteLocalSlotModel(), CapabilityExecutor(workspace))
            draft = service.handle({"type": "goal_propose", "request_id": "remote-local-slot",
                                    "text": "持续整理合成目录变化",
                                    "context_refs": [{"ref": "resource:test-notes", "purpose": "合成目录"}]})
            _reviewed_decision(service, {"type": "goal_decide", "goal_id": draft["goal_id"],
                            "revision": 1, "decision": "approve"})
            run = service.on_event({"event_id": "private-1", "source": "workspace_watcher",
                                    "observed_at": datetime.now(timezone.utc).isoformat(),
                                    "topic": "file.changed", "subject": "first.txt", "sensitivity": "personal",
                                    "payload_ref": "resource:test-notes"})[0]
            self.assertEqual(run["status"], "WAITING_USER")
            self.assertEqual(run["error"], "private_event_requires_local_model")
            self.assertFalse((workspace / "notes/update-v1.md").exists())


if __name__ == "__main__":
    unittest.main()
