# TODO_NEXT

更新时间：2026-05-22

## 下一轮最重要任务

0. 完善本地开发测试环境
   - 安装或恢复 `pytest` 后运行 `python -m pytest`。
   - 重点复核新增的 Elsevier 诊断测试，以及既有检索脚本合约测试。
   - 如后续需要把 ScienceDirect 纳入正式检索流程，应在 `src/search_elsevier.py` 基础上补充结果规范化、审计 CSV 和去重接口，不要直接打印或保存 API key。

1. 人工核验本地核心候选文献的来源级别
   - 对 `reports/local_literature/core_literature_candidates.md` 中的核心必读和背景支撑文献，核验 SCI、JCR 分区、中科院分区、中文期刊来源和年份。
   - 对 `reports/local_literature/sci_mainstream_relevance_audit.md` 中已标注 SCIE 的期刊，通过 Web of Science/JCR/中科院分区做正式复核。
   - 对 DOI 为 `unclear` 的中文或题录不足文献，人工补充题录信息。
   - 运行 `scripts/index_local_literature.py` 前先确认本机 Python 环境可用。

2. 完成开题报告大纲
   - 基于 E+D+A 组合形成研究问题。
   - 覆盖研究背景、研究意义、国内外现状、研究内容、技术路线、创新点和可行性。
   - 明确主线为“碳化固废 SCM + CO2 养护 + 超重力/等效强化碳化变量”。

3. 建立 E/D/A 核心文献精读表
   - 优先从 `reports/reading_list_by_direction.md` 和 `data/processed/reading_list_by_direction.csv` 选择代表论文。
   - 纳入本地核验中与 E/A 相关的候选文献：concrete sludge-derived material 和 CO2-CaO dry grinding。
   - 每篇提取研究问题、材料体系、实验方法、关键指标、主要结论、可借鉴点和局限性。
   - 摘要或全文信息不足时标注“数据不足，需人工补充检索或下载全文”。

4. 设计第一轮最小可行实验矩阵
   - 优先选择一种来源稳定的废混凝土粉或钢渣粉。
   - 设置未碳化、常规静态碳化、强化碳化三个材料状态。
   - 在水泥净浆或砂浆体系中设置 0%、10%、20% 固废替代率。
   - A 方向先用高 CO2 浓度、湿度、薄层暴露、搅拌等方式作为等效强化变量。

5. 建立实验数据记录模板
   - 至少包括原材料信息、预碳化条件、配合比、养护制度、质量变化、强度、pH/酚酞、XRD/TG、碳酸盐含量等字段。
   - 对尚未确认的仪器和测试条件标注“待确认”。
