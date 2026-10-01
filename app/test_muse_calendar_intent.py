import unittest
from datetime import datetime
from zoneinfo import ZoneInfo

from muse_calendar_intent import (describe_proposal, describe_proposal_friendly,
                                  is_agreement, is_refusal, parse_calendar_change,
                                  parse_calendar_request, propose_from_mail)


class CalendarIntentTests(unittest.TestCase):
    NOW = datetime(2026, 9, 29, 14, 45, tzinfo=ZoneInfo("Asia/Shanghai"))  # a Tuesday

    def parse(self, text):
        return parse_calendar_request(text, self.NOW)

    def test_bare_evening_hour_uses_next_clock_reading(self):
        result = self.parse("创建一个 8 点睡觉的")
        self.assertEqual(result["title"], "睡觉")
        self.assertEqual(result["start"][:10], "2026-09-29")
        self.assertEqual(result["start"][11:16], "20:00")
        self.assertEqual(result["end"][11:16], "21:00")

    def test_relative_day_and_pm_period(self):
        result = self.parse("帮我加个日程：明天下午3点开会")
        self.assertEqual(result["title"], "开会")
        self.assertEqual(result["start"][:10], "2026-09-30")
        self.assertEqual(result["start"][11:16], "15:00")

    def test_weekday_with_am_period_and_minutes(self):
        result = self.parse("提醒我周五上午10点交材料")
        self.assertEqual(result["title"], "交材料")
        self.assertEqual(result["start"][:10], "2026-10-02")  # next Friday
        self.assertEqual(result["start"][11:16], "10:00")

    def test_half_hour_and_tonight(self):
        result = self.parse("加日程：睡觉 今晚8点半")
        self.assertEqual(result["title"], "睡觉")
        self.assertEqual(result["start"][:10], "2026-09-29")
        self.assertEqual(result["start"][11:16], "20:30")

    def test_next_week_day_is_the_following_calendar_week(self):
        # Tuesday 2026-09-29 -> next week's Monday is 2026-10-05, not 10-12.
        result = self.parse("下周一 9:30 项目评审 加到日历")
        self.assertEqual(result["title"], "项目评审")
        self.assertEqual(result["start"][:10], "2026-10-05")
        self.assertEqual(result["start"][11:16], "09:30")

    def test_this_week_day_stays_in_the_current_week(self):
        result = self.parse("加日程：本周五 下午2点 述职")
        self.assertEqual(result["start"][:10], "2026-10-02")

    def test_chinese_numerals_are_understood(self):
        self.assertEqual(self.parse("加个日程：八点半 吃药")["start"][11:16], "20:30")
        self.assertEqual(self.parse("加日程：八点三十 吃药")["start"][11:16], "20:30")
        self.assertEqual(self.parse("加日程：明天下午三点 和老王开会")["start"][11:16], "15:00")
        self.assertEqual(self.parse("加日程：晚上八点一刻 看电影")["start"][11:16], "20:15")
        self.assertEqual(self.parse("加日程：8点15分 出发")["start"][11:16], "20:15")

    def test_lone_chinese_digit_after_hour_is_a_word_not_a_minute(self):
        # "八点一起吃饭" means 20:00 + 一起, never 20:01.
        result = self.parse("加日程：今晚八点一起吃饭")
        self.assertEqual(result["start"][11:16], "20:00")
        self.assertEqual(result["title"], "吃饭")

    def test_question_tail_is_not_part_of_the_title(self):
        # "8点去咖啡厅不" is "shall we go at 8"; the title is 咖啡厅.
        self.assertEqual(self.parse("加日程：8点去咖啡厅不")["title"], "咖啡厅")
        self.assertEqual(self.parse("加日程：8点睡觉不")["title"], "睡觉")
        self.assertEqual(self.parse("加个日程：明天下午3点开会不")["title"], "开会")
        self.assertEqual(self.parse("加日程：8点去咖啡厅吗")["title"], "咖啡厅")

    def test_plain_sentences_are_not_calendar_requests(self):
        self.assertIsNone(self.parse("他8点说的"))
        self.assertIsNone(self.parse("今天天气怎么样"))
        self.assertIsNone(self.parse(""))

    def test_out_of_range_hour_is_rejected(self):
        self.assertIsNone(self.parse("加日程：25点开会"))


class MailProposalTests(unittest.TestCase):
    NOW = datetime(2026, 9, 29, 14, 45, tzinfo=ZoneInfo("Asia/Shanghai"))

    def test_a_time_in_the_message_becomes_a_proposal(self):
        proposal = propose_from_mail("周末约饭", "我们今晚八点一起吃饭？", self.NOW)
        self.assertIsNotNone(proposal)
        self.assertEqual(proposal["title"], "吃饭")
        self.assertEqual(proposal["start"][11:16], "20:00")
        self.assertEqual(describe_proposal(proposal, self.NOW), "今天 20:00 吃饭")

    def test_message_without_a_time_proposes_nothing(self):
        self.assertIsNone(propose_from_mail("收到", "收到，谢谢", self.NOW))

    def test_subject_is_used_when_the_body_has_no_time(self):
        proposal = propose_from_mail("周五下午两点团建", "记得来", self.NOW)
        self.assertIsNotNone(proposal)
        self.assertEqual(proposal["start"][11:16], "14:00")

    def test_readable_description_uses_weekday_inside_the_week(self):
        proposal = propose_from_mail("", "周六下午两点一起打球", self.NOW)
        self.assertIsNotNone(proposal)
        self.assertEqual(proposal["title"], "打球")
        self.assertTrue(describe_proposal(proposal, self.NOW).startswith("周六"))

    def test_friendly_description_reads_like_speech(self):
        cases = [("我们今晚八点一起吃饭？", "今晚8点"),
                 ("明天下午3点见面吧", "明天下午3点"),
                 ("周六上午十点打球", "周六上午10点")]
        for body, expected in cases:
            proposal = propose_from_mail("", body, self.NOW)
            self.assertIsNotNone(proposal, body)
            self.assertEqual(describe_proposal_friendly(proposal, self.NOW), expected)


class ChangeRequestTests(unittest.TestCase):
    NOW = datetime(2026, 9, 29, 14, 45, tzinfo=ZoneInfo("Asia/Shanghai"))

    def change(self, text):
        return parse_calendar_change(text, self.NOW)

    def test_the_last_time_wins(self):
        # "8点去不了，改成9点" -> 21:00, not the abandoned 20:00.
        result = self.change("8点去不了，改成9点")
        self.assertEqual(result["start"][11:16], "21:00")
        self.assertEqual(result["title"], "")

    def test_short_corrections_resolve_to_the_new_time_only(self):
        self.assertEqual(self.change("改成9点")["start"][11:16], "21:00")
        self.assertEqual(self.change("不是8点，是9点")["start"][11:16], "21:00")
        self.assertEqual(self.change("8点半吧")["start"][11:16], "20:30")
        self.assertEqual(self.change("推迟到9点")["start"][11:16], "21:00")
        self.assertEqual(self.change("改为明天下午4点")["start"][11:16], "16:00")

    def test_a_new_title_in_a_correction_is_kept(self):
        result = self.change("8点改成9点去咖啡厅")
        self.assertEqual(result["start"][11:16], "21:00")
        self.assertEqual(result["title"], "咖啡厅")

    def test_change_without_a_time_is_not_a_change(self):
        self.assertIsNone(self.change("算了"))
        self.assertIsNone(self.change("好"))

    def test_cannot_go_is_a_refusal(self):
        self.assertTrue(is_refusal("8点去不了了"))
        self.assertFalse(is_agreement("8点去不了了"))


class AgreementTests(unittest.TestCase):
    def test_short_agreements(self):
        for text in ("好", "好的", "同意", "可以呀", "行", "没问题", "ok", "我已经同意了"):
            self.assertTrue(is_agreement(text), text)

    def test_short_refusals(self):
        for text in ("算了", "不用了", "不同意", "不行", "不加", "没空"):
            self.assertTrue(is_refusal(text), text)
            self.assertFalse(is_agreement(text), text)

    def test_long_sentences_are_not_treated_as_short_replies(self):
        self.assertFalse(is_agreement("我同意这个方案，但是还有一些细节需要再讨论一下再说"))
        self.assertFalse(is_refusal("这个方案我暂时不能接受，因为时间安排上和我另外一个会议冲突了"))


if __name__ == "__main__":
    unittest.main()
