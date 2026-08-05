---
type: entity
title: 接口_企业LIMS系统_对接契约
created: '2026-07-19'
updated: '2026-07-19'
confidence: low
sources:
- raw/permit_system/排污许可/
tags:
- entity
- data_contract
- LIMS
- flow-wiki
status: reviewed
aliases:
- 接口_企业LIMS系统_对接契约
ace_review:
  generator: '2026-07-19'
  reflector: '2026-07-19'
  curator: '2026-07-19'
---
# 接口_企业LIMS系统_对接契约

> 数据中台接口契约

## 接口描述

本接口用于数据中台与企业LIMS（实验室信息管理系统）之间的数据对接，实现废水、废气、土壤等环境监测分析结果的自动采集与归档，支撑排放达标判定和自行监测数据管理。

## 对接系统

企业LIMS系统（实验室信息管理系统）

## 关联资源

- [[排污许可制]]
## 数据字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| lab_results | JSON | 实验室检测结果（样品编号、检测项目、检测结果、判定结论） |
| sample_info | Array | 样品信息（采样时间、采样点位、样品类型、保存条件） |
| instrument_status | Array | 仪器设备状态（设备名称、校准状态、维护计划） |
| qa_qc_records | Array | 质控记录（平行样偏差、加标回收率、空白值） |

## 接口规范

- 协议：HTTPS RESTful API
- 认证方式：OAuth 2.0
- 数据格式：JSON
- 调用频率：实时推送 + 每日增量同步


## 关联页面
- [[concepts/环境影响评价]]
- [[concepts/排污许可制]]