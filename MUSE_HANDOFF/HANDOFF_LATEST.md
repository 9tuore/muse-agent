# Handoff

## Task

ZC-00：用户最新要求独立Intel APP、移除模拟环境、补账号删除/第二账号。

## Result

PARTIAL。桌面Muse-rc8-正式版-20261012.app已启动、x86_64、PID80429/native1718，三动态SecCode0。旧fixture Host21195已正常退出；未带入模拟账号。

## Changed

d550b975/source c4dc95e2：官方mail.remove_account、确认取消、多账号添加入口。独立包指向原正式资料，无凭据复制。

## Tests

24实际VM FIXTURE_PASS，失败保留；codesign strict/deep及LaunchServices真实通过。新账号GUI/真实收发未验证。旧seq8 Calendar读回存在，但证据清单需修复，不计完整PASS。

## Commit

产品d550b975，证据19482520、90928ca0；最后归档SHA以git log/同步回执为准。

## Remaining

生产安装仍rc7，rc8权限页已打开但本人Install未完成。模拟账号旧隔离存储未删除；新版删除/第二账号需实际UI验证。三轮、邮件日历、自发自收未完成。

## Important Boundaries

不模拟可信批准、不读Secret、不直接写生产DB。延长截至21:11:25仍未全通；最新独立包请求另行收口，不发布/比赛提交。
