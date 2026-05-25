# 四方向 ScienceDirect 文献格局报告

- 检索时间：2026-05-25T14:34:28.758173+00:00
- 数据源：ScienceDirect / Elsevier API。未混入 Crossref、Semantic Scholar 或 Google Scholar 记录。
- 合规边界：仅保存 API 返回的 metadata、摘要/teaser、DOI、ScienceDirect/Elsevier 稳定链接；未抓取付费全文，未绕过访问权限。

## 为什么从六方向收敛到四方向

原六方向把高重力碳化、CO2 养护、碳化 SCM、旋转填充床等拆得较细，适合发散，但国际文献实际检索时容易把同一批 carbonation/mineralization 文献重复切分；同时“hypergravity concrete”本身不是常用题名词。四方向改按国际常用命名收敛：离心成型混凝土、土工离心模型、水泥水化重力效应、高重力碳化/矿化。这样既保留超重力主题，又能减少化工、土工、普通碳化文献之间的混淆。

## 检索数量概览

| 方向 | ScienceDirect query total 合计 | API返回记录 | 去重后数量 | 初筛相关数量 | 判断 |
| --- | ---: | ---: | ---: | ---: | --- |
| 离心成型混凝土 | 64096 | 182 | 116 | 51 | 可形成初步阅读池 |
| 土工离心模型 | 3698 | 180 | 152 | 25 | 可形成初步阅读池 |
| 水泥水化重力效应 | 26346 | 104 | 94 | 2 | 该方向 ScienceDirect 直接文献不足 |
| 高重力碳化/矿化 | 13580 | 200 | 155 | 79 | 可形成初步阅读池 |

## 分方向分析

### 离心成型混凝土

- 国际常用叫法：centrifuged concrete; centrifugal casting concrete; centrifugally cast concrete; centrifugally formed concrete; spun concrete; PHC pile; prestressed high-strength concrete pipe pile; hollow concrete pile; concrete pipe pile; centrifugal forming technique
- ScienceDirect 检索结果数量：query total 合计 64096；API 实际返回 182。
- 去重后数量：116；初筛后相关文献数量：51。
- 不跑偏判断：Directly studies concrete materials or concrete members under centrifugal forming.
- 研究热点：spun/centrifuged pipe piles, hollow members, fiber reinforcement, durability gradients, centrifugal forming process.
- 近年趋势：离心管桩和离心成型构件持续有工程论文，但材料微结构与低碳胶凝体系耦合仍可深化。
- 与“超重力混凝土”的关系：直接对应超重力/离心加速度下混凝土成型、密实、分层和构件性能。
- 是否适合作为硕士论文方向：适合作为候选主线，由导师结合设备、材料来源和论文目标决定。
- 风险与不足：容易停留在构件工程性能，需把离心制度、浆体迁移、分层和材料参数拉回材料问题。

代表性文献（10篇以内）：

1. Effect of installation-induced damage on the pull-out capacity of interlocking joints in PHC pipe piles (2026). Structures. DOI/URL: 10.1016/j.istruc.2026.111996 / https://api.elsevier.com/content/article/pii/S2352012426009458
   - 相关性：It studies concrete or cementitious members made under centrifugal acceleration, which is the closest established literature family to hypergravity concrete forming.
2. Flexural behavior of circular PHC piles strengthened with steel sleeve grouting (2026). Ocean Engineering. DOI/URL: 10.1016/j.oceaneng.2026.124385 / https://api.elsevier.com/content/article/pii/S0029801826002192
   - 相关性：It studies concrete or cementitious members made under centrifugal acceleration, which is the closest established literature family to hypergravity concrete forming.
3. Full-scale spun-cast cementless concrete pipes: Effects of manufacturing parameters and hybrid fibers reinforcement on structural performance (2026). Case Studies in Construction Materials. DOI/URL: 10.1016/j.cscm.2026.e06121 / https://api.elsevier.com/content/article/pii/S2214509526003724
   - 相关性：It studies concrete or cementitious members made under centrifugal acceleration, which is the closest established literature family to hypergravity concrete forming.
4. Steel crosspieces for medium voltage lines on spun concrete poles (2026). Transportation Research Procedia. DOI/URL: 10.1016/j.trpro.2025.12.016 / https://api.elsevier.com/content/article/pii/S2352146525009032
   - 相关性：It studies concrete or cementitious members made under centrifugal acceleration, which is the closest established literature family to hypergravity concrete forming.
5. Study on the horizontal dynamic characteristics of cement-soil composite pipe Piles: Field test and finite element analysis (2026). Soil Dynamics and Earthquake Engineering. DOI/URL: 10.1016/j.soildyn.2025.109989 / https://api.elsevier.com/content/article/pii/S0267726125007833
   - 相关性：It studies concrete or cementitious members made under centrifugal acceleration, which is the closest established literature family to hypergravity concrete forming.
6. Study on the influence of concrete core filling on the dynamic response and crack resistance of offshore prestressed pipe piles during hammering piling (2026). Soil Dynamics and Earthquake Engineering. DOI/URL: 10.1016/j.soildyn.2026.110326 / https://api.elsevier.com/content/article/pii/S0267726126002381
   - 相关性：It studies concrete or cementitious members made under centrifugal acceleration, which is the closest established literature family to hypergravity concrete forming.
7. A novel paraffin/graphite PCM backfill for PHC energy pile: Numerical and experimental analysis on thermal performance (2025). Applied Thermal Engineering. DOI/URL: 10.1016/j.applthermaleng.2024.124656 / https://api.elsevier.com/content/article/pii/S135943112402324X
   - 相关性：It studies concrete or cementitious members made under centrifugal acceleration, which is the closest established literature family to hypergravity concrete forming.
8. Durability of prestressed high-strength concrete (PHC) piles in landfill leachate: Corrosion behavior, microstructural evolution, and structural integrity assessment (2025). Case Studies in Construction Materials. DOI/URL: 10.1016/j.cscm.2025.e05111 / https://api.elsevier.com/content/article/pii/S221450952500909X
   - 相关性：It studies concrete or cementitious members made under centrifugal acceleration, which is the closest established literature family to hypergravity concrete forming.
9. Experimental and numerical investigation for the flexural behavior of pretensioned spun precast concrete piles (2025). Engineering Structures. DOI/URL: 10.1016/j.engstruct.2025.121071 / https://api.elsevier.com/content/article/pii/S0141029625014622
   - 相关性：It studies concrete or cementitious members made under centrifugal acceleration, which is the closest established literature family to hypergravity concrete forming.
10. Experimental investigation and statistical evaluation of mechanical properties of centrifuged PHC pipe pile concrete (2025). Structures. DOI/URL: 10.1016/j.istruc.2025.110821 / https://api.elsevier.com/content/article/pii/S2352012425026384
   - 相关性：It studies concrete or cementitious members made under centrifugal acceleration, which is the closest established literature family to hypergravity concrete forming.

### 土工离心模型

- 国际常用叫法：geotechnical centrifuge modeling; geotechnical centrifuge modelling; centrifuge model test; geotechnical centrifuge test; shield tunnel AND centrifuge; cross passage AND centrifuge; soil-structure interaction AND centrifuge; concrete lining AND centrifuge; pile foundation AND centrifuge
- ScienceDirect 检索结果数量：query total 合计 3698；API 实际返回 180。
- 去重后数量：152；初筛后相关文献数量：25。
- 不跑偏判断：Studies geotechnical models involving concrete structures; use as parallel field reference, not as hypergravity concrete material evidence.
- 研究热点：shield tunnels, cross passages, concrete linings, pile-soil-structure interaction under scaled gravity fields.
- 近年趋势：土工离心模型文献量较大，但混凝土材料本体不是核心变量。
- 与“超重力混凝土”的关系：对应重力相似和离心试验方法，可参考加载与相似理论，但不是材料制备路线。
- 是否适合作为硕士论文方向：不建议作为超重力混凝土材料主线，可作为方法参考或背景对照。
- 风险与不足：文献多但容易跑偏到土体、边坡、液化和海床；需坚持只作平行领域参考。

代表性文献（10篇以内）：

1. Centrifuge modelling of dewatering-excavation effects on overlying and adjacent large-diameter shield tunnels (2026). Tunnelling and Underground Space Technology. DOI/URL: 10.1016/j.tust.2025.107389 / https://api.elsevier.com/content/article/pii/S0886779825010272
   - 相关性：It uses a centrifuge to scale gravity stress fields around concrete infrastructure, so it is useful as a parallel modeling reference but not direct material research.
2. Effect of pile foundation on seismic response of adjacent subway station buried in sand site by centrifuge shaking table tests (2026). Engineering Structures. DOI/URL: 10.1016/j.engstruct.2026.122728 / https://api.elsevier.com/content/article/pii/S0141029626006413
   - 相关性：It uses a centrifuge to scale gravity stress fields around concrete infrastructure, so it is useful as a parallel modeling reference but not direct material research.
3. Face instability mechanisms of shield tunnel undercrossing an existing tunnel: Insights from centrifuge model tests and FDM-DEM simulations (2026). Transportation Geotechnics. DOI/URL: 10.1016/j.trgeo.2026.102016 / https://api.elsevier.com/content/article/pii/S2214391226001261
   - 相关性：It uses a centrifuge to scale gravity stress fields around concrete infrastructure, so it is useful as a parallel modeling reference but not direct material research.
4. Failure mechanism of tunnels subjected to stick-slip behavior of reverse fault using centrifuge model tests (2026). Soil Dynamics and Earthquake Engineering. DOI/URL: 10.1016/j.soildyn.2026.110154 / https://api.elsevier.com/content/article/pii/S0267726126000667
   - 相关性：It uses a centrifuge to scale gravity stress fields around concrete infrastructure, so it is useful as a parallel modeling reference but not direct material research.
5. Influences of the pile loads on the dynamic interaction between soft clay foundations and piles: A dynamic centrifuge study (2026). Journal of Building Engineering. DOI/URL: 10.1016/j.jobe.2026.115571 / https://api.elsevier.com/content/article/pii/S235271022600392X
   - 相关性：It uses a centrifuge to scale gravity stress fields around concrete infrastructure, so it is useful as a parallel modeling reference but not direct material research.
6. Seismic Response and Pile-Rock Interaction Mechanisms in Bedding Rock Slope: A Combined Centrifuge Modeling and Numerical Simulation Study (2026). Transportation Geotechnics. DOI/URL: 10.1016/j.trgeo.2025.101809 / https://api.elsevier.com/content/article/pii/S2214391225003289
   - 相关性：It uses a centrifuge to scale gravity stress fields around concrete infrastructure, so it is useful as a parallel modeling reference but not direct material research.
7. Soil-tunnel interaction for segmental linings with non-planar longitudinal joints via centrifuge modeling (2026). Tunnelling and Underground Space Technology. DOI/URL: 10.1016/j.tust.2025.107206 / https://api.elsevier.com/content/article/pii/S0886779825008442
   - 相关性：It uses a centrifuge to scale gravity stress fields around concrete infrastructure, so it is useful as a parallel modeling reference but not direct material research.
8. Centrifuge modeling of ground thaw settlement during metro tunnel construction using AGF method (2025). Transportation Geotechnics. DOI/URL: 10.1016/j.trgeo.2025.101655 / https://api.elsevier.com/content/article/pii/S2214391225001746
   - 相关性：It uses a centrifuge to scale gravity stress fields around concrete infrastructure, so it is useful as a parallel modeling reference but not direct material research.
9. Seismic response of cross-passages between parallel tunnels with varied connection rigidities in centrifuge model tests (2025). Soil Dynamics and Earthquake Engineering. DOI/URL: 10.1016/j.soildyn.2025.109385 / https://api.elsevier.com/content/article/pii/S0267726125001782
   - 相关性：It uses a centrifuge to scale gravity stress fields around concrete infrastructure, so it is useful as a parallel modeling reference but not direct material research.
10. Study on the instability mode of a tunnel face under variable seepage conditions in sandy soil shield tunnels: Centrifuge tests and numerical simulation (2025). Tunnelling and Underground Space Technology. DOI/URL: 10.1016/j.tust.2025.106515 / https://api.elsevier.com/content/article/pii/S0886779825001531
   - 相关性：It uses a centrifuge to scale gravity stress fields around concrete infrastructure, so it is useful as a parallel modeling reference but not direct material research.

### 水泥水化重力效应

- 国际常用叫法：cement hydration AND microgravity; cement hydration AND hypergravity; cement paste AND gravity; cement hydration AND centrifugation; calcium silicate hydrate AND microgravity; C-S-H AND gravity; cement solidification AND microgravity
- ScienceDirect 检索结果数量：query total 合计 26346；API 实际返回 104。
- 去重后数量：94；初筛后相关文献数量：2。
- 不跑偏判断：Directly studies cementitious hydration/microstructure only when gravity, microgravity, hypergravity, or centrifugation is an experimental variable.
- 研究热点：microgravity cement paste, hydration kinetics, bleeding/sedimentation, pore and C-S-H microstructure.
- 近年趋势：ScienceDirect 直接命中文献偏少，趋势判断需谨慎。
- 与“超重力混凝土”的关系：对应重力场对水泥浆体水化、沉降、泌水和孔结构的机制影响。
- 是否适合作为硕士论文方向：创新性高，但若没有可控重力/离心实验条件，硕士阶段风险较高。
- 风险与不足：该方向 ScienceDirect 直接文献不足；检索词敏感且样本少，普通水化文献不能强行归类。

代表性文献（10篇以内）：

1. Influence of gravity on the micromechanical properties of portland cement and lunar regolith simulant composites (2023). Cement and Concrete Research. DOI/URL: 10.1016/j.cemconres.2023.107232 / https://api.elsevier.com/content/article/pii/S0008884623001461
   - 相关性：It links gravity level or centrifugation to cement hydration, C-S-H, settling, or microstructure, matching the mechanism side of hypergravity concrete.
2. Early hydration of Portland cement studied under microgravity conditions (2015). Construction and Building Materials. DOI/URL: 10.1016/j.conbuildmat.2015.05.074 / https://api.elsevier.com/content/article/pii/S0950061815005711
   - 相关性：It links gravity level or centrifugation to cement hydration, C-S-H, settling, or microstructure, matching the mechanism side of hypergravity concrete.

### 高重力碳化/矿化

- 国际常用叫法：high gravity carbonation; rotating packed bed AND carbonation; rotating packed bed AND cement; rotating packed bed AND calcium hydroxide; rotating packed bed AND CaO; CO2 mineralization AND cement; CO2 mineralisation AND cement; accelerated carbonation AND cement paste; accelerated carbonation AND recycled concrete fines; carbonation curing AND cementitious
- ScienceDirect 检索结果数量：query total 合计 13580；API 实际返回 200。
- 去重后数量：155；初筛后相关文献数量：79。
- 不跑偏判断：Often chemical-engineering carbonation; only keep records transferable to cementitious/calcium-rich materials.
- 研究热点：rotating packed bed carbonation, CO2 mineralization, carbonation curing, recycled concrete fines, calcium-rich wastes.
- 近年趋势：碳化养护、CO2 矿化和再生粉体方向近年更活跃，高重力/旋转填充床是可迁移的过程强化支线。
- 与“超重力混凝土”的关系：对应高重力传质强化下的 CO2 碳化/矿化，可迁移到水泥基材料固碳与强化。
- 是否适合作为硕士论文方向：适合作为候选主线，由导师结合设备、材料来源和论文目标决定。
- 风险与不足：化工 CO2 吸收文献很多，必须排除纯胺吸收和普通气液传质。

代表性文献（10篇以内）：

1. High-gravity intensified carbonation of larger steel slag particles: Dual-path CO 2 mineralization and valorization in sustainable construction materials (2025). Journal of Environmental Chemical Engineering. DOI/URL: 10.1016/j.jece.2025.117004 / https://api.elsevier.com/content/article/pii/S2213343725017002
   - 相关性：It examines intensified carbonation or mineralization of cementitious/calcium-rich materials, which can be transferred to hypergravity CO2 curing or strengthening concepts.
2. Simultaneously comparing various CO 2 -mineralized steelmaking slags as supplementary cementitious materials via high gravity carbonation (2024). Journal of CO2 Utilization. DOI/URL: 10.1016/j.jcou.2024.102985 / https://api.elsevier.com/content/article/pii/S2212982024003202
   - 相关性：It examines intensified carbonation or mineralization of cementitious/calcium-rich materials, which can be transferred to hypergravity CO2 curing or strengthening concepts.
3. High-gravity carbonation of basic oxygen furnace slag for CO 2 fixation and utilization in blended cement (2016). Journal of Cleaner Production. DOI/URL: 10.1016/j.jclepro.2016.02.072 / https://api.elsevier.com/content/article/pii/S0959652616002493
   - 相关性：It examines intensified carbonation or mineralization of cementitious/calcium-rich materials, which can be transferred to hypergravity CO2 curing or strengthening concepts.
4. Systematic approach to determination of optimum gas-phase mass transfer rate for high-gravity carbonation process of steelmaking slags in a rotating packed bed (2015). Applied Energy. DOI/URL: 10.1016/j.apenergy.2015.03.047 / https://api.elsevier.com/content/article/pii/S0306261915003311
   - 相关性：It examines intensified carbonation or mineralization of cementitious/calcium-rich materials, which can be transferred to hypergravity CO2 curing or strengthening concepts.
5. Kinetics of carbonation reaction of basic oxygen furnace slags in a rotating packed bed using the surface coverage model: Maximization of carbonation conversion (2014). Applied Energy. DOI/URL: 10.1016/j.apenergy.2013.07.035 / https://api.elsevier.com/content/article/pii/S0306261913006016
   - 相关性：It examines intensified carbonation or mineralization of cementitious/calcium-rich materials, which can be transferred to hypergravity CO2 curing or strengthening concepts.
6. Process Intensification of Steel Slag Carbonation via a Rotating Packed Bed: Reaction Kinetics and Mass Transfer (2014). Energy Procedia. DOI/URL: 10.1016/j.egypro.2014.11.244 / https://api.elsevier.com/content/article/pii/S1876610214020591
   - 相关性：It examines intensified carbonation or mineralization of cementitious/calcium-rich materials, which can be transferred to hypergravity CO2 curing or strengthening concepts.
7. Kinetic modeling on CO 2 capture using basic oxygen furnace slag coupled with cold-rolling wastewater in a rotating packed bed (2013). Journal of Hazardous Materials. DOI/URL: 10.1016/j.jhazmat.2013.06.052 / https://api.elsevier.com/content/article/pii/S0304389413004524
   - 相关性：It examines intensified carbonation or mineralization of cementitious/calcium-rich materials, which can be transferred to hypergravity CO2 curing or strengthening concepts.
8. Accelerated carbonation of steelmaking slags in a high-gravity rotating packed bed (2012). Journal of Hazardous Materials. DOI/URL: 10.1016/j.jhazmat.2012.05.021 / https://api.elsevier.com/content/article/pii/S0304389412005031
   - 相关性：It examines intensified carbonation or mineralization of cementitious/calcium-rich materials, which can be transferred to hypergravity CO2 curing or strengthening concepts.
9. Accelerated carbonation fronts in cement pastes: Mechanistic insights and simplified modeling (2026). Cement and Concrete Research. DOI/URL: 10.1016/j.cemconres.2025.108050 / https://api.elsevier.com/content/article/pii/S0008884625002698
   - 相关性：It examines intensified carbonation or mineralization of cementitious/calcium-rich materials, which can be transferred to hypergravity CO2 curing or strengthening concepts.
10. CO 2 mineralization through local cement dust: A sustainable sequestration pathway (2026). Next Sustainability. DOI/URL: 10.1016/j.nxsust.2026.100327 / https://api.elsevier.com/content/article/pii/S2949823626000826
   - 相关性：It examines intensified carbonation or mineralization of cementitious/calcium-rich materials, which can be transferred to hypergravity CO2 curing or strengthening concepts.

## 候选主线

- 候选主线 A：离心成型混凝土 / PHC 管桩 / 离心浇筑材料性能。
- 候选主线 B：高重力 CO2 矿化 / 水泥基材料碳化强化。
- 候选主线 C：重力场影响水泥水化与微结构演化。

土工离心模型更适合作为“平行领域参考”，不应直接等同于超重力混凝土材料研究。
