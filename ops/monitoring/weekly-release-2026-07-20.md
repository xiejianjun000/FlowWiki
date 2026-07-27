# FlowWiki 每周发布报告

**版本：v0.4.0**  
**日期：2026-07-20（周一）**  
**发布人：小谢总（Claw）**

---

## 测试结果

| 阶段 | 状态 | 详情 |
|------|------|------|
| Phase 1: 脚本编译 | ✅ | 13/13 通过 |
| Phase 2: CI Lint | ✅ | 13 页 wiki 零告警 |
| Phase 3: 5 知识库 | ✅ | 5/5 行业全部通过 |
| Phase 4: Hermes 验证 | ✅ | LLM 模式 |
| Phase 5: Docker 构建 | ⚠️ | 非阻塞失败（Docker 不可用） |
| Phase 6: 关系图质量 | ⚠️ | 16 节点 / 7 边 / 75% 孤立（需后续优化） |

**结论：核心测试全部通过，批准发布。**

---

## 本周变更摘要（2026-07-13 ~ 2026-07-20）

### 新增功能（8 项）

1. **执法督察评查知识库全栈升级** — 155 篇文档的 enforcement-review 参考实现完全落地
   - 109 节点 479 边关系图谱，85%+ 可路由率
   - 6 页 00_首页/运营看板，7 行业适配器数据同步
2. **ACE 原文指针铁律** — 强制指针+按需展开替代全文入库
3. **4 项方法论迭代** — status 修复 / strict 模式 / 引用追踪 / 知识缺口检测
4. **Lint 增强** — 新增 4 项检查 + index 自动同步
5. **raw 入仓时间戳** — 文件采集自动记录 + 每日采集记录
6. **Playbook 模板增强** — coverage 报告新增类型建议
7. **行业路由完整性** — 7 行业适配器路由验证 + 限值表标准化

### 修复（2 项）

8. 修复入仓时间戳重复 `updated` 字段
9. 刷新 00_首页/6 页 enforcement-review 运营数据

### 工程变更（1 项）

10. 仓库治理：彻底移除知识库内容 + `.gitignore` 路径防护

---

## 版本演进

```
v0.1.0 (2026-07-17) → v0.2.0 (2026-07-18) → v0.3.0 (2026-07-20)
   7层架构首发          MCP Server+Docker        竞品研究驱动迭代
                                                    ↓
                                              v0.4.0 (2026-07-20)
                                              执法评查全栈落地
```

---

## 下周计划

根据 article-plan.yaml 进度：

| 文章 | 标题 | 状态 |
|------|------|------|
| Article-02 | ACE 反思循环深度拆解 | ready_for_review |
| Article-03 | A-MEM 卡片记忆系统 | draft |
| Article-04 | 任务→知识→Skill 三元组 | draft |

**优先事项：**
1. Article-02 审核发布（当前 ready_for_review）
2. 关系图质量优化（当前 75% 孤立率需降至 60% 以下）
3. Docker 构建修复（确保 CI 环境可用）
4. Article-03 完成初稿

---

## 发布产物

- CHANGELOG: `CHANGELOG.md#040---2026-07-20`
- Git Tag: `v0.4.0`
- GitHub Release: https://github.com/xiejianjun000/FlowWiki/releases/tag/v0.4.0
- 测试报告: `ops/monitoring/daily-test-2026-07-20.md`
- 本报告: `ops/monitoring/weekly-release-2026-07-20.md`
