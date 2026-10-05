<script setup lang="ts">
import { useLocale } from '../useLocale'
const { t } = useLocale()
const hubUrl = 'https://github.com/OctoSense-org/OctoSense-App-Hub'
const publishingUrl = `${hubUrl}/blob/97c2a1fd9aa49a6b87586f228e070e0c16b1067b/docs/PUBLISHING.md`
</script>

<template>
  <section id="submission" class="section app-hub-submission" aria-labelledby="submission-title">
    <div class="section-heading">
      <p class="eyebrow">{{ t('作品提交 / OCTOSENSE APP HUB') }}</p>
      <h2 id="submission-title">{{ t('让作品可提交、可运行、可复现。') }}</h2>
      <p>{{ t('OctoSense App Hub 为应用提供打包规范、基础准入检查与签名目录，并配有商店模块。参赛作品先准备完整交付，再用实际任务证明 Agent 的能力。') }}</p>
    </div>

    <ol class="submission-flow">
      <li>
        <span class="submission-step" aria-hidden="true">01</span>
        <h3>{{ t('提交与基础预检') }}</h3>
        <p>{{ t('整理源码、版本、运行说明与应用资料。采用 Hub 卡片包的作品，按规范打包并运行本地预检，检查资料、内容完整性和权限声明。') }}</p>
      </li>
      <li>
        <span class="submission-step" aria-hidden="true">02</span>
        <h3>{{ t('实际运行验收') }}</h3>
        <p>{{ t('在注明版本的 OctoSense 或 Rinx 环境中启动作品，演示真实输入、授权、Agent 操作与结果核验，并提交复现步骤和运行证据。') }}</p>
      </li>
      <li>
        <span class="submission-step" aria-hidden="true">03</span>
        <h3>{{ t('评委评奖') }}</h3>
        <p>{{ t('先评价应用的 Agent 自动化能力，再看项目反哺与 OctoSense ROM 技术突破。预检报告是交付证据，最终验收与获奖由评审确定。') }}</p>
      </li>
    </ol>

    <div class="submission-details">
      <div>
        <h3>{{ t('提交材料，提前备齐。') }}</h3>
        <ul>
          <li><strong>{{ t('开源代码与固定版本') }}</strong><span>{{ t('公开源码仓库、提交号或发布版本、Apache 2.0 许可证，以及宿主版本、支持平台和启动说明。') }}</span></li>
          <li><strong>{{ t('应用资料与权限') }}</strong><span>{{ t('功能描述、图标、截图、作者与支持方式；说明数据来源、使用权限和隐私处理。') }}</span></li>
          <li><strong>{{ t('任务演示与复现证据') }}</strong><span>{{ t('列出 Agent 完成的步骤、结果核验方式、授权与失败处理，附运行截图、日志或视频；视频不能代替可运行作品。') }}</span></li>
        </ul>
        <p class="submission-note">{{ t('按作品形态交付：Hub 卡片包遵循官方包规范；网页小程序交付源码、可运行页面与 URL 卡片；原生宿主或 ROM 扩展交付可构建版本和复现说明。') }}</p>
      </div>
      <div>
        <h3>{{ t('Hub 能帮你检查什么？') }}</h3>
        <ul>
          <li><strong>{{ t('资料与包完整性') }}</strong><span>{{ t('应用资料、图标和截图文件是否齐全，包摘要、签名、文件类型与大小是否符合规则。') }}</span></li>
          <li><strong>{{ t('权限与版本规则') }}</strong><span>{{ t('检查声明的能力、网络目标和 Agent 工具；约束资源配额，并结合目录检查重复版本及发布者连续性。') }}</span></li>
          <li><strong>{{ t('可接入 Agent 辅助审核') }}</strong><span>{{ t('配置审核器后，可辅助检查功能声明与权限是否相符、是否存在欺骗性内容，并给出通过、转人工或拒绝的建议。') }}</span></li>
        </ul>
        <p class="submission-note">{{ t('基础预检不替代启动、交互与任务验证。当前检查尚未完整覆盖页面解析、图片有效性和实际运行，仍需提供可复现的作品演示。') }}</p>
      </div>
    </div>

    <aside class="submission-status" aria-labelledby="hub-status-title">
      <h3 id="hub-status-title">{{ t('当前可用范围') }}</h3>
      <p>{{ t('可参考 Hub 规范准备卡片包并进行本地预检。Rinx 的通用商店接入与自动提交入口仍在建设，开放后将公布使用方式；现阶段各轮评审仍以公开源码仓库和可运行作品为准，无需等待上架。') }}</p>
    </aside>
    <div class="submission-links">
      <a class="inline-link" :href="hubUrl" target="_blank" rel="noopener noreferrer">{{ t('查看 OctoSense App Hub ↗') }}</a>
      <a class="inline-link" :href="publishingUrl" target="_blank" rel="noopener noreferrer">{{ t('阅读应用包与预检规范 ↗') }}</a>
      <a class="inline-link" href="#awards">{{ t('查看奖项与评价标准 ↓') }}</a>
    </div>
  </section>
</template>

<style scoped>
.submission-flow { list-style: none; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 36px; padding: 0; margin: 42px 0; }
.submission-flow > li { min-width: 0; padding-top: 24px; border-top: 1px solid var(--border); }
.submission-step { font: 36px/1.2 var(--serif); color: var(--accent); }
.app-hub-submission h3 { font-size: 22px; line-height: 1.5; font-weight: 500; margin: 16px 0 14px; }
.submission-flow p, .submission-details li, .submission-status p { font-size: 15px; line-height: 1.85; color: var(--muted); margin: 0; }
.submission-details { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: clamp(28px, 5vw, 64px); padding-top: 28px; border-top: 1px solid var(--border); }
.submission-details > div { min-width: 0; }
.submission-details h3 { margin-top: 0; }
.submission-details ul { list-style: none; padding: 0; margin: 0; }
.submission-details li + li { margin-top: 18px; }
.submission-details strong { display: block; color: var(--ink); font-weight: 500; margin-bottom: 4px; }
.submission-note { font-size: 13px; line-height: 1.85; color: var(--muted); border-left: 2px solid var(--border); padding-left: 14px; margin: 24px 0 0; }
.submission-status { border-block: 1px solid var(--border); margin-top: 36px; padding-block: 24px; }
.submission-status h3 { font-size: 16px; color: var(--accent); margin: 0 0 10px; }
.submission-links { display: flex; flex-wrap: wrap; align-items: flex-start; gap: 18px 28px; margin-top: 28px; font-size: 14px; line-height: 1.9; }
.submission-links a { white-space: normal; overflow-wrap: anywhere; }
@media (max-width: 760px) {
  .submission-flow, .submission-details { grid-template-columns: 1fr; gap: 28px; }
  .submission-flow { margin-block: 28px; }
}
</style>
