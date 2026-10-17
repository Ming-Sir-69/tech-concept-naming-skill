# 兼容性与排错

| 路径 | 当前证据 | 边界 |
| --- | --- | --- |
| Codex 仓库级 Skill | 真实 CLI 发现、读取 Skill 与模型完成命名任务已有记录 | 本机默认模型传输曾超时；临时 HTTP 调用成功不代表每台机器或默认传输正常 |
| Claude Code | 采用官方项目级 Skill 约定；安装包落位另作发布检查 | 尚未完成 Claude Code 模型端到端命名验收 |
| 其他 Agent Skills 宿主 | 提供标准 `SKILL.md` 和相对资源路径 | 未逐个验收，请按宿主文档安装 |
| 可选 helper | Python 3.9.6、3.12.12：18 项回归通过 | 需要可执行本地命令；仅限串行写入 |

纯 Skill 使用不要求 Python。helper 不要求 Node 或 pip 依赖。只有可选的 `skills@1.7.2` 安装器要求 Node.js 22.20.0+。

## 未发现 Skill

确认安装在当前项目的 `.agents/skills/tech-concept-naming/`（Codex）或 `.claude/skills/tech-concept-naming/`（Claude Code），其中直接包含 `SKILL.md`，没有多套一层 ZIP 目录。重新打开项目会话后显式调用。宿主也可能有自己的发现范围与开关，应查其官方文档：

- [Codex Skills](https://learn.chatgpt.com/docs/build-skills)
- [Claude Code Skills](https://code.claude.com/docs/en/skills)
- [Agent Skills 规范](https://agentskills.io/specification)

## 模型超时或没有工具

先确认宿主能完成一条普通对话。Skill 不提供模型连接、账户或代理配置；此类错误请保留脱敏报错并按宿主文档排查。无法运行 Python 时可直接用对话或简短决策笔记保留偏好，无需中断命名。

## helper 报 stale revision

先 `show` 读取当前状态，再针对该状态决定修改并传入最新 `--expect`。不要盲目重试旧命令。两个 Agent 不应同时写同一状态文件。

## 卸载后仍可发现 Skill

同时安装多个宿主时，安装器可能保留 `.agents/skills/` 共享目录。使用 README 中不带 `--agent` 的项目级 `remove tech-concept-naming --yes`，然后重新打开会话。它移除当前项目各宿主中的此 Skill，独立保存的命名状态不受影响。
