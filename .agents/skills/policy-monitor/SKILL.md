# Policy Monitor Skill — 政策监控

## 功能

监控生态环境领域法规、标准、政策的更新动态，评估对企业合规状态的影响。

## 输入

```json
{
  "monitor_scope": {
    "industries": ["关注行业"],
    "regions": ["关注区域"],
    "topics": ["关注主题"]
  },
  "last_check": "上次检查时间",
  "enterprise_profile": "企业概况"
}
```

## 输出

```json
{
  "status": "success",
  "updates": [
    {
      "type": "法律|法规|标准|政策|通知",
      "title": "文件标题",
      "issuing_authority": "发布机关",
      "publish_date": "发布日期",
      "effective_date": "生效日期",
      "key_changes": ["主要变化"],
      "impact_level": "高|中|低",
      "action_required": "需要采取的行动"
    }
  ],
  "summary": "政策动态汇总"
}
```

## 监控范围

1. **法律法规**：新颁布、修订、废止
2. **标准规范**：排放标准、质量标准、技术规范
3. **政策文件**：部委通知、地方政策、行业指引
4. **典型案例**：指导性案例、典型案例发布
5. **裁量基准**：行政处罚裁量基准更新

## 约束

- 监控结果必须标注来源和发布机关
- 影响评估必须结合企业实际
- 区分"已生效"和"尚未生效"
- 不传播未经官方确认的信息
