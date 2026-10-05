<script setup lang="ts">
import { useLocale } from '../useLocale'
import TrainingApproach from './TrainingApproach.vue'
const { t } = useLocale()

const stages = [
  { date: '09.13–09.23', title: '报名与组队', deadline: '9/13 09:00 开放 · 9/23 23:59 截止', description: '单人或多人均可参赛。队长和每位队员分别报名，可边组队边开始初赛。' },
  { date: '09.13–10.04', title: '初赛海选 · 场景与可运行作品', deadline: '10/4 23:59 提交截止', description: '9/26–27 完成机制入门，9/28–10/4 留出一周用 Agent 制作作品。提交场景、可运行原型、源码、截图与演示，以及已报名成员名单。' },
  { date: '10.05–10.06', title: '初赛评审 · 2 天', deadline: '10/6 20:00 公布 50 人晋级名单与反馈', description: '独立评阅、运行核验与交叉复核，海选出 50 人晋级。评审使用 10/4 冻结版本；所有队伍可继续完善同一作品，为复赛做准备。', review: true },
  { date: '10.05–10.09', title: '持续完善作品 · 复赛准备与开发', deadline: '10/9 23:59 复赛提交截止', description: '初赛提交后即可继续迭代，10/6 公布名单后由晋级的 50 人提交复赛作品。沿用同一选题，重点改善任务完成、可用性与验证证据，无需从头开发。' },
  { date: '10.10–10.11', title: '复赛材料评审 · 2 天', deadline: '10/10–10/11 安装复现、任务验证与评分', description: '核验 10/9 冻结的应用版本与任务证据；技术进阶作品另核验贡献。评委专注材料审阅，10/11 连线检查由赛务组织。', review: true },
  { date: '10.12', title: '线上决赛答辩与评奖', deadline: '13:00–17:00 分组答辩 · 20:00 公布获奖结果', description: '50 名复赛选手按项目分组答辩：3 分钟应用演示 + 2 分钟 Agent 自动化与可选技术贡献说明，另留问答与切换时间。本场完成复赛评奖，不另设晋级筛选；总排名前三名获邀现场展示。', award: true },
  { date: '10.13–10.16', title: '受邀确认与展示准备 · 4 天', deadline: '10/13 18:00 确认代表 · 10/15 18:00 展示包冻结', description: '前三名优胜团队异步确认到场代表、安排出行并准备展示；提供展示指南与反馈，10/17 正式展示前联调与彩排。' },
  { date: '10.17', title: 'GOSIM 黑客松现场展示与颁奖', deadline: '10 月 17 日（周六）· 具体时段另行通知', description: '总排名前三名将到 GOSIM 黑客松现场展示作品并参加颁奖。获奖结果在 10/12 线上决赛确定，现场展示及到场情况不影响排名。' },
  { date: '10.18–10.31', title: '赛后采纳与归档', deadline: '10/18–10/31 贡献合入窗口', description: '完善 PR、应用和规范，跟进项目采纳并归档优秀作品；不改变线上评奖结果。' },
]

const sessions = [
  { date: '09.22', time: '19:30–21:00', audience: '开营说明', title: '赛事与八个项目全景', description: '介绍 OctoSense 场景、Rinx 参赛基线、八个项目的分工与评奖规则。选手定义目标和判断结果，Agent 协助完成小程序；机制入门从 9/26 周六开始。' },
  { date: '09.26', time: '10:00–12:00', audience: '机制入门', title: 'OctoSense × Makepad：让意图成为应用', description: '以参会天气卡为例，理解 OctoSense、AppCard、Makepad 与 Octos 如何把意图变成可操作的应用。观察真实数据、状态与失败反馈，写出自己的任务和完成标准。' },
  { date: '09.26', time: '14:00–16:00', audience: '机制入门', title: 'octoscode × Octoscript：和 Agent 一起做应用', description: '延续同一张卡片，用 octoscode 与 Agent 完成一次修改，理解 Octoscript 的界面、数据与交互机制。通过运行、反馈和复核改进作品，带走源码、截图与复现说明。' },
  { date: '09.27', time: '10:00–12:00', audience: '机制入门', title: 'octos × OctoLoop：执行与审查如何配合', description: '理解 octos 如何组织 Agent 的上下文、工具和任务执行，以及 OctoLoop 的内环执行、外环审查机制。通过派任务、看结果、退回改进和人工验收，学会管理 Agent 的工作。' },
  { date: '09.27', time: '14:00–15:30', audience: '机制入门', title: 'Rinx × hagency：从分享小程序到协作交付', description: '演示小程序分享、接收者独立授权、草稿隔离与确认发送，再用 hagency 任务验收说明软件工厂协作。选手规划自己的小程序与 Agent 分工，区分内置示例和需要完成的服务接入。' },
  { date: '09.27', time: '16:00–17:00', audience: '可选工作坊', title: '把课程变成自己的参赛计划', description: '为自己的场景写出目标、Agent 分工、可用项目和完成标准。9/27 完成机制入门，9/28–10/4 留出一周制作初赛作品，不增加新的必修内容。' },
  { date: '10.03', time: '14:00–16:00', audience: '国庆 · 可选答疑', title: 'Agent 作品门诊', description: '围绕选手正在制作的应用，讨论如何描述需求、组织 Agent、观察结果和调整任务；复用入门课的方法，不新增必修内容，不讲底层实现。' },
  { date: '10.04', time: '10:00–11:00', audience: '国庆 · 可选门诊', title: '初赛提交检查', description: '核对已报名成员、可运行作品、来源说明、截图和演示材料；初赛当日 23:59 截止，课后留出上传时间。' },
  { date: '10.07', time: '10:00–11:30', audience: '国庆 · 复赛工作坊', title: '从 Agentic 应用到技术突破', description: '根据 10/6 的晋级反馈，用 Agent 完善同一作品，比较改进前后的任务效果；理解生态反哺和 OctoSense ROM 突破如何服务应用，选择复赛目标，不讲实现细节。' },
  { date: '10.07', time: '14:00–15:30', audience: '国庆 · 复赛队伍', title: '讲清你的 Agentic 作品', description: '练习场景、Agent 分工、任务结果与技术价值的演示，准备问答和备用视频。作品 10/9 冻结，10/12 线上决赛；正式演示与备用视频使用冻结版本。' },
  { date: '10.11', time: '10:00–12:00', audience: '决赛准备 · 分队预约', title: '线上决赛连线检查', description: '按队检查音视频、屏幕共享与备用视频，使用 10/9 冻结版本；10/12 正式答辩。该环节为赛务检查，由非评分人员组织。' },
  { date: '10.17', time: '展示前 · 按队预约', audience: '现场准备', title: '现场设备联调与彩排', description: '前三名在当天正式展示前检查启动、投屏、网络、计时与备用视频；具体时段随 GOSIM 会务公布，不再评分。' },
]
</script>

<template>
  <section id="schedule" class="section event-schedule">
    <div class="section-heading wide">
      <p class="eyebrow">{{ t('07 / 赛程与培训') }}</p>
      <h2>{{ t('9.22 开营，9.26 周六开课。') }}</h2>
      <p>{{ t('9/27 完成机制入门，9/28–10/4 留出一周制作初赛作品。初赛海选晋级 50 人，10/12 线上决赛完成复赛评奖；前三名于 10/17 到 GOSIM 现场展示作品并参加颁奖，10/13–16 预留行程与展示准备。') }}</p>
      <p class="schedule-timezone">{{ t('2026 年 · 全部时间为北京时间 UTC+8') }}</p>
      <p class="schedule-draft">{{ t('9/13 报名、9/22 开营、9/26 开课、10/12 线上决赛、10/17 现场展示与颁奖及初赛晋级 50 人已确定；中间节点与具体时段为配套排期。') }}</p>
    </div>
    <TrainingApproach />
    <div class="schedule-columns">
      <div class="competition-calendar">
        <h3 class="calendar-heading">{{ t('比赛进程') }}</h3>
        <ol class="stage-list">
          <li v-for="stage in stages" :key="stage.title" :class="{ 'review-stage': stage.review, 'award-stage': stage.award }">
            <p class="stage-date">{{ stage.date }}</p>
            <h4>{{ t(stage.title) }}</h4>
            <p class="stage-deadline">{{ t(stage.deadline) }}</p>
            <p class="stage-description">{{ t(stage.description) }}</p>
          </li>
        </ol>
      </div>
      <div class="training-calendar">
        <h3 class="calendar-heading">{{ t('跟着作品进度学') }}</h3>
        <p class="training-intro">{{ t('9/22 开营说明，9/26–27 集中讲八个项目的机制与 Agent 参赛方法。国庆保留作品答疑和复赛工作坊；后续课程均在周末或假期，所有课程提供回放。') }}</p>
        <div class="training-list">
          <details v-for="session in sessions" :key="session.title">
            <summary>
              <span class="training-date">{{ session.date }}</span>
              <span class="training-info"><span class="training-audience">{{ t(session.audience) }}</span><strong>{{ t(session.title) }}</strong><span class="training-time">{{ t(session.time) }}</span></span>
              <span class="training-expand" aria-hidden="true"></span>
            </summary>
            <p class="training-description">{{ t(session.description) }}</p>
          </details>
        </div>
        <p class="calendar-note">{{ t('入门课在 9/27 结束，9/28–10/4 是完整的作品制作周。10/3 答疑与 10/4 提交检查均为可选支持，不增加新的必修内容。') }}</p>
        <p class="calendar-note">{{ t('初赛提交后即可继续完善同一作品，10/6 公布晋级名单，10/7 安排复赛工作坊。10/10–11 留给评审，10/12 举行线上决赛；决赛是比赛环节，不增加工作日晚课。') }}</p>
        <p class="calendar-note">{{ t('9/26 使用课前验证的 OctoSense / AppCard 环境与练习卡片，9/27 使用 Rinx 小程序示例；安装、账号配置与异步自检在课前完成。') }}</p>
      </div>
    </div>
    <div class="advancement-note">
      <h3>{{ t('晋级与评奖规则') }}</h3>
      <div>
        <p>{{ t('1. 初赛海选：50 人晋级复赛。') }}</p>
        <p>{{ t('2. 复赛评奖：50 人参与复赛，统一评选一等奖 1 名、二等奖 2 名、三等奖 3 名。') }}</p>
        <p>{{ t('初赛 10/4 截止、10/5–6 评审；复赛 10/9 截止、10/10–11 审阅材料，10/12 线上决赛与评奖使用 10/9 冻结版本。决赛是复赛的最终答辩，不增加第三轮晋级；前三名 10/17 到 GOSIM 现场展示与颁奖，现场不再评分。') }}</p>
        <a class="text-link" href="#participate">{{ t('查看报名说明 →') }}</a>
      </div>
    </div>
  </section>
</template>

<style scoped>
.event-schedule { padding-block: clamp(56px, 6vw, 88px); }
.section-heading .schedule-timezone { color: var(--accent); font-size: 14px; margin-bottom: 8px; }
.section-heading .schedule-draft { font-size: 13px; margin-top: 0; }
.schedule-columns { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: clamp(36px, 7vw, 96px); margin-top: 40px; }
.calendar-heading { margin: 0 0 24px; font-size: 25px; font-weight: 500; }
.stage-list { list-style: none; margin: 0; padding: 0; }
.stage-list li { border-top: 1px solid var(--border); padding: 20px 0 24px; }
.stage-date { color: var(--accent); font: 14px/1.7 var(--mono); margin: 0 0 8px; }
.stage-list h4 { font-size: 20px; font-weight: 500; margin: 0 0 10px; }
.stage-deadline { font-size: 14px; color: var(--ink); margin: 0 0 8px; }
.stage-description, .training-intro, .calendar-note, .training-description { color: var(--muted); font-size: 14px; margin: 0; line-height: 1.85; }
.stage-list .review-stage { padding-left: 18px; border-left: 2px solid var(--accent); }
.stage-list .award-stage { border-top: 2px solid var(--accent); }
.award-stage h4 { color: var(--accent); font-size: 24px; }
.training-intro { margin-bottom: 24px; }
.training-list details { border-top: 1px solid var(--border); }
.training-list summary { display: grid; grid-template-columns: 64px minmax(0, 1fr) 12px; gap: 14px; padding: 17px 0; cursor: pointer; list-style: none; }
.training-list summary::-webkit-details-marker { display: none; }
.training-date { font: 13px/1.8 var(--mono); color: var(--accent); padding-top: 2px; }
.training-info { display: flex; flex-direction: column; gap: 4px; min-width: 0; }
.training-audience { color: var(--muted); font-size: 12px; line-height: 1.6; }
.training-info strong { font-size: 16px; line-height: 1.7; font-weight: 500; }
.training-time { color: var(--accent); font: 12px/1.7 var(--mono); }
.training-expand::after { content: '+'; color: var(--accent); }
details[open] .training-expand::after { content: '−'; }
.training-description { padding: 0 26px 18px 78px; }
.calendar-note { border-left: 1px solid var(--border); padding-left: 16px; margin-top: 24px; font-size: 13px; }
.advancement-note { display: grid; grid-template-columns: 1fr 2fr; gap: 40px; border-top: 1px solid var(--border); padding-top: 30px; margin-top: 32px; }
.advancement-note h3 { font-size: 23px; font-weight: 500; margin: 0; line-height: 1.6; }
.advancement-note p { font-size: 14px; color: var(--muted); margin: 0 0 14px; }
.advancement-note a { color: var(--accent); border-bottom: 1px solid currentColor; }
@media (max-width: 760px) {
  .schedule-columns, .advancement-note { grid-template-columns: 1fr; gap: 36px; }
  .training-list summary { grid-template-columns: 56px minmax(0, 1fr) 12px; gap: 10px; }
  .training-description { padding-left: 66px; padding-right: 0; }
}
</style>
