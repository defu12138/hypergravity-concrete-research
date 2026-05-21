# Codex Project Entry Rules

本项目是“超重力与混凝土结合方向的文献侦察与选题可行性分析”。

## 新会话入口

- 开始处理本项目任务前，先读取项目根目录的 `NEXT_SESSION_PROMPT.md`。
- 如果 `NEXT_SESSION_PROMPT.md` 缺失，先读取这些关键文件并向用户报告缺失情况：
  - `reports/final_research_map.md`
  - `reports/direction_score_report.md`
  - `reports/reading_list_by_direction.md`
  - `reports/research_results_file_summary.xlsx`
- 不要从零开始重建项目，不要重新检索论文，除非用户明确要求。

## 当前研究判断

- E：碳化固废辅助胶凝材料，作为主体方向。
- D：CO2养护与碳化混凝土，作为应用场景。
- A：超重力碳化固废，作为强化工艺变量。
- B/C/F：暂缓，不作为当前主攻方向。

## 持续更新要求

- 每次完成开题报告、文献精读、实验矩阵、数据记录模板或其他重要新产出后，同步更新 `NEXT_SESSION_PROMPT.md`。
- 推荐使用：

```powershell
python scripts\update_next_session_prompt.py
```

- 如果关键文件缺失，先列出缺失文件，不要编造论文、数据或结论。
