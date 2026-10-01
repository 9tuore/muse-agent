# G-01 UI integration notes

Scope: `official_muse/app/bundle/main.splash` at `7451bdd` (calendar timestamp fix) on `codex/muse-official-migration`. These are local developer checks, not Mail or Calendar live acceptance.

## Source and tests

- Main Splash SHA-256: `084ebdfec92df1f6c069115bc105e96cd61560269f09c48f176d26261fbf5898`.
- Stock release card-host loaded the prior `9e41ece` source (SHA-256 `6f45c85154cb9248017b41e1867f59f53877ac64d7d5d3483da4388daf423576`, 180064 bytes) at 990×539, created and approved a Goal, wrote and read back `results/result-1790748288-530769425.json` (SHA-256 `b56c99c6a5aa4cb1a99cf6581b281ab8a17c1ec2f44a7d227212c053e597954e`), and restored that Goal/Run with the same app-data after restart. This test used port 8253 then 8254 and app-data `/tmp/muse-g01-calendar-state2`.
- The same prior source, an isolated stock host manifest with `mail`, `model`, `storage`, and fresh app-data `/tmp/muse-g01-narrow-mail` loaded at requested 412×892 on port 8259. The actual window was 412×805; `/snap` showed 36 widgets, central view 296 px wide and input 262 px wide. This does not verify the extended Shell or Calendar service.
- A `/tmp` only fixture forced calendar grant/full-access state and an in-memory test calendar to exercise the UI branch. Before the timestamp fix, real TextInput `.val` values `2026-10-03T14:00:00+08:00` and `2026-10-03T15:00:00+08:00` were rejected because Splash `.parse_json()` returned `nil` for top-level numerals. The verified runtime string API `.to_f64()` now converts them to `2026-10-03T06:00:00Z` and `2026-10-03T07:00:00Z`. The fixture then reached `calendar.list`; stock card-host has no Calendar service, so no live conflict or CRUD result is claimed.
- `git diff --check` passed for both G-01 commits. Only `main.splash` changed in those commits. No real mailbox login, send, TCC click, or system calendar action was performed by G-01.

## Current UI boundaries

- Nav: 对话、长期目标、记忆、活动记录、邮箱、日历、能力授权、设置. Right rail switches 能力/结果. The rail starts collapsed so a 412 px window keeps the central input usable. Wide windows expose a visible `三栏（宽窗）` control. No verified Splash viewport-width API exists for automatic width switching; record automatic three-column adaptation as partial.
- Mail is a **new message** workflow. The verified host contract lacks Reply-To and threading headers. SMTP `accepted` is not delivery; `verified` is a user declaration after checking the recipient side. A persistent action is written before calling `mail.send`; unknown results are never automatically retried.
- Calendar calls are gated by the runtime `calendar` grant and actual `full_access` permission. The locked stock host has no Calendar service. Extended-host source/build checks and real EventKit/TCC acceptance belong to the host and final-test owners.
- The linked path creates a Goal and account/message-scoped external-claim Memory source from a selected host mail message. A model may suggest candidate event fields, which remain unapproved until a bounded conflict query and an exact user confirmation. The Calendar create action binds Goal/Run/revision/request ID and only completes after `calendar.get` matches. A later Mail confirmation replans the same Goal into a new Run; recipient-side verification completes that Run. The end-to-end path still needs independent extended Shell and user-authorized live testing.
