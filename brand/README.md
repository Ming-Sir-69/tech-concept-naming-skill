# Essonym · Brand Kit

**以名达意**<br>
**Meaning finds a name.**

中文与英文均为正式 Slogan，分别用于各自语言受众。它们围绕同一主张创作，语法与视角可以不同，不要求互为逐字翻译。

完整生产文件在 `Essonym-brand-kit-v1.0.0.zip`。Git 跟踪矢量母版、规范与检查；PNG、PDF、ICO、ICNS 等导出格式随 ZIP 提供。

## 使用入口

- `svg/`：可编辑矢量母版。`symbol` 图形、`wordmark` 英文字标、`horizontal` 横组合、`stacked` 竖组合。
- 文件名中的 `zh`、`en`：分别带中文、英文 Slogan。没有语言后缀的主标不带 Slogan。
- `color`：G1 桑葚紫微明暗图形，深墨色字标；`black`、`white`：纯黑与反白；`plum`：桑葚紫单色。
- `png/symbol/`：16、24、32、48、64、128、256、512、1024 像素透明图标。
- `png/lockup/`：600、1200、2400 像素宽的透明字标与组合。
- `pdf/`：相同内容的矢量 PDF。
- `web/`：favicon.svg、16/32/48 多尺寸 ICO、Apple Touch、192/512 图标、maskable 图标和引用片段。
- `mac/`：macOS ICNS 图标。
- `reference/`：本人选定的 G1 原始 PNG，逐字节保留。
- `preview.png`：完整资产总览；[使用规范](guidelines.md)、[来源与生产记录](production.json)、[实际检查](checks.json)。

## 选用

| 用途 | 文件 |
| --- | --- |
| README、产品介绍 | `svg/essonym-horizontal-color.svg` |
| 中文品牌介绍 | `svg/essonym-horizontal-zh-color.svg` |
| 英文品牌介绍 | `svg/essonym-horizontal-en-color.svg` |
| 头像、Skill 图标 | `svg/essonym-symbol-color.svg` 或 `web/essonym-app-icon.svg` |
| 深底、单色反白 | 对应 `white` 文件 |
| 单色印刷 | 对应 `black` 或 `plum` 文件 |

母版均为真实路径，所有文字已转曲，不需要安装字体即可显示。字标采用 Source Serif 4 Semibold 并调整字距；这是基于开放字体的品牌排版，不是自制字体。中文 Slogan 采用思源宋体，英文 Slogan 采用 Source Serif 4 Regular。字体来源及许可证见 `fonts/` 与 production.json。

本包的原创文档与 Logo 资产沿用项目 MIT 许可；随附未修改字体保留 SIL OFL 1.1。未包含第三方 Logo、研究截图、私人对话或凭据。
