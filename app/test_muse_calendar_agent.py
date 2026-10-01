import tempfile
import unittest
from pathlib import Path

from agent_app import LocalAgent


class FakeCalendar:
    def __init__(self):
        self.created = []
        self.permission = "FULL_ACCESS"

    def request_permission(self):
        return {"status": self.permission}

    def create_event(self, *, title, start, end, timezone_name, calendar_id=None,
                     notes=None, approved=False):
        if not approved:
            return {"status": "WAITING_APPROVAL"}
        if self.permission != "FULL_ACCESS":
            return {"status": "WAITING_USER_PERMISSION", "authorization": self.permission}
        self.created.append({"title": title, "start": start, "end": end,
                             "calendar_id": calendar_id, "notes": notes})
        return {"status": "COMPLETED", "readback_matches": True,
                "event": {"title": title, "start": start, "end": end, "event_id": "evt-1"},
                "calendar_id": calendar_id or "default-cal"}


class AgentCalendarTests(unittest.TestCase):
    def agent(self, tmp):
        agent = LocalAgent(Path(tmp))
        fake = FakeCalendar()
        agent._muse_calendar = fake
        return agent, fake

    def test_calendar_request_proposes_then_creates_with_readback(self):
        with tempfile.TemporaryDirectory() as tmp:
            agent, fake = self.agent(tmp)
            proposed = agent.handle({"type": "chat_message", "text": "帮我加个日程：明天下午3点开会"})
            self.assertEqual(proposed["status"], "PROPOSED")
            self.assertEqual(proposed["route"], "calendar_create")
            self.assertTrue(proposed["task_card"]["requires_confirmation"])
            self.assertEqual(proposed["task_card"]["metadata"]["title"], "开会")
            self.assertEqual(fake.created, [])
            confirmed = agent.handle({"type": "confirm", "approved": True})
            self.assertTrue(confirmed["ok"])
            self.assertEqual(confirmed["result_card"]["status"], "COMPLETED")
            self.assertEqual(confirmed["result_card"]["verification"], "READBACK_MATCH")
            self.assertEqual(fake.created[0]["title"], "开会")

    def test_rejection_never_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            agent, fake = self.agent(tmp)
            agent.handle({"type": "chat_message", "text": "加日程：睡觉 今晚8点"})
            rejected = agent.handle({"type": "confirm", "approved": False})
            self.assertEqual(rejected["task_card"]["status"], "rejected")
            self.assertEqual(fake.created, [])

    def test_missing_permission_reports_blocked_permission(self):
        with tempfile.TemporaryDirectory() as tmp:
            agent, fake = self.agent(tmp)
            fake.permission = "NOT_DETERMINED"
            agent.handle({"type": "chat_message", "text": "加日程：睡觉 今晚8点"})
            result = agent.handle({"type": "confirm", "approved": True})
            self.assertFalse(result["ok"])
            self.assertEqual(result["result_card"]["status"], "BLOCKED_PERMISSION")
            self.assertEqual(fake.created, [])

    def test_plain_chat_still_replies_normally(self):
        with tempfile.TemporaryDirectory() as tmp:
            agent, fake = self.agent(tmp)
            result = agent.handle({"type": "chat_message", "text": "今天天气怎么样"})
            self.assertNotEqual(result.get("route"), "calendar_create")
            self.assertEqual(fake.created, [])

    def test_mail_reply_offers_calendar_when_a_time_is_mentioned(self):
        with tempfile.TemporaryDirectory() as tmp:
            agent, fake = self.agent(tmp)
            agent.pending_mail_reply = {"request_id": "r1", "sender": "friend@example.com",
                                        "card_id": "card-1", "mail_text": "我们明天下午3点见面吧"}
            result = agent._mail_reply_result({"request_id": "r1", "status": "SENT"})
            self.assertEqual(result["status"], "REPLY_SENT")
            self.assertIn("task_card", result)
            metadata = result["task_card"]["metadata"]
            self.assertEqual(metadata["kind"], "calendar_create")
            self.assertIn("见面", metadata["title"])
            self.assertEqual(metadata["start"][11:16], "15:00")
            confirmed = agent.handle({"type": "confirm", "approved": True})
            self.assertTrue(confirmed["ok"])
            self.assertEqual(fake.created[0]["title"], metadata["title"])

    def test_mail_reply_without_a_time_only_prompts(self):
        with tempfile.TemporaryDirectory() as tmp:
            agent, fake = self.agent(tmp)
            agent.pending_mail_reply = {"request_id": "r2", "sender": "friend@example.com",
                                        "card_id": "card-2", "mail_text": "收到，谢谢"}
            result = agent._mail_reply_result({"request_id": "r2", "status": "SENT"})
            self.assertEqual(result["status"], "REPLY_SENT")
            self.assertNotIn("task_card", result)
            self.assertIn("加日程", result["result_card"]["next_step"])
            self.assertEqual(fake.created, [])

    def test_mail_invitation_in_chinese_numerals_offers_a_named_proposal(self):
        with tempfile.TemporaryDirectory() as tmp:
            agent, fake = self.agent(tmp)
            agent.pending_mail_reply = {"request_id": "r3", "sender": "laowang@example.com",
                                        "subject": "周末约饭",
                                        "card_id": "card-3", "mail_text": "我们今晚八点一起吃饭？"}
            result = agent._mail_reply_result({"request_id": "r3", "status": "SENT"})
            metadata = result["task_card"]["metadata"]
            self.assertEqual(metadata["title"], "吃饭")
            self.assertEqual(metadata["start"][11:16], "20:00")
            self.assertEqual(metadata["origin"], "mail_reply")
            # The proposal is worded for a person, not as a machine trace.
            self.assertIn("吃饭", result["task_card"]["title"])
            self.assertIn("加进日历", result["chat_reply"])
            self.assertIn("加进日历", result["result_card"]["next_step"])
            self.assertEqual(fake.created, [])

    def test_replying_hao_in_chat_confirms_the_pending_calendar_card(self):
        with tempfile.TemporaryDirectory() as tmp:
            agent, fake = self.agent(tmp)
            agent.pending_mail_reply = {"request_id": "r4", "sender": "laowang@example.com",
                                        "subject": "周末约饭",
                                        "card_id": "card-4", "mail_text": "我们今晚八点一起吃饭？"}
            agent._mail_reply_result({"request_id": "r4", "status": "SENT"})
            answered = agent.handle({"type": "chat_message", "text": "好"})
            self.assertTrue(answered["ok"])
            self.assertEqual(answered["route"], "calendar_create")
            self.assertIn("已经加进日历", answered["chat_reply"])
            self.assertEqual(fake.created[0]["title"], "吃饭")
            self.assertEqual(fake.created[0]["start"][11:16], "20:00")

    def test_replying_suan_le_in_chat_declines_the_pending_calendar_card(self):
        with tempfile.TemporaryDirectory() as tmp:
            agent, fake = self.agent(tmp)
            agent.handle({"type": "chat_message", "text": "加日程：睡觉 今晚8点"})
            answered = agent.handle({"type": "chat_message", "text": "算了"})
            self.assertTrue(answered["ok"])
            self.assertIn("不加日历", answered["chat_reply"])
            self.assertEqual(fake.created, [])

    def test_a_new_calendar_request_replaces_the_pending_proposal(self):
        with tempfile.TemporaryDirectory() as tmp:
            agent, fake = self.agent(tmp)
            agent.handle({"type": "chat_message", "text": "加日程：睡觉 今晚8点"})
            second = agent.handle({"type": "chat_message", "text": "加日程：开会 明天上午10点"})
            self.assertEqual(second["status"], "PROPOSED")
            self.assertEqual(second["task_card"]["metadata"]["title"], "开会")
            agent.handle({"type": "chat_message", "text": "好的"})
            self.assertEqual([item["title"] for item in fake.created], ["开会"])

    def test_question_tail_never_becomes_the_title(self):
        with tempfile.TemporaryDirectory() as tmp:
            agent, fake = self.agent(tmp)
            proposed = agent.handle({"type": "chat_message", "text": "加日程：8点去咖啡厅不"})
            self.assertEqual(proposed["task_card"]["metadata"]["title"], "咖啡厅")
            self.assertEqual(proposed["task_card"]["metadata"]["start"][11:16], "20:00")

    def test_correcting_the_time_replaces_the_pending_card(self):
        # The reported bug: "8点去" then "8点去不了，改成9点" used to keep 8点.
        with tempfile.TemporaryDirectory() as tmp:
            agent, fake = self.agent(tmp)
            agent.handle({"type": "chat_message", "text": "加日程：8点去咖啡厅不"})
            revised = agent.handle({"type": "chat_message", "text": "8点去不了，改成9点"})
            self.assertEqual(revised["status"], "PROPOSED")
            self.assertEqual(revised["task_card"]["metadata"]["start"][11:16], "21:00")
            self.assertEqual(revised["task_card"]["metadata"]["title"], "咖啡厅")
            self.assertIn("改成", revised["chat_reply"])
            self.assertEqual(fake.created, [])
            agent.handle({"type": "chat_message", "text": "好"})
            self.assertEqual(len(fake.created), 1)
            self.assertEqual(fake.created[0]["start"][11:16], "21:00")
            self.assertEqual(fake.created[0]["title"], "咖啡厅")

    def test_correction_survives_a_mail_born_proposal(self):
        with tempfile.TemporaryDirectory() as tmp:
            agent, fake = self.agent(tmp)
            agent.pending_mail_reply = {"request_id": "r5", "sender": "laowang@example.com",
                                        "subject": "周末约饭",
                                        "card_id": "card-5", "mail_text": "我们今晚八点一起吃饭？"}
            agent._mail_reply_result({"request_id": "r5", "status": "SENT"})
            revised = agent.handle({"type": "chat_message", "text": "改成九点半"})
            self.assertEqual(revised["task_card"]["metadata"]["start"][11:16], "21:30")
            self.assertEqual(revised["task_card"]["metadata"]["origin"], "mail_reply")
            self.assertEqual(revised["task_card"]["metadata"]["title"], "吃饭")

    def test_cannot_go_declines_instead_of_revising(self):
        with tempfile.TemporaryDirectory() as tmp:
            agent, fake = self.agent(tmp)
            agent.handle({"type": "chat_message", "text": "加日程：8点去咖啡厅不"})
            answered = agent.handle({"type": "chat_message", "text": "8点去不了了"})
            self.assertIn("不加日历", answered["chat_reply"])
            self.assertEqual(fake.created, [])

    def test_chat_proposal_reply_is_human_and_states_the_time(self):
        with tempfile.TemporaryDirectory() as tmp:
            agent, fake = self.agent(tmp)
            proposed = agent.handle({"type": "chat_message", "text": "帮我加个日程：明天下午3点开会"})
            self.assertIn("开会", proposed["chat_reply"])
            self.assertIn("明天下午3点", proposed["chat_reply"])
            self.assertIn("明天下午3点", proposed["task_card"]["title"])
            # The exact clock is still on the card so the user can verify it.
            self.assertIn("15:00", proposed["task_card"]["steps"][1])

    def test_agreeing_guidance_produces_an_agreeing_draft(self):
        with tempfile.TemporaryDirectory() as tmp:
            agent, fake = self.agent(tmp)
            session = {"state": "NEEDS_GUIDANCE", "card_id": "card-9",
                       "sender": "laowang@example.com", "subject": "周末约饭",
                       "summary": "约饭", "mail_text": "我们今晚八点一起吃饭？"}
            agent.pending_mail_reply = session
            result = agent._mail_guidance({"card_id": "card-9", "text": "同意"})
            draft = result["result_card"]["draft"]
            self.assertIn("好的", draft)
            self.assertIn("今晚8点", draft)
            self.assertNotIn("稍后给你答复", draft)

    def test_agreeing_guidance_without_a_time_asks_for_details(self):
        with tempfile.TemporaryDirectory() as tmp:
            agent, fake = self.agent(tmp)
            agent.pending_mail_reply = {"state": "NEEDS_GUIDANCE", "card_id": "card-10",
                                        "sender": "friend@example.com", "subject": "聚一下",
                                        "summary": "聚一下", "mail_text": "周末出来见面吗？"}
            result = agent._mail_guidance({"card_id": "card-10", "text": "可以"})
            self.assertIn("愿意", result["result_card"]["draft"])


if __name__ == "__main__":
    unittest.main()
