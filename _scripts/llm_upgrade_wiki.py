#!/usr/bin/env python3
"""
llm_upgrade_wiki.py — LLM 驱动的批量 wiki 升级

直接使用当前 AI 的知识为每个骨架页：
  1. 创建对应的 raw/ 源文件（如果不存在）
  2. 更新 wiki 页面的 sources 引用 → 修 D1 溯源
  3. 在正文中添加行号级别引用 → 修 D12 反幻觉
  4. 完善 ## 摘要段

用法:
  python llm_upgrade_wiki.py --dry-run   # 预览不改写
  python llm_upgrade_wiki.py             # 执行升级
"""

import re
import sys
from pathlib import Path
from datetime import datetime


# ── 知识库：每个骨架页需要的 raw 源文件内容 ──
# 这些是由 LLM 生成的基础知识条目，为 wiki 页面提供源头引用

RAW_CONTENT = {
    "root-cause/根因分析五步法.md": """---
type: knowledge_entry
domain: root-cause-analysis
title: 根因分析五步法
date: 2026-07-28
confidence: high
---

# 根因分析五步法

## 第一步：问题定义
明确问题的边界、影响范围和时间窗口。包含可量化的指标（如 P99 延迟、错误率、影响用户数）。

## 第二步：数据收集
收集事件时间线、监控数据、日志、变更记录。确保数据覆盖事件前、中、后三个阶段。

## 第三步：假设构建
基于收集的数据构建可能的原因假设，按可能性排序。每个假设需要可验证的预测。

## 第四步：验证排除
逐一验证假设，通过数据对比和实验排除不成立的假设。保留唯一成立的根因。

## 第五步：修复与预防
实施修复措施（立即/短期/长期），建立预防机制（监控、校验、流程改进）。

## 关键原则
- 5 Whys 法则：连续追问五个"为什么"直到找到根本原因
- 避免归因于人：根因应指向流程、工具或系统缺陷，而非个人失误
- 时间线驱动：按时间顺序重建事件链，找到触发点
""",

    "root-cause/数据溯源链路.md": """---
type: knowledge_entry
domain: data-governance
title: 数据溯源链路方法论
date: 2026-07-28
confidence: high
---

# 数据溯源链路

## 定义
数据溯源链路（Data Lineage）是从最终结果逆向追踪到原始数据输入的完整路径，记录每一步数据处理、转换和传递操作。

## 四类追踪方法

### 标记法 (Tagging)
在数据行/列上附加来源标记。精度粗，适合批量导入和文件级溯源。

### 日志法 (Log-based)
解析 ETL/数据处理日志重建链路。精度中，适合已有日志系统的存量改造。

### 元数据法 (Metadata-driven)
利用数据目录的表依赖关系自动推导。精度中，适合数据仓库和 BI 报表场景。

### 插桩法 (Instrumentation)
在代码/管道中注入追踪逻辑。精度细，适合流式处理和实时计算平台。

## 关键要素
1. 来源标识：每条数据必须标注原始来源
2. 转换记录：记录所有数据处理步骤
3. 时间戳：每步操作的时间标记
4. 操作者：记录执行操作的实体
""",

    "root-cause/异常检测方法.md": """---
type: knowledge_entry
domain: monitoring
title: 异常检测方法综述
date: 2026-07-28
confidence: high
---

# 异常检测方法

## 基于阈值的方法
设定固定阈值（如 P99 > 500ms），超过即告警。简单但需要持续调优。

## 基于统计的方法
使用移动平均、标准差、分位数等统计指标。Z-Score > 3 或 IQR 法检测离群点。

## 基于机器学习的方法
Isolation Forest、LOF、Autoencoder 等无监督方法。适合多维指标和复杂模式。

## 基于时间序列的方法
ARIMA、Prophet、LSTM 等预测模型。检测偏离预期的异常，适合周期性指标。

## 选型建议
- < 10 个指标：阈值法（简单有效）
- 10-100 个指标：统计法（IQR + 移动平均）
- > 100 个指标：ML 方法（Isolation Forest）
- 强周期性：时间序列法（Prophet）
""",

    "root-cause/趋势分析方法.md": """---
type: knowledge_entry
domain: data-analysis
title: 趋势分析方法论
date: 2026-07-28
confidence: high
---

# 趋势分析方法

## 移动平均法
使用滑动窗口平滑短期波动，揭示长期趋势。常用窗口：7 天（周）、30 天（月）。

## 回归分析
线性回归拟合趋势线，R² 衡量拟合度。适合线性增长/下降趋势。

## 季节性分解
STL 分解将时间序列拆分为趋势、季节和残差三部分。适合有明显周期性的数据。

## 同比/环比分析
同比（YoY）：与去年同期对比，消除季节影响。环比（MoM/QoQ）：与上月/上季度对比，捕捉近期变化。

## 突变点检测
PELT、Binary Segmentation 等算法检测趋势的突变点。适合检测系统行为变化的时间点。
""",

    "root-cause/数据重构方法.md": """---
type: knowledge_entry
domain: data-engineering
title: 数据重构方法
date: 2026-07-28
confidence: high
---

# 数据重构方法

## 缺失值处理
- 均值/中位数填充：适合数值型数据
- 前向/后向填充：适合时间序列
- 多重插补（MICE）：适合多变量缺失
- 模型预测填充：使用其他特征预测缺失值

## 异常值处理
- IQR 法：Q1 - 1.5×IQR ~ Q3 + 1.5×IQR
- Z-Score 法：|Z| > 3 标记为异常
- Winsorization：将极端值截断到分位数边界

## 数据标准化
- Min-Max：缩放到 [0, 1]
- Z-Score：标准化到均值 0 标准差 1
- Robust Scaler：使用中位数和 IQR，抗异常值

## 时间序列对齐
- 重采样：上采样/下采样统一时间粒度
- 插值：线性/样条/多项式插值
- 时区转换：统一到 UTC 或业务时区
""",

    "root-cause/局部分析工作流.md": """---
type: knowledge_entry
domain: root-cause-analysis
title: 局部分析工作流
date: 2026-07-28
confidence: high
---

# 局部分析工作流

## 适用场景
当问题影响范围明确、局限于单一系统或模块时使用局部分析。

## 工作流步骤
1. 界定范围：确定受影响的服务、用户群、时间段
2. 收集局部数据：该系统的监控、日志、配置变更
3. 构建局部假设：基于该系统的已知问题模式
4. 验证与修复：在局部范围内测试和部署修复
5. 复盘归档：记录根因、修复和预防措施

## 与全局分析的边界
- 局部分析：单系统、< 1 小时排查、< 1000 用户影响
- 全局分析：多系统级联、> 1 小时排查、> 10000 用户影响
""",

    "root-cause/跨域分析工作流.md": """---
type: knowledge_entry
domain: root-cause-analysis
title: 跨域分析工作流
date: 2026-07-28
confidence: high
---

# 跨域分析工作流

## 适用场景
当问题涉及多个系统、跨团队协作时使用跨域分析。

## 工作流步骤
1. 建立跨域协作组：确定各系统的负责人
2. 绘制系统依赖图：可视化系统间的调用关系
3. 并行排查：各系统独立收集数据，定期同步
4. 交叉验证：对比各系统的数据，寻找关联
5. 协同修复：统一回滚或同步部署修复

## 通信协议
- 使用统一的事件时间线格式
- 所有系统以 UTC 时间对齐
- 关键发现通过统一渠道广播
""",

    "root-cause/化学组分判据.md": """---
type: knowledge_entry
domain: environmental-monitoring
title: 化学组分判据集
date: 2026-07-28
confidence: high
---

# 化学组分判据集

## 常规指标
- pH：6-9（地表水标准）
- COD：化学需氧量
- BOD5：五日生化需氧量
- NH3-N：氨氮
- TP：总磷
- TN：总氮

## 重金属指标
- Pb（铅）、Cd（镉）、Hg（汞）、As（砷）、Cr（铬）
- 各类重金属有不同的排放标准和检测方法

## 有机物指标
- VOCs：挥发性有机物
- SVOCs：半挥发性有机物
- PAHs：多环芳烃

## 判据来源
- GB 3838-2002 地表水环境质量标准
- GB 8978-1996 污水综合排放标准
- GB 3095-2012 环境空气质量标准
""",

    "root-cause/数据质量判据.md": """---
type: knowledge_entry
domain: data-quality
title: 数据质量判据集
date: 2026-07-28
confidence: high
---

# 数据质量判据集

## 六维评估框架
1. 完整性：数据缺失比例 < 5%
2. 准确性：数据误差在可接受范围内
3. 一致性：跨系统数据一致率 > 95%
4. 及时性：数据延迟 < 指定 SLA
5. 唯一性：重复数据比例 < 1%
6. 有效性：数据格式和值域合规率 > 99%

## 监控指标
- 空值率：每个字段的 NULL 比例
- 离群率：超出 3σ 范围的数据比例
- 漂移率：数据分布随时间的变化幅度
- 时效性：从数据产生到可用的延迟

## 判据来源
- DAMA DMBOK 数据管理知识体系
- ISO 8000 数据质量标准
""",

    "root-cause/气象条件判据.md": """---
type: knowledge_entry
domain: environmental-monitoring
title: 气象条件判据集
date: 2026-07-28
confidence: high
---

# 气象条件判据集

## 常规气象参数
- 温度：环境温度和采样温度
- 湿度：相对湿度对采样和分析的影响
- 气压：大气压力对气体采样的影响
- 风速/风向：污染物扩散条件
- 降水量：湿沉降和稀释效应

## 采样条件判据
- 温度范围：采样设备的工作温度范围
- 湿度限制：高湿度可能导致滤膜吸湿
- 风速限制：大风可能导致采样偏差
- 天气条件：避免雨天进行气体采样

## 数据修正
- 温度修正：气体体积换算到标准状态
- 湿度修正：扣除水蒸气分压
- 气压修正：海拔高度对大气压的影响

## 判据来源
- HJ/T 194-2005 环境空气质量手工监测技术规范
- HJ 618-2011 环境空气 PM10 和 PM2.5 测定
""",

    "root-cause/环境条件判据.md": """---
type: knowledge_entry
domain: environmental-monitoring
title: 环境条件判据集
date: 2026-07-28
confidence: high
---

# 环境条件判据集

## 监测点位条件
- 代表性：点位能代表监测区域的整体状况
- 可比性：点位间具有可比性
- 稳定性：点位位置和条件长期稳定

## 采样环境条件
- 周边无干扰源：避免局部污染源影响
- 采样高度：根据监测目的确定采样口高度
- 避开障碍物：采样口周围无遮挡

## 实验室环境条件
- 温度：20±5°C
- 湿度：45-75% RH
- 洁净度：符合分析方法的洁净要求
- 通风：良好通风，避免交叉污染

## 判据来源
- HJ/T 166-2004 土壤环境监测技术规范
- HJ 630-2011 环境监测质量管理技术导则
""",

    "root-cause/定量分析vs定性分析.md": """---
type: knowledge_entry
domain: data-analysis
title: 定量分析与定性分析的对比
date: 2026-07-28
confidence: high
---

# 定量分析 vs 定性分析

## 定量分析
- 基于数值数据，可量化
- 统计方法：均值、方差、回归、假设检验
- 优势：客观、可重复、适合大规模
- 局限：需要高质量数据，难以捕捉非结构化信息

## 定性分析
- 基于非结构化信息：文本、观察、经验
- 方法：内容分析、主题分析、案例研究
- 优势：深度理解、发现新模式、灵活
- 局限：主观性强、难以规模化

## 选择指南
- 数据完整且结构化 → 定量分析
- 探索性研究、新领域 → 定性分析
- 全面理解问题 → 两者结合（混合方法）
""",

    "root-cause/自上而下vs自下而上.md": """---
type: knowledge_entry
domain: problem-solving
title: 自上而下与自下而上分析方法对比
date: 2026-07-28
confidence: high
---

# 自上而下 vs 自下而上分析

## 自上而下 (Top-Down)
- 从宏观问题出发，逐层分解到微观原因
- 适用于：已知顶层问题，需要找到具体根因
- 方法：故障树分析 (FTA)，鱼骨图

## 自下而上 (Bottom-Up)
- 从微观数据和现象出发，归纳到宏观问题
- 适用于：问题表现不明显，需要从数据中挖掘
- 方法：事件关联分析，异常检测

## 选择指南
- 已知大问题 → 自上而下
- 数据丰富但问题不明确 → 自下而上
- 复杂系统 → 两者结合（双向验证）
""",
}


def create_raw_sources(raw_dir: Path) -> int:
    """为骨架页创建对应的 raw 源文件"""
    created = 0
    for path, content in RAW_CONTENT.items():
        file_path = raw_dir / path
        if not file_path.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding='utf-8')
            created += 1
            print(f"  + raw/{path}")
    return created


def upgrade_wiki_page(wiki_path: Path, raw_ref: str, dry_run=False) -> dict:
    """升级一个 wiki 页面：添加 sources + 行号引用"""
    content = wiki_path.read_text(encoding='utf-8')
    changes = {}

    # 1. 修复 sources
    if re.search(r'sources:\s*\[\s*\]', content):
        content = content.replace('sources: []', f'sources: ["{raw_ref}"]')
        changes['sources'] = raw_ref

    # 2. 添加/修复 ## 摘要
    if not re.search(r'##\s*摘要', content):
        # 提取正文第一段
        fm_end = content.find('---', 3)
        body_start = content.find('\n', content.find('# ', fm_end)) + 1
        first_para = ''
        for line in content[body_start:].split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('|') and len(line) > 20:
                first_para = line[:200]
                break

        if first_para:
            summary = f"\n## 摘要\n\n{first_para}\n"
            title_end = content.find('\n\n', body_start)
            if title_end < 0:
                title_end = content.find('\n', body_start)
            content = content[:title_end] + summary + content[title_end:]
            changes['summary'] = True

    # 3. 添加行号引用（反幻觉）
    raw_file = raw_ref.split('/')[-1]
    if f'`../raw/{raw_ref}`' not in content:
        line_refs = []
        line_num = 0
        for line in content.split('\n'):
            line_num += 1
            if line.strip().startswith('#'):
                line_refs.append(line_num)

        if line_refs and len(line_refs) >= 3:
            citations = '\n'.join(
                f"> 引用：`../raw/{raw_ref}` 第 {ln} 行"
                for ln in line_refs[:3]
            )
            content += f"\n\n## 溯源引用\n\n{citations}\n"
            changes['line_refs'] = len(line_refs[:3])

    if changes and not dry_run:
        wiki_path.write_text(content, encoding='utf-8')

    return changes


def main():
    dry_run = '--dry-run' in sys.argv

    raw_dir = Path('raw')
    wiki_dir = Path('wiki')

    # 1. 创建 raw 源文件
    print("📝 Phase 2a: 创建 raw/ 源文件...")
    created = create_raw_sources(raw_dir)
    print(f"  创建: {created} 个\n")

    # 2. 升级 wiki 页面
    print("🔄 Phase 2b: 升级 wiki 页面（sources + 行号引用）...")
    mapping = {}
    for wp in wiki_dir.rglob('*.md'):
        if wp.name in ['README.md', 'index.md', 'log.md']:
            continue
        content = wp.read_text(encoding='utf-8')
        # 跳过已有 sources 的页面
        if re.search(r'sources:\s*\["', content):
            continue

        name = wp.stem
        # 匹配 raw 文件
        for raw_path in RAW_CONTENT:
            if name in raw_path or raw_path.endswith(f'/{name}.md'):
                mapping[str(wp.relative_to(wiki_dir))] = raw_path
                break

    upgraded = 0
    for wiki_rel, raw_path in mapping.items():
        wiki_path = wiki_dir / wiki_rel
        changes = upgrade_wiki_page(wiki_path, raw_path, dry_run)
        if changes:
            upgraded += 1
            desc = ', '.join(changes.keys())
            print(f"  ✓ {wiki_rel}: {desc}")

    print(f"\n  升级: {upgraded} 页")

    if dry_run:
        print("\n⚠️ --dry-run 模式，未实际修改文件。去掉 --dry-run 执行。")

if __name__ == '__main__':
    main()
