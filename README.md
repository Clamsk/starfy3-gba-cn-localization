# starfy3-gba-cn-localization

Starfy 3 简体中文汉化工程。

非官方、免费、非商业的简体中文汉化差异补丁与编辑工程。当前公开版本为 **v25 测试版**，尚未完成全流程人工验收，不作为正式完整汉化发布。

## 权利声明

原作品著作权归 Nintendo / TOSE 所有。

本项目为非官方爱好者作品，与权利方无关。

本作至今无官方中文版本，本补丁供已通过 Nintendo Switch Online 或其他合法渠道获得游戏的用户使用。

如权利方提出异议将立即移除。

本项目零商业化：不收费、不挂打赏、不接广告。不销售补丁、工程或汉化镜像。

请自备原版镜像。本仓库不提供 ROM，也不提供 ROM 下载链接或获取教程。仓库、发行附件和文档均不包含官方 logo、封面、卡带图、游戏截图、官方美术文件或日文/英文原文转储。

Nintendo 的[官方游戏目录](https://www.nintendo.com/en-gb/Nintendo-Switch-Online/Classic-games/Classic-games-Nintendo-Switch-Online-2719182.html)将本作标记为仅日文版本；此状态最近核对于 2026-10-02。

## 使用补丁

使用 `patches/Starfy3_CN_v25_Rev0.bps`。适用镜像为日版 Rev0，校验的是**未压缩文件**：

| 项目 | 数值 |
| --- | --- |
| 原版大小 | 16,777,216 字节（16 MiB） |
| 原版 CRC32 | `FCAF1AA8` |
| 原版 SHA256 | `8a7eff8a20319a966465da429dfbb744def4d12f1353f22f21743259c2247533` |
| 补丁大小 | 677,697 字节（约 662 KiB） |
| 输出 SHA256 | `acc0fca232ba9fd5ae3816defb27ae1546400cd9287a9820fe71e3adc7f8d139` |

可用兼容 BPS 的补丁工具，例如 [Flips](https://github.com/Sir-Walrus/Flips)，在本地应用补丁。也可以使用 Python 3.10 或以上版本运行本仓库工具，无第三方依赖：

```text
python scripts/build.py --source "local/original.gba" --output "local/Starfy3_CN_v25.gba"
```

工具严格检查原版、补丁与输出校验值；不会下载镜像，也不会覆盖已有文件。生成的镜像只保留在本地，禁止提交或作为发行附件上传。

继续测试时使用游戏自己的普通存档，并为本版使用独立保存目录。不要跨版本载入旧即时存档，它们会恢复旧字库、图块及内存状态。

## 当前进度与限制

- 覆盖 2304 条脚本消息，保留控制指令边界；译文经过 GPT 辅助校对，仍欢迎人工指出误译与上下文问题。
- 包含此前的菜单、教学、美术风格保留、HUD 场景重载与存档弹窗修复。
- v25 在标题空位加入“（v25）汉化 by Clamsk”，采用原生点阵、金黄渐变与蓝色描边；现有标题、角色、背景和 START 提示保留。
- 继承 v24 的物品说明改为 12×12 原生点阵字；33 条非空说明重新排版，只改变换行，不改变其正文。
- 仍有海报、关卡告示牌、联机提示等日文图块候选待处理；尚未完成所有关卡、小游戏、图鉴、换装、商店、结局、保存/读档及双角色切换的人工验收。
- 这是测试版本；编码尚未宣布冻结。验证范围见 [验证记录](docs/VALIDATION.md)。

## 工程与编辑

工程使用本次 BPS 作为可复现的 v25 基线。原版代码、图像、控制数据均从用户的本地镜像读取，不随工程分发。

`translation/messages.zh.json` 包含当前版本的中文文本及控制边界位置，不含日文/英文参考原文或原始控制包。`translation/encoding.json` 保留现有编码；`engineering/bmg_layout.json` 记录脚本地址和指针位置。

可以复制中文表到 `local/edits.zh.json`，只修改 `zh` 字段，然后在本地重建：

```text
python scripts/build.py --source "local/original.gba" --edits "local/edits.zh.json" --output "local/Starfy3_CN_edited.gba"
```

重建工具保留所有未编辑的文本及控制包，拒绝修改控制边界，并检查物品说明的 7 字×5 行范围。新汉字需要补充字模与编码，当前编辑器会拒绝编码表以外的字；其他对白仍需人工确认排版。美术修改已包含在差异补丁中；本仓库不附带完整原图或截图。更多说明见 [工程文档](docs/ENGINEERING.md)。

开源字库及其原许可证位于 `fonts/`，权利归各字库作者所有，见 [声明](NOTICE.md)。

## 发布与备份

仅发布差异补丁、原创工程代码、中文译文、开源字库及纯文字文档。BPS 使用 SourceRead / SourceCopy 引用自备镜像中的未改动数据，并使用 TargetCopy 去除重复；补丁还原已经校验到 v25 的完整 SHA256。

`.gitignore` 排除镜像、存档、截图、可执行文件与备份。提交前执行 `python scripts/audit_public.py`，CI 也会检查 Git 实际跟踪的文件。差异补丁设有 1 MiB 大小门槛。

完整研发工程已在发布者本地另存 ZIP 备份，Git 历史另存 bundle；这些备份不上传。维护者应保留自己的离线副本，不将 GitHub 作为唯一副本。

