# Handoff

## Task
GPT-02；修Calendar→Mail VM r1 probe缺少runner截断后生产定义。正式source0c7f9812不改。

## Result
PARTIAL：fixture依赖修复已交，中央新out真实VM重跑未做。

## Changed
仅probe/expectations及自有说明。逐字补7个真实action-chain全局和ac_field/ac_goal_allowed/ac_current_goal，登记SHA；40预期不变，不删当前事项检查。

## Tests
中央r1实际log报ac_selected_chat缺失；原report/log/state保留。离线核508其他prefix函数不变、3尾部函数与生产字节一致、114可达函数调用/裸赋值声明。不把离线检查称VM测试，未运行VM/Host/Node/GUI/Cargo。

## Commit
本地提交见最终回复，未push。

## Remaining
中央新out重跑完整40集合。当前正式源实际符号ac_current_goal，不存在current_action_goal。

## Important Boundaries
r1是probe截取依赖缺口，不是正式main缺变量；未动main/runner/Host。期待值非PASS；真实Calendar/Mail批准与投递未验证。
