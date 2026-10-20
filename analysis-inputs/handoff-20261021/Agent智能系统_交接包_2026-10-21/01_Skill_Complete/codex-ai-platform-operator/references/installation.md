# 安装、依赖与兼容性

本 Skill 的核心是 Markdown 指令和标准 JSON/文件检查。Codex 专属元数据放在 `agents/openai.yaml`，其他 Agent 即使不识别该文件，也能读取 `SKILL.md` 和本目录。

## 已验证基线

2026-10-20 在本机 Windows 环境中实际验证过以下组合：

| 组件 | 已验证版本/结果 |
|---|---|
| Codex CLI | `0.163.0-alpha.10.2` |
| Node.js | `v24.19.0` |
| `@playwright/mcp` | `0.0.83` |
| Playwright Extension | `0.4.0` |
| 完整能力 | Lovart 上传、一次生成、下载和本地 PNG 核验 PASS；即梦参考图拖放和单批生成 PASS |

这些是本机历史证据，不是对所有版本、账号和平台的兼容保证。新宿主必须重新做最小探测。

2026-10-21 的 v1.1.0 升级新增了 Agent 智能系统六层模型、项目接续规则和常见交付类型路由；现有平台控制、证据门、JSON 契约和三个校验脚本继续保留。升级包的结构、引用和脚本会重新验证，但新宿主的 Skill 发现与真实平台行为仍需单列验收。

## 安装 Skill

当前官方 Codex 文档支持在项目和用户目录的 `.agents/skills/` 中发现 Skill。较旧版本或特定安装可能仍扫描 `.codex/skills/`，所以安装时先确认宿主实际搜索位置。

推荐优先级：

1. 项目共享：`<project>/.agents/skills/codex-ai-platform-operator/`
2. 当前用户全局：`~/.agents/skills/codex-ai-platform-operator/`
3. 兼容旧版：`~/.codex/skills/codex-ai-platform-operator/`

安装步骤：

1. 解压后核对目标目录；若已存在，先备份或换名，不覆盖用户已有 Skill。
2. 将整个 `codex-ai-platform-operator/` 目录复制到上述一个位置。
3. 确认目标位置包含 `SKILL.md`，不是只复制了 ZIP 或参考文件。
4. 重启 Codex，或按宿主提示重新扫描 Skill。
5. 用 `$codex-ai-platform-operator` 显式调用一次；再检查普通任务是否会误触发。

Codex 会读取 `agents/openai.yaml` 中的展示信息和 Playwright MCP 依赖。不同版本的 `openai.yaml` 支持程度可能不同；该文件缺失或字段不被识别时，`SKILL.md` 仍可手工使用。

如果目标项目使用 `AGENTS.md` 和 `agent-memory/`，先把本 Skill 安装到宿主可发现的位置，再在项目根目录运行 `preflight.py --project-root <项目根目录>`。预检只核对文件存在与工具配置，不证明项目记忆内容正确，也不启动浏览器。

## Playwright MCP

### 推荐：扩展现有登录浏览器

先在 Chrome 或 Edge 安装微软官方 Playwright MCP browser extension。官方页面：

<https://playwright.dev/mcp/configuration/browser-extension>

然后用 Codex CLI 添加 MCP：

```text
codex mcp add playwright -- npx -y @playwright/mcp@latest --extension
```

Windows 上若 Codex 启动 `npx` 失败，可使用已解析的 `npx.cmd` 路径，或像本机一样固定 Node 可执行文件加 `cli.js`。不要凭猜测填写 Node 路径。

项目级配置示例：

```toml
[mcp_servers.playwright]
command = "npx"
args = ["-y", "@playwright/mcp@latest", "--extension"]
startup_timeout_sec = 30
tool_timeout_sec = 120
default_tools_approval_mode = "prompt"
```

生产复用建议固定已验证版本，例如 `@playwright/mcp@0.0.83`，而不是长期无审查跟随 `latest`。升级前记录旧版本、验证标签读取、普通点击、文件选择器、附件上传和下载；只升级而不重测不能声称兼容。

### 普通隔离浏览器

去掉 `--extension` 后，Playwright MCP 会启动自己的浏览器配置。它适合普通网页测试和本地探针，但默认没有用户现有登录态。不要把隔离浏览器的成功写成已登录平台成功。

### CDP

CDP 可以控制整个浏览器并暴露已打开页面。连接用户登录配置前必须取得明确授权，并说明影响范围。优先只连接新建的一次性 profile、回环地址和单一测试页；不要把登录 Cookie 或 CDP WebSocket 路径写入日志、Skill 或聊天交付。

## Windows 桌面控制

Windows Computer Use 当前可能在活动桌面上移动指针、输入文字并抢占焦点。运行时优先使用独立 VM、Windows Sandbox、第二台机器或远程 Worker。不能把以下做法当作隔离：

- 最小化目标窗口；
- 切换 Windows 虚拟桌面；
- 声称“用户看不见所以不会干扰”。

若宿主没有桌面控制能力，网页任务仍可用 Playwright；桌面任务应报告 `BLOCKED`，不要用网页替代用户明确指定的桌面客户端。

## 最小连通性检查

只读顺序：

1. `codex --version`
2. `node --version`
3. `codex mcp list`
4. 一次浏览器标签列表调用
5. 一次目标平台页面标题/可访问性读取
6. 关闭额外空白标签

不要打开或保存 Playwright Extension 的连接状态页完整快照；该页面可能展示连接令牌。连接异常时，优先用户手动断开/重连扩展，再执行一次轻量标签调用。

## 官方依据

- Codex Skills 与安装位置：<https://developers.openai.com/codex/skills>
- Codex MCP 配置：<https://developers.openai.com/codex/mcp>
- Playwright MCP browser extension：<https://playwright.dev/mcp/configuration/browser-extension>
- Playwright MCP 选项：<https://playwright.dev/mcp/configuration/options>
