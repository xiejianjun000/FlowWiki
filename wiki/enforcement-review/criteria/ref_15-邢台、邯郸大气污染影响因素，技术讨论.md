---
title: 15-邢台、邯郸大气污染影响因素，技术讨论
category: 外部资料
subcategory: ''
source_type: external
source_path: raw/inbox/online_monitoring_external_v3/raw/00-微信原文/微信原文-主库/15-邢台、邯郸大气污染影响因素，技术讨论.md
created: '2026-07-26'
updated: '2026-07-26'
confidence: medium
status: draft
ace_review:
  generator: auto
  reflector: auto
  curator: auto
  ingested_date: '2026-07-26'
  source_inbox: online_monitoring_external_v3
tags:
- 企业合规
- 环保
---

# 邢台、邯郸大气污染影响因素，技术讨论

——春季O3与PM2.5复合污染的日内切换特征与协同控制讨论
（应读者留言撰写）
一、问题
2026年3月中旬，邢台与邯郸两市逐时监测数据揭示了一个值得关注的现象：O3（臭氧）与PM2.5（细颗粒物）的浓度峰值并不重合，而是呈现出"午后O3冲顶、深夜PM2.5封顶"的时间错位结构。以2026年3月10日为例，邢台在16时出现O3峰值146 ug/m3，邯郸在15时出现O3峰值141 ug/m3；但两市PM2.5峰值均推迟至23时，分别为167.6 ug/m3和172.3 ug/m3，O3峰值与PM2.5峰值之间的时滞分别约为7小时和8小时[1][2]。这一现象并非偶发，而是贯穿整个样本期的系统性特征。
从样本期整体均值看，两市呈现出有差异的污染结构。邯郸PM2.5平均浓度为82.6 ug/m3，高于邢台的73.6 ug/m3；但邢台O3平均浓度64.7 ug/m3，高于邯郸的60.2 ug/m3。邯郸NO2（二氧化氮）平均浓度24.7 ug/m3，也高于邢台的19.7 ug/m3[1][2]。这提示两市虽然地理相邻，但在污染类型的主导特征上已有所分化。
本文基于两市数据，结合国内外大气化学与空气质量管理领域的研究文献，讨论该现象的成因机制及其对春季协同控制策略的潜在影响。文中涉及的分析以观测相关性为主，旨在为后续数值模拟和控制方案设计提供参考方向，不构成定量因果推断。
图1  邢台与邯郸样本期O3和PM2.5平均日变化曲线（2026年3月9—19日）
注：蓝色阴影区为午后光化学活跃时段，橙色阴影区为夜间累积时段
二、关键日过程
2026年3月10日是本轮样本期内O3和PM2.5同时表现突出的典型日。邢台当日O3-8h（最大日8小时滑动平均浓度，MDA8，Maximum Daily 8-hour Average）达129.9 ug/m3，邯郸达126.5 ug/m3[1][2]。该指标的计算方式为MDA8 = max{(C1+C2+...+C8)/8, (C2+C3+...+C9)/8, ...}，其中Ci为连续小时浓度值[3][4]。这意味着当天的O3高浓度并非一个瞬间尖峰，而是维持了至少8小时的高平台。
从逐时变化看，午后O3在辐射增强、温度升高的驱动下持续攀升，而NO2在同一时段被显著消耗（邢台16时NO2仅15.4 ug/m3，邯郸15时仅16.4 ug/m3）。入夜后，随着BLH（Boundary Layer Height，边界层高度）急剧下降（邢台23时BLH仅100 m，邯郸仅25 m），风速回落，NO2回升至40—53 ug/m3，PM2.5在边界层压缩效应下快速攀升至峰值[1][2]。
图2  2026年3月10日邢台与邯郸O3、PM2.5、NO2逐时变化
注：虚线标注O3峰值和PM2.5峰值出现时刻，时滞约7—8小时
三、日夜分相与扩散条件
将样本期数据按白天（08—18时）和夜间（21—05时）分组统计，两市均呈现出鲜明的日夜分相特征。邯郸白天O3均值81.8 ug/m3，夜间39.1 ug/m3，白夜比约2.09；邢台分别为83.9和46.1 ug/m3，白夜比约1.82。PM2.5则相反：邯郸夜间均值99.9 ug/m3，白天69.1 ug/m3，夜昼比约1.45；邢台夜间86.8 ug/m3，白天63.1 ug/m3，夜昼比约1.38[1][2]。
BLH的日夜差异更为显著。邯郸白天BLH均值897.8 m，夜间208.7 m，白夜比约4.30倍；邢台白天893.6 m，夜间仅139.7 m，白夜比达6.39倍。将通风系数简化为VC = BLH x WS（其中WS为风速），则邯郸白天VC约12453 m^2/s，夜间仅1746 m^2/s，白夜比7.13；邢台白天约11930 m^2/s，夜间约1376 m^2/s，白夜比8.67[1][2]。这意味着白天和夜间的大气容积存在近一个数量级的差异，同等排放量在夜间会产生更高的地面浓度。
图3  邢台与邯郸O3、PM2.5、NO2、BLH的日夜均值对比
注：BLH以1/100比例显示，便于同坐标轴呈现
图4  逐日平均通风系数VC时间序列（2026年3月9—19日）
注：灰色虚线为低扩散参考阈值3000 m^2/s
四、O3与气象因子的相关结构
样本期内，两市O3浓度与温度呈强正相关（邯郸r=0.811，邢台r=0.782），与BLH呈中等正相关（邯郸r=0.663，邢台r=0.655），与相对湿度呈强负相关（邯郸r=-0.745，邢台r=-0.699），与NO2呈显著负相关（邯郸r=-0.644，邢台r=-0.654）[1][2]。这一相关结构与已有的华北平原O3观测研究基本一致：当温度升高、辐射增强、相对湿度下降时，光化学反应链加速，O3净生成速率上升[5][6][7][8]。
O3与NO2的负相关值得特别讨论。在光化学活跃时段，NO2通过光解（NO2 + hv -> NO + O，O + O2 -> O3）被消耗为O3生成的原料；而在夜间无紫外辐射条件下，NO2通过与O3反应生成NO3自由基（NO2 + O3 -> NO3），进而与NO2结合形成N2O5，N2O5水解生成HNO3（硝酸），若有足够NH3（氨）存在且温度和湿度条件适宜，则NH3 + HNO3可向NH4NO3（硝酸铵）颗粒相转化，推高PM2.5[9][10][11][12]。这就是白天光化学与夜间颗粒化学双相过程的化学基础。
图5  邢台与邯郸主要污染物和气象参数Pearson相关系数矩阵
注：暖色为正相关、冷色为负相关，O3与温度正相关、与湿度和NO2负相关的结构清晰
图6  O3浓度与温度的散点关系（点色表示相对湿度）
注：高温低湿条件下O3浓度明显偏高
五、O3-8h与国内外标准的对比
目前全球主要O3空气质量标准均以8小时均值为核心指标。WHO（世界卫生组织）2021年全球空气质量指南建议O3-8h不超过100 ug/m3[3]；欧盟长期目标为O3-8h不超过120 ug/m3[13][27]；美国EPA（Environmental Protection Agency，环境保护署）现行NAAQS（National Ambient Air Quality Standards，国家环境空气质量标准）为O3-8h不超过70 ppb（约137 ug/m3），按三年第四高日统计[4][14]。中国现行GB 3095-2026标准中O3日最大8小时滑动平均二级标准维持160 ug/m3[15]。
在本轮样本中，两市有多天O3-8h超过WHO指南值100 ug/m3：3月10日邢台129.9 ug/m3、邯郸126.5 ug/m3，均已超过欧盟长期目标120 ug/m3；3月19日邢台再次达到104.4 ug/m3，超过WHO指南值[1][2]。虽然距离中国二级标准160 ug/m3仍有余量，但WHO指出在100 ug/m3以下仍可能存在健康影响[3]。区域研究表明，京津冀地区O3高风险期从4月即开始，当最高气温达到25-28 C时，O3-8h超标概率显著上升[16][17]。
图7  逐日O3-8h最大值与WHO、欧盟、中国标准阈值对比
注：3月10日两市O3-8h已超过欧盟120 ug/m3长期目标
六、两市差异的量化比较
虽然邢台与邯郸同处太行山东麓、华北平原西缘，但本轮样本呈现出有意义的差异。邢台O3均值（64.7 ug/m3）高于邯郸（60.2 ug/m3），3月19日邢台O3-8h达104.4 ug/m3而邯郸为91.9 ug/m3，提示邢台对春季午后臭氧的响应更为敏感[1][2]。邯郸PM2.5均值（82.6 ug/m3）和NO2均值（24.7 ug/m3）均高于邢台（73.6和19.7 ug/m3），且PM2.5与BLH的负相关在邯郸更强（r=-0.477 vs 邢台r=-0.403），表明邯郸在静稳条件下的颗粒物累积更为显著[1][2]。
以3月10日为例，邢台全天平均风速仅5.0 m/s，日均VC约2618 m^2/s，明显低于邯郸同日的9.7 m/s和4753 m^2/s；但邢台当日O3-8h达129.9 ug/m3，高于邯郸的126.5 ug/m3[1][2]。这暗示邢台当日处于低风速但白天混合层仍可抬升的配置，有利于光化学反应产物的局地积累。简化概括来说，邢台更像"午后先亮"（O3响应更快），邯郸更像"深夜更重"（颗粒物底盘更厚），这种差异对控制策略的排序有实际影响。
七、三维视角：O3与PM2.5的气象依赖结构
为更直观地展现O3和PM2.5在多维气象空间中的分布特征，以三维散点图方式呈现两市的观测结构。
图8  O3浓度在温度-BLH三维空间中的分布
注：暖色代表高O3值，高温且BLH较高时O3浓度明显偏高
图9  PM2.5浓度在NO2-BLH三维空间中的分布
注：暖色代表高PM2.5值，低BLH且NO2偏高时PM2.5浓度最高
图8中可以看到，高O3值集中在温度较高（10 C以上）且BLH较高（500-1200 m）的区域，与白天光化学驱动的机制一致。图9则显示高PM2.5值集中在低BLH（200 m以下）且NO2较高（30 ug/m3以上）的区域，与夜间边界层压缩和二次硝酸盐生成的过程方向一致[9][10][11]。两张图共同说明同一城市的污染物高值区在气象参数空间中占据不同位置，进一步佐证了白天O3与夜间PM2.5的分相结构。
八、O3时空分布的三维曲面
图10  O3浓度在日期-时刻二维平面上的三维曲面分布
注：午后O3高值带（12-17时）呈脊状分布，3月10日和12日尤为突出
图10以三维曲面形式展现了O3在日期和时刻两个维度上的空间结构。两市均可观察到明显的午后高值脊线——每天12-17时形成O3高值区域，3月10日、12日等日最为突出。这种时空结构直观印证了O3的光化学日变化特征：随太阳辐射增强午后出现峰值，随辐射减弱夜间迅速回落[5][6][8]。对比两市曲面形态，邢台的高值脊线在部分日期更为尖锐，这与其O3响应更敏感的统计结论相吻合。
九、控制策略讨论：分时段协同的必要性
上述分析表明，两市面对的并非单一污染物主导的简单问题，而是一个在24小时内不断切换主导机制的复合系统。白天光化学活跃期间，VOCs（Volatile Organic Compounds，挥发性有机化合物）经OH自由基氧化生成RO2/HO2，这些过氧自由基将NO再氧化为NO2，为O3净生成持续供料[5][6][7]。夜间无紫外辐射，光化学主链减弱，但N2O5非均相水解和NH3-HNO3气粒转化开始主导二次颗粒物的生成[9][10][11][12]。
从控制灵敏度角度看，O3生成对前体物的响应并非线性。经典的O3-NOx-VOCs敏感性分析表明[6][7][18][19]，在VOC受限区制下，削减VOCs对降低O3更有效；在NOx受限区制下，削减NOx更有效；若处于共同受限区间，则需协同减排。近年研究发现，华北平原部分城市正从典型的VOC受限向VOC-NOx共限迁移[18][19][20][21]，这意味着固定的单因子优先策略可能并非最优。
基于上述讨论，可以考虑的策略方向包括：（1）在午后光化学活跃时段（11-17时），重点关注高活性VOCs排放源（涂装、溶剂使用、油气挥发等）和移动源NOx排放；（2）在夜间静稳累积时段（21-06时），关注燃烧源NOx和NH3相关排放，以减缓硝酸盐二次生成对PM2.5的贡献[10][11][12]；（3）在气象预报显示温度跃升、湿度下降、BLH白天明显抬升时，提前启动O3防控措施；（4）考虑到邢台和邯郸的差异特征，避免完全相同的一致性方案。
需要指出的是，以上策略方向基于有限样本期的统计分析和文献推理，实际控制方案需依托更长时间序列数据、排放源清单、空气质量模型和敏感性模拟结果予以验证和量化。本文目的是基于观测数据提出值得关注的方向，而非给出定量的减排比例建议。
十、新标准影响
GB 3095-2026《环境空气质量标准》已于2026年3月1日起实施，替代GB 3095-2012[15]。配套的HJ 633-2026《环境空气质量指数（AQI）技术规定》和HJ 663-2026《环境空气质量评价技术规范》同步落地[22][23]。本轮修订在PM2.5方面做了重要调整：第一阶段（2026-2030年）过渡期PM2.5年均和日均二级限值分别为30和60 ug/m3（原标准为35和75 ug/m3）；第二阶段（2031年起）进一步收严至25和50 ug/m3[15]。同时收严了PM10、SO2和NO2限值。O3的8小时二级标准在本轮修订中维持160 ug/m3未变。
这一标准框架意味着：一方面，PM2.5达标压力将持续加大，夜间颗粒物累积对达标率的影响不容忽视；另一方面，虽然O3的国标阈值暂未调整，但WHO指南值（100 ug/m3）和欧盟长期目标（120 ug/m3）构成了更严格的健康风险参照，两市在3月样本中多日已越过这些阈值[1][2][3][13]。从管理趋势看，将O3风险关口前移、在春季即开始部署协同控制，可能比等到盛夏再应对更为主动。
数据样本期：2026年3月9日—3月19日
参考文献
[1] 邢台监测数据。
[2] 邯郸监测数据。
[3] World Health Organization. WHO global air quality guidelines: particulate matter (PM2.5 and PM10), ozone, nitrogen dioxide, sulfur dioxide and carbon monoxide[M]. Geneva: WHO, 2021.
注：世界卫生组织. 全球空气质量指南：颗粒物（PM2.5和PM10）、臭氧、二氧化氮、二氧化硫和一氧化碳[M]. 日内瓦：世界卫生组织，2021.
[4] U.S. Environmental Protection Agency. Ozone National Ambient Air Quality Standards (NAAQS)[EB/OL]. Washington, D.C.: U.S. EPA, 2026.
注：美国环境保护署. 臭氧国家环境空气质量标准[EB/OL]. 华盛顿：美国环保署，2026.
[5] Sillman S. The relation between ozone, NOx and hydrocarbons in urban and polluted rural environments[J]. Atmospheric Environment, 1999, 33(12): 1821-1845. DOI:10.1016/S1352-2310(98)00345-8.
注：Sillman S. 城市及受污染乡村环境中臭氧、NOx与烃类之间的关系[J]. 大气环境，1999，33（12）：1821-1845.
[6] Monks P S, Archibald A T, Colette A, et al. Tropospheric ozone and its precursors from the urban to the global scale from air quality to short-lived climate forcer[J]. Atmospheric Chemistry and Physics, 2015, 15(15): 8889-8973. DOI:10.5194/acp-15-8889-2015.
注：Monks P S，Archibald A T，Colette A，等. 从城市到全球尺度的对流层臭氧及其前体物[J]. 大气化学与物理，2015，15（15）：8889-8973.
[7] Liu C, Shi K. A review on methodology in O3-NOx-VOC sensitivity study[J]. Environmental Pollution, 2021, 291: 118249. DOI:10.1016/j.envpol.2021.118249.
注：Liu C，Shi K. O3-NOx-VOCs敏感性研究方法综述[J]. 环境污染，2021，291：118249.
[8] U.S. Environmental Protection Agency. Integrated Science Assessment (ISA) for Ozone and Related Photochemical Oxidants[R]. Washington, D.C.: U.S. EPA, 2020.
注：美国环境保护署. 臭氧及相关光化学氧化剂综合科学评估[R]. 华盛顿：美国环保署，2020.
[9] Wen L, Xue L, Wang X, et al. Summertime fine particulate nitrate pollution in the North China Plain: increasing trends, formation mechanisms and implications for control policy[J]. Atmospheric Chemistry and Physics, 2018, 18: 11261-11275. DOI:10.5194/acp-18-11261-2018.
注：Wen L，Xue L，Wang X，等. 华北平原夏季细颗粒物硝酸盐污染：增长趋势、形成机制及控制政策启示[J]. 大气化学与物理，2018，18：11261-11275.
[10] Zhou W, Du H, Liu M, et al. Role of N2O5 heterogeneous hydrolysis in summer nitrate formation in Beijing[J]. npj Clean Air, 2025, 1: 40. DOI:10.1038/s44407-025-00039-0.
注：Zhou W，Du H，Liu M，等. N2O5非均相水解在北京夏季硝酸盐形成中的作用[J]. npj清洁空气，2025，1：40.
[11] Lin Z, Ying C, Xu L, et al. Measurement report: High contribution of N2O5 uptake to particulate nitrate formation in NO2-limited urban areas[J]. Atmospheric Chemistry and Physics, 2025, 25: 17747-17759. DOI:10.5194/acp-25-17747-2025.
注：Lin Z，Ying C，Xu L，等. N2O5吸收对颗粒硝酸盐形成的高贡献[J]. 大气化学与物理，2025，25：17747-17759.
[12] Mayorga R J, Zhao Z, Zhang H. Formation of secondary organic aerosol from nitrate radical oxidation of phenolic VOCs[J]. Atmospheric Environment, 2021, 244: 117910. DOI:10.1016/j.atmosenv.2020.117910.
注：Mayorga R J，Zhao Z，Zhang H. 由硝酸根自由基氧化酚类VOCs生成二次有机气溶胶[J]. 大气环境，2021，244：117910.
[13] European Environment Agency. Ozone: Air quality status report 2025[R/OL]. Copenhagen: EEA, 2025.
注：欧洲环境署. 臭氧：2025年空气质量状况报告[R/OL]. 哥本哈根：欧洲环境署，2025.
[14] U.S. Environmental Protection Agency. 2015 Revision to 2008 Ozone NAAQS[EB/OL]. Washington, D.C.: U.S. EPA, 2015.
注：美国环境保护署. 2015年臭氧NAAQS修订[EB/OL]. 华盛顿：美国环保署，2015.
[15] 中华人民共和国生态环境部，国家市场监督管理总局. 环境空气质量标准：GB 3095-2026[S]. 北京，2026.
[16] Yang Y, Zhou Y, Wang H, et al. Meteorological characteristics of extreme ozone pollution events in China and their future predictions[J]. Atmospheric Chemistry and Physics, 2024, 24: 1177-1191. DOI:10.5194/acp-24-1177-2024.
注：Yang Y，Zhou Y，Wang H，等. 中国极端臭氧污染事件的气象特征及未来预测[J]. 大气化学与物理，2024，24：1177-1191.
[17] Ren J, Guo F, Xie S. Diagnosing ozone-NOx-VOC sensitivity and revealing causes of ozone increases in China based on 2013-2021 satellite retrievals[J]. Atmospheric Chemistry and Physics, 2022, 22: 15035-15047. DOI:10.5194/acp-22-15035-2022.
注：Ren J，Guo F，Xie S. 基于2013-2021年卫星反演诊断中国O3-NOx-VOCs敏感性[J]. 大气化学与物理，2022，22：15035-15047.
[18] Zhao Y, Li Y, Kumar A, et al. Separately resolving NOx and VOC contributions to ozone formation[J]. Atmospheric Environment, 2022, 285: 119224. DOI:10.1016/j.atmosenv.2022.119224.
注：Zhao Y，Li Y，Kumar A，等. 分别解析NOx和VOCs对臭氧生成的贡献[J]. 大气环境，2022，285：119224.
[19] Chen T, Chu B, Ma J, et al. Ozone Pollution in China: Current Status and Control Strategies[J]. Engineering, 2025. DOI:10.1016/j.eng.2025.06.044.
注：Chen T，Chu B，Ma J，等. 中国臭氧污染现状及控制策略[J]. 工程，2025.
[20] Zhu C, Gai Y, Liu Z, et al. Long-term changes of surface ozone and ozone sensitivity over the North China Plain based on 2015-2021 satellite retrievals[J]. Air Quality, Atmosphere & Health, 2024, 17: 2753-2766. DOI:10.1007/s11869-024-01598-z.
注：Zhu C，Gai Y，Liu Z，等. 华北平原地表臭氧及敏感性长期变化[J]. 空气质量、大气与健康，2024，17：2753-2766.
[21] Zhu S, Ma J, Wang S, et al. Shifts of Formation Regimes and Increases of Atmospheric Oxidation Led to Ozone Increase in North China Plain and Yangtze River Delta[J]. Journal of Geophysical Research: Atmospheres, 2023, 128: e2022JD038373. DOI:10.1029/2022JD038373.
注：Zhu S，Ma J，Wang S，等. 生成区制迁移与大气氧化性增强导致华北平原和长三角O3上升[J]. 地球物理研究杂志：大气，2023，128：e2022JD038373.
[22] 中华人民共和国生态环境部. 环境空气质量指数（AQI）技术规定：HJ 633-2026[S]. 北京，2026.
[23] 中华人民共和国生态环境部. 环境空气质量评价技术规范：HJ 663-2026[S]. 北京，2026.
[24] National Oceanic and Atmospheric Administration Global Monitoring Laboratory. Ozone in the troposphere[EB/OL]. Boulder: NOAA GML, 2026.
注：美国国家海洋和大气管理局全球监测实验室. 对流层中的臭氧[EB/OL]. 博尔德：NOAA GML，2026.
[25] Li R, Xu M, Li M, et al. Identifying the spatiotemporal variations in ozone formation regimes across China from 2005 to 2019[J]. Atmospheric Chemistry and Physics, 2021, 21: 15631-15646. DOI:10.5194/acp-21-15631-2021.
注：Li R，Xu M，Li M，等. 识别2005-2019年中国臭氧生成区制时空变化[J]. 大气化学与物理，2021，21：15631-15646.
[26] 国务院. 空气质量持续改善行动计划[EB/OL]. 北京：中国政府网，2023.
[27] European Environment Agency. Ozone: 8-hour mean target value for the protection of human health[EB/OL]. Copenhagen: EEA, 2025.
注：欧洲环境署. 保护人体健康的臭氧8小时均值目标值[EB/OL]. 哥本哈根：欧洲环境署，2025.
[28] U.S. Environmental Protection Agency. Ground-level Ozone Basics[EB/OL]. Washington, D.C.: U.S. EPA, 2026.
注：美国环境保护署. 近地面臭氧基础知识[EB/OL]. 华盛顿：美国环保署，2026.
[29] World Health Organization. Air Quality Standards database[DB/OL]. Geneva: WHO, 2026.
注：世界卫生组织. 空气质量标准数据库[DB/OL]. 日内瓦：世界卫生组织，2026.
[30] European Environment Agency. Exposure of Europe's ecosystems to ozone[R/OL]. Copenhagen: EEA, 2025.
注：欧洲环境署. 欧洲生态系统臭氧暴露情况[R/OL]. 哥本哈根：欧洲环境署，2025.