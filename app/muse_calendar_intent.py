"""Deterministic natural-language parsing for Muse calendar requests.

The small local model is not reliable enough to extract dates and titles, so
this parser is rule-based and fully testable. It only proposes; the host still
shows the parsed result to the user for confirmation before anything is written.

Two entry points matter:

* :func:`parse_calendar_request` — a user telling *Muse* to add something
  ("帮我加个日程：明天下午3点开会"). It requires an explicit scheduling cue.
* :func:`propose_from_mail` — an incoming message that already contains a plan
  ("今晚八点一起吃饭？"). It is deliberately lenient: a time mention in a
  message is enough for Muse to *offer* to schedule it, never to do it.

:func:`is_agreement` / :func:`is_refusal` let the host understand a short
natural reply ("好", "同意", "算了") when a calendar proposal is pending.
"""

from __future__ import annotations

import os
import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

CALENDAR_WORDS = ("日程", "日历", "calendar")
SCHEDULE_VERBS = ("加个", "加入", "加到", "创建", "新建", "安排", "提醒我", "记到", "记一下",
                  "定个", "约", "排个", "帮我记")

_WEEKDAYS = {"一": 0, "二": 1, "三": 2, "四": 3, "五": 4, "六": 5, "日": 6, "天": 6}
_PM_PERIODS = ("下午", "傍晚", "晚上", "中午", "今晚")
_AM_PERIODS = ("凌晨", "早上", "早晨", "上午", "今早")
_CN_DIGITS = {"零": 0, "〇": 0, "一": 1, "二": 2, "两": 2, "三": 3, "四": 4,
              "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
_CN_CLASS = "零〇一二三四五六七八九十两"

_WEEK_PREFIX = ("本周", "这周", "下周", "本星期", "这星期", "下星期",
                "本礼拜", "这礼拜", "下礼拜")
_WEEK_LEAD = "(?:本周|这周|下周|本星期|这星期|下星期|本礼拜|这礼拜|下礼拜|星期|礼拜|周)"

_TIME_RE = re.compile(
    r"(?P<qual>今天|明天|后天|大后天"
    r"|" + _WEEK_LEAD + r"[一二三四五六日天]"
    r"|(?P<month>\d{1,2})月(?P<day>\d{1,2})[日号])?\s*"
    r"(?P<period>凌晨|早上|早晨|上午|中午|下午|傍晚|晚上|今晚|今早)?\s*"
    r"(?P<hour>\d{1,2}|[" + _CN_CLASS + r"]{1,3})\s*"
    r"(?:(?P<sep>[:：])\s*(?P<minute_colon>半|一刻|三刻|\d{1,2}|[" + _CN_CLASS + r"]{1,3})"
    r"|(?P<dot>点)\s*(?P<minute_dot>半|一刻|三刻|\d{1,2}|[" + _CN_CLASS + r"]{1,3})?\s*(?P<unit>分|钟)?)"
)

_CLEAN_WORDS = ("帮我", "麻烦", "请", "给我", "把", "加个日程", "加入日历", "加到日历", "记到日历",
                "创建日程", "新建日程", "加日程", "排个日程", "加进日历", "日程", "日历", "安排",
                "提醒我", "记一下", "帮我记", "加个", "加入", "加到", "加进", "创建", "新建",
                "提醒", "记到", "定个", "排个", "约", "一个", "一下")
_PRONOUNS = ("我们", "咱们", "咱俩", "咱", "大家", "一起", "一块", "我", "你", "来", "去")
_TAIL_WORDS = ("好不好", "怎么样", "行不行", "可以吗", "行吗", "好吗", "要不要", "如何", "怎样",
               "吧", "吗", "呢", "啊", "呀", "哦", "嘛", "哈", "呗", "的", "不", "没")
# Words people use when they change their mind about an existing plan.
_REVISION_WORDS = ("改成", "改为", "改到", "换到", "换成", "变成", "变更", "推迟到", "延到",
                   "提前到", "不是", "而是", "不对", "改成", "改在", "换在", "那就", "算了改")
_CHANGE_HINTS = ("改成", "改为", "改到", "换到", "换成", "变成", "推迟", "延到", "提前",
                 "不是", "改为", "不对", "别")
# Filler that survives after the times are cut out of a correction.
_CHANGE_FILLER = ("去不了", "不了了", "不了", "改天", "再说", "算了", "那就", "那", "就",
                  "是", "吧", "了", "吧。", "呢")
_NOISE_RE = re.compile(r"[，,。.：:；;！!？?、\s\"'“”‘’]+")
_MINUTES_WORD = {"半": 30, "一刻": 15, "三刻": 45}
_DURATION = timedelta(minutes=60)

# Short replies the host uses to confirm/decline a pending calendar proposal.
AGREE_WORDS = ("同意", "可以", "好的", "好呀", "好啊", "好", "行", "没问题", "沒問題", "答应",
               "接受", "愿意", "确认", "就这么定", "去吧", "参加", "准时", "ok", "okay", "yes",
               "成", "恩", "嗯")
REFUSE_WORDS = ("不同意", "不用", "不要", "不加", "别加", "不想", "不必", "不行", "算了",
                "拒绝", "婉拒", "没空", "没时间", "不去", "取消", "不了", "改天", "再说吧",
                "no", "nope")


def local_timezone_name() -> str:
    try:
        link = os.readlink("/etc/localtime")
        if "zoneinfo/" in link:
            return link.split("zoneinfo/", 1)[1]
    except OSError:
        pass
    return "UTC"


def _cn_to_int(token):
    """Convert the clock numbers people actually type: 8, 八, 十, 十五, 二十, 两."""
    if token is None:
        return None
    token = token.strip()
    if not token:
        return None
    if token.isdigit():
        return int(token)
    if token in _MINUTES_WORD:
        return _MINUTES_WORD[token]
    if "十" in token:
        left, _, right = token.partition("十")
        if left and left not in _CN_DIGITS:
            return None
        if right and right not in _CN_DIGITS:
            return None
        return (_CN_DIGITS[left] if left else 1) * 10 + (_CN_DIGITS[right] if right else 0)
    if len(token) == 1 and token in _CN_DIGITS:
        return _CN_DIGITS[token]
    if len(token) <= 3 and all(char in _CN_DIGITS for char in token):
        # "零五"/"零五" style clock minutes written digit by digit.
        return int("".join(str(_CN_DIGITS[char]) for char in token))
    return None


def _polish_title(text: str) -> str:
    """Turn a chatty sentence fragment into a short, human event title."""
    body = text
    for _ in range(4):
        before = body
        for word in _PRONOUNS:
            if body.startswith(word) and len(body) - len(word) >= 2:
                body = body[len(word):]
        for word in _TAIL_WORDS:
            if body.endswith(word) and len(body) > len(word):
                body = body[: -len(word)]
        body = re.sub(r"^[\s的个、,，]+", "", body)
        body = re.sub(r"[\s的、,，]+$", "", body)
        if body == before:
            break
    return body.strip()


def _title_from(text: str, spans, extra_words=()) -> str:
    """Build a title from the text with every time phrase cut out.

    ``spans`` is a list of ``(start, end)`` offsets to drop, so a correction
    like "8点去不了，改成9点" does not leak "8点" or "9点" into the title.
    """
    keep, cursor = [], 0
    for start, end in sorted(spans):
        if start < cursor:
            continue
        keep.append(text[cursor:start])
        cursor = end
    keep.append(text[cursor:])
    body = " ".join(keep)
    for word in tuple(_REVISION_WORDS) + _CLEAN_WORDS + tuple(extra_words):
        body = body.replace(word, " ")
    body = _NOISE_RE.sub(" ", body).strip()
    body = re.sub(r"^[\s的个]+", "", body)
    return _polish_title(body)


def _resolve_date(match: re.Match, current: datetime):
    """Resolve the day phrase against a real week.

    ``下周X`` means the next calendar week, so on Tue 2026-09-29 ``下周一`` is
    Mon 2026-10-05 (not a week later). ``周五``/``星期X`` means the next such
    weekday, and today's weekday rolls to the following week.
    """
    qual, month, day = match.group("qual"), match.group("month"), match.group("day")
    if not qual:
        return None
    if qual in ("今天", "明天", "后天", "大后天"):
        offset = {"今天": 0, "明天": 1, "后天": 2, "大后天": 3}[qual]
        return (current + timedelta(days=offset)).date()
    weekday = _WEEKDAYS.get(qual[-1])
    if weekday is None:
        return None
    monday = current - timedelta(days=current.weekday())
    if any(qual.startswith(prefix) for prefix in ("下周", "下星期", "下礼拜")):
        return (monday + timedelta(days=7 + weekday)).date()
    if any(qual.startswith(prefix) for prefix in ("本周", "这周", "本星期", "这星期",
                                                  "本礼拜", "这礼拜")):
        return (monday + timedelta(days=weekday)).date()
    target = monday + timedelta(days=weekday)
    if target.date() <= current.date():
        target = target + timedelta(days=7)
    return target.date()


def _resolve_time(match: re.Match, current: datetime, zone: ZoneInfo, zone_name: str):
    """Turn one parsed time expression into ``(start_dt, end_dt, consumed_end)``."""
    hour = _cn_to_int(match.group("hour"))
    if hour is None or not 0 <= hour <= 23:
        return None
    consumed = match.end()
    if match.group("sep"):
        minute = _cn_to_int(match.group("minute_colon"))
    else:
        raw_minute = match.group("minute_dot")
        minute = _cn_to_int(raw_minute) if raw_minute else 0
        if (minute and raw_minute and not raw_minute.isdigit()
                and raw_minute not in _MINUTES_WORD and len(raw_minute) == 1
                and not match.group("unit")):
            # "八点一起吃饭" — a lone Chinese digit right after 点 starts a word
            # (一起/一块), it is not the minute. Keep it out of the match so the
            # title keeps its real wording.
            minute = 0
            consumed = match.end("dot")
    if minute is None or not 0 <= minute <= 59:
        return None
    period = match.group("period")
    if period in _PM_PERIODS and hour < 12:
        hour += 12
    elif period in _AM_PERIODS and hour == 12:
        hour = 0
    target_date = _resolve_date(match, current)
    if target_date is None and period is None and 1 <= hour <= 11:
        # A bare hour means the next time that clock reading occurs today.
        am = current.replace(hour=hour, minute=minute, second=0, microsecond=0)
        pm = am.replace(hour=hour + 12)
        start_dt = am if am > current else (pm if pm > current else am + timedelta(days=1))
    else:
        if target_date is None:
            target_date = current.date()
        start_dt = datetime(target_date.year, target_date.month, target_date.day,
                            hour, minute, tzinfo=zone)
        if target_date == current.date() and start_dt <= current:
            start_dt = start_dt + timedelta(days=1)
    return start_dt, start_dt + _DURATION, consumed


def _zone_and_now(now):
    zone_name = local_timezone_name()
    try:
        zone = ZoneInfo(zone_name)
    except Exception:
        return None, None, None
    return zone, (now.astimezone(zone) if now else datetime.now(zone)), zone_name


def parse_calendar_request(text, now: datetime | None = None, *, require_cue: bool = True) -> dict | None:
    if not isinstance(text, str):
        return None
    raw = text.strip()
    if not raw or len(raw) > 200:
        return None
    zone, current, zone_name = _zone_and_now(now)
    if zone is None:
        return None
    match = _TIME_RE.search(raw)
    if match is None:
        return None
    if require_cue and not (any(word in raw for word in CALENDAR_WORDS)
                            or any(word in raw for word in SCHEDULE_VERBS)):
        return None
    resolved = _resolve_time(match, current, zone, zone_name)
    if resolved is None:
        return None
    start_dt, end_dt, consumed = resolved
    title = _title_from(raw, [(match.start(), consumed)]) or raw
    return {"title": title[:160], "start": start_dt.isoformat(),
            "end": end_dt.isoformat(), "timezone": zone_name}


def looks_like_change(text) -> bool:
    """True when a message reads as a correction: "改成9点", "不是8点，是9点"."""
    if not isinstance(text, str):
        return False
    raw = text.strip()
    return any(word in raw for word in _CHANGE_HINTS)


def parse_calendar_change(text, now: datetime | None = None) -> dict | None:
    """Read a *correction* to a plan already on the table.

    People correct by appending: "8点去不了，改成9点". The **last** time wins,
    and none of the times may leak into the title.
    """
    if not isinstance(text, str):
        return None
    raw = text.strip()
    if not raw or len(raw) > 200:
        return None
    zone, current, zone_name = _zone_and_now(now)
    if zone is None:
        return None
    matches = list(_TIME_RE.finditer(raw))
    if not matches:
        return None
    resolved = _resolve_time(matches[-1], current, zone, zone_name)
    if resolved is None:
        return None
    start_dt, end_dt, _ = resolved
    spans = []
    for match in matches:
        span = _resolve_time(match, current, zone, zone_name)
        spans.append((match.start(), span[2] if span else match.end()))
    return {"title": _title_from(raw, spans, _CHANGE_FILLER)[:160], "start": start_dt.isoformat(),
            "end": end_dt.isoformat(), "timezone": zone_name}


def describe_proposal(proposal: dict, now: datetime | None = None) -> str:
    """A short, unambiguous description such as ``今晚 20:00 吃饭``."""
    zone_name = proposal.get("timezone") or local_timezone_name()
    try:
        zone = ZoneInfo(zone_name)
        current = now.astimezone(zone) if now else datetime.now(zone)
        start = datetime.fromisoformat(str(proposal["start"]))
    except Exception:
        return str(proposal.get("title") or "日程")
    delta = (start.date() - current.date()).days
    label = {0: "今天", 1: "明天", 2: "后天"}.get(delta)
    if label is None:
        if 0 <= delta <= 6:
            label = "周" + "一二三四五六日"[start.weekday()]
        else:
            label = f"{start.month}月{start.day}日"
    return f"{label} {start.strftime('%H:%M')} {proposal.get('title', '')}".strip()


def _period_word(hour: int) -> str:
    if hour < 6:
        return "凌晨"
    if hour < 9:
        return "早上"
    if hour < 12:
        return "上午"
    if hour == 12:
        return "中午"
    if hour < 18:
        return "下午"
    return "晚上"


def describe_proposal_friendly(proposal: dict, now: datetime | None = None) -> str:
    """A spoken-style time, the way a person would write it: ``今晚8点``."""
    zone_name = proposal.get("timezone") or local_timezone_name()
    try:
        zone = ZoneInfo(zone_name)
        current = now.astimezone(zone) if now else datetime.now(zone)
        start = datetime.fromisoformat(str(proposal["start"]))
    except Exception:
        return str(proposal.get("title") or "这个时间")
    delta = (start.date() - current.date()).days
    hour, minute = start.hour, start.minute
    if delta == 0:
        day, period = ("今晚" if hour >= 18 else "今天"), ""
    elif delta == 1:
        day, period = "明天", _period_word(hour)
    elif delta == 2:
        day, period = "后天", _period_word(hour)
    elif 0 <= delta <= 6:
        day, period = "周" + "一二三四五六日"[start.weekday()], _period_word(hour)
    else:
        day, period = f"{start.month}月{start.day}日", _period_word(hour)
    if minute == 0:
        clock = f"{hour % 12 or 12}点"
    elif minute == 30:
        clock = f"{hour % 12 or 12}点半"
    else:
        clock = f"{hour % 12 or 12}点{minute}分"
    return f"{day}{period}{clock}"


def propose_from_mail(subject, body, now: datetime | None = None) -> dict | None:
    """Offer to schedule a plan that an incoming message already mentions.

    Lenient by design: any time mention is enough to *ask* the user. It never
    writes anything; the caller still shows a confirmation card.
    """
    subject = (subject or "").strip()
    body = (body or "").strip()
    if not subject and not body:
        return None
    proposal = None
    for candidate in (body, subject, f"{subject} {body}".strip()):
        if not candidate:
            continue
        proposal = parse_calendar_request(candidate, now, require_cue=False)
        if proposal is not None:
            break
    if proposal is None:
        return None
    proposal["source_text"] = (body or subject)[:200]
    proposal["summary"] = describe_proposal(proposal, now)
    return proposal


def _normalized(text) -> str:
    if not isinstance(text, str):
        return ""
    return _NOISE_RE.sub("", text.strip().lower())


def is_agreement(text) -> bool:
    """True for short natural replies that accept a pending proposal."""
    value = _normalized(text)
    if not value or len(value) > 16:
        return False
    if any(word in value for word in ("不", "别", "取消", "算了")):
        return False
    return any(word in value for word in AGREE_WORDS)


def is_refusal(text) -> bool:
    """True for short natural replies that decline a pending proposal."""
    value = _normalized(text)
    if not value or len(value) > 16:
        return False
    return any(word in value for word in REFUSE_WORDS)
