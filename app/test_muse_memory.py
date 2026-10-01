import sqlite3
import tempfile
import unittest
from pathlib import Path

from memory_store import MemoryStore


class MuseMemoryTests(unittest.TestCase):
    def test_cjk_question_stops_recalling_corrected_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            memory = MemoryStore(Path(tmp))
            memory.remember("fact", "user", "午餐安排已确定", "lunch:1", record_type="fact")
            self.assertTrue(memory.search("午餐安排怎么样"))
            record_id = memory.list_records()[0]["id"]
            self.assertTrue(memory.correct(record_id, "晚餐计划已确定"))
            self.assertEqual(memory.search("午餐安排怎么样"), [])
            self.assertTrue(memory.search("晚餐计划怎么样"))

    def test_cjk_question_stops_recalling_deleted_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            memory = MemoryStore(Path(tmp))
            memory.remember("fact", "user", "午餐安排已确定", "lunch:2", record_type="fact")
            record_id = memory.list_records()[0]["id"]
            self.assertTrue(memory.delete(record_id))
            self.assertEqual(memory.search("午餐安排怎么样"), [])

    def test_legacy_rows_survive_migration_and_can_be_managed(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            path = workspace / "memory.sqlite3"
            with sqlite3.connect(str(path)) as db:
                db.execute("CREATE TABLE memories (id INTEGER PRIMARY KEY, kind TEXT NOT NULL, "
                           "source TEXT NOT NULL, external_id TEXT UNIQUE, content TEXT NOT NULL, "
                           "created_at TEXT NOT NULL)")
                db.execute("INSERT INTO memories(kind,source,external_id,content,created_at) "
                           "VALUES ('chat_user','local_user','legacy:1','旧有的项目记忆','2026-09-01T00:00:00+00:00')")
            memory = MemoryStore(workspace)
            self.assertEqual(memory.search("旧有")[0]["content"], "旧有的项目记忆")
            item = memory.list_records()[0]
            self.assertTrue(memory.correct(item["id"], "已纠正的项目记忆"))
            self.assertTrue(memory.pin(item["id"], True))
            self.assertEqual(memory.search("已纠正")[0]["content"], "已纠正的项目记忆")
            self.assertTrue(memory.list_records()[0]["pinned"])
            self.assertTrue(memory.delete(item["id"]))
            self.assertEqual(memory.search("已纠正"), [])
            memory.remember("chat_user", "local_user", "不能复活", "legacy:1")
            self.assertEqual(memory.count(), 0)
            with sqlite3.connect(str(path)) as db:
                self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0], "ok")

    def test_scope_isolation_and_recording_pause(self):
        with tempfile.TemporaryDirectory() as tmp:
            memory = MemoryStore(Path(tmp))
            memory.remember("fact", "file", "教师项目事实", "fact:1",
                            scope="school", account_scope="teacher", record_type="fact")
            memory.remember("fact", "file", "个人项目事实", "fact:1",
                            scope="personal", account_scope="local", record_type="fact")
            self.assertEqual(len(memory.search("项目事实")), 1)
            self.assertEqual(memory.search("项目事实")[0]["content"], "个人项目事实")
            self.assertEqual(memory.search("项目事实", scope="school", account_scope="teacher")[0]["content"],
                             "教师项目事实")
            memory.set_recording(False, scope="school", account_scope="teacher")
            memory.remember("fact", "file", "不应记录", "fact:2", scope="school", account_scope="teacher")
            self.assertEqual(memory.count(scope="school", account_scope="teacher"), 1)
            self.assertFalse(memory.recording_enabled("school", "teacher"))
            self.assertFalse(MemoryStore(Path(tmp)).recording_enabled("school", "teacher"))

    def test_goal_result_aggregation_requires_selected_scopes_and_respects_forget(self):
        with tempfile.TemporaryDirectory() as tmp:
            memory = MemoryStore(Path(tmp))
            memory.remember("goal_result", "muse_goal", "目标甲 已验证完成", "goal:a",
                            account_scope="local-workspace", record_type="fact", confirmed=True)
            memory.remember("goal_result", "muse_goal", "目标乙 已验证完成", "goal:b",
                            account_scope="local-qqmail", record_type="fact", confirmed=True)
            memory.remember("goal_result", "muse_goal", "午餐安排 已完成并验证", "goal:c",
                            account_scope="qqmail:account-7", record_type="fact", confirmed=True)
            self.assertEqual(memory.search_goal_results("午餐安排怎么样", ["qqmail:account-7"])[0]["account_scope"],
                             "qqmail:account-7")
            self.assertEqual(memory.search_goal_results("已验证完成", ["local-workspace"])[0]["account_scope"],
                             "local-workspace")
            self.assertEqual(len(memory.search_goal_results("已验证完成", ["local-workspace"])), 1)
            self.assertEqual(len(memory.search_goal_results("已验证完成", ["local-workspace", "local-qqmail"])), 2)
            self.assertEqual(memory.list_goal_result_scopes(), ["local-qqmail", "local-workspace", "qqmail:account-7"])
            with self.assertRaises(ValueError):
                memory.search_goal_results("已验证完成", [])
            memory.set_recording(False, account_scope="local-qqmail")
            self.assertEqual(len(memory.search_goal_results("已验证完成", ["local-workspace", "local-qqmail"])), 1)
            self.assertEqual(memory.list_goal_result_scopes(), ["local-workspace", "qqmail:account-7"])
            record = memory.list_records(account_scope="local-workspace")[0]
            self.assertTrue(memory.delete(record["id"], account_scope="local-workspace"))
            self.assertEqual(memory.search_goal_results("已验证完成", ["local-workspace"]), [])
            self.assertEqual(memory.list_goal_result_scopes(), ["qqmail:account-7"])


if __name__ == "__main__":
    unittest.main()
