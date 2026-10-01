import fcntl
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

from agent_app import LocalAgent
from muse_action_bus import ApprovedActionBus
from muse_capability_catalog import CapabilityCatalog
from muse_capabilities import BUILTIN_SCOPE
from muse_goal_store import GoalStore, utc_now
from muse_goals import GoalService
from test_muse_goals import (_FixtureModel, _MultiResearchExecutor, _ResearchModel,
                             _SearchResearchExecutor, _SearchResearchModel, spec_for)
from muse_search_policy import select_results


class RecordingExecutor:
    def __init__(self):
        self.calls = []

    def execute(self, call, *, approved, context):
        self.calls.append((call, approved, context))
        return {"ok": True, "status": "COMPLETED", "action_id": call["action_id"],
                "capability": call["capability"], "output": {}, "verification": {"readback": True}}


def fixture(workspace):
    store = GoalStore(workspace)
    spec = spec_for("批准执行测试")
    spec["goal_id"] = "goal:test"
    store.save_draft(spec, "request:test", {})
    approved = store.decide(spec["goal_id"], 1, "approve",
                            reviewed_digest=store.get(spec["goal_id"])["digest"])
    running = store.claim(spec["goal_id"], utc_now() + timedelta(seconds=1), "interval", None)
    executor = RecordingExecutor()
    bus = ApprovedActionBus(workspace, executor)
    call = {"goal_id": spec["goal_id"], "revision": 1,
            "action_id": running["run_id"] + ":save", "capability": "workspace.write_artifact",
            "args": {"relative_path": "notes/speech.md", "content": "提纲\n测试"}}
    context = {"approval_id": approved["approval_id"], "plan_digest": approved["digest"],
               "permissions": spec["permissions"], "budget": spec["budget"],
               "run_id": running["run_id"]}
    return store, executor, bus, call, context


class ActionBusTests(unittest.TestCase):
    def test_fifth_search_candidate_requires_its_own_approved_rank(self):
        class FiveResults(RecordingExecutor):
            def execute(self, call, *, approved, context):
                self.calls.append((call, approved, context))
                if call["capability"] == "web.search":
                    return {"ok": True, "status": "COMPLETED", "capability": "web.search",
                            "output": {"results": [
                                {"title": f"Python asyncio documentation {index}",
                                 "snippet": "Python asyncio reference",
                                 "url": f"https://docs.example.test/{index}",
                                 "source_id": f"web:{index}"} for index in range(5)]}}
                return {"ok": True, "status": "COMPLETED", "capability": "web.read",
                        "output": {"source_url": call["args"]["url"]}}

        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            spec = spec_for("Python asyncio")
            spec["goal_id"] = "goal:fifth-candidate"
            spec["steps"] = [
                {"id": "search", "capability": "web.search",
                 "args": {"query": "Python asyncio", "max_results": 10}},
                {"id": "read_5", "capability": "web.read",
                 "args": {"url_from_step": "search", "selected_rank": 4},
                 "input_refs": ["step:search"]}]
            spec["permissions"]["capabilities"] = ["web.search", "web.read"]
            store = GoalStore(workspace)
            store.save_draft(spec, "request:fifth-candidate", {})
            approved = store.decide(spec["goal_id"], 1, "approve",
                                    reviewed_digest=store.get(spec["goal_id"])["digest"])
            run = store.claim(spec["goal_id"], utc_now() + timedelta(seconds=1), "interval", None)
            context = {"approval_id": approved["approval_id"], "plan_digest": approved["digest"],
                       "permissions": spec["permissions"], "budget": spec["budget"]}
            executor = FiveResults()
            bus = ApprovedActionBus(workspace, executor)
            base = {"goal_id": spec["goal_id"], "revision": 1}
            self.assertTrue(bus.execute(dict(base, action_id=run["run_id"] + ":search",
                                             capability="web.search", args=spec["steps"][0]["args"]),
                                        approved=True, context=context)["ok"])
            read = dict(base, action_id=run["run_id"] + ":read_5", capability="web.read",
                        args={"url": "https://docs.example.test/4"})
            self.assertTrue(bus.execute(read, approved=True, context=context)["ok"])
            self.assertEqual(bus.execute(dict(read, args={"url": "https://docs.example.test/3"}),
                                         approved=True, context=context)["error"], "action_args_changed")

    def test_browser_lease_comes_only_from_approved_scope_and_host_lock(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            store = GoalStore(workspace)
            spec = spec_for("浏览器隔离研究")
            spec["goal_id"] = "goal:browser-test"
            spec["steps"] = [{"id": "browse", "capability": "browser.research",
                              "args": {"query": "asyncio", "engine": "python.org", "max_pages": 1}}]
            spec["permissions"]["capabilities"] = ["browser.research"]
            spec["permissions"]["resource_refs"] = ["app:com.microsoft.edgemac", "site:python.org"]
            store.save_draft(spec, "request:browser-test", {})
            approved = store.decide(spec["goal_id"], 1, "approve",
                                    reviewed_digest=store.get(spec["goal_id"])["digest"])
            run = store.claim(spec["goal_id"], utc_now() + timedelta(seconds=1), "interval", None)
            executor = RecordingExecutor()
            bus = ApprovedActionBus(workspace, executor, gui_lock_path=workspace / "gui.lock")
            call = {"goal_id": spec["goal_id"], "revision": 1,
                    "action_id": run["run_id"] + ":browse", "capability": "browser.research",
                    "args": spec["steps"][0]["args"]}
            context = {"approval_id": approved["approval_id"], "plan_digest": approved["digest"],
                       "permissions": spec["permissions"], "budget": spec["budget"],
                       "gui_control_granted": False, "allowed_domains": ["attacker.example.test"]}
            self.assertTrue(bus.execute(call, approved=True, context=context)["ok"])
            trusted = executor.calls[0][2]
            self.assertIs(trusted["gui_control_granted"], True)
            self.assertEqual(trusted["allowed_domains"], ["python.org"])
            self.assertEqual((workspace / "gui.lock").read_text(), "")
            with (workspace / "gui.lock").open("r+") as held:
                fcntl.flock(held, fcntl.LOCK_EX | fcntl.LOCK_NB)
                self.assertEqual(bus.execute(call, approved=True, context=context)["error"],
                                 "gui_resource_busy")
            self.assertEqual(bus.execute(dict(call, args=dict(call["args"], max_pages=3)),
                                         approved=True, context=context)["error"], "action_args_changed")

    def test_textedit_lease_requires_exact_goal_resources_and_host_lock(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            store = GoalStore(workspace)
            spec = spec_for("TextEdit 合成资料")
            spec["goal_id"] = "goal:textedit-test"
            args = {"recipe_id": "textedit.synthetic_save.abcdef0123456789", "revision": 1,
                    "digest": "a" * 64, "target_bundle_id": "com.apple.TextEdit",
                    "window_title": "Muse-Test-Alpha.txt",
                    "relative_path": "notes/Muse-Test-Alpha.txt", "content": "合成内容"}
            spec["steps"] = [{"id": "edit", "capability": "app.recipe", "args": args}]
            spec["permissions"]["capabilities"] = ["app.recipe"]
            spec["permissions"]["resource_refs"] = [
                "app:com.apple.TextEdit", "resource:workspace/notes/Muse-Test-Alpha.txt",
                "window:com.apple.TextEdit:Muse-Test-Alpha.txt"]
            store.save_draft(spec, "request:textedit-test", {})
            approved = store.decide(spec["goal_id"], 1, "approve",
                                    reviewed_digest=store.get(spec["goal_id"])["digest"])
            run = store.claim(spec["goal_id"], utc_now() + timedelta(seconds=1), "interval", None)
            executor = RecordingExecutor()
            bus = ApprovedActionBus(workspace, executor, gui_lock_path=workspace / "gui.lock")
            call = {"goal_id": spec["goal_id"], "revision": 1,
                    "action_id": run["run_id"] + ":edit", "capability": "app.recipe", "args": args}
            context = {"approval_id": approved["approval_id"], "plan_digest": approved["digest"],
                       "permissions": spec["permissions"], "budget": spec["budget"],
                       "gui_control_granted": False}
            self.assertTrue(bus.execute(call, approved=True, context=context)["ok"])
            self.assertIs(executor.calls[0][2]["gui_control_granted"], True)
            self.assertNotIn("allowed_domains", executor.calls[0][2])
            self.assertEqual((workspace / "gui.lock").read_text(), "")
            with (workspace / "gui.lock").open("r+") as held:
                fcntl.flock(held, fcntl.LOCK_EX | fcntl.LOCK_NB)
                self.assertEqual(bus.execute(call, approved=True, context=context)["error"],
                                 "gui_resource_busy")
            self.assertEqual(bus.execute(dict(call, args=dict(args, content="伪造")),
                                         approved=True, context=context)["error"], "action_args_changed")

        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            store = GoalStore(workspace)
            spec = spec_for("TextEdit 错误权限")
            spec["goal_id"] = "goal:textedit-bad-scope"
            spec["steps"] = [{"id": "edit", "capability": "app.recipe", "args": args}]
            spec["permissions"]["capabilities"] = ["app.recipe"]
            spec["permissions"]["resource_refs"] = ["app:com.apple.TextEdit"]
            store.save_draft(spec, "request:textedit-bad-scope", {})
            approved = store.decide(spec["goal_id"], 1, "approve",
                                    reviewed_digest=store.get(spec["goal_id"])["digest"])
            run = store.claim(spec["goal_id"], utc_now() + timedelta(seconds=1), "interval", None)
            executor = RecordingExecutor()
            bus = ApprovedActionBus(workspace, executor, gui_lock_path=workspace / "gui.lock")
            call = {"goal_id": spec["goal_id"], "revision": 1,
                    "action_id": run["run_id"] + ":edit", "capability": "app.recipe", "args": args}
            context = {"approval_id": approved["approval_id"], "plan_digest": approved["digest"],
                       "permissions": spec["permissions"], "budget": spec["budget"]}
            self.assertEqual(bus.execute(call, approved=True, context=context)["error"],
                             "textedit_scope_not_approved")
            self.assertEqual(executor.calls, [])

    def test_search_result_url_is_bound_to_authoritative_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            executor = _SearchResearchExecutor(workspace)
            bus = ApprovedActionBus(workspace, executor)
            service = GoalService(workspace, _SearchResearchModel(), bus)
            draft = service.handle({"type": "goal_propose", "request_id": "search-binding",
                                    "text": "持续整理 Python asyncio 的公开资料"})
            approved = service.handle({"type": "goal_decide", "goal_id": draft["goal_id"],
                                       "revision": 1, "plan_digest": draft["plan_digest"],
                                       "decision": "approve"})
            self.assertEqual(approved["status"], "ACTIVE")
            goal = bus.store.get(draft["goal_id"])
            run = bus.store.claim(goal["goal_id"], utc_now() + timedelta(seconds=1), "interval", None)
            context = {"approval_id": run["approval_id"], "plan_digest": goal["digest"],
                       "permissions": goal["spec"]["permissions"], "budget": goal["spec"]["budget"]}
            search = next(step for step in goal["spec"]["steps"] if step["id"] == "search")
            search_call = {"goal_id": goal["goal_id"], "revision": 1,
                           "action_id": run["run_id"] + ":search", "capability": "web.search",
                           "args": search["args"]}
            read_call = dict(search_call, action_id=run["run_id"] + ":read_1",
                             capability="web.read", args={"url": "https://docs.example.test/one"})
            self.assertEqual(bus.execute(read_call, approved=True, context=context)["error"],
                             "search_receipt_missing")
            result = bus.execute(search_call, approved=True, context=context)
            self.assertTrue(result["ok"])
            self.assertEqual(executor.searches, 1)
            self.assertTrue(bus.execute(search_call, approved=True, context=context)["ok"])
            self.assertEqual(executor.searches, 1)
            selected = select_results(search["args"]["query"], result["output"]["results"], limit=3)
            self.assertEqual(len(selected), 3)
            forged = dict(read_call, args={"url": "https://attacker.example.test/"})
            self.assertEqual(bus.execute(forged, approved=True, context=dict(
                context, step_outputs={"search": {"results": [{"url": forged["args"]["url"]}]}}))["error"],
                             "action_args_changed")
            valid = dict(read_call, args={"url": selected[0]["url"]})
            self.assertTrue(bus.execute(valid, approved=True, context=context)["ok"])
            wrong_rank = dict(valid, action_id=run["run_id"] + ":read_2")
            self.assertEqual(bus.execute(wrong_rank, approved=True, context=context)["error"],
                             "action_args_changed")

    def test_search_goal_runs_through_bus_and_relevant_pages(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            executor = _SearchResearchExecutor(workspace)
            service = GoalService(workspace, _SearchResearchModel(), ApprovedActionBus(workspace, executor))
            draft = service.handle({"type": "goal_propose", "request_id": "bus-search-complete",
                                    "text": "持续整理 Python asyncio 的公开资料"})
            service.handle({"type": "goal_decide", "goal_id": draft["goal_id"],
                            "revision": 1, "plan_digest": draft["plan_digest"],
                            "decision": "approve"})
            run = service.tick()[0]
            self.assertEqual(run["status"], "COMPLETED", run.get("error"))
            self.assertEqual(len(executor.read_urls), 3)

    def test_multiple_source_output_keeps_declared_dynamic_arguments(self):
        planned = {"relative_path": "notes/research.md", "content_from_step": "compose",
                   "sources_from_steps": ["read_1", "read_2"], "versioned_max": 16}
        actual = {"relative_path": "notes/research-v1.md", "content": "提纲",
                  "sources": [{"url": "https://example.org/", "retrieved_at": "2026-09-28T00:00:00Z"}]}
        self.assertTrue(ApprovedActionBus._args_match(planned, actual))
        self.assertFalse(ApprovedActionBus._args_match(planned, dict(actual, unauthorized=True)))

    def test_three_source_goal_uses_approved_bus_and_writes_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            executor = _MultiResearchExecutor(workspace)
            service = GoalService(workspace, _ResearchModel(), ApprovedActionBus(workspace, executor))
            draft = service.handle({"type": "goal_propose", "request_id": "bus-three-sources",
                                    "text": "持续整理 " + " ".join(executor.bodies)})
            self.assertEqual(draft["status"], "DRAFT")
            approved = service.handle({"type": "goal_decide", "goal_id": draft["goal_id"],
                                       "revision": 1, "plan_digest": draft["plan_digest"],
                                       "decision": "approve"})
            self.assertEqual(approved["status"], "ACTIVE")
            run = service.tick()[0]
            self.assertEqual(run["status"], "COMPLETED", run.get("error"))
            self.assertEqual(len(run["receipts"][-1]["output"]["sources"]), 3)
            self.assertTrue((workspace / "notes/research-v1.md").is_file())

    def test_local_agent_uses_bus_for_real_workspace_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            agent = LocalAgent(workspace)
            agent.muse_models = _FixtureModel()
            proposed = agent.handle({"type": "goal_propose", "request_id": "bus-local-agent",
                                     "text": "准备一份演讲资料"})
            self.assertEqual(proposed["status"], "DRAFT")
            approved = agent.handle({"type": "goal_decide", "goal_id": proposed["goal_id"],
                                     "revision": proposed["revision"],
                                     "plan_digest": proposed["plan_digest"], "decision": "approve"})
            self.assertEqual(approved["status"], "ACTIVE")
            runs = agent.handle({"type": "goal_tick"})["results"]
            self.assertEqual(len(runs), 1)
            self.assertEqual(runs[0]["status"], "COMPLETED")
            self.assertTrue((workspace / "notes/speech.md").read_text(encoding="utf-8").startswith("提纲"))
            self.assertTrue(runs[0]["receipts"][-1]["verification"]["readback_matches"])

    def test_local_agent_respects_persisted_capability_revocation(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            agent = LocalAgent(workspace)
            agent.muse_models = _FixtureModel()
            proposed = agent.handle({"type": "goal_propose", "request_id": "bus-revoked",
                                     "text": "准备一份演讲资料"})
            agent.handle({"type": "goal_decide", "goal_id": proposed["goal_id"],
                          "revision": proposed["revision"],
                          "plan_digest": proposed["plan_digest"], "decision": "approve"})
            self.assertTrue(CapabilityCatalog(workspace).revoke("workspace.write_artifact", BUILTIN_SCOPE))
            result = agent.handle({"type": "goal_tick"})["results"][0]
            self.assertNotEqual(result["status"], "COMPLETED")
            self.assertFalse((workspace / "notes/speech.md").exists())
            self.assertEqual(CapabilityCatalog(workspace).get(
                "workspace.write_artifact", BUILTIN_SCOPE)["status"], "revoked")

    def test_current_approved_step_executes(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, executor, bus, call, context = fixture(Path(tmp))
            self.assertTrue(bus.execute(call, approved=True, context=context)["ok"])
            self.assertEqual(len(executor.calls), 1)

    def test_rejects_forged_approval_and_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, executor, bus, call, context = fixture(Path(tmp))
            for changed in ({"approval_id": "approval:forged"}, {"plan_digest": "forged"},
                            {"permissions": {"capabilities": ["workspace.write_artifact"]}},
                            {"budget": {"max_model_tokens": 999999}}, {"run_id": "run:forged"}):
                self.assertFalse(bus.execute(call, approved=True, context=dict(context, **changed))["ok"])
            self.assertFalse(bus.execute(call, approved=False, context=context)["ok"])
            self.assertEqual(executor.calls, [])

    def test_rejects_changed_step_and_expired_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            store, executor, bus, call, context = fixture(Path(tmp))
            for changed in ({"action_id": "run:other:save"},
                            {"action_id": call["action_id"] + ":other"},
                            {"capability": "web.read"},
                            {"args": {"relative_path": "notes/other.md", "content": "changed"}}):
                self.assertFalse(bus.execute(dict(call, **changed), approved=True, context=context)["ok"])
            with store._connect() as db:
                db.execute("UPDATE muse_goals SET approval_expires_at='2000-01-01T00:00:00+00:00'")
            self.assertEqual(bus.execute(call, approved=True, context=context)["error"], "approval_expired")
            self.assertEqual(executor.calls, [])

    def test_finished_run_cannot_execute(self):
        with tempfile.TemporaryDirectory() as tmp:
            store, executor, bus, call, context = fixture(Path(tmp))
            store.finish(call["goal_id"], context["run_id"], "completed", {"ok": True}, None)
            self.assertEqual(bus.execute(call, approved=True, context=context)["error"], "run_not_active")
            self.assertEqual(executor.calls, [])


if __name__ == "__main__":
    unittest.main()
