# Agent 总控台与 Obsidian 知识库

这是一个 Windows 本地单用户原型：复用 AgentScope 官方服务与 Web UI，把 Agent、任务规划、会话、模型配置和本地 Markdown 知识库放在同一个入口。

当前部署验证结果见 [部署验收记录（2026-10-21）](部署验收记录_2026-10-21.md)。本地测试通过的范围以该记录为准。

默认地址为 **http://127.0.0.1:8765**。前端和 API 使用同一端口。程序只监听本机回环地址；它目前没有面向互联网的用户注册、登录和权限体系。

## 开源来源

- 官方上游：[agentscope-ai/agentscope](https://github.com/agentscope-ai/agentscope)，Apache License 2.0，见 [上游许可证](agentscope/LICENSE)。
- 当前固定源码提交：`58da57a565832ac3710d0f22318a5d0ee326a406`，对应 `2.0.11dev`。这是固定开发版提交，不能写成已基于稳定版完成生产验收。
- 本地 `control/` 负责 SQLite 配置、知识库接口和单端口托管；`agentscope/examples/web_ui/` 保留官方界面并增加知识库入口。
- 安装脚本在 Git 工作区验证上游来源及提交；迁移包没有 `.git` 时验证随包 `UPSTREAM.json` 中的源码 SHA-256。不会自动拉取、重置或覆盖已有修改，也不会在定制源码缺失时下载官方原版代替。

## 使用

已经安装好依赖时，双击 **启动总控台.cmd**。它在后台启动服务并打开浏览器；再次启动会复用同一个已验证服务。关闭浏览器不会停止服务。双击 **停止总控台.cmd** 停止本项目记录且通过健康检查的进程，保留数据库、资料和日志。

首次安装或重建依赖，在项目根目录打开 PowerShell：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\install.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\start.ps1
```

需要 Python 3.11+、Node.js 20.19+ 或 22.12+、pnpm 10+（本机验证 11.25.0）；保留 `.git` 的开发工作区另需 Git，完整迁移源码包可在没有 Git 的电脑安装。脚本优先寻找真实可执行文件，并尝试当前 Codex 捆绑运行时；不会使用 WindowsApps 的 Python 商店占位程序。如自动发现失败，可显式指定：

```powershell
.\install.ps1 -PythonPath C:\Python312\python.exe -NodePath C:\nodejs\node.exe -PnpmPath C:\tools\pnpm.cmd
```

安装期间需要联网下载 Python 包和前端依赖。Python 包使用 `control/requirements.lock.txt` 的已验证版本作为约束，前端使用 `pnpm-lock.yaml` 冻结安装。Python 与 Node.js 运行时需要预先安装，脚本不会下载安装运行时。所有临时与下载缓存定向到项目 `.cache/`。源码缺失或校验失败时停止并要求恢复完整源码包，保留现有文件；启动脚本不自动下载或更新任何东西。`ExecutionPolicy Bypass` 仅作用于本次 PowerShell 进程，不修改系统执行策略。

只启动后台服务而不打开浏览器：

```powershell
.\start.ps1 -NoBrowser
.\stop.ps1
```

## 模型和 Agent

官方界面可创建模型供应商凭据、选择模型、建立 Agent 与会话，并使用任务规划、人工确认和运行事件。**没有配置有效模型密钥时，不能进行真实模型推理。** 安装、健康检查、知识库读写和界面可用不代表模型调用已经成功；本项目不提供模拟模型成功记录。

在本机模型配置界面录入自己的 API Key 和服务地址，无需把密钥发到聊天里。模型调用费用由配置的供应商计费。本地 SQLite 会保存模型凭据；界面遮罩不等于数据库静态加密，因此 `runtime/` 不应共享或打包。

Lovart、即梦、DeepSeek 网页版、WorkBuddy 等现有平台的网页或桌面执行适配器尚未接入。配置同名模型 API 不代表获得该平台客户端内置 Agent 的全部功能。现有 Skill 和历史成果也不会仅因启动此控制台就自动成为已经验证的执行通道。

## Obsidian 知识库

在 Obsidian 选择“打开本地仓库”，打开项目根目录下的 **Obsidian知识库** 文件夹。资料以普通 UTF-8 Markdown、YAML 属性、双向链接及附件文件保存。总控台和 Obsidian 读取同一份目录，可直接用 Obsidian 编辑，也可在总控台查看、检索和更新。

当前知识库接口支持笔记目录与文本检索、读取、写入和图片附件；更新笔记使用版本校验防止覆盖较新内容，并在 `runtime/vault-history/` 保留更新前副本。Agent 通过 `VaultSearch`、`VaultRead`、`VaultWrite` 使用同一套接口；真实自主规划和整理仍需有效模型及实际任务验证。

这版检索为文本和属性检索。自动分类、语义检索、OCR、跨文档抽取、复杂格式导出与长期迭代评估应按后续任务接入和验收，不将知识库目录的建立视为这些能力已全部实现。

## 数据与故障排查

- `runtime/`：SQLite、启动记录、日志、Agent 工作区及知识库历史。包含可能敏感的模型凭据、运行内容，不要发给他人或提交到公开仓库。
- `Obsidian知识库/`：可迁移、可备份的资料原文与附件。迁移时保留链接使用的相对路径。
- `.venv/`、`.cache/`、前端 `node_modules/` 和 `dist/`：本机环境、缓存与构建文件，可按安装流程重建。
- `runtime/server.stdout.log`、`runtime/server.stderr.log`：启动与运行日志。
- `/control/status`：返回本项目标识、进程 ID、版本、上游提交和知识库位置。

如果端口 8765 被其他程序占用，启动脚本会报错并保留现状。停止脚本只有在项目标识、根目录、进程 ID、Python 路径、启动时间及本地记录全部匹配时才停止服务；健康检查失败时会拒绝终止，避免误停其他服务。Windows 虚拟环境若通过启动器创建 Python 子进程，脚本额外根据 `pyvenv.cfg` 验证基础 Python，只记录和停止实际服务进程，启动器随后自然退出。

SQLite 保存配置、会话及相关记录；内存消息总线中的实时事件和活跃任务无法保证跨重启恢复。停止前请让正在执行的任务结束，并先保存重要成果。本原型未部署到公网，也未进行多用户或生产环境验收。

## 制作不含私人运行资料的迁移包

在完整项目中运行：

```powershell
.\.venv\Scripts\python.exe .\pack_source.py --output .\release\Agent-Control-Console-source.zip
```

脚本不启动或停止服务。它保留固定上游源码、本地修改过的界面及已构建的 `dist`、`control` 服务和测试、安装与启停脚本、打包脚本及 README。已有 `dist` 随包提供，`install.ps1` 仍会根据锁定依赖重新构建。知识库只取两篇初始说明、`.obsidian/app.json` 和 `知识目录.base`；不收集其他笔记、图片或附件。`.git`、`.venv`、`.cache`、`node_modules`、`runtime`、`analysis-inputs`、日志及常见私钥和数据库文件均不进入包。上游未跟踪的资料不会被整目录扫描收进；新增加的前端代码和构建产物除外。

每份包内包含 `UPSTREAM.json`：记录官方仓库、固定开发版提交、本地源码修改路径及文件 SHA-256。它用于检测包是否缺文件或被改动，不是数字签名，也不替代可信来源校验。安装不校验初始知识库笔记的原始哈希，因此以后编辑资料不会阻止重装依赖；受校验源码被修改时需审核并重新打包，脚本不会重置修改。

在另一台 Windows 电脑将 ZIP 完整解压到新目录，先进行不下载依赖的源码核验，再安装和启动：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -VerifySourceOnly
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\install.ps1
```

迁移包不包含已经配置的密钥、会话、运行成果与用户资料；如确需迁移个人知识库，请自己另行备份并恢复到知识库目录。这里描述的是源码迁移流程；本轮没有在另一台电脑、其他操作系统或生产环境完成验收。

包内 `control/browser-smoke.cjs` 是浏览器 QA 脚本，需另行安装 Playwright 并使用其指定的浏览器；它不是生产运行依赖。执行它会产生验收用笔记、技术图片及 `runtime/evidence/` 记录，应在测试资料副本上运行；这些运行产物不随源码包交付。
