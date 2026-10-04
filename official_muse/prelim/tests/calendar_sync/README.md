# Calendar sync incremental fixtures

These tests run frozen production Splash functions in a real card-host with an entirely synthetic Host transport. They do not prove native Calendar changes, UI clicks, Shell cold boot, or real-account acceptance. Each process has an isolated HOME and app-data, hidden fixture window, unchanged SDK 64 ms budget, source/Host/probe hashes, retained original logs, and a function audit. Only the known render/capability substitutions are permitted for integrated-source runs. Proposed helper/replacement runs are labeled `PROPOSAL_FIXTURE` separately.

The runner writes only under the assigned `official_muse/app/build/repair-delivery-20261004-115054/thread-calendar/`. It rejects an occupied port and never stops another process. Do not use an existing app or window such as 8422.

Example from the worktree root, after Root finishes the Calendar integration:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 official_muse/prelim/tests/calendar_sync/run.py \
  --source-bundle official_muse/app/bundle \
  --host official_muse/app/build/repair-delivery-20261004-115054/baseline-card-host \
  --host-cwd official_muse/app/build/three-hour-20261003-214720/host-sources \
  --probe official_muse/prelim/tests/calendar_sync/outside_readback.splash \
  --out official_muse/app/build/repair-delivery-20261004-115054/thread-calendar/integrated-outside-r1 \
  --port 8651
```

Use a fresh output directory per attempt; failed runs remain unchanged. All synthetic service requests are recorded. Unexpected services cause a failure; no request is forwarded to the real Host.

| Probe | Specific behavior |
| --- | --- |
| `baseline.splash` | Actual generated preview, selected-event refresh, stale-range guard, foreign calendar rejection. Also reproduces the original three failures on a490. |
| `linked_refresh.splash` | Persisted synthetic completed Goal/link/receipt/artifact; same original event refresh; preserve prior execution evidence. Reproduces baseline association failures. |
| `date_candidate.splash` | Authorized writable date entry; no guessed hours/duration; clear old association; Beijing date consistency, UTC equivalent expression; no external request. Requires integrated day helper/date validation. |
| `outside_readback.splash` | List absence followed by exactly one original-ID get; missing/changed ID; late callback after real candidate edit; pending cleanup; malformed/foreign/truncated data; query-only date marks. |
| `linked_observation.splash` | Current result projection plus untouched historical artifact; repeated refresh retains external-change flag; latest observation persists; formerly created verified link reopens the existing event for update. |
| `local_done_write.splash` | Separate local flag saves against exact calendar/event pair, without touching completed execution or Calendar fields. |
| `local_done_restart.splash` | A new Host process reads the first process's exact synthetic persisted state, reverses local completion, reloads the undo, and checks old schema1/malformed optional fields. |

For the last probe, pass `--state-seed .../integrated-local-write-r1/state`. The seed must be from this owned evidence directory; its file hashes are recorded and the old report is removed only from the new copy so the new process must produce a fresh report. Use the same frozen source-bundle and matching Host as the write run. This is a fixture process restart, separate from manual app/Shell reboot acceptance.

No broad rerun of the previous 111 unaffected checks is required. Keep original T01–T20 status and add A-CAL evidence without replacing native/manual requirements.

## 0.3.20 完成事项再改期

`completed_replan.splash`与`completed_replan_guards.splash`是实际成功的窄修补probe，沿用同一run.py和合成异步Host传输。成功流程26/26、十种状态变体63/63；原反例10 PASS/1 FAIL报告保留在host-0320。新版本计划、旧批准失效、同事件一次update和前后get被断言；未访问真实账号/系统事件/模型。完整绑定见`../../evidence/host-0320/completed-replan.json`（路径去掉空格）。原81项未重复执行。
