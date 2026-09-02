# Codex 账号快捷切换

这套脚本用于在同一份 `~/.codex` 状态中只切换 `auth.json`。

- `config.toml`、Codex 对话记录、日志、skills、plugins、缓存等继续共享同一份。
- VSCode 用户配置、扩展、工作区配置不做隔离，继续共享同一份。
- 两个账号只分别保存自己的 `auth.json` 到 `~/.codex-accounts/gm/auth.json` 和 `~/.codex-accounts/fox/auth.json`。

## 命名约定

当前脚本以两个账号为例：

- `gm` / `code-gm`：表示 gmail 邮箱对应的 Codex 账号。
- `fox` / `code-fox`：表示 foxmail 邮箱对应的 Codex 账号。

这里的 `gm`、`fox` 只是账号标签，方便日常快速区分。其他用户可以按同样思路改成自己的账号标签和快捷命令，例如工作账号、个人账号、不同组织账号等。

## 适用范围和账号状态

本工具只处理 Codex 本地状态目录里的登录态文件：

```text
~/.codex/auth.json
```

### VSCode 中的 Codex

`code-gm` 和 `code-fox` 会先把目标账号的 `auth.json` 复制到 `~/.codex/auth.json`，再启动 VSCode。

因此，VSCode 中的 Codex 通常会读取刚切换过去的账号。若 VSCode 已经打开，Codex 扩展可能继续使用旧缓存，建议重载窗口或关闭后重新打开。

### ChatGPT App

ChatGPT 桌面 App 的登录状态不由本工具管理。

执行 `code-gm` 或 `code-fox` 不会让 ChatGPT App 自动切换账号，也不会让 ChatGPT App 退出登录。ChatGPT App 仍会保持它自己当前的登录状态。

### Codex CLI 或其他 Codex 使用方式

如果某个 Codex CLI 或其他 Codex 客户端读取的是同一个 `CODEX_HOME`，默认也就是 `~/.codex`，那么它会受到当前 `~/.codex/auth.json` 的影响。

也就是说，先通过本工具切换到某个账号后，再启动读取同一份 `~/.codex/auth.json` 的 Codex CLI，通常会使用刚切换后的账号。

如果 CLI 或其他工具设置了独立的 `CODEX_HOME`，或使用自己的账号存储机制，则不会被这里的 `code-gm`、`code-fox` 影响。

## 安装

```bash
mkdir -p ~/.local/bin
cp codex-account ~/.local/bin/codex-account
cp code-gm ~/.local/bin/code-gm
cp code-fox ~/.local/bin/code-fox
chmod +x ~/.local/bin/codex-account ~/.local/bin/code-gm ~/.local/bin/code-fox
```

确保 `~/.local/bin` 在 `PATH` 中：

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
exec zsh -l
```

## 首次登记

如果当前 VSCode/Codex 是 gmail 账号登录状态：

```bash
codex-account save-current gm
```

然后在 VSCode/Codex 中手动退出 gmail，登录 foxmail，登录成功后执行：

```bash
codex-account save-current fox
```

重要：首次登记之外，日常切换不要再在 Codex 里执行“退出登录”。退出登录可能会让当前账号保存下来的 refresh token 被服务端撤销，表现为切回该账号后能显示账号信息，但无法加载 Codex 额度，使用时报 token 失效。

重要：切换账号不会自动覆盖已保存的登录态。只有明确执行 `codex-account save-current gm` 或 `codex-account save-current fox` 时，才会更新对应账号的 `auth.json`。

## 日常使用

切换到 gmail 并打开当前目录：

```bash
code-gm .
```

切换到 foxmail 并打开当前目录：

```bash
code-fox .
```

查看状态：

```bash
codex-account status
```

## 注意

如果 VSCode 已经打开，Codex 扩展可能缓存了旧登录态。最稳的使用方式是先关闭当前 VSCode 窗口，再执行 `code-gm .` 或 `code-fox .`。如果没有关闭窗口，切换后执行 VSCode 的 `Developer: Reload Window` 通常也可以让扩展重新读取登录态。

不要把真实登录态文件提交到仓库。`~/.codex/auth.json` 和 `~/.codex-accounts/*/auth.json` 都应视为敏感文件。

当前项目文件本身不包含真实 `auth.json`、token、cookie 或 API key。文档中的本机路径用于说明项目目录和系统目录，没有包含个人姓名、用户名等个人标识路径信息，不影响按当前内容自用。

如果准备作为通用开源项目发布，可以按需要把 gmail、foxmail、具体项目名改成更通用的示例；如果主要保留给自己使用，可以继续保留当前表述。

如果某个账号提示 token 失效，需要手动重新登录该账号，并重新执行：

```bash
codex-account save-current gm
```

或：

```bash
codex-account save-current fox
```
