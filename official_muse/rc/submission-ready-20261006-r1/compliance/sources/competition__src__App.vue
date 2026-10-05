<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useLocale } from './useLocale'
const { locale, t, toggleLocale } = useLocale()
import ConferenceText from './components/ConferenceText.vue'
import HeroDetail from './components/HeroDetail.vue'
import HeroMedia from './components/HeroMedia.vue'
import EventSwitcher from './components/EventSwitcher.vue'
import ApplicationScenarios from './components/ApplicationScenarios.vue'
import RegistrationPanel from './components/RegistrationPanel.vue'
import ProjectShowcase from './components/ProjectShowcase.vue'
import EventSchedule from './components/EventSchedule.vue'
import TierMascot from './components/TierMascot.vue'
import AwardEvaluation from './components/AwardEvaluation.vue'
import SponsorSupport from './components/SponsorSupport.vue'
import AppHubSubmission from './components/AppHubSubmission.vue'
const menuOpen = ref(false)
const octosenseSite = computed(() => locale.value === 'en' ? 'https://octosense.org' : 'https://octosense.org/cn')
const base = import.meta.env.BASE_URL
// Keep both photographs mounted so lighting can crossfade without a blank frame.
const isNight = ref(document.documentElement.dataset.theme === 'night')
const displayedNight = ref(isNight.value)
const themeLoading = ref(true)
const scrolled = ref(window.scrollY > 24)
const dayImage = `${base}videos/agent2app-day-v2.jpg`
const nightImage = `${base}videos/agent2app-night-v2.jpg`
let disposed = false
function updateScroll() { scrolled.value = window.scrollY > 24 }
watch(displayedNight, (night) => {
  document.documentElement.dataset.theme = night ? 'night' : 'day'
}, { immediate: true })
// Browser chrome follows the chosen theme.
watch(isNight, (night) => {
  document.documentElement.dataset.browserTheme = night ? 'night' : 'day'
  document.documentElement.style.colorScheme = night ? 'dark' : 'light'
  document.querySelector('meta[name="theme-color"]')?.setAttribute('content', night ? '#18242f' : '#f3ede2')
}, { immediate: true })
function toggleTheme() {
  if (themeLoading.value) return
  isNight.value = !isNight.value
  displayedNight.value = isNight.value
  try { localStorage.setItem('agent2app-theme', isNight.value ? 'night' : 'day') } catch { /* Optional preference storage. */ }
}
onMounted(async () => {
  window.addEventListener('scroll', updateScroll, { passive: true })
  await Promise.allSettled([dayImage, nightImage].map(async (src) => {
    const image = new Image()
    image.src = src
    await image.decode()
  }))
  if (disposed) return
  themeLoading.value = false
})
onUnmounted(() => {
  disposed = true
  window.removeEventListener('scroll', updateScroll)
})
const nav = [['challenge', '参赛命题'], ['tracks', '场景选题'], ['showcase', '实机预览'], ['steps', '实现与提交'], ['awards', '奖项与评分'], ['bounties', '悬赏榜'], ['schedule', '赛程与培训']]
const bounties = [
  { title: 'hagency 软件工厂小程序', description: '围绕任务进度、Agent 状态、结果验收或协作交接提交 Rinx 小程序，附 hagency 接入说明和完整任务演示。', repo: 'Rinx + hagency' },
  { title: '小程序能力与契约测试', description: '为工厂小程序补充一个受限数据能力、状态回放或权限测试，并接回实际参赛应用。', repo: 'Rinx + hagency' },
  { title: 'L0 Web Playground', description: '输入脚本，实时预览卡片。头号悬赏；若赛前已有 MVP，则转为体验增强。', repo: 'Octoscript' },
  { title: 'check-ui CLI 与 LSP 接入', description: '把 L0 校验带进命令行与编辑器，让创作反馈更及时。', repo: 'Octoscript' },
  { title: '更有用的错误诊断', description: '错误码与修复建议，帮助模型理解失败并完成自修复。', repo: 'Octoscript' },
  { title: '结构化 lint 引擎', description: '从子串匹配走向 OR、禁止与计数规则，提升卡片质量校验。', repo: 'AppCard / Octoscript' },
  { title: '跨仓库 schema 契约测试', description: '为 Octoscript 与 OctoSense 的接口一致性提供自动检查。', repo: '双仓协作' },
  { title: 'L0 parser fuzz', description: '测试解析器边界，提高面对复杂输入时的稳定性。', repo: 'Octoscript' },
  { title: 'L1 规范撰写', description: '把语言行为写成清晰规范，技术写作者也可认领。', repo: 'Octoscript' },
  { title: 'UI Protocol 最小客户端', description: '用 TypeScript 或 Python，把 Octos 接到手机之外的界面。', repo: 'Octos' },
  { title: '协议 schema / typegen / conformance', description: '完善 schema 导出、类型生成或协议一致性测试。', repo: 'Octos' },
  { title: 'new-skill 脚手架', description: '简化 manifest 与注册流程，让新能力更容易起步。', repo: 'Octos' },
  { title: '「生产回路 Agent」演示', description: '读取自身运行指标，发现卡片失败，自动修复并重新发布。', repo: 'Octos' },
]
const faqs = [
  { q: '作品需要先在 App Hub 上架吗？', a: '目前无需等待上架，各轮评审仍以公开源码仓库和可运行作品为准。采用 Hub 卡片包时，可按官方规范准备资料并完成本地预检；Rinx 通用商店接入与自动提交入口开放后，将另行公布使用方式。网页小程序与原生宿主扩展按各自形态提交。' },
  { q: '通过 Hub 检查，就算作品验收通过吗？', a: '不等同。Hub 主要检查应用资料、包完整性、权限与版本规则；仍需在注明版本的 OctoSense 或 Rinx 环境中演示真实任务、授权和结果核验。Agent 自动化水平及技术突破由评委依据作品和复现证据评价。' },
  { q: '分享小程序就算完成 Agentic 作品吗？', a: '分享只是入口。原生文章编辑器演示了授权、草稿和发送机制；参赛作品还要展示 Agent 如何读取获授权的状态、完成操作并核验结果。新增原生应用需提交包含宿主扩展的可运行版本。' },
  { q: '必须到 GOSIM 现场才能获奖吗？', a: '不需要。比赛在复赛结束时确定一、二、三等奖；总排名前三名将到 GOSIM 黑客松现场展示作品并参加颁奖，到场情况不影响名次与获奖资格。' },
  { q: '小程序从哪里开始？', a: '从 hagency-org/Rinx 小程序宿主开始。在“发现”或聊天“+”中打开文章编辑器，体验授权、草稿、原生预览、分享应用与确认发送。网页小程序也可通过 URL 卡片分享；软件工厂选题可扩展 hagency 协作。' },
  { q: '不会 Rust，也能独立参赛吗？', a: '可以。从一个具体场景出发，使用已发布的环境、数据能力和参考卡片，设计 Agent 能完成的任务。需要新增能力时可以组队协作；应用层作品同样可以争取最佳 Agentic 奖。' },
  { q: '必须组队吗？没有技术伙伴怎么办？', a: '可以单人或多人参赛。单人队伍由本人报名；多人队伍的队长和每位队员都须分别报名，队长不能代替成员报名。拟定 9/23 23:59 截止个人报名，10/4 初赛提交时锁定已报名成员名单。' },
  { q: '没有 Android 手机怎么办？', a: '可使用公布支持的桌面环境，不强制手机演示。当前原生文章编辑器的验证记录来自 macOS；移动端和加密会话需单独验证。OctoSense ROM 是可选技术进阶方向。' },
  { q: '什么是 no-facts？', a: '在 AppCard L0 路径中，模型写布局与数据绑定，事实由数据能力提供。邮件、消息、天气和工厂任务都要注明来源，不得编造状态、操作成功或执行结果。' },
  { q: '做工具链或内核，就不用做应用了吗？', a: '仍需完成自己的 Agentic 应用。最佳技术突破奖在应用自动化的基础上评价项目反哺与 OctoSense ROM 突破；不以修改底层、刷机成功或 PR 数量直接判定。' },
  { q: '作品必须开源吗？用什么许可证？', a: '必须。作品代码以 Apache License 2.0 在公开仓库提交，各轮评审均以仓库为准。平台各项目同样采用 Apache 2.0。优秀创意将进入 OctoSense-org 主仓库的合并流程。' },
  { q: '只提交创意、设计稿或视频可以吗？', a: '不可以。创意必须通过可运行的开源代码实现。设计图可以交给 AI 生成，再转成原生界面与卡片；服务规则与交互逻辑需要你自己设计。' },
  { q: '从哪里报名？奖金是多少？', a: '9 月 13 日起，通过本页动态二维码或腾讯问卷报名。初赛海选晋级 50 人，50 人参加复赛并评出一、二、三等奖，10 月 12 日线上决赛并公布结果；总排名前三名将于 10 月 17 日到 GOSIM 黑客松现场展示作品并参加颁奖。获奖奖池 ¥50,000，含现金奖金与 MiniMax Token 额度：一等奖 1 名，每名 ¥20,000；二等奖 2 名，每名 ¥9,000；三等奖 3 名，每名 ¥4,000。' },
]
</script>

<template>
  <a class="skip-link" href="#main">{{ t('跳转到主要内容') }}</a>
  <header class="header" :class="{ 'is-scrolled': scrolled, 'menu-is-open': menuOpen }">
    <div class="header-brand-group"><a class="brand" href="/" :aria-label="t('GOSIM Create 首页')"><span class="brand-logo" aria-hidden="true" :style="{ maskImage: `url(${base}gosim-logo.svg)`, WebkitMaskImage: `url(${base}gosim-logo.svg)` }"></span><span class="create-wordmark">Create</span></a><EventSwitcher /></div>
    <div class="header-controls"><button class="locale-toggle" type="button" :aria-label="locale === 'zh' ? 'Switch to English' : '切换到中文'" @click="toggleLocale">{{ locale === 'zh' ? 'EN' : '中文' }}</button><button class="theme-toggle" type="button" :aria-pressed="isNight" :aria-label="isNight ? t('切换到白天模式') : t('切换到夜晚模式')" :title="isNight ? t('切换到白天模式') : t('切换到夜晚模式')" :disabled="themeLoading" :aria-busy="themeLoading" @click="toggleTheme">
      <svg v-if="isNight" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1.5 1.5m11 11L19 19M5 19l1.5-1.5m11-11L19 5"/></svg>
      <svg v-else viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M20.5 14A8.6 8.6 0 0 1 10 3.5 8.8 8.8 0 1 0 20.5 14Z"/></svg>
    </button><a class="registration-status registration-desktop" href="#participate">{{ t('报名参赛 ↗') }}</a><button class="menu-toggle" :aria-expanded="menuOpen" aria-controls="navigation" @click="menuOpen = !menuOpen">{{ menuOpen ? t('关闭') : t('菜单') }}</button></div>
    <nav id="navigation" :class="{ open: menuOpen }" :aria-label="t('主导航')"><a v-for="[id, label] in nav" :key="id" :href="`#${id}`" @click="menuOpen = false">{{ t(label) }}</a><a class="registration-status registration-mobile" href="#participate" @click="menuOpen = false">{{ t('报名参赛 ↗') }}</a></nav>
  </header>
  <main id="main">
    <section class="hero" aria-labelledby="event-title">
      <HeroMedia :night="displayedNight" />
      <div class="hero-shade" aria-hidden="true"></div>
      <div class="hero-stage">
        <div class="hero-copy">
          <p class="eyebrow"><a href="https://shenzhen2026.gosim.org/" target="_blank" rel="noopener noreferrer">{{ t('GOSIM 深圳 2026') }}</a> / AGENTIC APP</p>
          <h1 id="event-title" v-if="locale === 'en'">The Intent<br>Is the <span>App.</span></h1><h1 id="event-title" v-else class="zh">意图，<br>即<span>应用。</span></h1>
          <div class="hero-details">
            <h2>{{ t('智能体应用 黑客松') }}</h2>
            <p class="hero-theme">{{ t('围绕 OctoSense，在 Rinx 中创造 Agent 能理解、能操作、能完成任务的小程序。') }}</p>
            <p class="hero-theme">{{ t('9.22 开营 · 10.12 线上决赛 · 10.17 现场展示与颁奖') }}</p>
            
            <a class="location" href="https://shenzhen2026.gosim.org/" target="_blank" rel="noreferrer">{{ t('10.17 前三名现场展示与颁奖 · GOSIM 深圳 2026 ↗') }}</a>
            
            <div class="actions"><a class="button primary" href="#participate">{{ t('参赛信息') }}<span>↗</span></a><a class="text-link" href="#showcase">{{ t('查看实机 ↓') }}</a></div>
            <div class="hero-sponsors" :aria-label="t('赞助商')">
              <span>{{ t('赞助商') }}</span>
              <div class="hero-sponsor-logos">
                <a href="https://www.minimaxi.com/" target="_blank" rel="noopener noreferrer" aria-label="MiniMax"><img class="minimax-logo" :src="`${base}sponsors/minimax.png`" alt="MiniMax"></a>
                <a href="https://www.kimi.com/" target="_blank" rel="noopener noreferrer" aria-label="Kimi"><img class="kimi-logo" :src="`${base}sponsors/kimi.png`" alt="Kimi"></a>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="hero-bottom"><a class="org-link" href="#tracks">OCTOSENSE / APPCARD / RINX</a><span>{{ t('OctoSense 场景 · Agentic 应用 · 技术突破') }}</span><a href="#challenge">{{ t('探索赛事 ↓') }}</a></div>
    </section>
    <section id="challenge" class="section challenge"><div class="section-heading"><p class="eyebrow">{{ t('01 / 参赛命题') }}</p><h2>{{ t('意图所至，') }}<br>{{ t('应用而生。') }}</h2><figure class="intent-detail"><HeroDetail region="design" :night="displayedNight" :alt="t('主视觉局部：创作者在绘图屏上绘制应用界面')" /></figure></div><div class="section-body"><p class="lead">{{ t('让 Agent 完成任务，应用为人保留控制。') }}</p><p>{{ t('本届大赛以 OctoSense 为核心，以 Rinx 小程序宿主为主要开发基线。围绕熟悉的聊天与小程序入口，让 Agent 读懂状态、执行操作、跟进变化，并让用户看清结果。') }}</p><p>{{ t('意图不一定来自你对 Agent 说的话。它可能藏在一封邮件、一条消息、一个时间点或一次状态变化里。比如买了一台空调：物流、预约安装、上门、付款、售后，Agent 读完邮件，把每一步整理成等你确认的卡片。') }} <a class="inline-link" :href="`${octosenseSite}/experience/aircon/`" target="_blank" rel="noopener noreferrer">{{ t('体验空调服务示例 ↗') }}</a></p><p>{{ t('面向设计师、产品人、OPC（一人公司）、学生与开发者。按 OctoSense 应用指南选择场景，在 Rinx 中制作小程序；即时消息沿用其会话界面，软件协作可以接入 hagency。') }}</p><p>{{ t('9 月 13 日开放报名与组队。可以单人参赛，也可以多人组队；队长和每位队员均须分别报名。') }}</p><div class="rule"><span>{{ t('共同交付') }}</span><strong>{{ t('跑通的演示 + 以 Apache 2.0 开源的代码') }}</strong><p>{{ t('以 Rinx 为主要基线，提交小程序及其可复现的宿主版本与启动说明。视频或设计稿不能代替可运行作品；平台和 ROM 扩展需展示对作品的实际改善。') }}</p><a class="inline-link" href="#submission">{{ t('查看提交材料与 Hub 预检 ↓') }}</a></div></div></section>
    <ApplicationScenarios />
    <ProjectShowcase :night="displayedNight" />
    <section id="steps" class="section steps"><div class="section-heading wide"><p class="eyebrow">{{ t('03 / 实现路径') }}</p><h2>{{ t('围绕一个场景，逐步深入。') }}</h2><p>{{ t('先把 Agentic 应用做好，再扩展能力和系统。应用层作品同样可以获得最佳 Agentic 奖，技术进阶必须服务于实际任务。') }}</p><a class="inline-link" href="#submission">{{ t('查看提交材料与 Hub 预检 ↓') }}</a></div><div class="steps-grid"><article><TierMascot kind="nautilus" :label="t('鹦鹉螺 / NAUTILUS')" /><div class="step-index">01 <span>{{ t('鹦鹉螺 / NAUTILUS') }}</span></div><span class="tag">{{ t('应用层 · 设计师与 vibe coder') }}</span><h3>{{ t('用现有能力，') }}<br>{{ t('造一个新 App。') }}</h3><p>{{ t('从 Rinx 的网页卡片或原生文章编辑器示例出发，让 Agent 帮你制作一个场景小程序。沿用 Rinx 的入口与会话界面，展示操作、授权和结果。') }}</p><div class="step-foot">{{ t('交付 / 需求说明 + 应用 + 测试证据') }}<br><span>{{ t('看重意图设计、信息设计与泛化能力') }}</span></div></article><article><TierMascot kind="crab" :label="t('帝王蟹 / RUSTACEAN')" /><div class="step-index">02 <span>{{ t('帝王蟹 / RUSTACEAN') }}</span></div><span class="tag">{{ t('能力层 · 用 Rust 扩展') }}</span><h3>{{ t('没有的数据，') }}<br>{{ t('自己接进来。') }}</h3><p>{{ t('为自己的场景补充数据或操作能力，接入邮件、日历、消息或设备状态。软件协作可接入 hagency；完善来源、权限、错误处理与可复用接口。') }}</p><div class="step-foot">{{ t('交付 / 新数据能力 + 应用演示') }}<br><span>{{ t('扩展所有参赛者都能使用的能力菜单') }}</span></div></article><article><TierMascot kind="octopus" :label="t('大章鱼 / GIANT OCTOPUS')" /><div class="step-index">03 <span>{{ t('大章鱼 / GIANT OCTOPUS') }}</span></div><span class="tag">{{ t('平台与系统层 · 技术突破') }}</span><h3>{{ t('改语言、改渲染，') }}<br>{{ t('也可以改内核。') }}</h3><p>{{ t('改进组件、协议、生成与测试工具，或在 OctoSense ROM 上打通系统事件、权限和跨应用任务。提供可复现的前后对照，说明突破如何改善自己的应用。') }}</p><div class="step-foot">{{ t('交付 / 平台贡献 + 应用演示') }}<br><span>{{ t('技术突破必须服务于自己的作品') }}</span></div></article></div></section>
    <AppHubSubmission />
    <section class="section stack"><div class="section-heading"><p class="eyebrow">{{ t('04 / 意图应用平台') }}</p><h2><a href="https://github.com/orgs/OctoSense-org/" target="_blank" rel="noopener noreferrer">Octos · OctoSense · Octoscript</a></h2><p class="stack-lead">{{ t('从内核、语言、UI 框架到 Shell，整条 Agentic 技术栈都用 Rust 写成，并以 Apache 2.0 开源。在手机上，Android 底座之上全部是 Rust。') }}</p><p class="stack-lead">{{ t('OctoSense 的方向是运行在操作系统之上的 Agent 交互 Shell：从熟悉的 launcher 和应用入口出发，探索意图理解、环境感知与应用重组。') }}</p><p class="stack-lead">{{ t('OctoSense 探索聊天之外的 Agent 交互：保留人们熟悉的应用入口，让数据、卡片与操作围绕意图组织。') }}</p><ul class="stack-principles"><li><strong>{{ t('熟悉的入口') }}</strong><span>{{ t('新闻、天气、行情、出行仍是稳定的起点，入口之下的内容围绕你的意图生成。') }}</span></li><li><strong>{{ t('主动，而非被动') }}</strong><span>{{ t('探索由时间和事件触发的应用变化，例如降温、航班延误和日程调整。') }}</span></li><li><strong>{{ t('删繁就简') }}</strong><span>{{ t('围绕具体需求组合界面与数据，减少使用应用时无关的信息和步骤。') }}</span></li><li><strong>{{ t('人在回路') }}</strong><span>{{ t('重要决定留给用户。应用应呈现需要确认的事项，并清楚反馈操作结果。') }}</span></li><li><strong>{{ t('情绪价值') }}</strong><span>{{ t('探索适合场景的风格、配色与字体，让动态应用保持可读、易用。') }}</span></li></ul><p class="stack-lead">{{ t('这些是平台探索的方向。参赛时可用的能力、设备与集成范围，以赛前发布包和验证说明为准。') }}</p><figure class="terminal-figure"><HeroDetail region="computing" :night="displayedNight" :alt="t('主视觉局部：创作者在复古电脑上输入，旁边的手机展示应用卡片')" /><figcaption>{{ t('PERSONAL COMPUTING / 从意图到应用') }}</figcaption></figure></div><div class="stack-list"><article><span>{{ t('交互层 / AGENT SHELL') }}</span><h3><a href="https://github.com/OctoSense-org/OctoSense" target="_blank" rel="noopener noreferrer">OctoSense</a></h3><p>{{ t('以跨平台为目标的 Agent 交互 Shell，提供应用入口与 launcher，并探索意图驱动的卡片和应用交互。实际支持的系统、数据能力和集成范围以发布包为准。') }}</p></article><article><span>{{ t('语言层 / DSL') }}</span><h3><a href="https://github.com/OctoSense-org/Octoscript" target="_blank" rel="noopener noreferrer">Octoscript</a></h3><p>{{ t('用声明式描述表达界面、状态和交互。Rinx 的原生文章编辑器用 Octoscript L0 定义输入与状态，由 Makepad 呈现；账号、授权和发送由 Rinx 宿主管理。') }}</p></article><article><span>{{ t('内核层 / HARNESS') }}</span><h3><a href="https://github.com/octos-org/octos" target="_blank" rel="noopener noreferrer">Octos</a></h3><p>{{ t('可嵌入的 Rust 原生 Agent harness 内核。多轮交互、上下文与记忆、模型 provider、多 agent 并发、工具与沙箱、用户审批流程，全部抽象为 OS UI protocol 提供给上层应用。') }}</p></article><article><span>{{ t('界面层 / UI') }}</span><h3><a href="https://github.com/OctoSense-org/makepad" target="_blank" rel="noopener noreferrer">Makepad</a></h3><p>{{ t('Rust 跨平台 UI 框架，一套代码运行在桌面、Android 与 Web（WebAssembly）。Agent 可以直接读取完整的 UI 树与每个节点的状态，不必靠截屏去“看”界面。') }}</p></article><article><span>{{ t('系统层 / ROM') }}</span><h3><a href="https://github.com/OctoSense-org/octosense-rom" target="_blank" rel="noopener noreferrer">OctoSense ROM</a></h3><p>{{ t('基于 LineageOS 的 OnePlus 6 ROM，内置 OctoSense launcher 与系统桥，让 Agent 进入系统层。') }}</p></article><a class="stack-github" href="https://github.com/orgs/OctoSense-org/" target="_blank" rel="noopener noreferrer">{{ t('在 GitHub 上查看 OctoSense-org →') }}</a></div></section>
    <section id="awards" class="section awards">
      <div class="section-heading wide">
        <p class="eyebrow">{{ t('05 / 奖项与评分') }}</p>
        <h2>{{ t('获奖奖池 ¥50,000') }}</h2>
        <p>{{ t('含现金奖金与 MiniMax Token 额度。所有场景统一参评，已公布的综合奖励共 6 个名额。') }}</p>
        <p class="prize-note">{{ t('以下金额均为人民币，每个获奖团队的综合奖励包含现金与 Token 额度。') }}</p>
        <p>{{ t('总排名前三名将于 10 月 17 日到 GOSIM 黑客松现场展示作品并参加颁奖。') }}</p>
      </div>
      <div class="awards-grid">
        <article class="champion">
          <span>{{ t('1 个获奖名额') }}</span>
          <h3>{{ t('一等奖') }}</h3>
          <p class="prize-amount">¥20,000 <span>{{ t('/ 名') }}</span></p>
          <p>{{ t('现金奖金 + MiniMax Token 额度') }}</p>
        </article>
        <article>
          <span>{{ t('2 个获奖名额') }}</span>
          <h3>{{ t('二等奖') }}</h3>
          <p class="prize-amount">¥9,000 <span>{{ t('/ 名') }}</span></p>
          <p>{{ t('现金奖金 + MiniMax Token 额度') }}</p>
        </article>
        <article>
          <span>{{ t('3 个获奖名额') }}</span>
          <h3>{{ t('三等奖') }}</h3>
          <p class="prize-amount">¥4,000 <span>{{ t('/ 名') }}</span></p>
          <p>{{ t('现金奖金 + MiniMax Token 额度') }}</p>
        </article>
      </div>
      <AwardEvaluation />
      <SponsorSupport />
    </section>
    <section id="bounties" class="section bounties"><div class="section-heading wide"><p class="eyebrow">{{ t('06 / 悬赏题目') }}</p><h2>{{ t('工具链与平台贡献') }}</h2><p>{{ t('围绕自己的应用选择生态或系统贡献，争取最佳技术突破奖。下列为建议题目；普通应用不强制认领悬赏，贡献需说明对实际任务的改善。') }}</p></div><div class="bounty-list compact-bounties"><details v-for="(bounty, i) in bounties" :key="bounty.title"><summary><span class="bounty-number">{{ String(i + 1).padStart(2, '0') }}</span><span>{{ t(bounty.title) }}</span><span class="repo">{{ t(bounty.repo) }}</span></summary><p>{{ t(bounty.description) }}</p></details></div><div class="contribution-note"><strong>{{ t('缺口，也是贡献。') }}</strong><p>{{ t('发现可复现的语言、协议或文档缺口，可以提交 issue 与复现证据。技术贡献参评时核验质量和应用效果，不按认领数量或 PR 数量直接加分。') }}</p></div></section>
    <EventSchedule />
    <section id="faq" class="section faq"><div class="section-heading"><p class="eyebrow">{{ t('08 / 常见问题') }}</p><h2>{{ t('参赛须知') }}</h2></div><div><details v-for="item in faqs" :key="item.q"><summary>{{ t(item.q) }}<span aria-hidden="true">+</span></summary><p><ConferenceText :text="t(item.a)" /></p></details></div></section>

    <section id="participate" class="section participate"><p class="eyebrow">{{ t('09 / 参赛信息') }}</p><h2>{{ t('智能体应用 黑客松 2026') }}</h2><p><ConferenceText :text="t('2026 年 9 月 13 日开放报名组队，9 月 22 日开营，9 月 26 日起在周末与国庆假期集中上课。初赛海选晋级 50 人，50 人参加线上复赛并评出一、二、三等奖，10 月 12 日线上决赛并公布获奖结果。前三名将于 10 月 17 日到 GOSIM Shenzhen 2026 黑客松现场展示作品并参加颁奖。单人、多人均可参赛；队长和每位队员都须分别报名。')" /></p><RegistrationPanel /><p class="small">{{ t('智能体应用 黑客松是独立赛事，与智能体软件工厂 黑客松、智能体巡天黑客松并行。') }}</p></section>
  </main>
  <footer><a href="/">GOSIM / CREATE</a><span>{{ t('智能体应用 黑客松 · 2026') }}</span><a href="/">{{ t('查看全部黑客松 ↗') }}</a></footer>
</template>
