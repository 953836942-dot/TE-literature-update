# TE Literature Radar

[English README](README.md)

TE Literature Radar 是一个面向热电研究的开源源码项目。它使用 Crossref、OpenAlex、arXiv 和可选 RSS 搜索新文献，先通过确定性的 TE 相关性、质量、研究方向匹配和时效性规则做筛选，再由 Codex 基于实际提供的 title/abstract/metadata 判断创新性并生成科研总结，最后由代码计算 A/B/C 等级。

## 主要功能

- 搜索 thermoelectric、Seebeck、zT、power factor、热/电输运、掺杂、band/defect/phonon engineering、ML/AI materials discovery 等方向。
- 支持重点期刊、作者、材料体系和关键词配置。
- DOI 优先去重，缺 DOI 时使用标题/作者回退。
- 支持 `auto`、`lookback` 和 `range` 三种时间模式。
- 正式期刊论文优先；低级别期刊如果创新很强仍可进入 A/B。
- Preprint 使用更严格阈值，并明确标注 `Preprint — not peer reviewed`。
- A/B 文献输出：目的、创新、如何解决、效果、机制、意义、局限和 Radar 判断。

## 真实性规则

- 高水平期刊不能绕过 TE relevance gate。
- Codex 不能直接决定总分和 A/B/C，最终等级由代码计算。
- Codex 输出中的科学数值必须能在提供的 title/abstract/metadata 中找到；不存在的数字会被 validator 拒绝。
- 只读取了摘要/metadata 时，不能写成“已阅读全文”。
- 自动模式只有在最终输出成功（若启用邮件则邮件也成功）后才推进 state。

## 运行要求

- Python 3.11+
- 真实搜索时需要联网访问公开文献 metadata API。
- V1 只使用 Python 标准库，不需要安装第三方 Python 包。
- 默认 Crossref/OpenAlex/arXiv/RSS 搜索不需要付费 API。

## 5 分钟开始

```bash
git clone https://github.com/953836942-dot/TE-literature-update.git
cd TE-literature-update
cp config.example.json config.json
python3 scripts/radar_cli.py fetch --config config.json --mode lookback --lookback-days 7
```

最后一条命令会完成确定性的：搜索 → 标准化 → 去重 → TE relevance gate → base scoring，并输出包含 `analysis_candidates` 的 fetch JSON。

它**不会假装自己已经完成 Codex 的创新判断和科研总结**。完整流程需要在 Codex 中使用仓库内的 `te-literature-radar` Skill。

## 在 Codex 中使用

仓库根目录包含 `SKILL.md` 和 `agents/openai.yaml`。在 Codex 中打开/clone 这个仓库后，使用 `te-literature-radar` repository Skill（通常引用为 `$te-literature-radar`），并让它使用你的本地 `config.json`。

完整流程：

```text
$te-literature-radar
→ Python 确定性搜索与初筛
→ Codex 基于已有证据判断 novelty 并总结
→ validate-analysis 检查证据/数字
→ Python 计算最终 A/B/C
→ Markdown/JSON/可选邮件
```

这个源码版**没有**一键安装器；一键安装会作为以后单独的版本处理。

## 时间模式

自动递增搜索：

```bash
python3 scripts/radar_cli.py fetch --config config.json --mode auto
```

重新搜最近 30 天，默认不改变每周自动 state：

```bash
python3 scripts/radar_cli.py fetch --config config.json --mode lookback --lookback-days 30
```

指定历史时间段：

```bash
python3 scripts/radar_cli.py fetch --config config.json --mode range --start-date 2026-01-01 --end-date 2026-06-30
```

`auto` 默认从上一次成功运行开始，并向前 overlap 48 小时，再通过去重避免重复推送。这样可以减少数据库延迟收录造成的漏文献。

## 配置

先复制：

```bash
cp config.example.json config.json
```

常改字段包括：

- `research_profile.core`
- `research_profile.transport`
- `research_profile.design`
- `research_profile.data_driven`
- `research_profile.priority_topics`
- `research_profile.watched_materials`
- `target_journals`
- `target_authors`
- `openalex.queries`
- `arxiv.queries`
- `rss_feeds`
- `language`

评分固定为：

```text
TE relevance     30
Research quality 30
Novelty          20
Research fit     10
Recency          10
```

## 邮件

邮件默认关闭。如果以后启用，请只把 SMTP 密码放在：

- 环境变量；或
- 本地 `.secrets/` 文件。

不要把密码直接写进 `config.json` 或提交到 GitHub。

## 输出

默认输出目录：`te-literature-radar-output/`

- `data/fetch-*.json`：候选和 base score
- `final/YYYY-MM-DD.json`：最终结构化结果
- `YYYY-MM-DD.md`：A/B/C 周报
- `state.json`：已处理 ID 和最近成功时间

## 测试

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q scripts
```

source adapter 测试全部使用 mock，不会为了单元测试真的访问 Crossref/OpenAlex/arXiv/RSS。

## 示例

`example-output/sample-digest.md` 和 `example-output/sample-final.json` 是**完全虚构的格式示例**。里面的论文、DOI、作者和科学结果都不是实际文献，仅用来展示输出长什么样。

## 当前限制

- V1 默认只分析 title/abstract/metadata，不自动下载付费全文。
- 数据库可能存在收录延迟和摘要缺失。
- Codex 对创新性的判断是受证据约束的科研判断，不等同于同行评议。
- 作者姓名在没有稳定 author ID 时可能有同名歧义。
- 一键安装、GUI、Zotero、数据库/vector store、自动全文下载、GitHub Actions 定时运行暂时都不属于这一源码版。

## License 与上游来源

本项目使用 MIT License，见 [LICENSE](LICENSE)。

架构受到 `lishn6/daily-econ-literature-radar` 启发并有部分适配，完整 attribution 见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
