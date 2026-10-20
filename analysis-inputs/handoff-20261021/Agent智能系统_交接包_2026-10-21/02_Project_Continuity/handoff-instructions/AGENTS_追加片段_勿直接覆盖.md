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

首次接班指令：`prompts/新模型接班指令.md`；阶段完成指令：`prompts/切换前交接指令.md`。
<!-- END AGENT_WORK_OS_CONTEXT_V1 -->
