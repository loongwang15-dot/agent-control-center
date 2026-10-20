# GitHub 版本备份说明

备份日期：2026-10-21（Asia/Shanghai）。仓库：loongwang15-dot/agent-control-center。

此快照保存当前定制源码、前端构建文件、安装和启停脚本、依赖锁定文件、Obsidian 知识库、项目分析及历史交接资料。AgentScope 源码以普通文件保存，包含本地修改，不依赖 Git 子模块。官方上游来源和固定提交见 README.md 与 UPSTREAM.json；保留上游许可证。

未包含 runtime/、模型凭据、SQLite 数据库、运行日志、Python 虚拟环境、Node 依赖、下载缓存和重复的 release ZIP。恢复后需重新安装依赖、配置模型凭据。此备份不包含正在运行的任务和会话数据库。

## 恢复

将仓库 clone 或完整下载并解压到新的 Windows 目录。在项目根目录执行：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -VerifySourceOnly
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\install.ps1
```

之后双击“启动总控台.cmd”。运行环境和能力边界见 README.md。

UPSTREAM.json 校验迁移包中的源码；BACKUP_MANIFEST.json 记录本次更完整备份的文件大小和 SHA-256（不包含清单自身）。根 .gitattributes 保持文件原字节，避免 Git 自动转换换行导致源码校验失败。

analysis-inputs/ 包含历史 Skill、任务成果与交接证据，其历史结论不代表本版已接通全部第三方执行平台。README.md 对迁移包不含该目录的说明仍适用于 pack_source.py；本 GitHub 私有备份额外保留了这些资料。

部分目录被现有 .gitignore 忽略，但本次已明确纳入清单。后续备份应同时核对新增文件、UPSTREAM.json 和 BACKUP_MANIFEST.json，不能仅依赖 git add .。
