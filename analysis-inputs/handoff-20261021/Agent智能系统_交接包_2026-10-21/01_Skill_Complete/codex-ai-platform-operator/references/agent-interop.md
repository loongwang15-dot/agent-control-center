# 跨 Agent 兼容与任务契约

## 兼容层次

| 宿主能力 | 推荐用法 |
|---|---|
| Codex，识别 Skill 与 MCP | 安装完整目录；使用 `agents/openai.yaml`，按 `SKILL.md` 路由 |
| Codex，只识别 Markdown 指令 | 至少安装 `SKILL.md` 和相关 `references/`；MCP 通过配置或 CLI 接入 |
| Claude、ChatGPT Work 或其他支持文件/提示词的 Agent | 把 `SKILL.md` 当操作手册，显式提供任务 JSON 和所需参考文件 |
| 支持 MCP 的 Agent | 复用 Playwright MCP；按宿主实际工具名调用，不写死 Codex tool 名称 |
| 只能对话的 Agent | 只做规划、检查和报告；没有工具证据时不得声称执行网页动作 |
| 独立 Windows Worker | 主 Agent 发任务契约，Worker 本地执行并回传结果与证据 |

不要把 Codex 专属字段、Skill 自动发现或子 Agent API 假定为所有宿主都有。核心兼容面是 Markdown、普通文件、JSON 和平台自身 UI/API。

## 最小任务契约

保存为 `task.json`：

```json
{
  "schema_version": "1.0",
  "task_id": "task-20261020-001",
  "goal": "生成一张无文字的品牌图标并下载原图",
  "platform": "Lovart",
  "deliverable": "可打开的 PNG 文件",
  "inputs": [
    {"kind": "file", "ref": "D:/work/reference.png"}
  ],
  "constraints": {
    "acceptance": ["图标无双色以外品牌标识", "文件可打开"],
    "allowed_tools": ["playwright"],
    "human_approval": ["generate"],
    "max_retries": 1,
    "max_cost": 15
  }
}
```

必需字段为 `schema_version`、`task_id`、`goal`、`platform`、`deliverable`、`constraints`。`constraints.allowed_tools` 是最小授权集合，不是建议列表；`human_approval` 使用 `upload`、`send`、`generate`、`publish`、`pay`、`delete`、`desktop_takeover` 等动作名。

## 最小结果契约

保存为 `result.json`：

```json
{
  "schema_version": "1.0",
  "task_id": "task-20261020-001",
  "run_id": "run-01",
  "status": "PASS",
  "summary": "上传、一次生成、下载和 PNG 核验完成",
  "actions": ["附件进入输入区", "提交一次", "下载并核验"],
  "evidence": [
    {"kind": "page", "ref": "evidence/attachment.png"},
    {"kind": "file", "ref": "evidence/result-metadata.json"}
  ],
  "artifacts": [
    {
      "path": "D:/outputs/result.png",
      "media_type": "image/png"
    }
  ],
  "cost": {
    "currency": "credits",
    "before": 40,
    "after": 25,
    "spent": 15
  },
  "next_action": "无"
}
```

`status` 只能使用 `PASS`、`PARTIAL`、`FAIL`、`BLOCKED`、`NOT_RUN`、`UNVERIFIED`。没有执行的关键动作必须明确列入 `summary` 或 `next_action`。

运行：

```text
python scripts/validate_task.py --kind task task.json
python scripts/validate_task.py --kind result result.json
```

## 主从 Agent 规则

1. 主 Agent 分配明确目标、输入路径、允许工具、审批动作、预算和停止条件。
2. 子 Agent 只在任务契约内操作；需要新权限时返回 `BLOCKED`，不得自行扩张。
3. 同一平台账号、标签或桌面窗口设置单一写操作者，避免双重提交。
4. 子 Agent 返回 `PASS` 时，主 Agent抽样核验页面或结果文件。
5. 子 Agent 自述、聊天摘要和模拟数据都不能替代真实证据。
6. 交接时携带 `task_id`、`run_id`、状态、最后安全动作、证据路径、费用和下一步。

## 通用宿主启动提示

无法加载 Codex Skill 的其他 Agent 可使用以下短提示，并附上本 Skill 目录或 `SKILL.md`：

```text
你是一个平台执行操作员。先盘点目标平台、输入、交付物、可用工具、登录态和审批范围；
按正式 API/MCP/CLI、已登录浏览器、隔离浏览器、隔离桌面控制的顺序选择路径。
每次关键动作后核验真实页面状态；上传需有附件证据，生成需有可打开产物，费用和对外操作需用户授权。
连续两次同类失败即停止并切换路径。输出 PASS/PARTIAL/FAIL/BLOCKED/NOT RUN/UNVERIFIED、
实际动作、证据、产物、费用、未完成项和下一步。不要读取或输出任何密钥、Cookie 或会话令牌。
```
