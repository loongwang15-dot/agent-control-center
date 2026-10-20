# Agent Work OS — 根目录协作索引

> 本仓库在本机制部署前没有根目录 AGENTS.md；以下为新增的根级引导索引。`Agent_Work_OS_v1.1/AGENTS.md` 是已有子目录约束，保持原样并继续适用于该子目录。

## 新会话启动与交接

1. 新模型开始任务前，必须先读取 `agent-memory/00_PROJECT_BRIEF.md`、`01_CURRENT_STATE.md`、`02_DECISIONS.md`、`03_NEXT_ACTION.md`、`04_EVIDENCE_INDEX.md`、`05_HANDOFF_LOG.md`，再核对引用的原始报告、配置和当前 MCP 工具状态。
2. 交接文件是索引和摘要，不代替本机真实文件/工具核验。只有真实测试通过才记 `PASS`；区分 `FAIL`、`BLOCKED`、`NOT RUN`、`UNVERIFIED`。
3. 每次模型切换、会话结束或阶段完成前，执行 `prompts/切换前交接指令.md`，更新当前状态、下一步、证据索引，并按需追加决策和交接日志。
4. 当前 P1-A 以最近用户指令为准：Codex 主控，Playwright MCP 直接控制 Lovart。OpenClaw、AgentScope、Skill 和平台实现是保留资产，不作为重建任务或 P1-A 验收替代物。
5. 未获明确批准，不执行会消耗 Lovart/即梦积分、付费、发布或不可逆操作。不得读取、打印、复制或提交 API Key、Cookie、会话 Token；不得将隔离浏览器误报为已登录浏览器。
6. 保留现有项目文件、运行配置、浏览器 Profile 和登录数据。变更前检查目标路径并避免覆盖；重试设上限，连续两次同类失败后切换诊断路线。
7. 新模型无法调用现有 MCP/浏览器时，如实报告工具或权限阻塞；读懂文件不等于实测成功。禁止告诉接任者从零重建或重复已有 PASS 验收。

## 项目记忆入口

- 目标：`agent-memory/00_PROJECT_BRIEF.md`
- 最新本机状态：`agent-memory/01_CURRENT_STATE.md`
- 有效决策：`agent-memory/02_DECISIONS.md`
- 唯一下一步：`agent-memory/03_NEXT_ACTION.md`
- 证据位置：`agent-memory/04_EVIDENCE_INDEX.md`
- 交接历史：`agent-memory/05_HANDOFF_LOG.md`
- 接班提示：`prompts/新模型接班指令.md`
- 切换前提示：`prompts/切换前交接指令.md`
- 自检：`qa/模型接班自检.md`
# 追加到现有根目录 AGENTS.md 的片段（不要覆盖原文件）

<!-- BEGIN AGENT_WORK_OS_CONTEXT_V1 -->
## 当前主线与跨模型连续性（2026-10-20 起）

1. 本项目最终目标：**Codex 作为 Windows 本地主 Agent，调用已有的子 Agent / Skill，并通过现成接口或桌面、浏览器自动化操作豆包、WorkBuddy、DeepSeek、Lovart、即梦等现有平台，完成实际任务交付**。用户优先希望复用现有客户端和网页版能力，而非把所有软件替换成模型 API。
2. 当前唯一优先执行的 P1-A：**Codex → 官方 Playwright MCP → 已登录 Lovart 页面 → 图片上传验证 →（得到用户积分授权之后）真实生成与文件下载**。暂不重新建设 Agent Work OS UI、AgentScope 画布或 OpenClaw 新调度链；这些是历史探索/保留资产。
3. 开始新会话或模型切换后，必须先按顺序读取：`agent-memory/00_PROJECT_BRIEF.md`、`agent-memory/01_CURRENT_STATE.md`、`agent-memory/02_DECISIONS.md`、`agent-memory/03_NEXT_ACTION.md`、`agent-memory/04_EVIDENCE_INDEX.md`，之后核对文件中引用的**本地真实原始报告和当前工具配置**。若文件缺失，应报告而不是自行虚构。
4. 如 `AGENTS.md` 旧版内容与以上最新决策冲突，以用户最近明确指令和 `agent-memory/02_DECISIONS.md` 的有效决策为准；不得因此删除旧资料。必须报告发现的冲突。
5. 不以旧模型的自然语言总结替代测试证据。验收状态区分 `PASS / PARTIAL / FAIL / BLOCKED / NOT RUN / UNVERIFIED`；模型切换前后均需要检查项目实际文件、MCP 连通性和报告最后更新时间。
6. 每完成一个有效任务或准备切换模型，更新 `agent-memory/01_CURRENT_STATE.md`、`agent-memory/03_NEXT_ACTION.md`、`agent-memory/04_EVIDENCE_INDEX.md`，必要时追加 `agent-memory/05_HANDOFF_LOG.md`；记录完成项、失败原因、测试命令/调用、证据路径和下一步。
7. 用户明确批准之前，不得执行 Lovart/即梦可能消耗积分的生成、不进行付费与不可逆操作；保留原 Codex、OpenClaw、AgentScope、Skill、浏览器 Profile 与登录配置，不覆盖既有资产。
8. 不将上传按钮点击成功、页面打开、模拟数据、Skill 已显示，等同于文件上传、真实调用或交付成功。遇到连续两次同类失败时，停下并切换到最小隔离测试，不无限循环重试。

## 前台不干扰与桌面控制边界（2026-10-20）

1. **网页优先用 Playwright MCP**：Lovart、即梦、豆包网页、DeepSeek 网页等浏览器任务默认通过 Playwright MCP Extension 在浏览器内容层执行，不调用 Windows Computer Use。
2. **优先专用接口/本地 MCP/CLI**：若目标软件提供正式 API、MCP、CLI 或插件，优先使用结构化集成，避免鼠标键盘模拟。
3. **Windows 原生 GUI 不得默认在用户当前桌面运行**：官方文档明确 Windows Computer Use 在当前活动桌面前台执行，会移动指针、输入文字并抢焦点；用户正在前台工作时不得启动。
4. **需要原生桌面操作时使用隔离环境**：优先独立 Windows 虚拟机、Windows Sandbox、第二台电脑或独立测试机。隔离环境需保留自己的登录态，不从主桌面复制 Cookie、Token 或浏览器资料。
5. **前台接管必须有明确授权**：只有用户在当前指令中明确同意“接管我的桌面”时，才可在主桌面运行 Computer Use；一旦用户按 Escape、移动焦点或要求停止，立即终止。
6. 工具无法后台化时，应如实报告并选择浏览器/API/隔离环境，不得以“自动化需要”为由持续抢占用户控制权。
7. 官方依据：<https://learn.chatgpt.com/docs/computer-use.md>（2026-10-20 读取；Windows 前台运行说明）。

首次接班指令：`prompts/新模型接班指令.md`；阶段完成指令：`prompts/切换前交接指令.md`。
<!-- END AGENT_WORK_OS_CONTEXT_V1 -->

