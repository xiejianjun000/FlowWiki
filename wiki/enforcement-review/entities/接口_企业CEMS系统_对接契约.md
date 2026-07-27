---
type: entity
title: 接口_企业CEMS系统_对接契约
created: '2026-07-19'
updated: '2026-07-19'
confidence: low
sources:
- raw/permit_system/排污许可/
tags:
- entity
- data_contract
- CEMS
- flow-wiki
status: reviewed
aliases:
- 接口_企业CEMS系统_对接契约
ace_review:
  generator: '2026-07-19'
  reflector: '2026-07-19'
  curator: '2026-07-19'
---
# 接口_企业CEMS系统_对接契约

> 数据中台接口契约

## 接口描述

本接口用于数据中台与企业CEMS（烟气排放连续监测系统）之间的数据对接，实现废气排放浓度、流量等实时监测数据的自动采集与入库，支撑污染物排放达标分析和预警提醒。

## 对接系统

企业CEMS系统（烟气排放连续监测系统）

## 关联资源

- [[排污许可制]]
## 数据字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| emission_realtime | JSON | 废气排放实时监测数据（浓度、流量、折算值） |
| alarm_records | Array | 超标报警记录（报警时间、污染物、超标倍数） |
| device_status | Object | CEMS设备运行状态（在线/离线/维护） |
| calibration_logs | Array | 标定记录（标定时间、标定结果、有效期） |

## 接口规范

- 协议：MQTT 实时推送 + HTTPS RESTful API 查询
- 认证方式：双向TLS证书认证
- 数据格式：JSON
- 调用频率：实时推送（秒级）


## 关联页面
- [[concepts/环境影响评价]]
- [[concepts/排污许可制]]