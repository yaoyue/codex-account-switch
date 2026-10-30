# Codex 账号快捷切换

使用自定义账号标签保存和切换 Codex 的文件登录态，并启动 VSCode。账号数量没有固定上限，新增第四个、第五个或更多账号无需修改脚本。

工具共享同一份 Codex 配置、对话记录、日志、skills、plugins、缓存，以及 VSCode 配置和扩展；每个标签分别保存自己的 `auth.json`。

## 安装

在本项目根目录执行：

```bash
mkdir -p ~/.local/bin
install -m 755 codex-account ~/.local/bin/codex-account
```

确保 `~/.local/bin` 位于 `PATH` 中。使用 zsh 时，若尚未配置，可在 `~/.zshrc` 添加以下内容并重新打开终端：

```bash
export PATH="$HOME/.local/bin:$PATH"
```

## 保存当前已登录的账号

确认 Codex 当前已登录目标账号后，为它选择一个本地标签，例如 `personal`：

```bash
codex-account save-current personal
```

登录另一个账号后，使用不同标签保存，例如 `work`、`team-2`、`project-4`。每个标签都需要在对应账号实际登录后单独保存。不要在同一个登录态下连续登记多个标签。

标签以英文字母或数字开头，其余字符允许英文字母、数字、下划线和连字符；`current` 及其大小写变体为内部保留名称。大小写是否区分取决于文件系统，建议标签统一使用小写。标签不需要包含真实姓名、邮箱或组织信息。

`save-current` 只复制当前登录态，不负责登录或核验邮箱。同名标签再次保存时，会先备份已有凭据，再更新副本。

## 切换账号

先完全退出 VSCode（macOS 使用 `Cmd+Q`），并结束其他使用同一份 `CODEX_HOME` 的 Codex 进程，再在外部终端执行目标账号对应的一条命令：

```bash
codex-account switch personal .
```

切换到其他账号时，把 `personal` 替换为已登记标签。例如切换到第四个账号并打开指定项目：

```bash
codex-account switch project-4 --new-window /path/to/project
```

命令会复制目标凭据到活动目录，然后调用 `code`。日常切换使用此命令，无需在 Codex 中退出登录。切换不会自动保存刚刚使用的账号；如需保存使用期间刷新的凭据，请在切换前执行对应标签的 `save-current`。

## 查看状态

```bash
codex-account status
```

该命令自动列出账号根目录下所有有效标签且含有 `auth.json` 的账号，无需维护名单。没有保存任何账号时，会显示空状态。

“已保存”只表示文件存在，不验证账号身份、令牌有效性或额度。“当前标记”是最后一次保存或切换时写入的标签，手动登录或从其他目录登记后可能与活动账号不同。

## 快捷命令

可以为任意标签创建快捷命令，例如在 `~/.local/bin/code-personal` 保存：

```bash
#!/usr/bin/env bash
set -euo pipefail

exec codex-account switch personal "$@"
```

为文件添加执行权限后，即可使用 `code-personal .`。仓库中已有的 `code-*` 包装脚本继续兼容，均可作为创建个人快捷命令的参考；主命令不依赖这些脚本。

## 文件位置

| 用途 | 默认位置 |
| --- | --- |
| 活动登录态 | `~/.codex/auth.json` |
| 各账号登录态 | `~/.codex-accounts/<账号标签>/auth.json` |
| 覆盖保存前的备份 | `~/.codex-accounts/<账号标签>/backups/auth.*.json` |
| 当前标签标记 | `~/.codex-accounts/current` |

`CODEX_HOME` 可覆盖活动目录，`CODEX_ACCOUNT_ROOT` 可覆盖账号根目录；保存和切换时应使用一致的路径配置。

## 适用范围

当前脚本为 Bash 实现，已在 macOS 验证。其他环境需具备 Bash、类 Unix 文件命令和可用的 VSCode `code` 命令。Windows 原生 PowerShell/CMD 无法直接运行，Git Bash/WSL 需确认实际客户端读取的是同一份目录。

本工具依赖文件形式的 `auth.json`；若使用系统钥匙串，需要先配置文件存储。官方文档介绍了 `CODEX_HOME`、`cli_auth_credentials_store` 和认证流程，见 [Codex 认证文档](https://learn.chatgpt.com/docs/auth)。

## 本地资料与凭据

个人账号对应关系和操作记录可以放在 `local-docs/` 中，该目录已加入 `.gitignore`。公开文档使用匿名示例，不保存真实账号信息、邮箱、登录状态或个人机器路径。

登录态文件及备份包含敏感凭据，不应提交到仓库。本项目的忽略规则覆盖任意层级的 `auth.json`、账号备份以及 `local-docs/`。已被 Git 跟踪的文件不会因新增忽略规则而自动停止跟踪。

更多登记方式、第四个及更多账号的操作、故障处理见 [使用说明](使用说明.md)。
