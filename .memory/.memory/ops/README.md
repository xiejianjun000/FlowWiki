# ops/ — 操作日志（结构化）

与 wiki/log.md 互补。wiki/log.md 是人类可读的追加式文本，ops/ 是 LLM 可解析的 JSONL 格式。

## 格式

每行一个 JSON 对象：

```json
{"time": "2026-07-18T10:00:00+08:00", "op": "ingest", "object": "25项一票否决清单", "result": "success", "actor": "ai", "ref": ["wiki/playbooks/25项一票否决清单"]}
```

## 字段

- `time`: ISO 8601
- `op`: ingest | query | lint | research | sync | restructure | init
- `object`: 操作对象描述
- `result`: success | warning | failure
- `actor`: ai | human
- `ref`: 引用的文件路径
