---
id: ZK-2026-07-17-example
date: 2026-07-17
tags: ['flow-wiki', 'root-cause', 'anomaly-detection', 'example']
source: raw/root-cause/sample-incident-report.md
related: ['ZK-2026-07-17-001']
confidence: high
---

# 异常检测方法的实际应用：支付网关延迟异常

> 从支付网关 P99 延迟异常案例中提炼的异常检测方法论要点

## 关键论点

- 百分位指标（P99/P95）比平均值更敏感，能更早发现尾部延迟恶化。平均值可能因少数低延迟请求而保持正常，掩盖真实问题
- 多层监控体系（指标 + 日志 + 链路追踪）交叉验证能大幅缩短 MTTR（Mean Time to Repair）：本案例中 Jaeger 追踪锁定了数据库连接池瓶颈
- 配置变更是高频根因来源：异常时间窗口（14:10-14:23）与变更时间高度吻合，验证了"变更倒查"作为根因分析入口的有效性
- 动态阈值优于静态阈值：如果基线 P99 为 200ms，静态阈值 500ms 以下可能漏报，而基于 3 倍标准差的动态阈值更精准

## 异常检测方法在本案例中的适用性评估

| 方法 | 适用性 | 原因 |
|------|--------|------|
| 3-Sigma 法则 | 高 | P99 延迟从 200ms 升至 2800ms，远超 3 倍标准差 |
| Isolation Forest | 中 | 适合多维指标异常检测，但单指标场景过于复杂 |
| 规则引擎 | 高 | 可定义"P99 > 500ms 且持续 3 分钟"的复合规则 |
| 动态阈值 | 最优 | 基于历史同期的统计特征动态调整阈值，减少误报 |

## 关联知识

- [[wiki/concepts/异常检测方法]]
- [[wiki/playbooks/根因分析五步法]]
- [[wiki/playbooks/局部分析工作流]]
- [[wiki/comparisons/定量分析-vs-定性分析]]

## 关联卡片


## 原始证据

- [[raw/root-cause/sample-incident-report.md]]
- [[raw/root-cause/sample-audit-log.md]]

## 入库信息

- 入库时间：2026-07-17T18:00:00.000000
- confidence: high
- ACE 状态：待审查
