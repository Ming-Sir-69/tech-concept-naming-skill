# 维护与发布

发布仅使用 Git、ZIP 和 GitHub 原生 Release，无需 CI、数据库或服务。`VERSION`、`CHANGELOG.md`、tag 与下载包版本应一致。

1. 对 Skill 做格式校验；修改 helper 后运行 `python3 -m unittest discover -s tests -v`。
2. 在临时项目测试安装、更新、卸载及 ZIP 解压路径。明确区分文件落位、宿主发现与真实模型执行，不能相互替代。
3. 检查将公开的**全部 Git 历史**：不带私人对话、凭据、用户状态、宿主调试日志和未经授权的第三方资产；提交身份使用公开邮箱。
4. 在干净的分发仓库提交并打版本 tag。仅从该仓库导出：

```sh
 git archive --format=zip --prefix=tech-concept-naming/ --output=../tech-concept-naming-v0.1.0.zip v0.1.0
```

5. 在包所在目录生成 `SHA256SUMS.txt`：macOS 使用 `shasum -a 256 tech-concept-naming-v0.1.0.zip > SHA256SUMS.txt`，Linux 可用 `sha256sum`。用户可用 `shasum -a 256 -c SHA256SUMS.txt` 校验。
6. GitHub Release 附上 ZIP、校验和与面向用户的变更说明。发布后匿名访问仓库和下载包，再检查安装命令。

公开分发库是 `Ming-Sir-69/tech-concept-naming-skill`，Skill ID 始终为 `tech-concept-naming`。研究资料和私人原始验证记录不在分发库中。维护期保持 GitHub Actions 关闭；未启用 Pages、Packages、Codespaces 或付费 API。普通 Git push、源文件与 Release 附件不依赖这些计量功能；GitHub 仍有一般容量与速率限制。
