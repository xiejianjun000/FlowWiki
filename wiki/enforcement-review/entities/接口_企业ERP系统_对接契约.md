---
type: entity
title: 接口_企业ERP系统_对接契约
created: '2026-07-19'
updated: '2026-07-19'
confidence: low
sources:
- raw/permit_system/排污许可/
tags:
- entity
- data_contract
- ERP
- flow-wiki
status: reviewed
aliases:
- 接口_企业ERP系统_对接契约
ace_review:
  generator: '2026-07-19'
  reflector: '2026-07-19'
  curator: '2026-07-19'
---
# 接口_企业ERP系统_对接契约

> 数据中台接口契约

## 接口描述

本接口用于数据中台与企业ERP系统之间的数据对接，实现生产计划、物料消耗、产能产量等生产经营数据的自动采集，为环境合规分析提供企业生产运营基础数据支撑。

## 对接系统

企业ERP系统

## 关联资源

- [[排污许可制]]
## 数据字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| production_info | JSON | 生产信息（产品名称、产量、工艺路线、原辅料消耗） |
| energy_consumption | JSON | 能源消耗数据（用电量、用煤量、用水量） |
| material_balance | JSON | 物料平衡数据（原辅料投入-产品产出-废料产出） |
| facility_info | Array | 设施信息（生产设施清单、运行状态、设计产能） |

## 接口规范

- 协议：HTTPS RESTful API / Webhook
- 认证方式：OAuth 2.0
- 数据格式：JSON
- 调用频率：每日批量同步


## 关联页面
- [[concepts/环境影响评价]]
- [[concepts/排污许可制]]