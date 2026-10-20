# codex-ai-platform-operator 需求与变更记录

- Task ID: `skill-update-agent-work-os-20261021`
- 模式/强度: `UPDATE` / `FULL`
- Canonical 来源: v1.0.0 Skill、当前仓库 `AGENTS.md`、`agent-memory/00` 至 `05`、P1-A/P1-B/P1-C 报告、平台任务报告、后台测试和 Skill 工程验收
- 版本: `1.1.0`
- 阶段: 包构建、离线验证和交付
- 状态: `COMPLETED`
- 恢复点: `releases/v1.0.0/` 与 `deliverables/codex-ai-platform-operator-v1.0.0.zip`

## Baseline

| ID | 来源 | 要求 | 优先级 | 目标规则/产物 | 验收 |
|---|---|---|---|---|---|
| REQ-001 | 用户：可部署到别的 Codex | 提供自包含 Skill 目录及可传输 ZIP | CRITICAL | `skills/codex-ai-platform-operator/`、交付 ZIP | 结构检查、解压后入口可读 |
| REQ-002 | 用户：适配性与其他 Agent 兼容 | 核心能力不能绑定唯一工具名或聊天历史 | CRITICAL | `SKILL.md`、`references/agent-interop.md`、JSON 契约 | 引用检查、契约脚本正反测试 |
| REQ-003 | 用户：网页界面操作注意事项 | 说明登录、点击、上传、生成、下载和连接恢复 | CRITICAL | `references/web-automation.md` | 内容覆盖核对 |
| REQ-004 | 用户：需要安装的插件 | 明确 Playwright MCP、浏览器扩展、Codex 配置和可选依赖 | CRITICAL | `references/installation.md`、`agents/openai.yaml` | 官方页面核对、本机预检 |
| REQ-005 | 项目安全决策 D-003/D-013/D-018/D-022 | 费用、授权、证据、桌面隔离和平台提示边界 | CRITICAL | 入口与 `references/evidence-and-safety.md` | 内容映射核对 |
| REQ-006 | 已实测 Lovart/即梦/DeepSeek/WorkBuddy/豆包 | 保留有用复现经验但不写成永久兼容承诺 | IMPORTANT | `references/platform-playbooks.md` | 来源映射核对 |
| REQ-007 | Skill 工程规范 | 提供必要校验工具并实际运行 | IMPORTANT | `scripts/*.py` | 语法、help、正反样例 |
| REQ-008 | 用户 2026-10-21：把当前 Agent 智能系统整理成一个 Skill | 用单一入口表达完整系统，而不是只保留网页操作技巧 | CRITICAL | `SKILL.md`、`references/system-model.md` | 系统六层、控制面、生命周期和状态语义可定位 |
| REQ-009 | 项目 `AGENTS.md`、`agent-memory/`、切换前交接指令 | 支持跨会话接续、原始证据核验和阶段收尾 | CRITICAL | `references/project-continuity.md`、`scripts/preflight.py` | 接续读取顺序、状态语义、交接最低信息集和文件探测 |
| REQ-010 | 现有平台真实任务与报告 | 对话、图片、研究、连接器、桌面 Agent、Skill 工程按交付类型路由到不同验收 | IMPORTANT | `references/delivery-recipes.md` | 每类任务有可观察验收条件和路径边界 |
| REQ-011 | 现有安全决策 D-003、D-013、D-018、D-022、D-025、D-026 | 保留费用、上传、前台隔离、矛盾提示和有限回退规则 | CRITICAL | 入口、`evidence-and-safety.md`、`platform-playbooks.md` | 旧安全能力映射和回归核对 |

## 明确排除

- 不在本次任务中安装 Skill 到另一台设备或另一 Codex 实例。
- 不自动连接已登录浏览器 Profile 的 CDP。
- 不执行 Lovart/即梦生成，不消耗积分。
- 不把当前仓库的项目记忆或用户登录数据打包进 Skill。
- 不创建或发布 Codex Plugin；本次交付物是 Skill 包。
- 不把项目报告、截图、聊天历史、账号状态或认证数据打包为 Skill 内容。
- 不安装或部署到其他 Codex；目标宿主发现和真实行为另立 DEPLOY 验收。
- 本轮不操作 Lovart/即梦或消耗积分。

## CR-001｜从单页平台操作 Skill 升级为 Agent 智能系统 Skill

- 提出者与原话：用户，“给我现在项目的Agent智能系统的整理成一个skill”。
- 关联 Baseline：REQ-001 至 REQ-007。
- 影响等级：行为与触发范围扩大，采用次版本 `1.0.0 → 1.1.0`；未删除旧能力。
- 原因：v1.0.0 已覆盖 AI 平台操作，但项目还包含跨会话记忆、证据索引、交接、交付类型路由和系统边界；这些内容若不进入入口，会在新会话中被遗漏。
- 授权依据：用户明确要求把当前 Agent 智能系统整理为一个 Skill。
- 回归范围：原有安装说明、网页规则、平台 playbook、JSON task/result 契约、三个脚本和安全门必须继续存在并可运行。
- 结果：新增三个参考文件，扩写入口、平台 playbook 和安装说明，扩展预检脚本报告项目接续文件；版本及 UI 元数据同步为 v1.1.0。

## 来源到产物映射

| 来源能力 | 目标位置 | 处理 |
|---|---|---|
| Codex 主控、优先现有平台 | `SKILL.md` 执行顺序 | preserved |
| 网页优先 Playwright、GUI 隔离 | `SKILL.md`、`installation.md` | preserved |
| 上传/生成/下载必须真实证据 | `SKILL.md`、`evidence-and-safety.md` | preserved |
| 授权与费用停止条件 | `SKILL.md`、`evidence-and-safety.md` | preserved |
| Extension 重连、点击失败阶梯 | `web-automation.md`、`platform-playbooks.md` | merged |
| Lovart/即梦实测流程 | `platform-playbooks.md` | conditional |
| 三平台桌面接入结论 | `platform-playbooks.md` | conditional |
| 跨 Agent 交接和权限 | `agent-interop.md`、JSON 契约 | changed：从项目架构摘要提炼为可移植任务协议 |
| Agent 智能系统六层结构与控制面 | `system-model.md`、`SKILL.md` | changed：从项目架构摘要提炼为稳定决策模型 |
| 根 `AGENTS.md` 和 `agent-memory/` 工作流 | `project-continuity.md`、预检脚本 | changed：从项目专用路径改为检测到后启用的可选模式 |
| 对话、图片、研究、连接器、桌面和 Skill 工程经验 | `delivery-recipes.md` | merged：按交付类型组织，保留原平台 playbook |
| WorkBuddy 钉钉连接器与免费额度边界 | `platform-playbooks.md` | merged |
| v1.0.0 入口、网页、安全、契约和脚本 | 原文件位置或扩展版本 | preserved |

## 完成状态

- v1.0.0 历史通过检查：Skill validator、SEH structure、YAML parse、脚本 syntax/help、task/result 正反样例、artifact verifier、ZIP 解压后 11/11 字节一致、SEH package gate。
- v1.1.0 最近通过检查：Skill validator、SEH structure（14 文件/12 链接/0 issue）、YAML、脚本 syntax/help、当前与无记忆目录两种预检、task/result 正反样例、artifact verifier、ZIP 解压后 14/14 字节一致和 SEH package gate。
- 当前有效产物：`skills/codex-ai-platform-operator/`、v1.1.0 ZIP 和 Skill 工程验收记录。
- 未验证：在另一台 Codex 的安装发现、模型触发行为和真实平台操作；v1.1.0 未新操作外部平台。
- 下一步：用户选择部署时，将 v1.1.0 源目录或 ZIP 安装到目标 Codex，运行预检并做一次只读浏览器标签调用。
