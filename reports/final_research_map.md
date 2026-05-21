# 超重力与混凝土结合方向的文献侦察与选题可行性分析

本报告由项目中已经生成的 CSV 与 Markdown 文件自动汇总，不新增、猜测或补造论文题录。若某项输入缺失或字段为空，统一标注为“数据不足，需人工补充检索”或 `unclear`。

## 数据完整性

- 本轮报告所需 7 个输入文件均已找到。

## 1. 研究背景

超重力与混凝土结合的核心动机，是把强化传质、矿化碳化、固废资源化和低碳胶凝材料设计连接起来。现有数据中，D（CO2养护与碳化混凝土）和 E（碳化固废辅助胶凝材料）与水泥/砂浆/混凝土最直接；A（超重力碳化固废）提供过程强化入口；B、C、F 分别对应离心成型、重力场水化和旋转填充床传质强化，但短期实验条件与题录相关性需要进一步复核。

## 2. 调研方法

- 数据来源：主表 `papers_master.csv` 当前来源计数为 OpenAlex 1558 条；Semantic Scholar 489 条。既有流程以 OpenAlex 为主，Semantic Scholar 和 Crossref 用于补充或校验；本最终报告不重新联网检索。
- 检索范围：A-F 六个方向的英文关键词和短语检索式，覆盖 high gravity carbonation、rotating packed bed、centrifuged concrete、microgravity cement paste、CO2 curing concrete、carbonated SCM 等表达。
- 清洗筛选：原始结果经 DOI、OpenAlex/Semantic Scholar ID、标题-年份相似度去重；阅读清单优先 2018 年后、高引用和 2023 年后新论文。
- 评分方法：热度、成熟度、创新空间、实验可行性、设备可获得性、混凝土相关性和发表潜力来自 `direction_score.csv`；代表论文优先来自 `reading_list_by_direction.csv`，不足时用 `top_cited_papers.csv` 补足。

## 3. 六个方向总体对比

| 方向 | 论文总数 | 2022-2026 论文数 | 总分 | 推荐类别 | 主要风险 |
| --- | ---: | ---: | ---: | --- | --- |
| A - 超重力碳化固废 | 294 | 169 | 3.3 | 备用方向 | 需要超重力/旋转填充床或等效强化碳化设备,且钢渣成分波动会影响可重复性。 |
| B - 离心/超重力成型混凝土 | 268 | 96 | 2.89 | 暂缓方向 | 离心成型设备、模具和安全控制门槛较高,实验尺度放大不容易。 |
| C - 重力场对水泥水化影响 | 278 | 120 | 2.91 | 暂缓方向 | 微重力/超重力水化实验设备可获得性弱,普通材料实验室难以稳定复现重力场条件。 |
| D - CO2养护与碳化混凝土 | 489 | 257 | 3.74 | 主攻方向 | 方向较成熟,单纯重复 CO2 养护容易缺少新意,需要与材料体系或强化过程结合。 |
| E - 碳化固废辅助胶凝材料 | 424 | 313 | 4.29 | 主攻方向 | 固废来源和预碳化条件会显著影响活性,需建立清楚的材料表征和性能评价链条。 |
| F - 旋转填充床与传质强化 | 451 | 172 | 2.82 | 暂缓方向 | 传质强化文献多来自化工过程,和水泥/混凝土的直接耦合需要重新设计验证场景。 |

## 4. 每个方向的研究现状

### A - 超重力碳化固废
- 数据概况：论文总数 294，2022-2026 年论文数 169。论文总数=294;2022-2026近五年=169;2017-2021=82;增长=87;期刊/会议数=147;平均引用=73.02;阅读清单=10。
- 代表期刊/会议：Materials; Construction and Building Materials; Journal of CO2 Utilization。
- 评分状态：热度 2.4/5，创新空间 4.09/5，混凝土相关性 3.5/5，推荐类别为 备用方向。

### B - 离心/超重力成型混凝土
- 数据概况：论文总数 268，2022-2026 年论文数 96。论文总数=268;2022-2026近五年=96;2017-2021=74;增长=22;期刊/会议数=148;平均引用=13.4;阅读清单=10。
- 代表期刊/会议：Buildings; Applied Sciences; Materials。
- 评分状态：热度 1.16/5，创新空间 3.02/5，混凝土相关性 5.0/5，推荐类别为 暂缓方向。 该方向部分高被引题录偏向离心制造、复合材料或数值方法，需人工复核其与混凝土离心成型的直接相关性。

### C - 重力场对水泥水化影响
- 数据概况：论文总数 278，2022-2026 年论文数 120。论文总数=278;2022-2026近五年=120;2017-2021=94;增长=26;期刊/会议数=160;平均引用=51.27;阅读清单=10。
- 代表期刊/会议：Cement and Concrete Research; Construction and Building Materials; Materials。
- 评分状态：热度 1.44/5，创新空间 4.53/5，混凝土相关性 4.0/5，推荐类别为 暂缓方向。 该方向可能混入 3D 打印、水化泛化或微重力相邻主题，需人工补充检索水泥浆体在重力场中的专门实验文献。

### D - CO2养护与碳化混凝土
- 数据概况：论文总数 489，2022-2026 年论文数 257。论文总数=489;2022-2026近五年=257;2017-2021=159;增长=98;期刊/会议数=139;平均引用=61.94;阅读清单=10。
- 代表期刊/会议：Construction and Building Materials; Cement and Concrete Composites; Journal of Cleaner Production。
- 评分状态：热度 3.39/5，创新空间 1.8/5，混凝土相关性 5.0/5，推荐类别为 主攻方向。

### E - 碳化固废辅助胶凝材料
- 数据概况：论文总数 424，2022-2026 年论文数 313。论文总数=424;2022-2026近五年=313;2017-2021=75;增长=238;期刊/会议数=145;平均引用=36.47;阅读清单=10。
- 代表期刊/会议：Construction and Building Materials; Materials; Journal of Building Engineering。
- 评分状态：热度 5.0/5，创新空间 4.25/5，混凝土相关性 4.5/5，推荐类别为 主攻方向。

### F - 旋转填充床与传质强化
- 数据概况：论文总数 451，2022-2026 年论文数 172。论文总数=451;2022-2026近五年=172;2017-2021=175;增长=-3;期刊/会议数=205;平均引用=82.06;阅读清单=10。
- 代表期刊/会议：Chemical Engineering Journal; Energies; Chemical Engineering and Processing - Process Intensification。
- 评分状态：热度 1.79/5，创新空间 3.2/5，混凝土相关性 2.5/5，推荐类别为 暂缓方向。 该方向化工传质强化文献较多，和水泥/混凝土体系的直接耦合证据不足，需人工复核应用场景。

## 5. 每个方向的代表论文

### A - 超重力碳化固废
- Strategies for mitigation of climate change: a review（2020，引用 1428；作者：Samer Fawzy; Ahmed I. Osman; John Doran; David W. Rooney；来源：Environmental Chemistry Letters；DOI/URL：10.1007/s10311-020-01059-w / https://doi.org/10.1007/s10311-020-01059-w）
- Biomass waste utilisation in low-carbon products: harnessing a major potential resource（2019，引用 598；作者：Nimisha Tripathi; Colin D. Hills; R. S. Singh; C. J. Atkinson；来源：npj Climate and Atmospheric Science；DOI/URL：10.1038/s41612-019-0093-5 / https://doi.org/10.1038/s41612-019-0093-5）
- Future and emerging supplementary cementitious materials（2023，引用 484；作者：Ruben Snellings; Prannoy Suraneni; Jørgen Skibsted；来源：Cement and Concrete Research；DOI/URL：10.1016/j.cemconres.2023.107199 / https://doi.org/10.1016/j.cemconres.2023.107199）
- CO2 mineral carbonation using industrial solid wastes: A review of recent developments（2021，引用 464；作者：Weizao Liu; Liumei Teng; Sohrab Rohani; Zhifeng Qin; Bin Zhao; Chunbao Xu; Shan Ren; Qingcai Liu; Bin Liang；来源：Chemical Engineering Journal；DOI/URL：10.1016/j.cej.2021.129093 / https://doi.org/10.1016/j.cej.2021.129093）
- Outlook of carbon capture technology and challenges（2018，引用 443；作者：Tabbi Wilberforce; Ahmad Baroutaji; Bassel Soudan; Abdul Hai Alami; A.G. Olabi；来源：The Science of The Total Environment；DOI/URL：10.1016/j.scitotenv.2018.11.424 / https://doi.org/10.1016/j.scitotenv.2018.11.424）

### B - 离心/超重力成型混凝土
- Functionally graded materials classifications and development trends from industrial point of view（2019，引用 264；作者：Islam M. El-Galy; Bassiouny Saleh; Mahmoud H. Ahmed；来源：SN Applied Sciences；DOI/URL：10.1007/s42452-019-1413-4 / https://doi.org/10.1007/s42452-019-1413-4）
- Novel Applications of Aluminium Metal Matrix Composites（2019，引用 144；作者：Francis Nturanabo; Leonard Masu; John Baptist Kirabira；来源：IntechOpen eBooks；DOI/URL：10.5772/intechopen.86225 / https://doi.org/10.5772/intechopen.86225）
- Advances in lightweight composite structures and manufacturing technologies: A comprehensive review（2024，引用 142；作者：Resego Phiri; Sanjay Mavinkere Rangappa; Suchart Siengchin; Oluseyi Philip Oladijo; Togay Ozbakkaloglu；来源：Heliyon；DOI/URL：10.1016/j.heliyon.2024.e39661 / https://doi.org/10.1016/j.heliyon.2024.e39661）
- Recent Trends in Treatment and Fabrication of Plant-Based Fiber-Reinforced Epoxy Composite: A Review（2023，引用 115；作者：Abdullahi Haruna Birniwa; Shehu Sa’ad Abdullahi; Mujahid Ali; Rania Edrees Adam Mohammad; Ahmad Hussaini Jagaba; Mugahed Amran; Siva Avudaiappan; Nelson Maureira-Carsalade; Erick I. Saavedra Flores；来源：Journal of Composites Science；DOI/URL：10.3390/jcs7030120 / https://doi.org/10.3390/jcs7030120）
- Advancements in Fiber-Reinforced Polymer Composites: A Comprehensive Analysis（2023，引用 106；作者：Alin Diniță; Răzvan George Rîpeanu; Costin Nicolae Ilincă; Diana Cursaru; Dănuţa Matei; Ibrahim Ramadan; Maria Tănase; Alexandra Ileana Portoacă；来源：Polymers；DOI/URL：10.3390/polym16010002 / https://doi.org/10.3390/polym16010002）

### C - 重力场对水泥水化影响
- 3D printing using concrete extrusion: A roadmap for research（2018，引用 1465；作者：Richard Buswell; W.R. Leal de Silva; Scott Z. Jones; Justin Dirrenberger；来源：Cement and Concrete Research；DOI/URL：10.1016/j.cemconres.2018.05.006 / https://doi.org/10.1016/j.cemconres.2018.05.006）
- Digital Concrete: A Review（2019，引用 566；作者：Timothy Wangler; Nicolas Roussel; Freek Bos; T.A.M. Salet; Robert J. Flatt；来源：Cement and Concrete Research；DOI/URL：10.1016/j.cemconres.2019.105780 / https://doi.org/10.1016/j.cemconres.2019.105780）
- Extrusion-based additive manufacturing with cement-based materials – Production steps, processes, and their underlying physics: A review（2020，引用 546；作者：Viktor Mechtcherine; Freek Bos; Arnaud Perrot; W.R. Leal da Silva; Venkatesh Naidu Nerella; Shirin Fataei; Rob Wolfs; Mohammed Sonebi; Nicolas Roussel；来源：Cement and Concrete Research；DOI/URL：10.1016/j.cemconres.2020.106037 / https://doi.org/10.1016/j.cemconres.2020.106037）
- Improving printability of limestone-calcined clay-based cementitious materials by using viscosity-modifying admixture（2020，引用 283；作者：Yu Chen; Stefan Chaves Figueiredo; Zhenming Li; Ze Chang; Koen Jansen; Oğuzhan Çopuroğlu; Erik Schlangen；来源：Cement and Concrete Research；DOI/URL：10.1016/j.cemconres.2020.106040 / https://doi.org/10.1016/j.cemconres.2020.106040）
- Valorization of sewage sludge in the fabrication of construction and building materials: A review（2019，引用 273；作者：Zhiyang Chang; Guangcheng Long; John L. Zhou; Cong Ma；来源：Resources Conservation and Recycling；DOI/URL：10.1016/j.resconrec.2019.104606 / https://doi.org/10.1016/j.resconrec.2019.104606）

### D - CO2养护与碳化混凝土
- Strategies for mitigation of climate change: a review（2020，引用 1428；作者：Samer Fawzy; Ahmed I. Osman; John Doran; David W. Rooney；来源：Environmental Chemistry Letters；DOI/URL：10.1007/s10311-020-01059-w / https://doi.org/10.1007/s10311-020-01059-w）
- The utilization of eco-friendly recycled powder from concrete and brick waste in new concrete: A critical review（2020，引用 504；作者：Qin Tang; Zhiming Ma; Huixia Wu; Wan Wang；来源：Cement and Concrete Composites；DOI/URL：10.1016/j.cemconcomp.2020.103807 / https://doi.org/10.1016/j.cemconcomp.2020.103807）
- Future and emerging supplementary cementitious materials（2023，引用 484；作者：Ruben Snellings; Prannoy Suraneni; Jørgen Skibsted；来源：Cement and Concrete Research；DOI/URL：10.1016/j.cemconres.2023.107199 / https://doi.org/10.1016/j.cemconres.2023.107199）
- Recent Progress in Green Cement Technology Utilizing Low-Carbon Emission Fuels and Raw Materials: A Review（2019，引用 386；作者：Ali Naqi; Jeong Gook Jang；来源：Sustainability；DOI/URL：10.3390/su11020537 / https://doi.org/10.3390/su11020537）
- Green remediation of As and Pb contaminated soil using cement-free clay-based stabilization/solidification（2019，引用 335；作者：Lei Wang; Dong-Wan Cho; Daniel C.W. Tsang; Xinde Cao; Deyi Hou; Zhengtao Shen; Daniel S. Alessi; Yong Sik Ok; Chi Sun Poon；来源：Environment International；DOI/URL：10.1016/j.envint.2019.02.057 / https://doi.org/10.1016/j.envint.2019.02.057）

### E - 碳化固废辅助胶凝材料
- Future and emerging supplementary cementitious materials（2023，引用 484；作者：Ruben Snellings; Prannoy Suraneni; Jørgen Skibsted；来源：Cement and Concrete Research；DOI/URL：10.1016/j.cemconres.2023.107199 / https://doi.org/10.1016/j.cemconres.2023.107199）
- Effects of carbonated hardened cement paste powder on hydration and microstructure of Portland cement（2018，引用 322；作者：Bao Lu; C. Shi; Jiake Zhang; Jiyun Wang；来源：Construction and Building Materials；DOI/URL：10.1016/j.conbuildmat.2018.07.159 / https://www.semanticscholar.org/paper/3e5e1a98afaa61c8b895223029da0113c1e9fccb）
- Carbonation of steel slag and gypsum for building materials and associated reaction mechanisms（2019，引用 259；作者：Xue Wang; W. Ni; Jiajie Li; Siqi Zhang; M. Hitch; R. Pascual；来源：Cement and Concrete Research；DOI/URL：10.1016/j.cemconres.2019.105893 / https://www.semanticscholar.org/paper/4150c266dff55cabab491c65948d07a0794308c9）
- An overview of utilizing CO2 for accelerated carbonation treatment in the concrete industry（2022，引用 258；作者：Liang Li; Min Wu；来源：Journal of CO2 Utilization；DOI/URL：10.1016/j.jcou.2022.102000 / https://doi.org/10.1016/j.jcou.2022.102000）
- Experimental characterization of the self-healing capacity of cement based materials and its effects on the material performance: A state of the art report by COST Action SARCOS WG2（2018，引用 246；作者：Liberato Ferrara; Tim Van Mullem; C. Alonso; Paola Antonaci; Ruben Paul Borg; Estefanía Cuenca; Anthony Jefferson; P.L. Ng; Alva Peled; Marta Roig‐Flores; Mercedes Sanchez; Christof Schroefl; Pedro Serna; Didier Snoeck; Jean‐Marc Tulliani; Nele De Belie；来源：Construction and Building Materials；DOI/URL：10.1016/j.conbuildmat.2018.01.143 / https://doi.org/10.1016/j.conbuildmat.2018.01.143）

### F - 旋转填充床与传质强化
- Removal of heavy metal ions from wastewater: a comprehensive and critical review（2021，引用 2029；作者：Naef A.A. Qasem; Ramy H. Mohammed; Dahiru U. Lawal；来源：npj Clean Water；DOI/URL：10.1038/s41545-021-00127-0 / https://doi.org/10.1038/s41545-021-00127-0）
- Strategies for mitigation of climate change: a review（2020，引用 1428；作者：Samer Fawzy; Ahmed I. Osman; John Doran; David W. Rooney；来源：Environmental Chemistry Letters；DOI/URL：10.1007/s10311-020-01059-w / https://doi.org/10.1007/s10311-020-01059-w）
- Bioethanol Production from Renewable Raw Materials and its Separation and Purification: a Review（2018，引用 594；作者：Arijana Bušić; Nenad Marđetko; Semjon Kundas; Galina Morzak; Halina Belskaya; Mirela Ivančić Šantek; Draženka Komes; Srđan Novak; Božidar Šantek；来源：Food Technology and Biotechnology；DOI/URL：10.17113/ftb.56.03.18.5546 / https://doi.org/10.17113/ftb.56.03.18.5546）
- Natural deep eutectic solvents for lignocellulosic biomass pretreatment: Recent developments, challenges and novel opportunities（2018，引用 524；作者：Alok Satlewal; Ruchi Agrawal; Samarthya Bhagia; Joshua Sangoro; Arthur J. Ragauskas；来源：Biotechnology Advances；DOI/URL：10.1016/j.biotechadv.2018.08.009 / https://doi.org/10.1016/j.biotechadv.2018.08.009）
- Chemical looping beyond combustion – a perspective（2020，引用 516；作者：Xing Zhu; Qasim Imtiaz; Felix Donat; Christoph R. Müller; Fanxing Li；来源：Energy & Environmental Science；DOI/URL：10.1039/c9ee03793d / https://doi.org/10.1039/c9ee03793d）

## 6. 每个方向的研究空白

### A - 超重力碳化固废
- 研究空白判断：需要超重力/旋转填充床或等效强化碳化设备,且钢渣成分波动会影响可重复性。
- 超重力或旋转填充床条件下固废碳化产物与胶凝活性之间的定量关系仍需收敛。
- 钢渣/转炉渣组成波动较大，需要把材料表征、碳化效率和砂浆性能放在同一评价链条中。
- 高重力强化过程与后续混凝土应用之间仍缺少低成本、小试可复现方案。

### B - 离心/超重力成型混凝土
- 研究空白判断：离心成型设备、模具和安全控制门槛较高,实验尺度放大不容易。
- 离心成型研究与材料微结构、耐久性、低碳胶凝体系之间的交叉仍需人工补充检索。
- 现有题录中存在相邻制造主题噪声，代表论文需人工筛掉非混凝土研究。
- 实验从试样到管桩或构件尺度的放大关系仍是主要不确定点。
- 数据不足，需人工补充检索：该方向部分高被引题录偏向离心制造、复合材料或数值方法，需人工复核其与混凝土离心成型的直接相关性。

### C - 重力场对水泥水化影响
- 研究空白判断：微重力/超重力水化实验设备可获得性弱,普通材料实验室难以稳定复现重力场条件。
- 水泥水化受微重力/超重力影响的专门数据较少，需补充针对 cement paste 的精确检索。
- 重力场变量、孔结构演化和力学性能之间的机制链条仍不清晰。
- 普通材料实验室难以稳定复现重力场条件，因此短期可做性受限。
- 数据不足，需人工补充检索：该方向可能混入 3D 打印、水化泛化或微重力相邻主题，需人工补充检索水泥浆体在重力场中的专门实验文献。

### D - CO2养护与碳化混凝土
- 研究空白判断：方向较成熟,单纯重复 CO2 养护容易缺少新意,需要与材料体系或强化过程结合。
- CO2 养护方向已较成熟，单独重复强度或吸碳率测试创新性不足。
- 更有价值的空白在于把 CO2 养护与固废 SCM、预碳化粉体或强化传质过程耦合。
- 需要同时报告碳吸收、早期性能、长期耐久性和环境收益，避免单指标结论。

### E - 碳化固废辅助胶凝材料
- 研究空白判断：固废来源和预碳化条件会显著影响活性,需建立清楚的材料表征和性能评价链条。
- 碳化固废作为 SCM 的活性来源、反应程度和水化贡献仍需更清晰地区分。
- 废混凝土粉、钢渣、再生细粉等原料差异会影响可重复性，需要建立材料分级策略。
- 预碳化制度与替代率、强度、耐久性之间的窗口仍有系统优化空间。

### F - 旋转填充床与传质强化
- 研究空白判断：传质强化文献多来自化工过程,和水泥/混凝土的直接耦合需要重新设计验证场景。
- 旋转填充床和传质强化研究多在化工体系中展开，直接迁移到水泥/混凝土需要新的反应器和浆体适配验证。
- 矿化碳化效率与后续胶凝性能之间的关联证据不足。
- 设备门槛较高，短期更适合作为 A/E/D 的过程强化变量，而非独立主线。
- 数据不足，需人工补充检索：该方向化工传质强化文献较多，和水泥/混凝土体系的直接耦合证据不足，需人工复核应用场景。

## 7. 每个方向的实验可行性

- A - 超重力碳化固废：实验难度 中（可行性 3.5/5）；设备需求 高（设备可获得性 2.5/5）；发表潜力 中高（3.51/5）。主要风险：需要超重力/旋转填充床或等效强化碳化设备,且钢渣成分波动会影响可重复性。
- B - 离心/超重力成型混凝土：实验难度 中（可行性 3/5）；设备需求 高（设备可获得性 2.5/5）；发表潜力 中低（3.16/5）。主要风险：离心成型设备、模具和安全控制门槛较高,实验尺度放大不容易。
- C - 重力场对水泥水化影响：实验难度 高（可行性 2/5）；设备需求 高（设备可获得性 1.5/5）；发表潜力 中高（3.44/5）。主要风险：微重力/超重力水化实验设备可获得性弱,普通材料实验室难以稳定复现重力场条件。
- D - CO2养护与碳化混凝土：实验难度 低（可行性 4.5/5）；设备需求 低（设备可获得性 4/5）；发表潜力 中高（3.75/5）。主要风险：方向较成熟,单纯重复 CO2 养护容易缺少新意,需要与材料体系或强化过程结合。
- E - 碳化固废辅助胶凝材料：实验难度 低（可行性 4/5）；设备需求 低（设备可获得性 4/5）；发表潜力 高（4.45/5）。主要风险：固废来源和预碳化条件会显著影响活性,需建立清楚的材料表征和性能评价链条。
- F - 旋转填充床与传质强化：实验难度 高（可行性 2.5/5）；设备需求 高（设备可获得性 2/5）；发表潜力 中低（3.14/5）。主要风险：传质强化文献多来自化工过程,和水泥/混凝土的直接耦合需要重新设计验证场景。

## 8. 每个方向可能的论文题目

以下为基于数据线索形成的可拟题目，不是已发表论文题录。

### A - 超重力碳化固废
- 可拟题目：超重力强化钢渣碳化及其作为低碳胶凝材料的性能评价
- 可拟题目：旋转填充床条件下转炉渣 CO2 矿化与砂浆性能耦合机制
- 可拟题目：高重力碳化固废的反应程度、微结构和胶凝活性关系研究

### B - 离心/超重力成型混凝土
- 可拟题目：离心成型对低碳胶凝混凝土密实度和耐久性的影响
- 可拟题目：管桩混凝土离心过程中的浆体迁移与界面结构演化
- 可拟题目：含碳化固废胶凝材料的离心成型混凝土性能初探

### C - 重力场对水泥水化影响
- 可拟题目：重力场变化对水泥浆体早期水化和孔结构形成的影响
- 可拟题目：超重力条件下水泥基材料水化动力学与微结构演化
- 可拟题目：微重力/超重力水泥浆体实验数据的系统复核与小试设计

### D - CO2养护与碳化混凝土
- 可拟题目：CO2 养护下含碳化固废 SCM 砂浆的早期性能与固碳效率
- 可拟题目：加速碳化养护对低熟料胶凝体系强度和耐久性的影响
- 可拟题目：CO2 养护与预碳化再生粉体协同提升水泥基材料性能研究

### E - 碳化固废辅助胶凝材料
- 可拟题目：碳化废混凝土粉作为辅助胶凝材料的活性评价与替代率优化
- 可拟题目：碳化钢渣 SCM 对水泥水化、孔结构和力学性能的影响
- 可拟题目：不同固废预碳化制度对低碳砂浆性能的调控机制

### F - 旋转填充床与传质强化
- 可拟题目：旋转填充床强化矿化碳化过程及其水泥基材料应用边界
- 可拟题目：传质强化条件下钙基固废 CO2 矿化效率与胶凝性能关联
- 可拟题目：面向低碳胶凝材料的高重力碳化反应器小试方案研究

## 9. 推荐主攻方向

- E - 碳化固废辅助胶凝材料：总分 4.29/5。主要依据：论文总数=424;2022-2026近五年=313;2017-2021=75;增长=238;期刊/会议数=145;平均引用=36.47;阅读清单=10。
- D - CO2养护与碳化混凝土：总分 3.74/5。主要依据：论文总数=489;2022-2026近五年=257;2017-2021=159;增长=98;期刊/会议数=139;平均引用=61.94;阅读清单=10。

主攻逻辑：E 能把固废资源化、碳化活化和水泥基性能直接连接；D 实验设备门槛较低、混凝土相关性强，但必须与材料体系或过程强化耦合以避免重复性选题。

## 10. 推荐备用方向

- A - 超重力碳化固废：总分 3.3/5。主要依据：论文总数=294;2022-2026近五年=169;2017-2021=82;增长=87;期刊/会议数=147;平均引用=73.02;阅读清单=10。

备用逻辑：A 与“超重力”主题最贴近，但设备可获得性和固废成分波动是主要风险。建议先把 A 作为 E/D 的强化碳化工艺变量，而不是立即独立成大课题。

## 11. 第一轮最小可行实验方案

- 目标：用普通材料实验室可执行的小试验证“预碳化固废 SCM + CO2 养护”是否能同时改善早期性能和固碳表现。
- 材料：优先选择一种来源稳定的废混凝土粉或钢渣粉；设置未碳化、常规静态碳化、强化碳化三个材料状态。若无超重力设备，强化碳化先用高 CO2 浓度、湿度和搅拌/薄层暴露模拟。
- 基准体系：水泥净浆或砂浆，设置 0%、10%、20% 固废替代率；D/E 主线先做砂浆强度、质量变化、pH/酚酞、XRD/TG 或碳酸盐含量等基础指标。
- 判据：若 10%-20% 替代率下强度不显著下降且碳酸盐生成/CO2 吸收有可测差异，则进入第二轮机制表征；若强度和工作性均恶化，则回到材料预处理和粒径分级。
- 暂缓项：C/B/F 不纳入第一轮核心实验，只保留文献补检和设备条件评估。

## 12. 下一步 30 天行动计划

- 第 1 周：人工复核各方向代表论文，重点清理 B/C/F 的检索噪声；补检关键词中缺失的 cement paste、pipe pile、rotating packed bed mineral carbonation 交叉论文。
- 第 2 周：确定 1-2 种固废来源、预碳化制度、基准水泥/砂浆配合比和最少测试指标；完成试验矩阵压缩。
- 第 3 周：完成第一轮材料预碳化与砂浆/净浆小试，记录工作性、早期强度、质量变化和基础碳化表征。
- 第 4 周：汇总实验数据与代表论文，判断主攻 E+D 或 E+D+A 耦合路线是否成立；若数据支撑不足，转入人工补充检索和第二轮方案修正。

## 最终推荐表

| 方向 | 热度 | 创新性 | 实验难度 | 设备需求 | 推荐程度 |
| --- | --- | --- | --- | --- | --- |
| A - 超重力碳化固废 | 中低（2.4/5） | 中高（4.09/5） | 中（可行性 3.5/5） | 高（设备可获得性 2.5/5） | 备用方向（总分 3.3/5） |
| B - 离心/超重力成型混凝土 | 中低（1.16/5） | 中低（3.02/5） | 中（可行性 3/5） | 高（设备可获得性 2.5/5） | 暂缓方向（总分 2.89/5） |
| C - 重力场对水泥水化影响 | 中低（1.44/5） | 高（4.53/5） | 高（可行性 2/5） | 高（设备可获得性 1.5/5） | 暂缓方向（总分 2.91/5） |
| D - CO2养护与碳化混凝土 | 中高（3.39/5） | 中低（1.8/5） | 低（可行性 4.5/5） | 低（设备可获得性 4/5） | 主攻方向（总分 3.74/5） |
| E - 碳化固废辅助胶凝材料 | 高（5/5） | 高（4.25/5） | 低（可行性 4/5） | 低（设备可获得性 4/5） | 主攻方向（总分 4.29/5） |
| F - 旋转填充床与传质强化 | 中低（1.79/5） | 中高（3.2/5） | 高（可行性 2.5/5） | 高（设备可获得性 2/5） | 暂缓方向（总分 2.82/5） |
