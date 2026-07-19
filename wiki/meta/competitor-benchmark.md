---
type: benchmark
title: 竞品对标分析报告
created: 2026-07-19
updated: 2026-07-19
tags: ["flow-wiki", "benchmark", "competitor"]
status: active
---

# 竞品对标分析报告

> 生成时间: 2026-07-19T10:22:46.019223
> 对标竞品数: 12

## 一、竞品总览

| 项目 | Star | Fork | 创建时间 | 语言 | 防幻觉 | 记忆 | 多 agent | UX | 可插拔 | 变更追溯 | 复利 Skill | 自适应检索 | 矛盾追踪 |
|------|------|------|---------|------|--------|------|---------|-----|--------|---------|-----------|----------|---------|
| [nashsu/llm_wiki](https://github.com/nashsu/llm_wiki) | 14,852 | 1,762 | 2026-04-08 | TypeScript | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| [AgriciDaniel/claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian) | 9,588 | 1,122 | 2026-04-07 | Python | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| [SamurAIGPT/llm-wiki-agent](https://github.com/SamurAIGPT/llm-wiki-agent) | 3,229 | 374 | 2023-04-21 | Python | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| [inkeep/open-knowledge](https://github.com/inkeep/open-knowledge) | 3,004 | 191 | 2026-06-03 | TypeScript | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ |
| [Ar9av/obsidian-wiki](https://github.com/Ar9av/obsidian-wiki) | 2,919 | 295 | 2026-04-06 | Python | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ❌ | ✅ |
| [sdyckjq-lab/llm-wiki-skill](https://github.com/sdyckjq-lab/llm-wiki-skill) | 2,183 | 266 | 2026-04-05 | TypeScript | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ |
| [atomicstrata/llm-wiki-compiler](https://github.com/atomicstrata/llm-wiki-compiler) | 1,789 | 170 | 2026-04-05 | TypeScript | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| [skyllwt/AutoSci](https://github.com/skyllwt/AutoSci) | 1,551 | 205 | 2026-04-09 | Python | ✅ | ❌ | ✅ | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ |
| [Astro-Han/karpathy-llm-wiki](https://github.com/Astro-Han/karpathy-llm-wiki) | 1,546 | 179 | 2026-04-05 | None | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ |
| [lucasastorian/llmwiki](https://github.com/lucasastorian/llmwiki) | 1,385 | 212 | 2026-04-04 | Python | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ |
| [kytmanov/obsidian-llm-wiki-local](https://github.com/kytmanov/obsidian-llm-wiki-local) | 778 | 123 | 2026-04-07 | Python | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ |
| [swarmclawai/swarmvault](https://github.com/swarmclawai/swarmvault) | 616 | 77 | 2026-04-06 | TypeScript | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

## 二、九维度对比矩阵

### 防幻觉机制

- **FlowWiki 水平**: ACE Generator→Reflector→Curator 三 agent 制约

| 竞品 | 能力等级 | 信号强度 |
|------|---------|---------|
| nashsu/llm_wiki | ace | 1 |
| AgriciDaniel/claude-obsidian | ace | 1 |
| SamurAIGPT/llm-wiki-agent | ace | 1 |
| inkeep/open-knowledge | none | 0 |
| Ar9av/obsidian-wiki | conflict_mark | 2 |
| sdyckjq-lab/llm-wiki-skill | conflict_mark | 1 |
| atomicstrata/llm-wiki-compiler | ace | 2 |
| skyllwt/AutoSci | ace | 1 |
| Astro-Han/karpathy-llm-wiki | conflict_mark | 1 |
| lucasastorian/llmwiki | ace | 1 |
| kytmanov/obsidian-llm-wiki-local | ace | 1 |
| swarmclawai/swarmvault | conflict_mark | 2 |

### 跨会话记忆

- **FlowWiki 水平**: A-MEM Zettelkasten 卡片，零数据库依赖

| 竞品 | 能力等级 | 信号强度 |
|------|---------|---------|
| nashsu/llm_wiki | vector_db | 2 |
| AgriciDaniel/claude-obsidian | hot_cache | 2 |
| SamurAIGPT/llm-wiki-agent | hot_cache | 1 |
| inkeep/open-knowledge | none | 0 |
| Ar9av/obsidian-wiki | hot_cache | 2 |
| sdyckjq-lab/llm-wiki-skill | hot_cache | 2 |
| atomicstrata/llm-wiki-compiler | vector_db | 2 |
| skyllwt/AutoSci | none | 0 |
| Astro-Han/karpathy-llm-wiki | vector_db | 1 |
| lucasastorian/llmwiki | hot_cache | 1 |
| kytmanov/obsidian-llm-wiki-local | vector_db | 2 |
| swarmclawai/swarmvault | vector_db | 1 |

### 多 agent 兼容

- **FlowWiki 水平**: Claude Code / Codex / Gemini / Amp / WorkBuddy 五家

| 竞品 | 能力等级 | 信号强度 |
|------|---------|---------|
| nashsu/llm_wiki | claude_only | 1 |
| AgriciDaniel/claude-obsidian | multi_platform | 1 |
| SamurAIGPT/llm-wiki-agent | claude_only | 1 |
| inkeep/open-knowledge | claude_only | 1 |
| Ar9av/obsidian-wiki | multi_platform | 1 |
| sdyckjq-lab/llm-wiki-skill | multi_platform | 1 |
| atomicstrata/llm-wiki-compiler | claude_only | 1 |
| skyllwt/AutoSci | claude_only | 1 |
| Astro-Han/karpathy-llm-wiki | claude_only | 1 |
| lucasastorian/llmwiki | claude_only | 1 |
| kytmanov/obsidian-llm-wiki-local | multi_platform | 1 |
| swarmclawai/swarmvault | claude_only | 1 |

### 人类 UX

- **FlowWiki 水平**: 双索引（机器 index + 人类 6 板块 MOC）

| 竞品 | 能力等级 | 信号强度 |
|------|---------|---------|
| nashsu/llm_wiki | gui | 2 |
| AgriciDaniel/claude-obsidian | obsidian_native | 3 |
| SamurAIGPT/llm-wiki-agent | obsidian_native | 3 |
| inkeep/open-knowledge | gui | 2 |
| Ar9av/obsidian-wiki | gui | 2 |
| sdyckjq-lab/llm-wiki-skill | gui | 1 |
| atomicstrata/llm-wiki-compiler | gui | 1 |
| skyllwt/AutoSci | gui | 1 |
| Astro-Han/karpathy-llm-wiki | none | 0 |
| lucasastorian/llmwiki | gui | 2 |
| kytmanov/obsidian-llm-wiki-local | obsidian_native | 3 |
| swarmclawai/swarmvault | obsidian_native | 3 |

### 业务可插拔

- **FlowWiki 水平**: L7 场景层外壳，industry.yaml 适配器

| 竞品 | 能力等级 | 信号强度 |
|------|---------|---------|
| nashsu/llm_wiki | scenario_layer | 1 |
| AgriciDaniel/claude-obsidian | plugin | 1 |
| SamurAIGPT/llm-wiki-agent | plugin | 1 |
| inkeep/open-knowledge | none | 0 |
| Ar9av/obsidian-wiki | none | 0 |
| sdyckjq-lab/llm-wiki-skill | none | 0 |
| atomicstrata/llm-wiki-compiler | plugin | 1 |
| skyllwt/AutoSci | none | 0 |
| Astro-Han/karpathy-llm-wiki | none | 0 |
| lucasastorian/llmwiki | none | 0 |
| kytmanov/obsidian-llm-wiki-local | none | 0 |
| swarmclawai/swarmvault | plugin | 1 |

### 变更追溯

- **FlowWiki 水平**: SpecCoding 七阶段 + openspec/changes/

| 竞品 | 能力等级 | 信号强度 |
|------|---------|---------|
| nashsu/llm_wiki | git_only | 2 |
| AgriciDaniel/claude-obsidian | git_only | 2 |
| SamurAIGPT/llm-wiki-agent | git_only | 2 |
| inkeep/open-knowledge | speccoding | 1 |
| Ar9av/obsidian-wiki | git_only | 2 |
| sdyckjq-lab/llm-wiki-skill | git_only | 2 |
| atomicstrata/llm-wiki-compiler | speccoding | 1 |
| skyllwt/AutoSci | git_only | 2 |
| Astro-Han/karpathy-llm-wiki | speccoding | 1 |
| lucasastorian/llmwiki | git_only | 1 |
| kytmanov/obsidian-llm-wiki-local | git_only | 2 |
| swarmclawai/swarmvault | git_only | 2 |

### 知识复利到能力

- **FlowWiki 水平**: 任务→知识→Skill 三元组，O(1) 调用

| 竞品 | 能力等级 | 信号强度 |
|------|---------|---------|
| nashsu/llm_wiki | skill_layer | 1 |
| AgriciDaniel/claude-obsidian | skill_layer | 2 |
| SamurAIGPT/llm-wiki-agent | skill_layer | 2 |
| inkeep/open-knowledge | skill_layer | 1 |
| Ar9av/obsidian-wiki | skill_layer | 1 |
| sdyckjq-lab/llm-wiki-skill | skill_layer | 2 |
| atomicstrata/llm-wiki-compiler | skill_layer | 1 |
| skyllwt/AutoSci | skill_layer | 2 |
| Astro-Han/karpathy-llm-wiki | skill_layer | 2 |
| lucasastorian/llmwiki | skill_layer | 1 |
| kytmanov/obsidian-llm-wiki-local | skill_layer | 1 |
| swarmclawai/swarmvault | skill_layer | 2 |

### 自适应检索

- **FlowWiki 水平**: BM25 → nano-graphrag → LightRAG 三档

| 竞品 | 能力等级 | 信号强度 |
|------|---------|---------|
| nashsu/llm_wiki | hybrid | 1 |
| AgriciDaniel/claude-obsidian | multi_tier | 1 |
| SamurAIGPT/llm-wiki-agent | none | 0 |
| inkeep/open-knowledge | none | 0 |
| Ar9av/obsidian-wiki | none | 0 |
| sdyckjq-lab/llm-wiki-skill | none | 0 |
| atomicstrata/llm-wiki-compiler | multi_tier | 1 |
| skyllwt/AutoSci | none | 0 |
| Astro-Han/karpathy-llm-wiki | none | 0 |
| lucasastorian/llmwiki | none | 0 |
| kytmanov/obsidian-llm-wiki-local | vector_only | 1 |
| swarmclawai/swarmvault | hybrid | 1 |

### 矛盾追踪

- **FlowWiki 水平**: conflict/ 目录显式记录，不静默覆盖

| 竞品 | 能力等级 | 信号强度 |
|------|---------|---------|
| nashsu/llm_wiki | mark_only | 2 |
| AgriciDaniel/claude-obsidian | mark_only | 1 |
| SamurAIGPT/llm-wiki-agent | mark_only | 1 |
| inkeep/open-knowledge | none | 0 |
| Ar9av/obsidian-wiki | mark_only | 1 |
| sdyckjq-lab/llm-wiki-skill | none | 0 |
| atomicstrata/llm-wiki-compiler | mark_only | 1 |
| skyllwt/AutoSci | none | 0 |
| Astro-Han/karpathy-llm-wiki | none | 0 |
| lucasastorian/llmwiki | none | 0 |
| kytmanov/obsidian-llm-wiki-local | mark_only | 2 |
| swarmclawai/swarmvault | mark_only | 2 |

## 三、差距分析与改进建议

按差距压力排序（压力 = 竞品渗透率 × 维度权重）：

| 优先级 | 维度 | 竞品渗透率 | 紧迫度 | 分析 |
|--------|------|-----------|--------|------|
| 1 | 知识复利到能力 | 12/12 (100%) | 🔴 high | 100% 竞品已具备，属基础标配，不能落后 |
| 2 | 防幻觉机制 | 11/12 (92%) | 🔴 high | 92% 竞品已具备，属基础标配，不能落后 |
| 3 | 多 agent 兼容 | 12/12 (100%) | 🔴 high | 100% 竞品已具备，属基础标配，不能落后 |
| 4 | 跨会话记忆 | 10/12 (83%) | 🔴 high | 83% 竞品已具备，属基础标配，不能落后 |
| 5 | 人类 UX | 11/12 (92%) | 🔴 high | 92% 竞品已具备，属基础标配，不能落后 |
| 6 | 变更追溯 | 12/12 (100%) | 🔴 high | 100% 竞品已具备，属基础标配，不能落后 |

## 四、反思与行动

### 保持优势（差异化护城河）

- ✅ **业务可插拔**: 仅 42% 竞品有，是差异化优势
  - 对标头部: nashsu/llm_wiki
- ✅ **自适应检索**: 仅 42% 竞品有，是差异化优势
  - 对标头部: nashsu/llm_wiki

### 持续加固（过半竞品已具备）

- 🟡 **矛盾追踪**: 过半竞品具备，需持续保持领先
  - 头部玩家: nashsu/llm_wiki

### 必须警惕（基础标配，不能丢）

- 🔴 **知识复利到能力**: 100% 竞品已具备，属基础标配，不能落后
  - 最高 Star 竞品: nashsu/llm_wiki (14,852 ★)
- 🔴 **防幻觉机制**: 92% 竞品已具备，属基础标配，不能落后
  - 最高 Star 竞品: nashsu/llm_wiki (14,852 ★)
- 🔴 **多 agent 兼容**: 100% 竞品已具备，属基础标配，不能落后
  - 最高 Star 竞品: nashsu/llm_wiki (14,852 ★)
- 🔴 **跨会话记忆**: 83% 竞品已具备，属基础标配，不能落后
  - 最高 Star 竞品: nashsu/llm_wiki (14,852 ★)
- 🔴 **人类 UX**: 92% 竞品已具备，属基础标配，不能落后
  - 最高 Star 竞品: nashsu/llm_wiki (14,852 ★)
- 🔴 **变更追溯**: 100% 竞品已具备，属基础标配，不能落后
  - 最高 Star 竞品: nashsu/llm_wiki (14,852 ★)

---
*本报告由 FlowWiki AI Self-Benchmark Engine 自动生成*
