# 可选 helper

helper 只管理确定性的构词状态，不生成名称，不判断词源，不访问网络。下面从 Skill 文件夹运行，实际命名时由 Agent 将脚本路径解析到安装位置，将状态放在用户命名工作区。

```sh
python3 scripts/naming_state.py init ./naming.json --brief 'An AI CLI that explains code changes'
python3 scripts/naming_state.py add ./naming.json --expect 0 --id a --parts-json '["Patch","weft"]' --zh '补织' --rationale 'Modern English-inspired compound; a demonstration candidate'
python3 scripts/naming_state.py preference ./naming.json --expect 1 --kind like --value 'Keep Patch'
python3 scripts/naming_state.py preference ./naming.json --expect 2 --kind ban --value 'bot'
python3 scripts/naming_state.py edit ./naming.json --expect 3 --id a --index 1 --text loom
python3 scripts/naming_state.py rationale ./naming.json --expect 4 --id a --text 'Patch + loom; explanation refreshed after changing the second fragment'
python3 scripts/naming_state.py preference ./naming.json --expect 5 --kind ban --value 'bot' --remove
python3 scripts/naming_state.py show ./naming.json --id a
```

结果是 `Patchloom`，中文仍为 `补织`，`Keep Patch` 仍保留，只有 `bot` 排除被撤回。以上是软件演示数据，不代表真实用户最终选名或名称可注册。每次实际写入前都先 `show` 核对当前 `revision`；示例编号只适用于从空文件按顺序执行。

| 命令 | 用途 |
| --- | --- |
| `init` / `show` | 新建（不覆盖）/ 查看全部或单个候选 |
| `add` | 添加 1–32 个非空词段组成的候选 |
| `edit` / `insert` / `remove` | 修改、插入、删除指定 0 起始索引的词段 |
| `localize` | 更新一个语言的独立名称，不重写其他语言 |
| `rationale` | 更新解释并保留之前的解释记录 |
| `preference` | 增加 like / avoid / ban；加 `--remove` 撤回一个偏好 |
| `status` | draft / shortlisted / rejected / chosen；同时只能一个 chosen |

用 `python3 scripts/naming_state.py COMMAND --help` 查看完整参数。

`like` / `avoid` 是给 Agent 理解的语义偏好，不由脚本强制执行。`ban` 对拼接后的名称进行不区分大小写的字面子串检查；已有候选只标记，不删除。片段修改不会自动重写中文或解释，Agent 应按用户意图检查并单独更新。字符长度是 Unicode code point 数，不是视觉宽度、音节数或美感评分。

状态文件不含完整对话；关键产品理解另存短笔记。文件使用本地 JSON，创建权限 0600，写入采用临时文件替换；没有加密、跨进程锁或自动云备份。保留 schema `tech-concept-naming/v1`，未知 schema 拒绝修改。不要并发写入，也不要把 `--expect` 当成文件锁。
