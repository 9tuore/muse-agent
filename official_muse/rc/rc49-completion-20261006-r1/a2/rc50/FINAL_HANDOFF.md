# Handoff

## Task
a2补测50r2冻结源码0e705f33宽1400×760、窄412×892，并直接复核用户原ZIP的T19定义。

## Result
PASS_SCOPED_UI。四组同SHA fixture共16检查组通过。宽窗6条完整可见；窄窗实际412×809、7条可见。矮窗可滚动首尾、选择和删除预览取消；不要求每种高度四条同时可见。原ZIP无此要求，已更正此前条件性PARTIAL解释并保留旧证据。

## Changed
仅a2/rc50新增宽/窄截图、快照、最终报告与摘要。主文件未改。

## Tests
2026-10-06，原生card-host52768f57，独立8517；标题全文保存、折叠、输入、正文滚动和四快捷入口通过。原生history_list与rc49逐字相同；短中文一行/长中文两行人工核对。新文本变体未重复执行。

## Commit
本地提交，见Git；未push。

## Remaining
Root汇总最终Shell与历史英文/混排/emoji变体的采用。请求892实际809，不冒充目标高度或手机。

## Important Boundaries
合成fixture，无模型/外部写入，未触8493/主profile。不是最终Shell全链结论；旧报告不覆盖，最新解释见FINAL_REPORT.md。
