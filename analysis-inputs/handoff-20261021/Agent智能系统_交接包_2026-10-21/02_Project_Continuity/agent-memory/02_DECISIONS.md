# Decisions｜有效技术决策与优先级

> 只记录能改变未来 Agent 行为的决策。补充新决定时新增条目，不要无痕删除旧记录。

## D-001｜Codex 是当前唯一主控

**有效（2026-10-20）**：Codex Windows 客户端优先作为本地任务主 Agent；OpenClaw、AgentScope 保留作可选能力/已验证资产，不作为当前 P1-A 的必经调度节点。

原因：用户当前最关心跨平台真正执行工作，避免重复调度、重复建立 UI。

## D-002｜优先控制现有平台，不强制改为模型 API

**有效**：现有豆包、WorkBuddy、DeepSeek、Lovart、即梦的桌面/网页版功能要尽可能直接复用。开放正式接口时可优先正式接口，但不以替换全部目标软件的能力为前提。

## D-003｜Lovart 上传必须有页面预览证据

**有效**：只读页面 PASS ≠ 上传 PASS；浏览器调用成功 ≠ 文件到达。需要页面出现新素材或有等价可验证证据；生成与消费积分必须事先得到用户许可。

## D-004｜保留已有配置和运行证据

**有效**：不重建整个平台、不覆盖已登录浏览器 Profile、原有 Codex/AgentScope/OpenClaw/Skill 文件；优先最小配置修复，任何额外安装与系统范围变更需审慎审批。

## D-005｜跨模型交接以项目文件为准

**有效**：`AGENTS.md` 为自动入口；`agent-memory/` 为持久化项目上下文；原始源码与实际测试报告优先于口头概述。不假设新模型继承旧会话上下文。

## D-006｜浏览器点击故障先最小复现

**被 D-007 更新**：扩展模式在普通本地 HTML 页点击失败；隔离普通 Playwright 与隔离 CDP 模式通过。保留最小复现和有限重试要求。

## D-007｜P1 浏览器交互故障定位（2026-10-20）

**有效**：失败定位在 Playwright Extension 控制/actionability 路径的可能性最高，而不是探针页面或单纯 5 秒超时；具体内部缺陷仍未确认。隔离 CDP 可用于本地验证，不代表已登录 Lovart 可用。不得在无单独明确授权时附着登录 Profile。证据：`P1_BROWSER_INTERACTION_FIX.md`。

## D-008｜跨模型记忆作为项目工作流（2026-10-20）

**有效**：新会话先读根 `AGENTS.md` 和 `agent-memory/00_PROJECT_BRIEF.md` 至 `05_HANDOFF_LOG.md`；阶段结束/模型切换前照 `prompts/切换前交接指令.md` 更新状态、下一步、证据和日志。验收状态只能由真实证据支持。来源：用户提供并已解压的模型切换记忆 ZIP。

## D-009｜根指令文件实际情况（2026-10-20）

**有效**：部署前仓库根目录没有 `AGENTS.md`，但 `Agent_Work_OS_v1.1/AGENTS.md` 存在。创建轻量根级引导与跨模型规则，不覆盖 v1.1 子目录文件；若后续发现其他根级规则文件，应先比对再合并。

## D-010｜状态必须区分历史结果与当前轮次（2026-10-20）

**有效**：验收状态必须写成“历史 PASS/FAIL”或“当前轮次 NOT RUN/UNVERIFIED”，不得用单轮的 `NOT RUN` 覆盖项目历史。尤其以 `验证记录.md` 为准保留 Lovart 自动上传、生成、修改和下载的真实证据；后续模型不得重复已通过的基础验收。

原因：本轮发现交接摘要把 Lovart 上传与生成写成项目级 `NOT RUN`，遗漏了 12:26 自动附件上传成功和余额 70→40 的真实生成/修改记录，导致根因判断过宽。  
影响：后续优先修复当前 Extension 会话复现性；只有在用户明确授权时才补测“自动上传→生成→下载”的新消耗闭环。  
证据：`P1_LOG_CONSISTENCY_ANALYSIS.md`、`验证记录.md`、`.playwright-mcp/page-2026-10-20T04-26-16-857Z.yml`。

## D-011｜Extension 状态页不作为常规诊断入口（2026-10-20）

**有效**：自动快照 Playwright Extension 状态页会展开连接配置并暴露敏感连接令牌。默认禁止再打开该页或其完整 accessibility snapshot；如需检查版本或连接状态，只允许使用窄范围、无凭据返回的只读查询。若发生意外暴露，不记录令牌值，立即删除自动快照并建议由用户在本地重新生成令牌。

原因：18:52 的常规连接诊断打开状态页后，自动快照包含连接令牌。页面已关闭、对应项目快照已删除，未使用令牌执行操作。  
影响：后续浏览器诊断优先使用 Lovart 当前页的窄 DOM 查询或普通本地探针；不回读扩展状态页。  
证据：18:52 状态检查与本轮交接记录；令牌值未写入项目文件。

## D-012｜P1-A 完成并进入 P1-B（2026-10-20）

**有效**：P1-A 以 19:06 的真实端到端结果记为 PASS；下一阶段切换为 P1-B——沿用同一 Codex + Playwright MCP 浏览器底座，对即梦网页做只读登录态、页面能力和控制入口核验。未获明确积分授权不得执行即梦生成。

原因：已真实完成自动附件上传、一次 GPT Image 2 生成、余额 40→25、页面下载和本地 PNG 核验。  
影响：不再重复 Lovart 上传/生成验收；其他平台接入不得借用 Lovart PASS 作为证据。  
证据：`P1_A_END_TO_END_ACCEPTANCE_2026-10-20.md`。

## D-013｜即梦登录由用户完成（2026-10-20）

**有效**：即梦工作台显示 `need_login=true` 时，Agent 不得自动完成第三方抖音授权、输入验证码或接受新授权条款。用户必须在现有 Chrome Profile 中手动登录；Agent 只保留正常页面并做后续只读核验。

原因：打开即梦工作台后，站点自动弹出多个抖音 OAuth 标签。自动操作登录会扩大账号授权范围且涉及认证数据。  
影响：P1-B 当前等待用户登录；未登录前不进行页面能力和生成测试。  
证据：`P1_B_JIMENG_READONLY_2026-10-20.md`。

## D-014｜P1-B 深层页面读取避免并行 ref 快照（2026-10-20）

**有效**：即梦工作台已登录后，较重的局部 accessibility snapshot 与 DOM 查询在并行调用时同时 120 秒超时；轻量 `browser_tabs(list)` 仍可用。后续优先使用单次、窄范围查询；若同类读取连续两次超时，停止并重连 Extension，不对局部 ref 并行做快照。

原因：页面可访问但桥接在重读取时再次卡顿，不能把超时误判为登录失败或页面缺失。  
影响：P1-B 保持 PARTIAL，先恢复稳定读取，再补全侧边栏与上传控件验证。  
证据：`P1_B_JIMENG_READONLY_2026-10-20.md`。

## D-015｜即梦上传入口尚未通过（2026-10-20）

**被 D-016 更新**：普通点击获得焦点但没有建立 File chooser；当时不得将入口点击单独记为上传 PASS。

原因：点击成功与文件选择器成功是不同验收层级。  
影响：P1-B 页面接入/只读能力可记 PASS，但上传链路保持 PARTIAL；生成仍为 NOT RUN。  
证据：`P1_B_JIMENG_READONLY_2026-10-20.md`、`.p1-codex-lovart/jimeng-workbench-readonly-2026-10-20-1925.png`。

## D-016｜即梦拖放上传可验收，P1-B 完成（2026-10-20）

**有效**：即梦“上传参考”普通 click 未打开 File chooser，但官方 `browser_drop` 将 `reference_test.png` 拖入后，生成区出现真实 blob 缩略图并可移除，足以证明文件进入页面。P1-B 页面接入与参考图上传记为 PASS；生成仍为 NOT RUN。

原因：拖放是网站实际支持的浏览器交互路径，结果由页面缩略图与 blob URL 双重验证。  
影响：不再重复即梦入口点击；进入 P1-C。  
证据：`.p1-codex-lovart/jimeng-upload-drop-2026-10-20-1929.png`。

## D-017｜P1-C 优先桌面现有客户端（2026-10-20）

**有效**：用户明确要求豆包直接连接桌面版，后续不以豆包网页替代桌面验收。WorkBuddy 桌面窗口可作为只读接入 PASS；豆包桌面窗口句柄异常时记录 BLOCKED，不用网页结果冒充。

原因：目标优先复用已有客户端能力，且用户明确指定豆包桌面版。  
影响：豆包桌面接入等待窗口句柄修复或客户端/helper 重启；WorkBuddy 可继续。  
证据：`P1_C_PLATFORM_ACCESS_2026-10-20.md`。

## D-018｜Windows 原生 GUI 默认隔离运行（2026-10-20）

**有效**：用户在前台工作时，不使用 Windows Computer Use 操作同一活动桌面。网页任务优先 Playwright MCP，软件有正式 API/MCP/CLI 时优先结构化集成；必须操作原生 GUI 时，使用独立 Windows VM、Windows Sandbox、第二台电脑或独立测试机。只有用户在当前指令中明确同意接管主桌面时才例外，并按 Escape/停止要求立即退出。

原因：用户反馈桌面自动化会抢占控制权。官方 Computer Use 文档明确说明 Windows 上会在当前活动桌面前台移动指针、输入文字并接管输入，没有同桌面后台控制模式。  
影响：后续不得让豆包/WorkBuddy/DeepSeek 等桌面接入默认打断用户前台操作；不能后台化的流程改在隔离设备执行。  
证据：<https://learn.chatgpt.com/docs/computer-use.md>；根 `AGENTS.md` “前台不干扰与桌面控制边界”。

## D-019｜后台操控桌面版采用隔离 VM 内 Worker（2026-10-20）

**有效**：若必须直接操控豆包、DeepSeek、WorkBuddy 等桌面客户端，首选在持久 Windows 虚拟机、第二台 Windows 电脑或远程工作站内运行独立 Codex Worker。主桌面 Codex 只负责任务派发、结果收集和验收，不把 SendInput/UIA 输入打到用户当前活动桌面。

明确排除：

- Windows“虚拟桌面”只切换桌面内容，不隔离输入焦点；
- 最小化窗口不能保证 UI 自动化不会切前台；
- 当前 Windows Computer Use 会占用活动桌面；
- 复制主浏览器/客户端 Cookie、Token 或登录数据到隔离环境不可接受。

原因：本机为 Windows 10 Pro，具备 Hyper-V 路线基础；目标桌面客户端包含 Electron/WebView，UIA 背景调用稳定性不足，隔离 Worker 是唯一能同时保证功能完整与前台不干扰的通用方案。  
影响：先验证/启用虚拟化，再创建持久 VM，并在 VM 内安装 Codex Worker 和目标客户端；完成前不承诺三平台桌面版后台任务。  
证据：<https://learn.chatgpt.com/docs/computer-use.md>、`background-tests/TASK_SPEC.md`。

## D-020｜三平台测试不得以单端成功代替（2026-10-20）

**有效**：DeepSeek 完成复杂任务只能记为 DeepSeek PASS；WorkBuddy 输入注入失败和豆包窗口句柄异常必须分别保持 BLOCKED，不能据此推断三平台后台能力已通过。

原因：本次只有 DeepSeek 真实提交并返回结果；其他两端没有发送任务。  
影响：三平台对比继续以 `background-tests/comparison.md` 为准；不得把网页版或其他客户端成功混算为桌面版验收。  
证据：`background-tests/deepseek/raw-response.md`、`background-tests/comparison.md`。

## D-021｜豆包桌面窗口绑定暂停重复重试（2026-10-20）

**有效**：当前 Computer Use `window2` 对豆包桌面窗口持续返回“窗口不属于该应用，但当前所有者仍是该应用”的矛盾错误。已排除登录、单次窗口陈旧和 helper 状态：Codex 重启后，豆包应用级和精确 exe 路径启动仍复现。后续不得继续用同一 API 重复绑定；应等待 Computer Use/豆包更新，或改用独立的 Windows UI Automation 适配器/隔离环境。

原因：连续三个新窗口 ID 在不同启动路径下均在同一读取调用失败，属于窗口标识兼容缺陷。  
影响：豆包复杂任务继续 BLOCKED；WorkBuddy/DeepSeek 结果不受影响。  
证据：2026-10-20 20:38 交接记录。

## D-022｜即梦单批创作授权与真实产出验收（2026-10-20）

**有效**：用户在当前指令中明确要求“用即梦设计字体”，视为对该单批生成及其必要积分消耗的授权。执行时只提交一次；后续追加生成、重新生成或付费仍需新的明确指令。

验收以页面真实产出的可打开图片和本地下载文件为准，不以内置 Agent 的状态提示单独覆盖结果；若页面同时出现矛盾提示，必须同时记录提示和真实资产。即梦输出若自带平台标识，不擅自移除或规避。

原因：本次生成页面最终显示“任务提交失败，请稍后再试”，但 4 张图均完整生成，积分 40→28，且 4 张 2560×1440 PNG 已实际下载并检查哈希。

影响：以后即梦字体/海报任务按“单批一次、产出和提示分开验收、平台水印保留”处理。

证据：`JIMENG_TYPOGRAPHY_2026-10-20.md`、`.p1-codex-lovart/jimeng-typography-2026-10-20-2054/`。

## D-023｜Pinterest 登录墙下的公开参考检索方式（2026-10-20）

**有效**：Pinterest 站内搜索在当前浏览器会话显示登录墙时，不自动登录、不输入第三方凭据。允许通过 Google 图片索引发现公开 Pinterest Pin，再直接访问 Pin 页面读取公开标题、描述和 `og:image` 元数据，形成来源可追溯的参考总览。

必须区分“索引缩略图”“Pin 页面公开元数据”和“登录后的站内收藏/完整推荐流”。引用图片仅用于版式研究，不把缩略图当成可商用素材。

原因：本次 Pinterest 搜索页连续两次截图失败且正文只有登录层；Google 索引返回真实 Pin 链接，12 个 Pin 均可读到公开元数据。

证据：`PINTEREST_HANDBOOK_COVER_REFERENCES_2026-10-20.md`、`.p1-codex-lovart/pinterest-research/pinterest-handbook-moodboard-verified-2026-10-20.png`。

## D-024｜WorkBuddy 钉钉连接器采用官方插件与 DWS 登录态（2026-10-20）

**有效**：WorkBuddy 的钉钉接入使用官方 `dingtalk@workbuddy-connector-plugins-official` 插件及其内置 `dws` CLI。插件安装不等于启用；需以 WorkBuddy 插件状态 `enabled: true` 和 `dws auth status` 的 `authenticated: true` 分别验收。后续可通过 WorkBuddy CLI 的 `plugin enable/disable` 管理启用状态，避免手工修改插件状态文件。

原因：本次发现该插件虽已安装且 DWS 可登录，但 WorkBuddy 账户状态中仍为禁用；启用后官方 CLI 才明确返回插件已启用。

影响：WorkBuddy 当前已打开的会话可能需新开任务或重载插件才能加载变更。WorkBuddy 独立 headless CLI 的模型登录状态与钉钉 connector 登录状态是两个独立验收项，不能用一方成功替代另一方。

证据：`WORKBUDDY_DINGTALK_WORK_SUMMARY_2026-10-20.md`。

## D-025｜额度每日任务不得代替用户接受数据授权或消费（2026-10-20）

**有效**：免费额度每日检查只处理官方页面中明确标示、免费且无需新增授权的“签到/领取”动作。火山方舟协作奖励涉及推理数据用于模型优化，WorkBuddy 国际站每日活跃任务要求桌面客户端真实提交且可能消耗积分；这两类不能由定时任务静默代为授权或提交，除非用户针对对应账号和动作另行明确批准。

原因：官方额度机制并非统一的每日签到；把“自动领取”扩大为自动接受数据共享、自动开通常用服务或每天消费积分，会改变授权范围和账号成本。

影响：已建立的 `AI平台额度每日核验与领取` 任务只做官方入口检查和安全领取；遇到登录、验证码、桌面接管、数据共享条款、付费或新增订购时停止并通知。

证据：`AI_PLATFORM_QUOTA_DAILY_CLAIM_RESEARCH_2026-10-20.md`、`C:\Users\AB\.codex\automations\ai\automation.toml`。

## D-026｜Lovart actionability 超时的有限回退（2026-10-20）

**有效**：当 Lovart 普通 Playwright 点击连续两次停在 visible/enabled/stable 等待，但只读诊断确认目标按钮未禁用、可见、可交互且中心无遮挡时，可在当前明确授权的单次任务内改用 Playwright `force:true` 激活。该回退不得用于跳过文件上传或生成成功验收；必须继续以页面进入真实处理状态、作品出现、预览可打开、下载文件可读等结果证据判定 PASS。

原因：本轮狮子海报的生成、缩略图预览和下载按钮均出现 actionability 超时，但按钮计算样式正常；force 激活后页面真实进入“生成中”，随后完成、预览和下载均成功。

影响：遇到同类 Lovart 桥接/稳定性问题时不再无限重复普通点击；先做一次窄范围只读诊断，再切换有限回退。连续结果失败仍按停止条件处理，不扩大为账号、付费或发布操作。

证据：`LOVART_LION_POSTER_2026-10-20.md`、`.p1-codex-lovart/lovart-lion-poster-complete-2026-10-20.png`、`C:\Users\AB\Downloads\1792507931892.png`。

## D-027｜Agent 智能系统采用单一可移植 Skill 入口（2026-10-21）

**有效**：当前项目的 Agent 智能系统以 `codex-ai-platform-operator` v1.1.0 作为可移植入口，不新增第二个功能重叠的“项目总 Skill”。入口负责系统模型和控制面选择，项目接续、交付类型、网页操作、平台经验、跨 Agent 契约、安全与安装说明按需加载。

原因：v1.0.0 已覆盖平台操作；本次用户需要的是把 Agent 智能系统作为整体复用。如果另建同义 Skill，会造成自动触发竞争、规则重复和版本分裂。

影响：后续系统性能力扩展优先更新该 Canonical 包并递增版本；项目专用截图、账号状态、聊天和认证信息仍留在项目证据层，不进入 Skill。安装到另一台设备属于独立部署动作，不能因包级 PASS 自动执行或宣称已部署。

证据：`skills/codex-ai-platform-operator/`、`deliverables/codex-ai-platform-operator-v1.1.0.zip`、`skill-engineering/codex-ai-platform-operator/ACCEPTANCE.md`。

## 变更规则

新增决定格式：日期 / ID / 状态（有效、取代、待验证）/ 决策 / 原因 / 影响 / 证据。新的用户明确授权和需求优先于历史架构文档；如冲突，先呈报并更新本文件。
