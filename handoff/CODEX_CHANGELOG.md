# CODEX_CHANGELOG

更新时间：2026-05-22

## 截至目前已完成的主要工作

- 建立并维护了“超重力与混凝土结合方向”的文献侦察项目结构。
- 围绕 A-F 六个方向完成初步文献检索与数据整理：
  - A - 超重力碳化固废
  - B - 离心/超重力成型混凝土
  - C - 重力场对水泥水化影响
  - D - CO2 养护与碳化混凝土
  - E - 碳化固废辅助胶凝材料
  - F - 旋转填充床与传质强化
- 对原始题录进行了 DOI、OpenAlex/Semantic Scholar ID、标题-年份相似度等维度的去重和清洗。
- 生成并整理了方向评分结果，形成 `reports/direction_score_report.md` 和相关 CSV 数据。
- 生成分方向阅读清单，形成 `reports/reading_list_by_direction.md` 与 `data/processed/reading_list_by_direction.csv`。
- 生成最终研究地图 `reports/final_research_map.md`，总结研究背景、方向对比、研究空白、代表论文、实验可行性、拟题方向和 30 天行动计划。
- 生成研究结果文件汇总 `reports/research_results_file_summary.xlsx`。
- 生成项目续接提示 `NEXT_SESSION_PROMPT.md`，明确后续不要从零开始、不要擅自扩展文献检索、优先围绕开题报告/精读/实验矩阵推进。

## 本次交接整理新增内容

- 新建 `handoff/` 目录，用于长期同步给 GPT/Codex 理解项目状态。
- 新增长期交接文件：
  - `handoff/PROJECT_STATE.md`
  - `handoff/CODEX_CHANGELOG.md`
  - `handoff/RESEARCH_DECISIONS.md`
  - `handoff/TODO_NEXT.md`
  - `handoff/NEXT_SESSION_PROMPT.md`
- 更新 `AGENTS.md`，加入交接文件维护、重要结论落盘、结束前执行 `git status`、提交前说明修改原因等规则。
- 更新 `.gitignore`，补充环境文件、密钥、虚拟环境、依赖目录和构建产物忽略规则。

## 重要约束

- 不要编造论文、作者、期刊、DOI 或实验结果。
- 不要删除已有研究成果文件。
- 不要重新设计方向评分体系，除非用户明确要求重新评估。
- 不要继续联网检索论文，除非用户明确要求。
