# NEXT_SESSION_PROMPT

更新时间：2026-05-22 01:35:03

以下内容是一段可直接复制给下次 Codex 新会话的完整提示词。下次在本项目中继续工作时，请优先使用这段提示词。

```text
请继续接手这个项目：超重力与混凝土结合方向的文献侦察与选题可行性分析。

当前项目路径：
D:\work\codex\超重力混凝土\hypergravity_concrete_scout

## 重要要求

请不要从零开始，不要重新搭建项目，不要重新设计研究方向，也不要继续检索论文或扩展文献数据库分析。

本轮项目已经完成了文献侦察、方向评分、阅读清单、最终研究地图和研究结果文件汇总。你需要基于现有文件继续推进后续工作。

## 开始前必须先阅读的文件

请先检查并阅读以下文件：

1. reports/final_research_map.md
2. reports/direction_score_report.md
3. reports/reading_list_by_direction.md
4. reports/research_results_file_summary.xlsx

如需要追溯数据，再查看：

- data/processed/papers_master.csv
- data/processed/direction_score.csv
- data/processed/reading_list_by_direction.csv
- data/processed/top_cited_papers.csv

如果上述关键文件缺失，先列出缺失文件，不要编造内容、不要凭记忆补论文、不要继续往下做结论。

## 当前关键文件状态

- `reports/final_research_map.md`：已存在
- `reports/direction_score_report.md`：已存在
- `reports/reading_list_by_direction.md`：已存在
- `reports/research_results_file_summary.xlsx`：已存在

## 当前已经确定的研究判断

请保留以下判断，不要推翻重来，除非用户明确要求重新评估：

1. E：碳化固废辅助胶凝材料，作为主体方向。
   理由：文献热度高、实验可行性较好、与水泥/砂浆/混凝土关系直接，适合作为开题报告的主线。

2. D：CO2养护与碳化混凝土，作为应用场景。
   理由：与混凝土应用直接相关，实验条件相对容易，但方向较成熟，需要和 E 或 A 结合形成新意。

3. A：超重力碳化固废，作为强化工艺变量。
   理由：最贴近“超重力”主题，但设备门槛较高，适合作为工艺强化因素嵌入 E/D 主线，而不是第一阶段单独作为大课题。

4. B/C/F 暂缓。
   - B：离心/超重力成型混凝土，设备和构件尺度门槛较高；
   - C：重力场对水泥水化影响，专门实验条件较难；
   - F：旋转填充床与传质强化，偏化工过程，和混凝土直接耦合证据不足。
   这些方向暂时作为背景或后续拓展，不作为当前主攻方向。

## 后续工作重点

工具链提示：2026-05-25 已新增 `src/search_elsevier.py`，可用以下命令诊断 ScienceDirect / Elsevier API：

```powershell
python src/search_elsevier.py --diagnose-elsevier
```

该诊断从 `ELSEVIER_API_KEY` 环境变量读取 key，禁用系统代理，只输出 key 是否存在、长度、请求域名、代理禁用状态、HTTP 状态码和 `X-ELS-Status`。最近一次联网实测返回 `http_status=200`、`x_els_status=OK`。当前本地 Python 环境缺少 `pytest`，后续测试前需先安装或恢复 pytest。

请围绕以下任务继续推进，不要继续扩大文献检索范围：

1. 开题报告
   - 基于 E+D+A 组合形成研究问题；
   - 梳理研究背景、研究意义、国内外现状、研究内容、技术路线、创新点和可行性；
   - 明确主线为“碳化固废 SCM + CO2 养护 + 超重力/强化碳化变量”。

2. 文献精读
   - 从 reading_list_by_direction.md 和 reading_list_by_direction.csv 中优先选择 E、D、A 方向代表论文；
   - 每篇精读时提取：研究问题、材料体系、实验方法、关键指标、主要结论、可借鉴点、局限性；
   - 不要编造论文细节。如果摘要或全文信息不足，标注“数据不足，需人工补充检索或下载全文”。

3. 实验矩阵
   - 优先设计普通材料实验室可完成的最小可行实验；
   - 主线建议为：废混凝土粉或钢渣粉预碳化，作为 SCM 掺入水泥/砂浆体系，再结合 CO2 养护；
   - A 方向作为强化碳化变量，可先用高 CO2 浓度、湿度、薄层暴露、搅拌或等效强化方式模拟；
   - 不要一开始设计过大的全因子实验。

4. 数据记录模板
   - 为后续实验建立可直接使用的记录表；
   - 至少包括：原材料信息、预碳化条件、配合比、养护制度、质量变化、强度、pH/酚酞、XRD/TG/碳酸盐含量等指标；
   - 如果某项仪器条件未知，标注“待确认”。

## 最近可能需要关注的后续产出

- `reports/reading_list.md`
- `reports/reading_list_by_direction.md`
- `data/processed/reading_list.csv`
- `data/processed/reading_list_by_direction.csv`

## 工作方式要求

- 用中文输出；
- 所有判断尽量引用已有文件中的数据或结论；
- 不要编造论文、作者、期刊、DOI 或实验结果；
- 如果发现数据不足，明确写“数据不足，需人工补充检索”；
- 如果用户要求生成新文件，优先保存在项目内的 reports/、data/processed/ 或合适的新目录；
- 保持当前项目结构，不要重建项目；
- 不要删除已有结果文件；
- 不要继续联网检索论文，除非用户明确要求。

## 持续更新要求

如果本次会话完成了开题报告、文献精读、实验矩阵、数据记录模板或其他重要新产出，请在结束前更新 NEXT_SESSION_PROMPT.md。

推荐运行：

python scripts\update_next_session_prompt.py

## 建议的下一步输出

请优先询问用户下一步想做哪一类产出；如果用户没有指定，推荐从以下三项之一开始：

1. 开题报告大纲；
2. E/D/A 三方向核心文献精读表；
3. 第一轮最小可行实验矩阵和数据记录模板。
```

## 维护说明

- 本文件由 `scripts/update_next_session_prompt.py` 生成或更新。
- 更新本项目的重要成果后，建议重新运行：

```powershell
python scripts\update_next_session_prompt.py
```

## 当前关键文件检查

- `reports/final_research_map.md`：已存在
- `reports/direction_score_report.md`：已存在
- `reports/reading_list_by_direction.md`：已存在
- `reports/research_results_file_summary.xlsx`：已存在

## 当前追溯数据文件检查

- `data/processed/papers_master.csv`：已存在
- `data/processed/direction_score.csv`：已存在
- `data/processed/reading_list_by_direction.csv`：已存在
- `data/processed/top_cited_papers.csv`：已存在

## 当前缺失关键文件

- 当前关键文件均存在。
