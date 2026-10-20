# Evidence Index｜本机真实证据路径

最后核对：2026-10-21 01:10（Asia/Shanghai）。下列路径均相对于仓库根目录 `D:\王文龙\其他\Codex仓库\Agent智能系统`，另有绝对路径会单独注明。账号认证数据不纳入索引。

| 文件/位置 | 本机核实 | 可支持的结论 / 限制 |
|---|---|---|
| `deliverables/新业态劳动者工伤预防宣传片脚本_DeepSeek_2026-10-20.md` | 存在，20,556 bytes，373 行 | DeepSeek Harness 桌面版生成的 3 分钟、8 场景宣传脚本；含完整分镜、台词、字幕、音效和拍摄清单。SHA-256 `8BBAF40AC38103BB99AFFEB3FF602C02994B6EE2FCBE86DCE3A13D7947F3FEF1`。 |
| `LOVART_LION_POSTER_2026-10-20.md` | 存在，本轮创建 | Lovart 狮子海报首次内容政策拒绝、简化提示词成功、下载和尺寸核验的完整记录。 |
| `deliverables/狮子主题艺术海报_Lovart_2026-10-20.png` | 存在，2,596,128 bytes | 最终狮子海报，1024×1536 PNG；SHA-256 `7F40F10479490DA7FF422ACC6320EAA1C48C543AA2D650FB9D8D0B3DE408A74B`。 |
| `C:\Users\AB\Downloads\1792507931892.png` | 存在，2,596,128 bytes | Lovart 浏览器下载原文件；与归档副本同尺寸、同体积、同哈希。 |
| `.p1-codex-lovart/lovart-lion-poster-retry-submit-2026-10-20.png` | 存在，本轮截图 | 简化提示词、GPT Image 2、中、2:3、1 张的提交前页面。 |
| `.p1-codex-lovart/lovart-lion-poster-complete-2026-10-20.png` | 存在，本轮截图 | 狮子海报已生成并打开预览的页面证据。 |
| `AI_PLATFORM_QUOTA_DAILY_CLAIM_RESEARCH_2026-10-20.md` | 存在，本轮创建 | DeepSeek、豆包/火山方舟、WorkBuddy 中国站/国际站免费额度的官方核验、区别、未执行项与每日自动化边界。 |
| `C:\Users\AB\.codex\automations\ai\automation.toml` | 存在，本轮读回 | Codex 每日 09:10 额度检查任务，状态 `ACTIVE`，仅做安全边界内检查，不自动付费、登录或授权数据共享。 |
| `WORKBUDDY_DINGTALK_WORK_SUMMARY_2026-10-20.md` | 存在，本轮创建 | WorkBuddy 钉钉插件由禁用改为启用、DWS 授权有效、今天/未来 7 天日程为空、10 条当前待办、26 条逾期待办；审批查询因 API 400002 未验证。 |
| `skills/codex-ai-platform-operator/` | 存在，14 个文件，v1.1.0 | 当前 Canonical Skill 源；入口 10,364 bytes，SHA-256 `82790c93b3be15994cba097fa3ad0d6908ce50151a2af6e9c5427813b9aae15f`。 |
| `deliverables/codex-ai-platform-operator-v1.1.0.zip` | 存在，33,961 bytes | 当前可传输 Skill 包；SHA-256 `bc1daa84e4803f4bdbe6e50c503a0b723d685c310ec45e661cddbb3d52ef10f4`；解压后与源目录 14/14 文件逐字节一致。 |
| `deliverables/Agent智能系统_交接包_2026-10-21.zip` | 存在 | 可审计交接 ZIP；含完整 Skill、项目接续、验收报告、实际成果、关键截图、任务 JSON 缺失说明、Skill 加载状态和模型切换记录。外层 ZIP 51/51 回读一致，包内清单 50/50 哈希有效。外层 ZIP SHA-256 由交付回复给出，不写入自身包内以免自引用。 |
| `handoff-package-build/Agent智能系统_交接包_2026-10-21/` | 存在，51 个文件 | 交接 ZIP 的暂存目录；含 `MANIFEST.sha256`。 |
| `skill-engineering/codex-ai-platform-operator/releases/v1.0.0/` | 存在 | v1.0.0 Skill 源和工程文档的可恢复快照。 |
| `deliverables/codex-ai-platform-operator-v1.0.0.zip` | 存在，22,543 bytes | 可传输 Skill 包；SHA-256 `a749a4c0a6c6e1bbe063675eb008b59d3fe443540b3fd2f79fea040f619e9e21`；解压后与源目录 11/11 文件逐字节一致。 |
| `deliverables/SHA256SUMS.txt` | 存在 | ZIP 校验清单。 |
| `skill-engineering/codex-ai-platform-operator/REQUIREMENTS.md` | 存在，v1.1.0 COMPLETED | 需求基线、CR-001、来源映射、排除项和未验证边界。 |
| `skill-engineering/codex-ai-platform-operator/ACCEPTANCE.md` | 存在 | v1.1.0 包级验收汇总；结构、YAML、脚本、预检、契约、产物和 ZIP 完整性通过。 |
| `skill-engineering/codex-ai-platform-operator/TEST_EVIDENCE_V1_1_0.md` | 存在 | 本轮实际命令结果、入口和 ZIP SHA-256、14/14 回读与未验证边界。 |
| `skill-engineering/codex-ai-platform-operator/qa-record.json` | 存在，SEH package gate PASS | 证据文件哈希完整；只证明记录完整性，不证明另一台 Codex 部署或模型行为。 |
| `skill-engineering/codex-ai-platform-operator/fixtures/` | 存在，4 个 JSON | task/result 正反样例与产物 manifest；用于脚本行为验证。 |
| `P1_BROWSER_INTERACTION_FIX.md` | 存在 | 最新浏览器交互故障报告：扩展模式 click 失败；普通模式和隔离 CDP click/upload 通过；Lovart 新素材未运行。 |
| `P1_CODEX_LOVART_ACCEPTANCE.md` | 存在 | 第一阶段 Codex–Lovart 真实验收记录；Lovart 页面可访问但登录身份未核实，附件上传未通过。 |
| `P1_AGENT_HANDOFF.md` | 存在 | P1-A 交接摘要，辅助索引，不替代原始报告。 |
| `P1_LOG_CONSISTENCY_ANALYSIS.md` | 存在，本分析创建并核对 | 统一历史 PASS 与当前轮次状态；指出上传、生成、下载证据被交接摘要遗漏。 |
| `P1_A_END_TO_END_ACCEPTANCE_2026-10-20.md` | 存在，本阶段报告 | P1-A 自动上传→一次生成→实际扣费→页面下载→本地原图核验的 PASS 证据汇总。 |
| `P1_B_JIMENG_READONLY_2026-10-20.md` | 存在，本阶段报告 | 即梦首页 PASS；用户登录后登录框消失；主创作区 PARTIAL；重读取桥接超时；无生成/额度消耗。 |
| `.p1-codex-lovart/jimeng-workbench-readonly-2026-10-20-1925.png` | 存在 | 即梦登录后工作台：创作/探索/资产/主体/画布、生成/画布切换、Agent 模式、提示词和附件入口可见；未生成。 |
| `.p1-codex-lovart/jimeng-upload-drop-2026-10-20-1929.png` | 存在 | 即梦参考图拖放后画面：输入区出现测试图缩略图；未提交、未生成。 |
| `JIMENG_TYPOGRAPHY_2026-10-20.md` | 存在，本次任务报告 | 即梦字体设计单批提交、积分 40→28、4 张实际产出与平台状态提示差异的完整记录。 |
| `.p1-codex-lovart/jimeng-typography-reference-2026-10-20.png` | 存在，191,977 bytes | 用户提供的蓝字排版样张副本；用于本轮拖放上传。 |
| `.p1-codex-lovart/jimeng-typography-2026-10-20-2054/` | 存在，4 个唯一 PNG 加 1 个推荐版副本 | 4 张即梦输出均为 2560×1440；大小、尺寸和 SHA-256 见任务报告。平台水印保留。 |
| `jimeng-typography-submit-ready-2026-10-20.png` | 存在；页面截图 | 提交前显示参考图、完整提示词和“海报设计”技能。 |
| `jimeng-typography-final-page-2026-10-20.png` | 存在；页面截图 | 4 张结果与“任务提交失败”提示同时出现；不能仅据提示判定生成失败。 |
| `PINTEREST_HANDBOOK_COVER_REFERENCES_2026-10-20.md` | 存在，本次任务报告 | 12 个 Pinterest 公开 Pin、现有封面视觉分析、三套新版方向与版权/来源边界。 |
| `.p1-codex-lovart/pinterest-research/original-handbook-cover-2026-10-20.png` | 存在，959,750 bytes | 用户提供的原版手册封面副本。 |
| `.p1-codex-lovart/pinterest-research/pinterest-handbook-moodboard-verified-2026-10-20.png` | 存在，698,770 bytes | 12 个经 Pin 页面公开元数据核验的封面参考总览。 |
| `ALL_WEB_HANDBOOK_COVER_REFERENCES_2026-10-20.md` | 存在，本次任务报告 | 花瓣、Pinterest、Behance、Dribbble、Freepik/Magnific、Canva 的全网参考索引及三项设计方向。 |
| `.p1-codex-lovart/cover-reference-research/original-handbook-cover-2026-10-20.png` | 存在，959,750 bytes | 原版封面副本，放于全网参考目录。 |
| `.p1-codex-lovart/cover-reference-research/huaban-5077834180-party-history-album.webp` | 存在，22,814 bytes | 花瓣政务活动册缩略图样例，仅作版式研究。 |
| `P1_C_PLATFORM_ACCESS_2026-10-20.md` | 存在 | DeepSeek/豆包网页未登录、豆包桌面句柄异常、WorkBuddy 桌面只读 PASS 的汇总。 |
| `background-tests/TASK_SPEC.md` | 存在 | 三平台统一复杂任务、100 分评分标准、原始结果与汇总格式。 |
| `background-tests/deepseek/raw-response.md` | 存在，真实回复 | DeepSeek 对统一复杂任务的完整 Markdown 结果。 |
| `background-tests/deepseek/meta.json` | 存在 | DeepSeek 执行方式、模型、时间、前台干扰和 PASS 状态。 |
| `background-tests/deepseek/score.md` | 存在 | DeepSeek 七维评分，总分 96/100。 |
| `background-tests/workbuddy/raw-response.md` | 存在，真实回复 | WorkBuddy 对统一复杂任务的完整 Markdown 结果。 |
| `background-tests/workbuddy/meta.json` | 存在 | WorkBuddy 执行方式、版本、模型、时间、前台干扰和 PASS 状态。 |
| `background-tests/workbuddy/score.md` | 存在 | WorkBuddy 七维评分，总分 99/100。 |
| `background-tests/comparison.md` | 存在 | 三平台实际执行/阻断状态，不把单端成功外推到其他平台。 |
| `background-tests/LONG_REASONING_TASK.txt` | 存在 | 可精确复核的长思考调度题原文。 |
| `background-tests/LONG_REASONING_EXPECTED.md` | 存在 | 标准最优答案、排程和自动验收条件。 |
| `background-tests/long-thinking/workbuddy/raw-response.md` | 存在，真实回复 | WorkBuddy 长思考题完整答复，最终值 110。 |
| `background-tests/long-thinking/deepseek/raw-response.md` | 存在，真实回复 | DeepSeek 长思考题完整答复，最终值 110。 |
| `background-tests/long-thinking/comparison.md` | 存在 | 两端 PASS、豆包 BLOCKED 及中断恢复记录。 |
| `验证记录.md` | 存在，本分析完整读取 | 关键历史原始记录：1 次生成、1 次修改、两次下载、12:26 自动附件上传成功。必须以新追加章节作为最新历史证据。 |
| `.playwright-mcp/page-2026-10-20T04-26-16-857Z.yml` | 存在，12:26 | 页面快照出现 `lovart-test-reference` 附件；文件内第 107 行对应附件 chip。 |
| `.playwright-mcp/page-2026-10-20T04-26-37-432Z.png` | 存在，12:26，1256×1194 | 页面截图显示 Lovart 输入区附件 chip；只证明附件已进入输入区，未发送。 |
| `C:\Users\AB\Downloads\1792468634751.png` | 存在，本分析核实 | 首次生成下载图；1,950,508 bytes，1254×1254。 |
| `C:\Users\AB\Downloads\1792469269766.png` | 存在，本分析核实 | 修改版下载图；2,172,135 bytes，1254×1254。 |
| `.playwright-mcp/page-2026-10-20T03-56-41-531Z.png`、`page-2026-10-20T04-07-02-639Z.png` | 存在 | 首次生成和修改完成的页面截图。 |
| `.playwright-mcp/console-2026-10-20T10-46-30-910Z.log` | 存在，18:46 更新 | 当前 MCP 标签调用仍可连接 Lovart 项目；不包含或导出认证数据。 |
| `.p1-codex-lovart/` 本轮尚无新截图 | 18:51 单次 Lovart 点击未产生任何页面变化 | 官方 `browser_click` 超时；事后 DOM 核验按钮 `data-state=closed`、无 dialog、无 file input、无附件。故本轮没有可支持的“上传已执行”证据。 |
| `.p1-codex-lovart/lovart-auto-upload-2026-10-20-1901.png` | 存在，399,870 bytes，1849×1194 | 重连后自动上传成功：Lovart 输入区出现 `reference_test` 附件 chip，余额仍显示 40；未发送、未生成。 |
| `.playwright-mcp/page-2026-10-20T11-01-14-896Z.yml` | 存在 | 上传调用后的页面快照，第 111 行包含 `reference_test`；可交叉确认附件 chip。 |
| `.p1-codex-lovart/lovart-submit-ready-2026-10-20-1905.png` | 存在 | 提交前画面：参考图、提示词、GPT Image 2、中/1:1/1 张、15 积分、余额 40。 |
| `.p1-codex-lovart/lovart-generation-complete-2026-10-20-1906.png` | 存在 | 新作品出现，余额显示 25。 |
| `.p1-codex-lovart/lovart-download-preview-2026-10-20-1906.png` | 存在 | 作品预览和下载按钮可见。 |
| `C:\Users\AB\Downloads\1792494403770.png` | 存在，本阶段核实 | P1-A 本地输出：1,146,988 bytes，1254×1254 PNG，图像可正常读取。 |
| `.codex/config.toml` | 存在 | 项目 Playwright MCP 启动配置，使用 `--extension`；不在此复制完整配置内容。 |
| `.tools/playwright-mcp/node_modules/@playwright/mcp/package.json` | 存在，本机读取版本 0.0.83 | MCP 包版本。 |
| `.p1-codex-lovart/interaction-probe.html` | 存在 | 本地按钮计数器与原生文件输入探针页。 |
| `.p1-codex-lovart/Agent_Work_OS_P1_Codex_Lovart_MCP_2026-10-20/fixtures/reference_test.png` | 本机已核实存在 | 测试 fixture；隔离页面读回 803 bytes、`image/png`。 |
| `.p1-codex-lovart/cdp-upload-success.png` | 本机已核实存在 | 隔离 loopback CDP 的真实本地上传结果截图。 |
| `.p1-codex-lovart/local-upload-success.png` | 本机已核实存在 | 隔离普通 Playwright 模式上传截图。 |
| `.p1-codex-lovart/isolated-15000-click.png` | 报告记录；需在使用时核实存在 | 单次 15 秒诊断截图。 |
| `.p1-codex-lovart/lovart-page.png`、`lovart-attachment-menu.png`、`lovart-upload-attempt-failed.png` | 本机已核实存在 | 先前 Lovart 页面/附件入口/失败状态；没有新附件预览。 |
| `.p1-codex-lovart/mcp-cdp-diagnostic.mjs`、`mcp-isolated-diagnostic.mjs`、`mcp-normal-5s.mjs` | 本机已核实存在 | 一次性诊断脚本；不可把脚本存在当作测试通过。 |
| `.playwright-mcp/` | 目录存在，共 76 个文件、约 2.23 MB | 原始 MCP 日志/快照；可能含页面隐私，不要整目录打印、提交或公开。 |
| `Agent_Work_OS_v1.1/reports/OPENCLAW_RUNTIME_ACCEPTANCE_2026-10-20.md` | 存在并已读取 | OpenClaw/Gateway/DeepSeek/主子 Agent 进度；只能证明各自测试，不是 Codex–Lovart 上传证据。 |
| `Agent_Work_OS_v1.1/reports/PROGRESS.md` | 存在并已读取 | AgentScope 2.0 项目进度与阻塞。 |
| `Agent_Work_OS_v1.1/reports/evidence/AS_local_verification.log` | 存在并已读取 | AgentScope 本地工具/测试记录；不代表真实在线 AgentScope UI/runtime 通过。 |
| `Agent_Work_OS_v1.1/AGENTS.md` | 存在，保留未改 | v1.1 子目录约束；根目录原来没有 `AGENTS.md`。 |
| ZIP：`C:\Users\AB\Downloads\Agent_Work_OS_%E6%A8%A1%E5%9E%8B%E5%88%87%E6%8D%A2%E4%B8%8E%E9%A1%B9%E7%9B%AE%E8%AE%B0%E5%BF%86_v1.0.zip` | 已读取清单、README 和所有 Markdown | 部署来源。路径带 URL 编码名称。 |

截图只证明画面当时可见的状态。文件上传必须有页面文件读回、附件 chip 或等价结果证据。任何引用状态在新会话中都应重新核实时间敏感项；`NOT RUN` 必须标明轮次，不能覆盖历史 PASS。Playwright Extension 状态页完整快照不得保存或纳入证据索引。

注：`P1_AGENT_HANDOFF.md` 中“本轮尚无新截图”的历史描述适用于 18:51；19:01 已产生新的成功截图，当前状态以本表新增行和 `01_CURRENT_STATE.md` 为准。

