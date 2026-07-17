# Ingest Skill — 入仓操作

## 功能

将原始资料入仓到 raw/，并触发 ingest pipeline 编译到 wiki/。

## 输入

```json
{
  "source_type": "law|standard|report|dataset",
  "content": "原始内容",
  "metadata": {
    "title": "文件标题",
    "source": "来源",
    "date": "日期",
    "version": "版本"
  }
}
```

## 输出

```json
{
  "status": "success|failed",
  "message": "操作结果",
  "file_path": "raw/目录/文件名.md",
  "wiki_pages": ["生成的 wiki 页面列表"]
}
```

## 执行流程

1. 验证输入参数
2. 写入 raw/ 目录
3. 更新 raw/README.md 索引
4. 触发 ingest_pipeline.py 编译
5. 返回结果

## 约束

- 内容必须是原始证据，未经 AI 修改
- 文件命名遵循规范
- 必须包含元数据