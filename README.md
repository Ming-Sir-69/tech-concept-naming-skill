<p><img src="assets/essonym-mark.png" width="112" alt="Essonym logo"></p>

# Essonym

**以名达意**

AI 技术概念命名 Skill。安装 ID 保持 `tech-concept-naming`。

为 **AI 工具、Agent、Skill、CLI 和开源项目**原创命名的 Agent Skill。先理解产品，再探索概念与词源，结合你的反馈逐步收敛；中文和英文可以独立构思。

[English](README.en.md) · [使用示例](examples/local-refinement.md) · [品牌资产包](brand/README.md) · [版本记录](CHANGELOG.md) · [反馈](https://github.com/Ming-Sir-69/tech-concept-naming-skill/issues)

支持保留已认可的词段、只修改前缀或后缀、撤回偏好、排除发音或文化含义，并说明构词依据。AI 负责创造与判断；可选 Python helper 只保存和精确修改候选状态。无需数据库或常驻服务。

## 安装

在**希望使用它的项目目录**中运行。以下是项目级安装，不是全局安装：

```sh
DISABLE_TELEMETRY=1 npx --yes skills@1.7.2 add Ming-Sir-69/tech-concept-naming-skill --skill tech-concept-naming --agent codex --copy --yes
```

使用 Claude Code 时，把 `--agent codex` 改为 `--agent claude-code`。此安装入口使用 [Vercel Skills](https://github.com/vercel-labs/skills)，要求 Node.js 22.20.0+ 和网络；环境变量关闭该 CLI 的遥测及关联审计请求，下载仍需联网。

不使用 Node：从 [Releases](https://github.com/Ming-Sir-69/tech-concept-naming-skill/releases) 下载 `tech-concept-naming-v0.1.3.zip` 并校验 `SHA256SUMS.txt`，将其中的 **tech-concept-naming** 文件夹放入：

| 宿主 | 当前项目内的安装目录 | 显式调用 |
| --- | --- | --- |
| Codex | `.agents/skills/tech-concept-naming/` | `$tech-concept-naming` |
| Claude Code | `.claude/skills/tech-concept-naming/` | `/tech-concept-naming` |

安装后重新打开项目会话。确认目录中有 `SKILL.md` 和 `scripts/naming_state.py`；只打开 GitHub 或阅读仓库根文件不代表宿主已发现 Skill。其他支持 Agent Skills 的宿主请按其安装约定操作。[兼容性与排错](docs/compatibility.md)

## 开始命名

在 Codex 中输入（Claude Code 换成上述斜杠命令）：

> 使用 $tech-concept-naming 帮我给一个 AI CLI 工具命名。它把代码修改整理成可审阅的解释，面向开源维护者。不要修改代码。先概括你对产品的理解，给三个不同概念方向，每个不超过两个名称；中文独立构思。无法核实的词源请标明。

继续用自然语言收敛：

> 我喜欢第二个方向。保留 Patch，只换后半段；不要 bot 或 -ify。中文名称先保持不变。

> 撤回“必须很短”的偏好，其他决定保留。解释新组合，不要沿用旧名称的词源说明。

预期得到产品理解、少量候选及依据、仍生效的偏好，以及需要你决定的一点。最终选择由你作出；不需要为了使用 Skill 先填表、运行脚本或授权仓库访问。[完整局部修改示例](examples/local-refinement.md)

## 可选状态保存

多轮精确修改或跨会话续接时，Agent 可使用 Python **3.9+**、仅标准库的 `scripts/naming_state.py`。不保存也能正常命名。脚本无模型调用、网络请求或 API key 要求。

```sh
python3 scripts/naming_state.py --help
python3 scripts/naming_state.py init ./naming.json --brief 'An AI CLI that explains code changes'
python3 scripts/naming_state.py show ./naming.json
```

以上命令在 Skill 安装目录运行；也可使用脚本的绝对路径，把状态路径指向你的命名工作区。状态含名称与偏好，保存在指定本地文件中；不要提交私人 brief。每次写入需要最新 `revision`，多个写入者须串行执行。[helper 使用与限制](docs/state-helper.md)

## 更新与卸载

从原来安装的项目目录运行：

```sh
DISABLE_TELEMETRY=1 npx --yes skills@1.7.2 update tech-concept-naming --project --yes
DISABLE_TELEMETRY=1 npx --yes skills@1.7.2 remove tech-concept-naming --yes
```

此卸载命令移除当前项目中各宿主的该 Skill；同时装有多个宿主时，可避免遗留共享目录。手工安装可用新版本替换 Skill 文件夹；卸载需删除该项目各宿主中的该文件夹。你独立保存的 `naming.json` 与决策笔记需自行保留或删除。

## 费用、数据与能力边界

本仓库采用 [MIT](LICENSE)，可免费使用、修改和分发。AI 宿主、模型订阅及外部检索服务的费用与数据政策由各自提供方决定；本项目不提供模型服务。[隐私与数据说明](docs/privacy.md)

本项目没有自带域名、商标、包名或词源数据库。Agent 可按任务使用获准的工具检索，并应标明实际查询来源、时间与未知。名称检查不等于商标法律意见，也不保证名称可注册。

## 开发与贡献

```sh
python3 -m unittest discover -s tests -v
```

请通过 [Issues](https://github.com/Ming-Sir-69/tech-concept-naming-skill/issues) 提交脱敏复现或使用反馈，修改说明见 [CONTRIBUTING.md](CONTRIBUTING.md)。发布不依赖 GitHub Actions、Pages、Packages 或付费 API。[维护与发布](docs/releasing.md)
