# Pattern Recognition Skill

> 模式识别 — 从数据特征中识别已知模式

## 功能

通过数据特征比对，识别数据中的已知模式或分类。

## 输入

```json
{
  "data": "待识别数据",
  "features": {"key": "value"},
  "known_patterns": ["已知模式列表（可选）"]
}
```

## 输出

```json
{
  "matched_patterns": [
    {
      "pattern": "模式名称",
      "confidence": 0.85,
      "evidence": "匹配证据"
    }
  ],
  "unmatched_features": ["未匹配的特征"]
}
```

## 约束

- 需要足够的已知模式库
- 置信度低于 0.6 时标注"待确认"
- 多模式匹配时按置信度排序
