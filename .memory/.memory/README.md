# .memory/ — FlowWiki Agent 记忆层（L4）

本库的跨会话记忆系统，基于 A-MEM（Zettelkasten）卡片 + ACE 反思循环 + 知识缺口追踪。

## 子目录

| 目录 | 用途 | 文件格式 |
|------|------|---------|
| `zettelkasten/` | A-MEM ZK 卡片，每次 ingest 生成 | `ZK-YYYY-MM-DD-NNN.md` |
| `episodic/` | 跨会话问答记录，每次 query 回存 | `EP-YYYY-MM-DD-NNN.md` |
| `conflict/` | 新旧知识矛盾追踪 | `<topic>.md` |
| `ace/` | ACE 反思循环记录 | `ace-YYYY-MM-DD-NNN.md` |
| `gaps/` | 知识缺口卡片 | `gap-YYYY-MM-DD-NNN.md` |
| `ops/` | 结构化操作日志 | `YYYY-MM-DD.jsonl` |

## 维护规则

- LLM 自动维护，人类仅 review conflict/ 和间隙提升为 skill 的审批
- ZK 卡片超过 30 天后由 LLM 自动蒸馏到 wiki/meta/
- 每次 query 后判断是否值得回存到 episodic/
