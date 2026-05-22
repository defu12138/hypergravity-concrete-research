# Codex Project Entry Rules

本项目是“超重力与混凝土结合方向的文献侦察与选题可行性分析”。

## 新会话入口

- 每次开始任务前，先执行：

```powershell
git status
git pull
```

- 然后读取 `handoff/` 目录下的长期交接文件：
  - `handoff/PROJECT_STATE.md`
  - `handoff/CODEX_CHANGELOG.md`
  - `handoff/RESEARCH_DECISIONS.md`
  - `handoff/TODO_NEXT.md`
  - `handoff/NEXT_SESSION_PROMPT.md`
- 如需进一步追溯，再读取项目根目录的 `NEXT_SESSION_PROMPT.md` 和这些关键文件：
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

- 每次完成开题报告、文献精读、实验矩阵、数据记录模板或其他重要新产出后，必须同步更新 `handoff/` 目录下的交接文件：
  - `handoff/PROJECT_STATE.md`：更新当前项目状态、最新成果、当前主线和未解决问题。
  - `handoff/CODEX_CHANGELOG.md`：记录本轮日期、任务、修改文件、关键结论和遗留问题。
  - `handoff/RESEARCH_DECISIONS.md`：如果本轮形成新的研究判断，记录判断和理由；如果没有新增判断，写明“本轮无新增研究决策”。
  - `handoff/TODO_NEXT.md`：更新下一轮最优先的 3-5 个任务。
  - `handoff/NEXT_SESSION_PROMPT.md`：更新下次给 GPT/Codex 使用的开场提示词。
- 重要结论不能只留在聊天记录中，必须写入项目文件。
- 如需维护旧入口提示，也可以同步更新项目根目录的 `NEXT_SESSION_PROMPT.md`。
- 如果关键文件缺失，先列出缺失文件，不要编造论文、数据或结论。

## Git 协作规则

- 每次结束前必须执行：

```powershell
git status
git diff --stat
```

- 每次提交前要说明修改了哪些文件和为什么修改。
- 提交前检查不要提交敏感信息，包括：
  - API key
  - `.env`
  - 密码
  - token
  - 私人账号信息
  - 不应公开的原始数据
- 如果有实际改动，执行：

```powershell
git add .
git commit -m "chore: update project handoff"
git push
```

- 如果没有实际改动，说明“working tree clean”，不要强行提交。
- 不要删除已有研究成果文件。
- 不要覆盖或回退用户未明确要求处理的改动。
