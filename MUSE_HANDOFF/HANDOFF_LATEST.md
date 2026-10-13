# Handoff

## Task
按用户要求删除邮箱连接页的登录名输入栏，避免误导。

## Result
PASS（输入页面范围）。桌面 Muse.app 已重建、更新并打开新版中文邮箱页，资料保留。

## Changed
SDK Mail 原生表单删除登录名标签、控件及 ui.username 引用；表单仅提交地址，后端原有回退逻辑使用邮箱地址登录。Main与Calendar修复字节未变。

## Tests
1项原生表单/地址回退单测通过；实际GUI确认登录名标签和控件不存在，邮箱与密码栏存在；成品签名及动态身份通过。证据 official_muse/integrated_release/evidence/input-fix-20261013/no-username-verification.json，原生截图留本机build。

## Commit
产品 ff70f1b1；仅本地，未推送。

## Remaining
本项未重测真实登录、发信；前轮Calendar/全功能验收限制仍见CURRENT_STATE。

## Important Boundaries
未读取或复制凭据，未修改用户资料。旧版app保留rollback-rc10-with-username。
