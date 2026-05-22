# 超重力混凝土文献侦察项目

本项目用于通过公开文献数据库 API 快速侦察“超重力与混凝土结合”相关方向的研究现状。代码不会读取上级目录中的 `参考文献/`，也不会把本地 PDF 当作证据来源。

## 1. 安装依赖

在本目录下运行：

```powershell
python -m pip install -r requirements.txt
```

## 2. 配置环境变量

OpenAlex 是主数据源。建议配置 API key 和联系邮箱，避免被限流或拒绝。

```powershell
$env:OPENALEX_API_KEY="你的 OpenAlex API key"
$env:CONTACT_EMAIL="you@example.com"
$env:SEMANTIC_SCHOLAR_API_KEY="可选"
```

如果暂时没有 key，可以先运行 `--dry-run` 或 `--sample` 命令检查项目结构。

## 3. 推荐运行流程

```powershell
python src/search_openalex.py --per-query 50
python src/search_semantic_scholar.py --per-query 50
python src/search_crossref.py --per-query 50
python src/merge_and_clean.py
python src/analyze_landscape.py
python src/select_reading_list.py
python src/score_directions.py
```

三个检索脚本都会直接读取 `queries.yaml` 中的所有方向和检索式，并分别输出 `data/raw/openalex_results.csv`、`data/raw/semantic_scholar_results.csv`、`data/raw/crossref_results.csv`。

## 4. 无网络样例运行

```powershell
python src/search_openalex.py --dry-run
python src/search_semantic_scholar.py --dry-run
python src/search_crossref.py --dry-run
python src/merge_and_clean.py --sample
python src/analyze_landscape.py --sample
python src/select_reading_list.py
python src/score_directions.py
```

## 5. 输出文件

- `data/raw/`：API 原始 JSONL。
- `data/processed/works_master.csv`：清洗和去重后的论文主表。
- `data/processed/query_audit.csv`：检索请求审计记录。
- `data/processed/*summary*.csv`：趋势、作者、期刊、方向评分等结构化结果。
- `data/local_literature/local_literature_index.csv`：本地文献文件夹的元数据索引，不包含 PDF 全文。
- `reports/`：Markdown 报告。
- `figures/`：PNG 图表。

## 6. 本地文献索引

如需基于本地文献文件夹重新生成元数据索引，可运行：

```powershell
python scripts/index_local_literature.py --source-dir "C:\Users\DELL\Desktop\超重力混凝土\孟老师资料\离心混凝土文献资料"
```

该脚本默认只读取文件名、扩展名、文件大小、修改时间，并尝试从文件名中识别 DOI、年份和关键词；如果环境中安装了可用的 PDF metadata 读取库，会尝试读取 PDF metadata。脚本不会做大规模 OCR，也不会复制、移动或提交原始 PDF。

## 7. 中文字体说明

报告使用中文，图表标题和坐标轴尽量使用英文以减少字体问题。如果本机 matplotlib 图中的中文显示为方块，可以安装或指定中文字体，例如 SimHei、Microsoft YaHei、Noto Sans CJK。必要时可在脚本开头加入：

```python
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC"]
plt.rcParams["axes.unicode_minus"] = False
```

## 8. 数据原则

- 不编造论文。
- 不使用本地 PDF 或上级目录 `参考文献/` 作为 seed。
- 不复制、不提交本地 PDF、Word、CAJ、压缩包或老师资料原件；本地文献只保存元数据索引和核验报告。
- API 请求失败时写入审计记录，不让整个流程直接崩溃。
- 缺失字段、冲突字段、无法确认字段统一写 `unclear`。
- 报告中的判断必须来自 `data/processed/` 中的结构化数据。
