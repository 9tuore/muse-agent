<script setup lang="ts">
import { useLocale } from '../useLocale'
const { t } = useLocale()
</script>

<template>
  <div class="award-evaluation">
    <h3>{{ t('先看 Agentic，再看技术突破。') }}</h3>
    <div class="evaluation-grid">
      <article>
        <p class="evaluation-stage">{{ t('01 / 应用自动化') }}</p>
        <h4>{{ t('最佳 Agentic 奖') }}</h4>
        <p>{{ t('谁的应用最面向 Agent 自动化，谁就更接近最佳。看 Agent 能否理解状态、完成多步操作、跟进变化，并把可靠结果交给用户。') }}</p>
        <ul>
          <li>{{ t('任务完成：从真实输入到执行与结果核验，而不止生成界面或摘要。') }}</li>
          <li>{{ t('可靠运行：展示状态变化、失败恢复与重复测试，说明仍需人工处理的步骤。') }}</li>
          <li>{{ t('人机协作：来源可查、授权清楚、操作有反馈，用户能够调整与接管。') }}</li>
        </ul>
        <p class="evaluation-note">{{ t('应用层作品可以直接争取此奖，不要求修改 ROM 或认领悬赏。') }}</p>
      </article>
      <article>
        <p class="evaluation-stage">{{ t('02 / 在应用基础上进阶') }}</p>
        <h4>{{ t('最佳技术突破奖') }}</h4>
        <p>{{ t('先完成可运行、可验证的 Agentic 应用，再看项目反哺与 OctoSense ROM 突破。技术进步必须改善自己的应用，并能被其他开发者复用或验证。') }}</p>
        <ul>
          <li>{{ t('项目反哺：应用接入、数据能力、组件、协议或测试工具带来可复用的改进。') }}</li>
          <li>{{ t('ROM 突破：系统事件、权限、系统桥或跨应用协作推动任务自动化。') }}</li>
          <li>{{ t('效果证据：提供版本、补丁、复现步骤与前后对照，同一成果不重复计分。') }}</li>
        </ul>
        <p class="evaluation-note">{{ t('完成基础应用即可参与技术进阶评审，无需先获得最佳 Agentic 奖；单纯刷机或累计 PR 数量不直接构成突破。') }}</p>
      </article>
    </div>
    <p class="evaluation-rules">{{ t('两类奖项的名额、与上述综合奖励的对应及兼得规则，将随最终评审细则公布。10/12 线上决赛完成复赛评奖，10/17 现场展示不另行评分。') }}</p>
  </div>
</template>

<style scoped>
.award-evaluation { border-top: 1px solid var(--border); margin-top: 48px; padding-top: 32px; }
.award-evaluation > h3 { font-size: clamp(25px, 3vw, 34px); line-height: 1.5; margin: 0 0 28px; }
.evaluation-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: clamp(28px, 5vw, 64px); }
.evaluation-grid article { min-width: 0; }
.evaluation-stage { font: 12px/1.8 var(--mono); color: var(--accent); }
.evaluation-grid h4 { margin: 10px 0 16px; font-size: 25px; font-weight: 500; }
.evaluation-grid p:not(.evaluation-stage), .evaluation-grid li { color: var(--muted); font-size: 15px; line-height: 1.85; }
.evaluation-grid ul { padding-left: 20px; }
.evaluation-grid li + li { margin-top: 10px; }
.evaluation-grid .evaluation-note { font-size: 13px; border-left: 2px solid var(--border); padding-left: 14px; margin-top: 22px; }
.evaluation-rules { color: var(--muted); font-size: 13px; line-height: 1.85; margin: 30px 0 0; }
@media (max-width: 760px) { .evaluation-grid { grid-template-columns: 1fr; gap: 28px; } }
</style>
