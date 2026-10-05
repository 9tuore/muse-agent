> **Website repository:** `gosimfoundation/hackathon-agenticapp26` · [Maintenance and publishing](MAINTAINING.md) · [Live site](https://create.gosim.org/agenticapp26/)

# Agent2App Hackathon 2026

Independent Vue + TypeScript + Vite event site, served at `/agenticapp26/` alongside Factory26 and Survey26. No shared event database or authentication is configured.

## Development

```sh
npm ci
npm run dev
npm run build
```

The independent release workflow packages this site. The shared publisher in `gosimfoundation/hackathon` assembles the successful release into `_site/agenticapp26/`. `VITE_BASE_PATH` can override the default base path. See [MAINTAINING.md](MAINTAINING.md) for publishing and rollback.

## 课程书 · mdBook

四小时课程通过 mdBook 组织，复用 `docs/courses/2026-09-26/` 中的原始讲稿与练习，目录见 [docs/SUMMARY.md](docs/SUMMARY.md)。课程书包含两堂课、学员练习、讲师演示手册、整合路线，以及赛程和参赛基线附录；支持搜索、关系图和整书打印。

已验证工具版本为 **mdbook 0.5.3**、**mdbook-mermaid 0.17.0**。已有命令时无需重装；新环境可安装固定版本：

```sh
cargo install mdbook --version 0.5.3 --locked
cargo install mdbook-mermaid --version 0.17.0 --locked
```

在仓库根目录运行：

```sh
npm run course:dev     # http://127.0.0.1:3206，编辑 Markdown 后自动刷新
npm run course:build   # 静态书籍输出到 book/
```

也可直接使用 `mdbook serve --hostname 127.0.0.1 --port 3206` 和 `mdbook build`。Markdown 是唯一内容源；增加章节时更新 `docs/SUMMARY.md`。Mermaid 的浏览器资源在 `book-theme/` 随仓库提供，阅读已构建课程书无需连接图表 CDN。使用顶栏打印按钮可打印整书或另存为 PDF。

课程书当前独立构建和本地预览，尚未加入官网的自动发布包。`npm run build` 仍构建活动官网；课程书成功构建不代表已经上线，也不代表课程中的最新 GUI 演示已通过实机预演。

## Content and visual direction

`src/App.vue` contains participant-facing copy, awards and optional contribution topics. `src/components/EventSchedule.vue` contains the dated competition and training calendars. The competition centers on OctoSense: entrants choose from the [12 official application scenarios](https://octosense.org/cn/#apps)—mail, messaging, calendar, weather, news, music, video, markets, navigation, shopping and logistics, writing and creation, and system and devices—and demonstrate a real task completed with Agent automation.

`src/components/ApplicationScenarios.vue` now owns the scenario entry points and the messaging focus. The primary competition baseline is [hagency-org/Rinx](https://github.com/hagency-org/Rinx). Entrants build scenario mini apps while retaining its chat, contacts and Discover UI. Software factory mini apps for [hagency](https://github.com/hagency-org/hagency) (formerly hafleet) are one messaging and collaboration example: a task event becomes an actionable card, the user reviews or authorizes an operation, and the result returns to the source conversation. Other scenarios do not require hagency.

The reviewed version includes HTTP(S) Web cards and a built-in native Octoscript article editor. The latter supports per-recipient consent, account-local drafts, native preview, app sharing and confirmed chat publication. Native packages are restricted to the built-in editor; new native apps require host changes and a build. Web pages do not receive Matrix credentials or a chat bridge. See the [source-based baseline and validation scope](docs/rinx-miniapps.md). The official scene guides include concept walkthroughs and do not establish that every service is implemented in the competition environment.

Training introduces the roles and mechanisms of eight projects—octos, octoscode, OctoLoop, Rinx, hagency, OctoSense, Octoscript and Makepad—and shows entrants how to direct Agents, inspect results and finish their own applications. It uses prepared environments and product demonstrations rather than syntax or implementation lessons. OctoLoop is a productized double-loop skill within octoscode: an inner loop executes while an outer loop plans, observes and independently reviews, with people responsible for goals and approvals. This overview does not imply that all eight projects are integrated or required for every entry. Best Agentic evaluates how effectively an application completes real tasks. Best Technical Breakthrough builds on a working Agentic application and evaluates reusable ecosystem contributions and OctoSense ROM or system advances; entrants need not win Best Agentic first. `src/components/AwardEvaluation.vue` owns the qualitative evaluation criteria. Final numeric scoring, prize-category allocation and compatibility with the existing monetary slots remain to be published.

Copy changes must be reflected in `src/en.json`, metadata in `src/useLocale.ts` / `index.html`, and the hub event entry. The competition concludes online; the top three teams overall will showcase their projects and attend the awards ceremony at the GOSIM Shenzhen Hackathon on October 17, as confirmed by the organizer. Attendance does not affect awards or rankings.
The current design uses the approved warm city/studio illustration as a full-viewport hero. The palette is cream, terracotta, slate blue and muted sage, drawn from the artwork. Chinese typography uses Noto Serif SC. English display text uses Cormorant Garamond, with Space Grotesk body text and IBM Plex Mono for small labels. All fonts include local fallbacks.

- `public/images/human-robot-city-v3.png`: current full-bleed hero, expanded classical city view.
- `public/images/human-robot-studio-v2.png`: matching workshop illustration in the technology section.
- `public/images/CITY-V3-PROMPT.md` and `STUDIO-V2-PROMPT.md`: generation provenance.

These are concept illustrations, not photographs of the actual event or product screenshots. `heroImage` and `terminalImage` in `src/App.vue` control the assets. The hero uses a left-weighted contrast overlay; the right side remains open to the city and workspace. Mobile retains the full-bleed composition with a stronger local overlay. Earlier artwork and temporary video files are unused variants.

The media layer can host a future video without changing the page layout. When restoring video, provide muted inline playback, pause controls and reduced-motion handling.

Registration links to the organizer-provided [Tencent Questionnaire form](https://wj.qq.com/s2/27846792/da0o/). `src/components/RegistrationPanel.vue` embeds the provided Qacman animated QR code and displays the registration URL as a direct alternative. The site does not store form responses. Registration opens September 13, 2026 and closes September 23 at 23:59; solo entrants, captains and all team members register individually. Registered team membership is finalized with the October 4 submission.

Kickoff is September 22, 19:30–21:00. Four mechanism workshops on September 26–27 introduce OctoSense × Makepad, octoscode × Octoscript, octos × OctoLoop, and Rinx × hagency. They total 7.5 hours, or 9 hours including orientation. September 28–October 4 is a full seven-day creation window with no new required lessons; October 3–4 provide optional support. October 7 provides two award-round workshops totaling 3 hours. Teaching takes place on weekends or during the October 1–7 National Day holiday, with kickoff as the single weekday-evening orientation. October 10 is an adjusted working day and has no classes.

The competition has two qualification/award rounds. Preliminary submissions freeze October 4 at 23:59; judges review them October 5–6 and announce 50 advancing participants at 20:00 on October 6. Holiday judging shifts must be reserved in advance. All teams can continue improving the same project from October 5 while the frozen preliminary version is reviewed. The 50 qualifiers submit award-round versions by October 9 at 23:59; they do not start over with a new project. Award-round materials are reviewed October 10–11, with connection checks on October 11, 10:00–12:00, handled by staff who are not judging.

The online final is Monday, October 12, 13:00–17:00, with prizes announced at 20:00. It completes the award round without an additional qualifying stage. This Monday event is a competition session, not an exception that adds weekday teaching. Two parallel groups allow for up to 50 solo projects, with shared calibration before prizes are awarded. Presentations and backup videos must show the frozen October 9 version; final slides and video materials are due October 12 at 12:00. Online results are final.

The top three teams overall will showcase projects and attend the awards ceremony at GOSIM on October 17. Invited representatives confirm asynchronously by October 13 at 18:00. October 13–16 provides four days for travel and showcase preparation, with the showcase package frozen October 15 at 18:00. Equipment checks and rehearsals take place by appointment before the October 17 showcase. No weekday-evening showcase classes are scheduled, and attendance or onsite performance does not change online awards or rankings.

All times are UTC+8. Locked environment packages, startup instructions, available capabilities and accepted example-data scope are due September 24 at 18:00, followed by asynchronous self-checks on September 25. Runtime readiness and alternatives must be explicit; course demonstrations do not establish completed integration. See [the operational schedule](docs/competition-schedule.md) and [curriculum](docs/curriculum.md). Resource redemption details remain to be published. Spotlight promotional copy describes a separate event and is not included.

## Day / night themes

The header theme button switches the full page palette and hero between `human-robot-city-v3.png` and `human-robot-city-night.png`. The default is day; explicit selection persists under the event-specific `agent2app-theme` localStorage key. A small head script restores the palette before first paint, and the toggle remains usable if storage is unavailable. Night artwork is a lighting edit of the same composition. The browser theme color and native color scheme follow the selected mode.

## Real application screenshots

`src/components/ProjectShowcase.vue` begins with four native Rinx captures at `#miniapp-showcase`: app details, account consent, native article preview and a received mini-app card. They come from the September 21 macOS hidden-window Palpo fixture run committed at `05daf9bd`, not a new UI run in this website update. All four are copied unchanged, with source commit, public source URL, receipt and SHA-256 in `public/screenshots/provenance.json`.

The OctoSense desktop themes, Omarchy view, AppCard weather reference and bilingual official service walkthroughs remain. The historical Agent2App gallery is replaced; its assets remain archived for provenance. The article editor is a working native example, not proof of automatic Agent content generation or a completed hagency integration. Desktop theme selection follows the site theme and also has its own controls.

## Awards and developer support

The prize pool remains RMB 50,000, comprising cash prizes and MiniMax token credits. The published monetary allocation is one First Prize of RMB 20,000, two Second Prizes of RMB 9,000 each and three Third Prizes of RMB 4,000 each. Each award is per team, including solo teams. All public amounts are the combined RMB award values.

Best Agentic and Best Technical Breakthrough are the progressive award directions. Their mapping to these six monetary slots, whether a project may receive both, and the corresponding overall ranking method for the top-three showcase invitations require final rules. This update does not create additional prize money or redefine the categories as honorary awards. All scenarios share the same award framework; ecosystem or ROM contributions are optional for application entries and require evidence of improving the submitted application when considered for technical advancement.

MiniMax API credits and Kimi coding benefits are provided separately for participant development, testing and improvements. Redemption and validity details will accompany distribution instructions. The post-event adoption window tracks contributions and archives projects without a separate promised cash award.

`src/components/SponsorSupport.vue` presents the official MiniMax and Kimi logos at `#sponsors` inside the awards section. MiniMax sponsors RMB 50,000 worth of token credits, allocated across competition rewards and participant development. Kimi sponsors coding benefits, with no public account quantity or duration. The existing RMB 50,000 combined prize pool remains unchanged; token credits included in prizes count toward those combined values. Local logo sources and hashes are recorded in `public/sponsors/provenance.json`, with further context in that directory's README.
