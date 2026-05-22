# NEXT_SESSION_PROMPT

请继续接手这个项目：超重力与混凝土结合方向的文献侦察与选题可行性分析。

当前 Git 仓库根目录：

```text
C:\Users\DELL\Desktop\超重力混凝土\hypergravity_concrete_scout
```

## 开始前必须先阅读

请先阅读 `handoff/` 目录下这些长期交接文件：

1. `handoff/PROJECT_STATE.md`
2. `handoff/CODEX_CHANGELOG.md`
3. `handoff/RESEARCH_DECISIONS.md`
4. `handoff/TODO_NEXT.md`
5. `handoff/NEXT_SESSION_PROMPT.md`

然后根据需要阅读支撑文件：

- `reports/final_research_map.md`
- `reports/direction_score_report.md`
- `reports/reading_list_by_direction.md`
- `reports/research_results_file_summary.xlsx`
- `reports/local_literature/local_literature_audit.md`
- `reports/local_literature/core_literature_candidates.md`
- `reports/local_literature/sci_mainstream_relevance_audit.md`
- `data/local_literature/local_literature_index.csv`
- `data/local_literature/local_literature_sci_relevance.csv`
- `scripts/index_local_literature.py`
- `data/processed/papers_master.csv`
- `data/processed/direction_score.csv`
- `data/processed/reading_list_by_direction.csv`
- `data/processed/top_cited_papers.csv`

说明：用户曾提到 `PROJECT_SUMMARY.md`，但当前项目中未找到该文件，不要把它作为内容来源。

## 重要要求

- 不要从零开始。
- 不要重建项目结构。
- 不要重新设计研究方向。
- 不要擅自继续联网检索论文或扩展文献数据库分析。
- 不要编造论文、作者、期刊、DOI 或实验结果。
- 如果数据不足，明确写“数据不足，需人工补充检索”。
- 不要删除已有研究成果文件。
- 不要把本地 PDF、Word、CAJ、压缩包或老师资料原件复制进仓库或提交到 GitHub。
- 用中文输出。

## 当前已经确定的研究判断

请保留以下判断，除非用户明确要求重新评估：

- E：碳化固废辅助胶凝材料，作为主体方向，总分 4.29/5。
- D：CO2 养护与碳化混凝土，作为应用场景，总分 3.74/5。
- A：超重力碳化固废，作为强化工艺变量，总分 3.3/5。
- B/C/F 暂缓，不作为当前第一阶段主攻方向。

推荐主线：

> 碳化固废 SCM + CO2 养护 + 超重力/等效强化碳化变量

## 本地文献核验结果

已完成对 `C:\Users\DELL\Desktop\超重力混凝土\孟老师资料\离心混凝土文献资料` 中 22 个 PDF 的元数据级核验，结果保存在：

- `data/local_literature/local_literature_index.csv`
- `reports/local_literature/local_literature_audit.md`
- `reports/local_literature/core_literature_candidates.md`

可用 `scripts/index_local_literature.py --source-dir "<本地文献目录>"` 重新生成本地文献索引。该脚本只读取文件属性、文件名线索和可选 PDF metadata，不做 OCR，不复制或移动原文文件。

本地资料明显偏 B（离心/超重力成型混凝土）方向，对 E+D+A 主线只形成局部补强。优先关注 concrete sludge-derived material 相关文献和 CO2-CaO dry grinding 文献；SCI/JCR/中科院分区仍需人工核验。

已补充 `reports/local_literature/sci_mainstream_relevance_audit.md` 和 `data/local_literature/local_literature_sci_relevance.csv`。公开期刊页可确认 13 篇英文文献来源期刊为 SCIE，但正式开题引用前仍建议人工复核 Web of Science/JCR/中科院分区。

## 下一步优先任务

如果用户没有指定具体产出，优先从以下任务之一开始：

1. 人工核验本地核心候选文献的 SCI/JCR/中科院分区和中文来源级别；
2. 开题报告大纲；
3. E/D/A 三方向核心文献精读表；
4. 第一轮最小可行实验矩阵；
5. 实验数据记录模板。

## 交接与 Git 规则

- 每次完成重要任务后，必须更新 `handoff/` 文件。
- 重要结论不能只留在聊天记录中，必须写入项目文件。
- 每次结束前执行 `git status`。
- 每次提交前说明修改了哪些文件和为什么修改。
