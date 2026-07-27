---
ace_review:
  curator: auto
  generator: auto
  reflector: auto
category: 技术规范
confidence: medium
created: '2026-07-24'
source_path: ''
source_type: regulatory
status: draft
subcategory: ''
tags:
- 在线监测
- 自动监控
title: 20-长三角两市PM2.5-O₃复合污染的气象驱动与日夜分相机制，技术讨论_2
updated: '2026-07-24'
---



# 长三角两市PM2.5-O₃复合污染的气象驱动与日夜分相机制，技术讨论

冬春季大气环境特征分析-以苏州、嘉兴为例
一、形势与过程概览
2026年冬春交替期间，苏州与嘉兴两市的大气环境呈现出典型的长三角腹地污染特征：PM2.5浓度在1月中下旬至2月上旬冬季高压控制期间维持偏高水平，随着春季转暖逐步回落；O₃（臭氧）浓度则呈现镜像式爬升，尤其进入3月后午后峰值明显抬升。。
分析过程可用"冬末颗粒物主导、春初光化学渐起"概括。诊断标签包括：气象驱动型污染积累、PM2.5-O₃日夜分相切换、边界层压缩效应显著、风速扩散阈值清晰、湿度对二次气溶胶的非线性响应。值得深挖的两个信号是：嘉兴O₃温度弹性系数明显高于苏州（约2.4 vs 1.0 ug/m3/C），以及两市在高湿度条件下PM2.5浓度分布呈现阶梯式跃升而非线性增长[3][4]。
二、两市逐日污染演变面板
图1呈现了苏州与嘉兴61天完整样本期的PM2.5日均、O₃-8h以及BLH（Boundary Layer Height，边界层高度）日均的联动变化。苏州PM2.5在1月29日达到样本期峰值，而嘉兴则在2月5日前后出现最高日均值。两市的污染峰值并不完全同步，时间差约5—7天，提示尽管同处长三角核心区，两市在区域输送路径和本地排放结构上存在差异[5][6]。
从过程分段看，整个样本期可划分为三个阶段：1月20日至2月10日为冬季积累段，高压脊控制下BLH偏低、风速较弱，PM2.5浓度多次突破日均限值；2月中旬至3月初为过渡震荡段，冷暖空气交替频繁，PM2.5与O₃呈现此消彼长的典型跷跷板结构；3月上旬至21日为春季光化学渐起段，随着太阳辐射增强和气温回升，O₃日峰值逐步抬高，PM2.5则明显回落。底部色带标注了基于PM2.5三日移动均值变化率的积累—改善—平稳相态。
图1  苏州与嘉兴逐日PM2.5·O₃-8h·BLH联动面板（2026年1月20日—3月21日）
注：橙色填充为PM2.5日均，蓝色折线为O₃-8h，淡紫色底层为BLH日均归一化；浅红背景区标注PM2.5超过75 ug/m3的高值日
三、污染物24小时节律与日夜切换
图2以极坐标形式呈现了两市三种关键污染物的24小时归一化节律。O₃在12—16时形成的午后峰值区域清晰可见，与NO₂（二氧化氮）在同时段被光解消耗形成的谷值互为镜像——这正是经典的光化学日变化特征：白天紫外辐射驱动NO₂光解（NO₂ + hv → NO + O, O + O₂ → O₃），O₃净生成速率上升；夜间无紫外辐射，O₃通过与NO反应被消耗，浓度迅速回落[7][8]。
PM2.5的节律则呈现"夜间偏高、午后略低"的特征，数据期内苏州白天均值约55 ug/m3、夜间约59 ug/m3，嘉兴白天约44 ug/m3、夜间约58 ug/m3。夜昼比在嘉兴更为显著（约1.33），主因是嘉兴夜间BLH均值仅264 m，显著低于白天的727 m，边界层压缩效应更为强烈。将通风系数简化为VC = BLH × WS（其中WS为风速），苏州白天VC约为夜间的2.2倍，嘉兴则达2.8倍[1][2]。这意味着同等排放负荷下，夜间的地面浓度响应显著高于白天。
图2  苏州与嘉兴PM2.5·O₃·NO₂的24小时极坐标节律图（样本期均值）
注：各污染物浓度归一化至各自最大值的百分比；浅金色扇区标示午后光化学活跃时段
四、苏嘉两市差异的结构性解读
图7以小提琴图叠加散点的方式对比了两市在PM2.5日均、O₃-8h、NO₂日均和BLH日均四项指标上的分布差异。Welch t检验显示，苏州PM2.5日均均值高于嘉兴约5 ug/m3，差异具有统计学意义。但嘉兴O₃-8h均值（约63 ug/m3）显著高于苏州（约55 ug/m3），且分布右尾更长，提示嘉兴在春季光化学活跃时段的O₃响应更为敏感。
两市差异的结构性成因至少涉及三个层面。首先，地形与气象配置不同：苏州西侧有穹窿山、阳山等低丘（周边100公里范围内最高海拔约1130 m），对西北方向来风有一定阻滞效应；嘉兴地势更为平坦（最高海拔约716 m），但地处杭州湾北岸，受海陆风影响更为显著[9]。其次，排放密度差异：苏州工业产值和机动车保有量均高于嘉兴，NO₂日均浓度偏高约10%佐证了这一点。第三，光化学活性：嘉兴平均湿度高出苏州约6个百分点，高湿条件下气溶胶水含量（AWC，Aerosol Water Content）增大，既促进液相氧化又影响光解速率，形成了与苏州不同的化学环境[10][11]。
图3  苏州与嘉兴关键指标分布对比（小提琴图+散点）
注：每个点代表一个样本日，p值来自Welch双样本t检验
五、多参量相关性诊断矩阵
图4以分裂三角热力图的形式同时呈现了两市的Pearson相关系数矩阵：右上三角为苏州，左下三角为嘉兴。逐时数据参与计算，样本量均为1464组（n = 1464）。
三对关键相关值得重点解读。PM2.5与O₃在两市均呈显著负相关（苏州r = -0.44，嘉兴r = -0.46），印证了经典的PM2.5-O₃跷跷板效应：白天光化学活跃期O₃升高、PM2.5偏低，夜间则相反[12][13]。PM2.5与BLH的负相关（苏州r = -0.36，嘉兴r = -0.43）表明边界层高度对颗粒物浓度有稀释作用，嘉兴该相关性更强，与其夜间BLH更低有关。O₃与温度的正相关在嘉兴（r = 0.52）显著强于苏州（r = 0.27），提示嘉兴的O₃生成对温度更为敏感——这对于评估气候变暖背景下的O₃ penalty（气候惩罚效应）有重要参考价值[14][15]。
图4  苏州(右上)与嘉兴(左下)逐时数据Pearson相关系数分裂矩阵
注：暖色正相关，冷色负相关；对角线为参量名称
六、边界层高度对颗粒物的驱动与反馈
图5以散点密度图的方式展示了BLH与PM2.5的关系，颜色编码为同时刻湿度，边缘直方图显示各自分布。两市均可观察到典型的非线性负相关结构：BLH低于400 m时，PM2.5浓度分布明显右移并出现极端高值；BLH高于800 m后，PM2.5浓度收敛至较低水平且离散度减小。密度等高线揭示了两个主要聚集核心——一个位于低BLH高PM2.5的"夜间累积态"，另一个位于高BLH低PM2.5的"白天扩散态"。
这一结构指向气溶胶-边界层正反馈机制（ARF，Aerosol Radiation Feedback）：当PM2.5浓度升高时，气溶胶对太阳辐射的散射和吸收削弱了地表增温，抑制热力对流发展，导致BLH进一步压低、扩散条件恶化，形成"污染自锁"正反馈环。从数据看，苏州BLH从800 m压缩至200 m的过程中，PM2.5均值从约40 ug/m3跃升至约100 ug/m3以上，增幅约150%；而BLH压缩比约为4:1，说明PM2.5的浓度响应显著超过BLH的线性压缩效应，提示存在非线性放大机制[16][17]。
图5  苏州与嘉兴BLH-PM2.5散点密度图（颜色=湿度，含边缘分布）
注：黑色等高线为核密度估计，右上角标注Pearson r值和样本量
七、风速-PM2.5非线性扩散的临界阈值
大气污染物的水平输送与扩散高度依赖风速，但这种关系并非线性。图6呈现了逐时风速与PM2.5浓度的分段统计关系。两市均可清晰辨识出约2.5—3.5 m/s的临界扩散阈值区间：当风速低于该阈值时，PM2.5对风速变化极不敏感，浓度维持在较高平台——即进入"静稳积累"模态；越过阈值后，浓度随风速增大呈近似指数衰减[18][19]。
这一阈值特征对重污染预警具有直接实操意义：当数值预报显示未来24—48小时风速持续低于3 m/s，即可判定大气扩散条件进入不利状态，为提前启动应急减排措施提供时间窗口。从样本期统计看，苏州逐时风速低于3 m/s的时次占比约38%，嘉兴约49%，嘉兴静稳条件出现频率更高，这也解释了其夜间PM2.5浓度偏高的部分原因。
图6  苏州与嘉兴风速-PM2.5非线性扩散响应曲线
注：实线为分段均值，阴影为95%置信区间；红色竖带标示临界扩散阈值区
八、O₃光化学生成的温度弹性系数
光化学反应速率常数本质上是温度的函数，因此O₃浓度对温度存在系统性的正响应。图7以日最高温度为自变量、O₃-8h为因变量的散点回归量化了这一关系。嘉兴的温度弹性系数为2.4 ug/m3/C（r = 0.55），即日最高温度每升高1摄氏度，O₃-8h平均升高约2.4 ug/m3；苏州为1.0 ug/m3/C（r = 0.27），温度敏感性显著低于嘉兴[14][20]。
嘉兴O₃对温度更敏感的原因可能涉及VOCs（Volatile Organic Compounds，挥发性有机化合物）排放结构差异和光化学区制位置不同。从文献看，长三角南部城市近年来VOCs排放中高活性组分（芳烃类、烯烃类）占比有所上升，在温度升高促进蒸发排放增加的条件下，光化学反应链效率的温度响应更为陡峭[21][22]。这一发现的政策含义在于：在全球变暖背景下，嘉兴面临的O₃ penalty可能更为严峻，需要在春夏季提前部署VOCs源头控制。颜色编码为日均湿度，可以观察到低湿日（干燥晴朗条件）集中在高温高O₃的右上区域，进一步佐证了晴朗高温天气与光化学污染的强耦合[23]。
图7  苏州与嘉兴O₃-8h对日最高温度的弹性回归（颜色=日均湿度）
注：虚线为线性回归，阴影为95%置信带；嘉兴温度弹性系数约为苏州的2.4倍
九、PM2.5-O₃跷跷板效应的时空诊断
PM2.5与O₃的负相关（"跷跷板效应"）是大气化学的经典现象之一，其机制至少涵盖三重路径：气溶胶对太阳辐射的遮挡削弱光化学反应速率、NO对O₃的滴定消耗（即NO + O₃ → NO₂）与NO₂向硝酸盐的转化此消彼长、以及边界层动力学的昼夜交替[12][13][24]。然而，在特定气象和化学条件下，这一负相关可能失效甚至反转，形成PM2.5与O₃同步偏高的"双高"复合污染——这是当前协同管控面临的核心难点。
图8以时空热力矩阵的方式呈现了61天×24小时网格上PM2.5与O₃标准化差值的分布。暖色区域（正值）表示PM2.5主导状态，冷色区域（负值）表示O₃主导状态。两市均清晰呈现出午后冷色带（12—17时，O₃主导）与夜间暖色带（21—06时，PM2.5主导）的交替结构，但在1月下旬至2月上旬的部分时段，暖色几乎覆盖全天——这正是冬季静稳期颗粒物绝对主导的时段。进入3月后，冷色带面积逐步扩大、强度增强，对应春季O₃的渐起趋势。
图8  苏州与嘉兴PM2.5-O₃标准化差值时空矩阵（2026年1月20日—3月21日）
注：暖色=PM2.5主导  冷色=O₃主导；插值处理后显示，能直观辨识冬春切换节点
十、湿度阈值与降水雾天对空气质量的非线性响应
相对湿度（RH，Relative Humidity）对PM2.5浓度的影响并非线性递增，而是存在明显的阈值效应。图9以分段箱线图叠加散点的方式展示了不同湿度区间下PM2.5浓度分布的差异。两市均呈现出以RH = 70%为拐点的阶梯式跃升：低于60%时PM2.5中位数处于较低水平，60%—70%区间略有抬升，70%—80%区间出现显著跳变，超过80%后浓度分布进一步右移且出现更多极端高值[10][25]。
这一阈值响应的化学机制与液相氧化路径密切相关。当RH超过约65%—70%时，气溶胶颗粒的吸湿性增长变得显著，颗粒物的含水量（AWC）快速上升，为SO₂向硫酸盐的液相氧化（SO₂ + H₂O₂ → H₂SO₄）和NO₂向硝酸盐的水解通道提供了反应介质[25][26]。同时，高湿条件下气溶胶粒径增大，消光效应增强，进一步削弱太阳辐射、抑制边界层发展，形成"高湿→化学生成加速→辐射反馈→BLH压低→浓度升高"的多环正反馈。
样本期内，两市均记录了大量降雨和雾天事件。苏州附近录得降雨小时次约181次；嘉兴附近降雨约202次小时次。雾天对近地层颗粒物有显著的"锁定"效应——低能见度条件通常伴随低BLH和低风速，颗粒物在浅薄边界层内堆积；而降雨过程则表现为双面效应，雨前湿度升高促进二次生成，雨中和雨后湿沉降对颗粒物有冲刷清除作用。嘉兴雾天频次约为苏州的5倍以上，这与其更高的平均湿度（约72% vs 苏州67%）和更低的夜间BLH相一致，也部分解释了嘉兴夜间PM2.5偏高的气象原因[27][28]。
图9  苏州与嘉兴不同湿度区间下PM2.5浓度分布（箱线图+散点）
注：箱体内数字为中位数；注意RH = 70%附近的阶梯式跃升
十一、三维视角：O₃时空曲面与PM2.5多维依赖
为更直观地呈现污染物在多维参数空间中的分布结构，以三维可视化方式展开分析。图10为O₃浓度在日期-时刻二维平面上的三维曲面，两市均可观察到午后高值脊线（12—16时），脊线强度从1月至3月逐步抬升，与太阳辐射季节性增强的趋势一致。苏州的高值脊线相对平坦，嘉兴的脊线在部分日期更为尖锐——与其O₃温度弹性更高的统计结论吻合。
图10  苏州与嘉兴O₃浓度时空曲面（日期×时刻）
注：暖色代表高O₃浓度；午后脊线从冬至春逐步抬升
图11将PM2.5置于NO₂-BLH-湿度三维空间中。高PM2.5值集中在低BLH（200 m以下）且NO₂偏高（30 ug/m3以上）的区域，同时湿度偏高（暖色）。这与夜间边界层压缩条件下N₂O₅（五氧化二氮）非均相水解生成硝酸盐、进而与NH₃（氨）结合形成NH₄NO₃（硝酸铵）颗粒物的过程方向一致[29][30][31]。两张三维图共同说明：同一城市的PM2.5高值区和O₃高值区在气象参数空间中占据完全不同的位置，这是白天光化学和夜间颗粒化学双相并行的直观佐证。
图11  苏州与嘉兴PM2.5在NO₂-BLH空间的三维分布（颜色=湿度）
注：暖色代表高湿度，PM2.5高值集中在低BLH、高NO₂、高湿度区间
十二、大气环境容量逐日估算与"超载日"识别
将大气自净能力简化为通风系数VC = BLH × WS的逐日动态值，可以粗略估算大气环境容量的时间变化。图12呈现了两市VC与PM2.5的逐日对照关系。苏州VC均值约2445 m²/s，最低约429 m²/s；嘉兴均值约1691 m²/s，最低约309 m²/s。以四分位数下界为阈值标定"超载日"（VC低于第25百分位数），苏州和嘉兴分别有约15天处于环境容量严重不足状态，这些天与PM2.5高值日高度重叠[32][33]。
嘉兴VC均值显著低于苏州（约为苏州的69%），一方面是嘉兴平均风速偏低（约3.2 m/s vs 苏州3.9 m/s），另一方面是其BLH日均偏低（约477 m vs 苏州579 m）。这一结构性劣势意味着在同等排放负荷下，嘉兴的大气环境更易进入"超载"状态。从管理角度看，基于VC的逐日预报可以为精细化的排放管控提供决策依据——当预报VC将持续低于下四分位数时，提前启动差异化减排措施。
图12  苏州与嘉兴大气环境容量（VC）与PM2.5逐日对照
注：紫色填充为通风系数VC = BLH × WS，浅红背景标注VC低于25百分位数的"超载日"
十三、风向条件概率与污染输送通道
图13以16方位条件概率风向玫瑰图（CPFR，Conditional Probability Function Rose）的形式识别PM2.5高值事件（浓度>第75百分位数）的主要风向来源。苏州PM2.5高值事件集中在偏北至西北方向（NNW—NW），与长三角冬季受西北高压脊控制时的主导风向一致，提示北方区域输送对苏州冬季颗粒物浓度有显著贡献[5][34]。嘉兴的高值风向呈现更宽的扇面分布，偏北（N—NNE）和偏西（W—WNW）均有较高概率，反映了嘉兴地处苏州和杭州之间、受多路径输送叠加影响的地理特征。
虚线叠加的风速加权曲线可辅助区分近距离本地源与远距离区域输送：高概率方向上风速偏大时，更可能代表远距离输送通道；风速偏低的高概率方向则提示近距离本地排放在低扩散条件下的累积效应。两市在偏北方向均呈现"高概率+中等风速"的组合，符合冬季冷空气南下夹带污染物的输送模式。
图13  苏州与嘉兴PM2.5高值事件条件概率风向玫瑰图
注：柱高度为各方位PM2.5高值事件的条件概率，颜色深浅与该方位平均风速正相关
十四、地形背景与扩散条件分析
图14展示了苏州和嘉兴为中心、各100公里范围内的地形三维曲面。苏州位于太湖东岸，西侧和西南侧有低丘分布（最高约1130 m），东侧则是长三角冲积平原和上海方向的低平地带，城市主体海拔仅数米至二十余米。嘉兴则更为平坦，位于杭嘉湖平原核心区，南侧较远处有莫干山余脉（最高约716 m），整体地势极为低平[9]。
这一地形特征对大气扩散有重要影响。苏州西侧低丘在冬季偏西北风条件下可形成一定的迎风坡抬升和背风侧下沉，局部地形辐合可能加剧特定方位的污染物累积。嘉兴由于缺乏地形阻滞，在区域输送事件中更易受到过境气团的均匀影响，但同时也意味着清除效率在风力增强时回升较快。两市均属于典型的平原型城市，边界层气象条件（BLH、风速、稳定度）对污染物浓度变化的解释力远大于地形因子，这与散点分析中BLH对PM2.5的高解释方差一致。
图14  苏州与嘉兴周边100公里地形三维曲面
注：颜色按海拔着色；两市均属平原型城市
十五、综合讨论与协同控制方向
综合以上分析，苏州与嘉兴在2026年冬春季呈现出既有共性又有差异的大气污染特征。共性方面：两市均表现出PM2.5-O₃日夜分相切换结构，边界层高度和风速是颗粒物浓度波动的主要气象驱动因子，湿度对二次气溶胶的阈值响应特征一致，且均存在约3 m/s的风速扩散临界阈值。差异方面：苏州PM2.5基线偏高，O₃温度弹性较低；嘉兴O₃对温度更敏感、雾天频次更高、大气环境容量结构性偏低。
基于上述发现，协同控制可关注以下方向：午后光化学活跃期重点管控高活性VOCs和移动源NOx排放；夜间静稳期关注燃烧源NOx和NH₃排放，以减缓硝酸盐二次生成；嘉兴应更关注春季O₃防控的前移部署；苏州则应侧重冬季颗粒物的排放总量控制。
需要指出的是，以上分析基于61天样本期的统计观测相关技术分析，不构成定量因果推断及决策依据。实际控制方案的制定还需依托更长时间序列数据、精细化排放源清单和空气质量模型的敏感性模拟。
参考文献
[1] 苏州市环境空气质量监测数据.
[2] 嘉兴市环境空气质量监测数据.
[3] World Health Organization. WHO global air quality guidelines: particulate matter (PM2.5 and PM10), ozone, nitrogen dioxide, sulfur dioxide and carbon monoxide[M]. Geneva: WHO, 2021. 注：世界卫生组织. 全球空气质量指南：颗粒物（PM2.5和PM10）、臭氧、二氧化氮、二氧化硫和一氧化碳[M]. 日内瓦：世界卫生组织，2021.
[4] 中华人民共和国生态环境部，国家市场监督管理总局. 环境空气质量标准：GB 3095-2026[S]. 北京，2026.
[5] 长三角城市群PM2.5时空格局演变与特征[J]. 地理研究，2018，37(8)：1641-1654. 注：基于2013-2016年实时监测数据，分析长三角41城PM2.5的时空演变规律.
[6] Huang X, Ding A, Gao J, et al. Enhanced secondary pollution offset reduction of primary emissions during COVID-19 lockdown in China[J]. National Science Review, 2021, 8(2): nwaa137. DOI:10.1093/nsr/nwaa137. 注：黄（Huang）X，丁（Ding）A，高（Gao）J，等. 新冠封锁期间中国二次污染增强抵消一次排放减少[J]. 国家科学评论，2021，8(2)：nwaa137.
[7] Sillman S. The relation between ozone, NOx and hydrocarbons in urban and polluted rural environments[J]. Atmospheric Environment, 1999, 33(12): 1821-1845. DOI:10.1016/S1352-2310(98)00345-8. 注：Sillman S. 城市及受污染乡村环境中臭氧、NOx与烃类之间的关系[J]. 大气环境，1999，33(12)：1821-1845.
[8] Monks P S, Archibald A T, Colette A, et al. Tropospheric ozone and its precursors from the urban to the global scale from air quality to short-lived climate forcer[J]. Atmospheric Chemistry and Physics, 2015, 15(15): 8889-8973. DOI:10.5194/acp-15-8889-2015. 注：Monks P S，Archibald A T，Colette A，等. 从城市到全球尺度的对流层臭氧及其前体物[J]. 大气化学与物理，2015，15(15)：8889-8973.
[9] 长三角区域一体化发展规划纲要[EB/OL]. 北京：中国政府网，2019.
[10] Wen L, Xue L, Wang X, et al. Summertime fine particulate nitrate pollution in the North China Plain: increasing trends, formation mechanisms and implications for control policy[J]. Atmospheric Chemistry and Physics, 2018, 18: 11261-11275. DOI:10.5194/acp-18-11261-2018. 注：Wen L，Xue L，Wang X，等. 华北平原夏季细颗粒物硝酸盐污染：增长趋势、形成机制及控制政策启示[J]. 大气化学与物理，2018，18：11261-11275.
[11] Zheng G, Duan F, Su H, et al. Exploring the severe winter haze in Beijing: the impact of synoptic weather, regional transport and heterogeneous reactions[J]. Atmospheric Chemistry and Physics, 2015, 15: 2969-2983. DOI:10.5194/acp-15-2969-2015. 注：郑（Zheng）G，段（Duan）F，苏（Su）H，等. 北京严重冬季灰霾：天气形势、区域输送和非均相反应的影响[J]. 大气化学与物理，2015，15：2969-2983.
[12] Liu C, Shi K. A review on methodology in O3-NOx-VOC sensitivity study[J]. Environmental Pollution, 2021, 291: 118249. DOI:10.1016/j.envpol.2021.118249. 注：Liu C，Shi K. O3-NOx-VOCs敏感性研究方法综述[J]. 环境污染，2021，291：118249.
[13] Li K, Jacob D J, Liao H, et al. A two-pollutant strategy for improving ozone and particulate air quality in China[J]. Nature Geoscience, 2019, 12: 906-910. DOI:10.1038/s41561-019-0464-x. 注：李（Li）K，Jacob D J，廖（Liao）H，等. 中国臭氧和颗粒物空气质量的双污染物改善策略[J]. 自然·地球科学，2019，12：906-910.
[14] Yang Y, Zhou Y, Wang H, et al. Meteorological characteristics of extreme ozone pollution events in China and their future predictions[J]. Atmospheric Chemistry and Physics, 2024, 24: 1177-1191. DOI:10.5194/acp-24-1177-2024. 注：Yang Y，Zhou Y，Wang H，等. 中国极端臭氧污染事件的气象特征及未来预测[J]. 大气化学与物理，2024，24：1177-1191.
[15] Fu T M, Tian H. Climate change penalty to ozone air quality: review of current understandings and knowledge gaps[J]. Current Pollution Reports, 2019, 5: 159-171. DOI:10.1007/s40726-019-00115-6. 注：傅（Fu）T M，田（Tian）H. 气候变化对臭氧空气质量的惩罚效应综述[J]. 当前污染报告，2019，5：159-171.
[16] Petaja T, Jarvi L, Kerminen V M, et al. Enhanced air pollution via aerosol-boundary layer feedback in China[J]. Scientific Reports, 2016, 6: 18998. DOI:10.1038/srep18998. 注：Petaja T，Jarvi L，Kerminen V M，等. 中国气溶胶-边界层反馈增强的大气污染[J]. 科学报告，2016，6：18998.
[17] Ding A J, Huang X, Nie W, et al. Enhanced haze pollution by black carbon in megacities in China[J]. Geophysical Research Letters, 2016, 43: 2873-2879. DOI:10.1002/2016GL067745. 注：丁（Ding）A J，黄（Huang）X，聂（Nie）W，等. 中国大城市黑碳加剧灰霾污染[J]. 地球物理研究快报，2016，43：2873-2879.
[18] Tai A P K, Mickley L J, Jacob D J. Correlations between fine particulate matter (PM2.5) and meteorological variables in the United States: implications for the sensitivity of PM2.5 to climate change[J]. Atmospheric Environment, 2010, 44: 3976-3984. DOI:10.1016/j.atmosenv.2010.06.060. 注：Tai A P K，Mickley L J，Jacob D J. 美国PM2.5与气象变量的相关性：对PM2.5气候敏感性的启示[J]. 大气环境，2010，44：3976-3984.
[19] 长三角城市群PM2.5浓度未达标天数占比对风速变化的响应研究[J]. 长江流域资源与环境，2023，32(8). 注：结合风向地形分析长三角PM2.5输送特征.
[20] Ren J, Guo F, Xie S. Diagnosing ozone-NOx-VOC sensitivity and revealing causes of ozone increases in China based on 2013-2021 satellite retrievals[J]. Atmospheric Chemistry and Physics, 2022, 22: 15035-15047. DOI:10.5194/acp-22-15035-2022. 注：Ren J，Guo F，Xie S. 基于2013-2021年卫星反演诊断中国O3-NOx-VOCs敏感性[J]. 大气化学与物理，2022，22：15035-15047.
[21] Zhu S, Ma J, Wang S, et al. Shifts of Formation Regimes and Increases of Atmospheric Oxidation Led to Ozone Increase in North China Plain and Yangtze River Delta[J]. Journal of Geophysical Research: Atmospheres, 2023, 128: e2022JD038373. DOI:10.1029/2022JD038373. 注：Zhu S，Ma J，Wang S，等. 生成区制迁移与大气氧化性增强导致华北平原和长三角O3上升[J]. 地球物理研究杂志：大气，2023，128：e2022JD038373.
[22] Chen T, Chu B, Ma J, et al. Ozone Pollution in China: Current Status and Control Strategies[J]. Engineering, 2025. DOI:10.1016/j.eng.2025.06.044. 注：Chen T，Chu B，Ma J，等. 中国臭氧污染现状及控制策略[J]. 工程，2025.
[23] U.S. Environmental Protection Agency. Integrated Science Assessment (ISA) for Ozone and Related Photochemical Oxidants[R]. Washington, D.C.: U.S. EPA, 2020. 注：美国环境保护署. 臭氧及相关光化学氧化剂综合科学评估[R]. 华盛顿：美国环保署，2020.
[24] Wang T, Xue L, Brimblecombe P, et al. Ozone pollution in China: a review of concentrations, meteorological influences, chemical precursors, and effects[J]. Science of the Total Environment, 2017, 575: 1582-1596. DOI:10.1016/j.scitotenv.2016.10.081. 注：王（Wang）T，薛（Xue）L，Brimblecombe P，等. 中国臭氧污染综述[J]. 环境科学总论，2017，575：1582-1596.
[25] Liu Y, Wu Z, Wang Y, et al. Submicrometer particles are in the liquid state rather than glassy solid state in the urbanized atmosphere of the megacity Beijing[J]. Environmental Science & Technology Letters, 2017, 4(10): 427-432. DOI:10.1021/acs.estlett.7b00352. 注：刘（Liu）Y，吴（Wu）Z，王（Wang）Y，等. 北京大气亚微米颗粒处于液态而非玻璃态[J]. 环境科学与技术快报，2017，4(10)：427-432.
[26] Zhou W, Du H, Liu M, et al. Role of N2O5 heterogeneous hydrolysis in summer nitrate formation in Beijing[J]. npj Clean Air, 2025, 1: 40. DOI:10.1038/s44407-025-00039-0. 注：Zhou W，Du H，Liu M，等. N2O5非均相水解在北京夏季硝酸盐形成中的作用[J]. npj清洁空气，2025，1：40.
[27] Zhao Y, Li Y, Kumar A, et al. Separately resolving NOx and VOC contributions to ozone formation[J]. Atmospheric Environment, 2022, 285: 119224. DOI:10.1016/j.atmosenv.2022.119224. 注：Zhao Y，Li Y，Kumar A，等. 分别解析NOx和VOCs对臭氧生成的贡献[J]. 大气环境，2022，285：119224.
[28] Zhu C, Gai Y, Liu Z, et al. Long-term changes of surface ozone and ozone sensitivity over the North China Plain based on 2015-2021 satellite retrievals[J]. Air Quality, Atmosphere & Health, 2024, 17: 2753-2766. DOI:10.1007/s11869-024-01598-z. 注：Zhu C，Gai Y，Liu Z，等. 华北平原地表臭氧及敏感性长期变化[J]. 空气质量、大气与健康，2024，17：2753-2766.
[29] Lin Z, Ying C, Xu L, et al. Measurement report: High contribution of N2O5 uptake to particulate nitrate formation in NO2-limited urban areas[J]. Atmospheric Chemistry and Physics, 2025, 25: 17747-17759. DOI:10.5194/acp-25-17747-2025. 注：Lin Z，Ying C，Xu L，等. N2O5吸收对颗粒硝酸盐形成的高贡献[J]. 大气化学与物理，2025，25：17747-17759.
[30] Mayorga R J, Zhao Z, Zhang H. Formation of secondary organic aerosol from nitrate radical oxidation of phenolic VOCs[J]. Atmospheric Environment, 2021, 244: 117910. DOI:10.1016/j.atmosenv.2020.117910. 注：马约尔加（Mayorga）R J，赵（Zhao）Z，张（Zhang）H. 由硝酸根自由基氧化酚类VOCs生成二次有机气溶胶[J]. 大气环境，2021，244：117910.
[31] Wang Y, Zhang Q, Jiang J, et al. Enhanced sulfate formation during China's severe winter haze episode in January 2013 missing from current models[J]. Journal of Geophysical Research: Atmospheres, 2014, 119: 10425-10440. DOI:10.1002/2013JD021426. 注：王（Wang）Y，张（Zhang）Q，蒋（Jiang）J，等. 2013年1月中国严重冬季灰霾中被模型遗漏的增强硫酸盐生成[J]. 地球物理研究杂志：大气，2014，119：10425-10440.
[32] 国务院. 空气质量持续改善行动计划[EB/OL]. 北京：中国政府网，2023.
[33] 中华人民共和国生态环境部. 环境空气质量指数（AQI）技术规定：HJ 633-2026[S]. 北京，2026.
[34] Li R, Xu M, Li M, et al. Identifying the spatiotemporal variations in ozone formation regimes across China from 2005 to 2019[J]. Atmospheric Chemistry and Physics, 2021, 21: 15631-15646. DOI:10.5194/acp-21-15631-2021. 注：Li R，Xu M，Li M，等. 识别2005-2019年中国臭氧生成区制时空变化[J]. 大气化学与物理，2021，21：15631-15646.
[35] European Environment Agency. Ozone: Air quality status report 2025[R/OL]. Copenhagen: EEA, 2025. 注：欧洲环境署. 臭氧：2025年空气质量状况报告[R/OL]. 哥本哈根：欧洲环境署，2025.
[36] 浙江省发展改革委，浙江省生态环境厅. 浙江省空气质量改善"十四五"规划[EB/OL]. 杭州，2021.
[37] 上海市生态环境局. 长三角区域污染物总量协同控制实施方案[EB/OL]. 上海，2023.
[38] U.S. Environmental Protection Agency. Ground-level Ozone Basics[EB/OL]. Washington, D.C.: U.S. EPA, 2026. 注：美国环境保护署. 近地面臭氧基础知识[EB/OL]. 华盛顿：美国环保署，2026.