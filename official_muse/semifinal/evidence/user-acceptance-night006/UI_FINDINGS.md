# NIGHT-006 独立 UI 静态发现

这些是源码审查线索，尚未通过 GUI 复现；不能计入 GUI FAIL 或 PASS。

| 编号 | 优先级 | 复现计划与风险 | 源码依据 | 状态 |
| --- | --- | --- | --- | --- |
| UA-N006-001 | P0 | 聊天生成日历候选，打开日历后编辑文本时间，再点击上方“添加到日历”。上方按钮仍读取旧候选 payload，可能提交与用户刚输入不同的时间；同页两个近义执行按钮容易误点。 | `calendar_agent_submit_candidate`、`calendar_agent_input` | 已通知总控，等待新候选 GUI 验证 |
| UA-N006-002 | P1 | 行动链仍出现“已核验”“查看依据”和记录 ID。检查普通页面默认展示及展开详情，技术字段建议收进诊断。 | `ResultContent`、`ac_state` | 已通知总控 |
| UA-N006-003 | P1 | 自由文字创建日程不带候选 binding；专用“按新时间改期/删除这项日程”按钮依赖绑定 authority。验证自由创建后有无清晰的下一步；文字指令成功不等同按钮可用。 | `calendar_agent_submit(text,nil)`、`calendar_agent_update_target`、`calendar_agent_delete_target` | 已通知总控 |

范围：当前浅色开关只作用于行动链卡片；设置明确声明整应用深色。不能以卡片切色宣称全应用浅色主题。邮件正文固定 160、来信展开固定 150，仍需真实小窗口验证滚动和底部操作可达。
