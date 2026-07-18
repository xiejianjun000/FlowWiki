# episodic/ — 跨会话记忆

每次 query 后，将高质量问答回存至此，供后续会话参考。

## 格式

```markdown
# EP-YYYY-MM-DD-NNN

## 问题
<用户原始问题>

## 答案
<AI 整合答案>

## 引用
- [[wiki/concepts/xxx]]
- [[wiki/playbooks/yyy]]

## 复利价值
- 是否值得提取为 playbook？是 / 否
- 是否值得抽象为 skill？是 / 否
```
