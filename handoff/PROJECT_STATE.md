# PROJECT_STATE

更新时间：2026-06-09

## 项目背景

本项目围绕“超重力与混凝土结合方向”的文献侦察与选题可行性分析展开，目标是把强化传质、矿化碳化、固废资源化和低碳胶凝材料设计连接起来，为后续开题报告、文献精读和实验方案设计提供依据。

当前项目已经完成文献检索、题录清洗、方向评分、阅读清单、最终研究地图和研究结果文件汇总。后续工作应基于现有结果继续推进，不要从零开始重建项目，也不要擅自扩大联网检索范围。

2026-06-09 已新增 GitHub 可见的组会记录区 `group_meetings/`，用于持续归档每次组会汇报内容、当前研究归总和四方向科研环境判断。后续组会记录优先写入该目录，不要只留在聊天记录中。

## 当前研究目标

当前目标是基于已有文献侦察结果，把研究主线收敛为：

> 碳化固废 SCM + CO2 养护 + 超重力/等效强化碳化变量

后续优先产出包括开题报告大纲、E/D/A 核心文献精读表、第一轮最小可行实验矩阵和实验数据记录模板。

## 已有成果文件

关键交接与总结文件：

- `NEXT_SESSION_PROMPT.md`
- `group_meetings/README.md`
- `group_meetings/2026-06-03_first_group_meeting.md`
- `group_meetings/current_research_summary.md`
- `group_meetings/four_directions_research_landscape_2026.md`
- `reports/final_research_map.md`
- `reports/direction_score_report.md`
- `reports/reading_list_by_direction.md`
- `reports/research_results_file_summary.xlsx`

主要数据与追溯文件：

- `data/processed/papers_master.csv`
- `data/processed/direction_score.csv`
- `data/processed/reading_list_by_direction.csv`
- `data/processed/top_cited_papers.csv`
- `reports/reading_list.md`
- `reports/landscape_summary.md`
- `reports/direction_scores.md`

本地文献核验成果：

- `data/local_literature/local_literature_index.csv`
- `data/local_literature/local_literature_sci_relevance.csv`
- `reports/local_literature/local_literature_audit.md`
- `reports/local_literature/core_literature_candidates.md`
- `reports/local_literature/sci_mainstream_relevance_audit.md`
- `scripts/index_local_literature.py`

本轮核验基于本地文件夹 `C:\Users\DELL\Desktop\超重力混凝土\孟老师资料\离心混凝土文献资料` 中的 22 个 PDF 文件，仅提取和保存文献元数据、方向匹配和使用建议；PDF、Word、CAJ 或老师资料原件不得复制进仓库或提交。
后续可使用 `scripts/index_local_literature.py --source-dir "<本地文献目录>"` 重新生成本地文献元数据索引。该脚本只写入 CSV 元数据，不复制或移动原文文件。

说明：用户曾提到 `PROJECT_SUMMARY.md`，但当前项目中未找到该文件，因此本交接不以它作为内容来源。

## 当前最推荐的研究方向

推荐采用 E+D+A 组合路线：

- E - 碳化固废辅助胶凝材料：主体方向，总分 4.29/5。该方向文献热度高、实验可行性较好、与水泥/砂浆/混凝土关系直接。
- D - CO2 养护与碳化混凝土：应用场景，总分 3.74/5。该方向混凝土相关性强、实验条件相对容易，但较成熟，需要与材料体系或强化过程结合。
- A - 超重力碳化固废：强化工艺变量，总分 3.3/5。该方向最贴近“超重力”主题，但设备门槛较高，更适合嵌入 E/D 主线。

B/C/F 当前暂缓，不作为第一阶段主攻方向。

本地文献核验显示：本地资料明显偏 B（离心/超重力成型混凝土）方向，可补强离心混凝土工程背景；对当前 E+D+A 主线仅形成局部补强，其中 `Comparative study of acid mine drainage neutralization by calcium hydroxide and concrete sludge-derived material` 可支撑 E 方向固废/污泥资源化背景，`Reaction between CO2 and CaO under dry grinding` 可支撑 A 方向等效强化碳化机制背景。
本轮进一步核验公开期刊页后，13 篇英文文献可通过期刊页确认来源期刊为 SCIE 收录；但对当前 E+D+A 主线直接有价值的主要仍是 1 篇 E 方向 concrete sludge 文献和 1 篇 A 方向 CO2-CaO 干磨文献。

2026-06-09 组会归总后的四方向口径：

- 高重力碳化/矿化：优先候选主线，对应旧 E/D/A 组合路线，最容易连接低碳、固废资源化、CO2 利用和水泥基材料性能。
- 离心成型混凝土：重要工程备选，对应旧 B 方向，适合导师更重视离心平台、PHC 管桩或预制构件时展开。
- 水泥水化重力效应：机制支撑，对应旧 C 方向，创新性高但直接文献和实验条件不足。
- 土工离心模型：平行领域参考，适合借用相似理论和平台背景，但不宜直接作为混凝土材料主线。

## 未解决问题

- E/D/A 主线需要进一步转化为开题报告中的研究问题、研究内容、技术路线和创新点。
- E/D/A 代表论文仍需人工精读；摘要或全文信息不足时必须标注“数据不足，需人工补充检索”。
- 第一轮实验矩阵需要结合实际材料来源、CO2 养护条件、仪器条件和测试周期压缩。
- 固废来源、粒径、预碳化制度、替代率和养护制度仍需明确。
- 第一次组会 PPT 需核对两个口径问题：封面日期为 `2025.06.03` 但文件名为 `2026-06-03`；第 4 页“涉及超重力”逐项合计为 157，但页脚写筛选后 79 篇，且当前 CSV 中高重力碳化/矿化 `included` 为 71。
- XRD、TG、碳酸盐含量、pH/酚酞等测试条件如未确认，应在实验模板中标注“待确认”。
- 本地文献的 SCI 收录、JCR 分区、中科院分区、中文来源级别和部分 DOI/年份仍需人工核验。
- 本地 SCI 主流性报告中的 SCIE 状态来自公开期刊页，正式开题引用前仍建议通过 Web of Science/JCR/中科院分区人工复核。
- 当前系统中的 `python` 可能是 Windows Store 占位符；运行 `scripts/index_local_literature.py` 前需确认 Python 环境可用。

## 2026-05-25 Elsevier / ScienceDirect API 修复状态

- 已新增 `src/search_elsevier.py`，提供 `--diagnose-elsevier` 诊断入口。
- Elsevier API key 仅从 `os.environ.get("ELSEVIER_API_KEY", "").strip()` 读取，不硬编码、不打印原文。
- ScienceDirect Search API 请求头使用 `X-ELS-APIKey` 和 `Accept: application/json`。
- 诊断请求使用 `requests.Session()` 且设置 `session.trust_env = False`，避免 Python 默认走系统/全局代理导致认证异常。
- 诊断输出仅包含 key 是否存在、key 长度、请求域名、是否禁用代理、HTTP 状态码、`X-ELS-Status` 和错误摘要。
- 2026-05-25 实测 `python src/search_elsevier.py --diagnose-elsevier` 返回 `http_status=200`、`x_els_status=OK`。
