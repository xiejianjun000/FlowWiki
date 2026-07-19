#!/usr/bin/env python3
"""
FlowWiki 竞品对标分析引擎
扫描 GitHub 同类项目，做 9 维度横向对比，生成反思报告和改进建议。

对比维度：
  1. 防幻觉机制
  2. 跨会话记忆
  3. 多 agent 兼容
  4. 人类 UX
  5. 业务可插拔
  6. 变更追溯
  7. 知识复利到能力
  8. 自适应检索
  9. 矛盾追踪

输出：
  - JSON 格式对标数据
  - Markdown 对比报告
  - 反思改进建议（按优先级排序）
"""

import json
import sys
import os
import re
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "wiki" / "meta"

COMPETITOR_KEYWORDS = [
    "llm wiki",
    "knowledge base ai agent",
    "obsidian ai knowledge",
]

COMPETITOR_WHITELIST = [
    "nashsu/llm_wiki",
    "AgriciDaniel/claude-obsidian",
    "SamurAIGPT/llm-wiki-agent",
    "atomicstrata/llm-wiki-compiler",
    "Ar9av/obsidian-wiki",
    "inkeep/open-knowledge",
    "skyllwt/AutoSci",
    "Astro-Han/karpathy-llm-wiki",
    "lucasastorian/llmwiki",
    "swarmclawai/swarmvault",
    "kytmanov/obsidian-llm-wiki-local",
    "sdyckjq-lab/llm-wiki-skill",
]

NINE_DIMENSIONS = [
    {
        "key": "anti_hallucination",
        "name": "防幻觉机制",
        "weight": 1.5,
        "flowwiki_level": "ace_tri_agent",
        "flowwiki_desc": "ACE Generator→Reflector→Curator 三 agent 制约",
        "signals": {
            "ace": ["ace", "reflector", "curator", "generator", "三 agent", "反思循环"],
            "conflict_mark": ["conflict", "矛盾", "contradict"],
            "citation_check": ["citation", "引用", "source verification"],
            "none": [],
        },
    },
    {
        "key": "cross_session_memory",
        "name": "跨会话记忆",
        "weight": 1.3,
        "flowwiki_level": "a_mem_zettelkasten",
        "flowwiki_desc": "A-MEM Zettelkasten 卡片，零数据库依赖",
        "signals": {
            "zettelkasten": ["zettelkasten", "卡片", "a-mem", "a_mem"],
            "hot_cache": ["hot cache", "cache", "缓存"],
            "vector_db": ["vector", "向量", "embedding"],
            "none": [],
        },
    },
    {
        "key": "multi_agent",
        "name": "多 agent 兼容",
        "weight": 1.2,
        "flowwiki_level": "five_agents",
        "flowwiki_desc": "Claude Code / Codex / Gemini / Amp / WorkBuddy 五家",
        "signals": {
            "multi_platform": ["multi-agent", "multi agent", "多 agent", "多平台", "5 家", "five"],
            "claude_only": ["claude code", "claude-only", "仅 claude"],
            "single": [],
        },
    },
    {
        "key": "human_ux",
        "name": "人类 UX",
        "weight": 1.1,
        "flowwiki_level": "dual_index_six_sections",
        "flowwiki_desc": "双索引（机器 index + 人类 6 板块 MOC）",
        "signals": {
            "dual_index": ["双索引", "dual index", "moc", "6 板块", "six section"],
            "gui": ["gui", "desktop", "桌面应用", "web ui", "interface"],
            "obsidian_native": ["obsidian", "graph view", "dataview"],
            "none": [],
        },
    },
    {
        "key": "business_pluggable",
        "name": "业务可插拔",
        "weight": 1.4,
        "flowwiki_level": "l7_scenarios",
        "flowwiki_desc": "L7 场景层外壳，industry.yaml 适配器",
        "signals": {
            "scenario_layer": ["scenario", "场景", "pluggable", "可插拔", "行业"],
            "plugin": ["plugin", "插件"],
            "none": [],
        },
    },
    {
        "key": "change_traceability",
        "name": "变更追溯",
        "weight": 1.0,
        "flowwiki_level": "speccoding",
        "flowwiki_desc": "SpecCoding 七阶段 + openspec/changes/",
        "signals": {
            "speccoding": ["speccoding", "openspec", "spec", "七阶段"],
            "git_only": ["git", "version"],
            "none": [],
        },
    },
    {
        "key": "compound_skill",
        "name": "知识复利到能力",
        "weight": 1.5,
        "flowwiki_level": "task_knowledge_skill",
        "flowwiki_desc": "任务→知识→Skill 三元组，O(1) 调用",
        "signals": {
            "skill_layer": ["skill", "技能", "compound", "复利", "三元组"],
            "prompt_only": ["prompt", "提示词"],
            "none": [],
        },
    },
    {
        "key": "adaptive_retrieval",
        "name": "自适应检索",
        "weight": 1.0,
        "flowwiki_level": "bm25_graphrag_lightrag",
        "flowwiki_desc": "BM25 → nano-graphrag → LightRAG 三档",
        "signals": {
            "multi_tier": ["bm25", "graphrag", "lightrag", "三档", "自适应"],
            "hybrid": ["hybrid", "混合检索"],
            "vector_only": ["vector", "向量"],
            "none": [],
        },
    },
    {
        "key": "conflict_tracking",
        "name": "矛盾追踪",
        "weight": 1.0,
        "flowwiki_level": "conflict_dir",
        "flowwiki_desc": "conflict/ 目录显式记录，不静默覆盖",
        "signals": {
            "conflict_dir": ["conflict/", "矛盾追踪", "conflict tracking"],
            "mark_only": ["标记", "flag", "warning"],
            "none": [],
        },
    },
]


def github_api_request(endpoint: str, token: str = None) -> Optional[dict]:
    url = f"https://api.github.com/{endpoint}"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "FlowWiki-Benchmark",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"  [WARN] GitHub API 请求失败 {endpoint}: {e}")
        return None


def search_repos(keyword: str, token: str = None, limit: int = 10) -> list[dict]:
    q = urllib.parse.quote(keyword)
    endpoint = f"search/repositories?q={q}&sort=stars&order=desc&per_page={limit}"
    data = github_api_request(endpoint, token)
    if not data or "items" not in data:
        return []
    return data["items"]


def get_repo_detail(full_name: str, token: str = None) -> Optional[dict]:
    return github_api_request(f"repos/{full_name}", token)


def get_readme(full_name: str, token: str = None) -> str:
    data = github_api_request(f"repos/{full_name}/readme", token)
    if not data or "content" not in data:
        return ""
    try:
        import base64
        return base64.b64decode(data["content"]).decode("utf-8", errors="ignore")
    except Exception:
        return ""


def analyze_dimensions(readme: str, description: str) -> dict:
    text = (description or "") + "\n" + (readme or "")
    text_lower = text.lower()

    result = {}
    for dim in NINE_DIMENSIONS:
        scores = {}
        for level, keywords in dim["signals"].items():
            if not keywords:
                continue
            count = sum(1 for kw in keywords if kw.lower() in text_lower)
            scores[level] = count

        best_level = "none"
        best_score = 0
        for level, score in scores.items():
            if score > best_score:
                best_score = score
                best_level = level

        result[dim["key"]] = {
            "level": best_level,
            "score": best_score,
            "has_feature": best_level != "none" and best_score > 0,
        }

    return result


def compute_gap_analysis(competitors: list[dict]) -> list[dict]:
    suggestions = []

    for dim in NINE_DIMENSIONS:
        dim_key = dim["key"]
        dim_name = dim["name"]
        weight = dim["weight"]

        competitors_with = sum(
            1 for c in competitors
            if c["dimensions"].get(dim_key, {}).get("has_feature", False)
        )
        total = len(competitors) if competitors else 1
        penetration = competitors_with / total

        max_stars = 0
        top_competitor = None
        for c in competitors:
            if c["dimensions"].get(dim_key, {}).get("has_feature", False):
                if c["stars"] > max_stars:
                    max_stars = c["stars"]
                    top_competitor = c["full_name"]

        flowwiki_has = True
        gap_pressure = penetration * weight

        if penetration >= 0.8:
            urgency = "high"
            comment = f"{penetration:.0%} 竞品已具备，属基础标配，不能落后"
        elif penetration >= 0.5:
            urgency = "medium"
            comment = f"过半竞品具备，需持续保持领先"
        else:
            urgency = "low"
            comment = f"仅 {penetration:.0%} 竞品有，是差异化优势"

        suggestions.append({
            "dimension": dim_name,
            "dimension_key": dim_key,
            "flowwiki_level": dim["flowwiki_level"],
            "flowwiki_desc": dim["flowwiki_desc"],
            "competitor_penetration": round(penetration, 3),
            "competitors_with_feature": competitors_with,
            "top_competitor_with_feature": top_competitor,
            "top_competitor_stars": max_stars,
            "urgency": urgency,
            "gap_pressure": round(gap_pressure, 2),
            "comment": comment,
        })

    suggestions.sort(key=lambda x: (-x["gap_pressure"], x["urgency"]))
    return suggestions


def generate_markdown_report(competitors: list[dict], suggestions: list[dict]) -> str:
    lines = []

    lines.append(f"---")
    lines.append(f"type: benchmark")
    lines.append(f"title: 竞品对标分析报告")
    lines.append(f"created: {datetime.now().strftime('%Y-%m-%d')}")
    lines.append(f"updated: {datetime.now().strftime('%Y-%m-%d')}")
    lines.append(f"tags: [\"flow-wiki\", \"benchmark\", \"competitor\"]")
    lines.append(f"status: active")
    lines.append(f"---")
    lines.append("")
    lines.append("# 竞品对标分析报告")
    lines.append("")
    lines.append(f"> 生成时间: {datetime.now().isoformat()}")
    lines.append(f"> 对标竞品数: {len(competitors)}")
    lines.append("")

    lines.append("## 一、竞品总览")
    lines.append("")
    lines.append("| 项目 | Star | Fork | 创建时间 | 语言 | 防幻觉 | 记忆 | 多 agent | UX | 可插拔 | 变更追溯 | 复利 Skill | 自适应检索 | 矛盾追踪 |")
    lines.append("|------|------|------|---------|------|--------|------|---------|-----|--------|---------|-----------|----------|---------|")

    dim_keys = [d["key"] for d in NINE_DIMENSIONS]
    for c in competitors:
        dims = c["dimensions"]
        marks = []
        for dk in dim_keys:
            marks.append("✅" if dims.get(dk, {}).get("has_feature") else "❌")
        created = c.get("created_at", "")[:10]
        lines.append(
            f"| [{c['full_name']}](https://github.com/{c['full_name']}) "
            f"| {c['stars']:,} "
            f"| {c['forks']:,} "
            f"| {created} "
            f"| {c.get('language', '-')} "
            f"| {' | '.join(marks)} |"
        )
    lines.append("")

    lines.append("## 二、九维度对比矩阵")
    lines.append("")
    for dim in NINE_DIMENSIONS:
        dk = dim["key"]
        dn = dim["name"]
        lines.append(f"### {dn}")
        lines.append("")
        lines.append(f"- **FlowWiki 水平**: {dim['flowwiki_desc']}")
        lines.append("")
        lines.append("| 竞品 | 能力等级 | 信号强度 |")
        lines.append("|------|---------|---------|")
        for c in competitors:
            info = c["dimensions"].get(dk, {})
            level = info.get("level", "none")
            score = info.get("score", 0)
            lines.append(f"| {c['full_name']} | {level} | {score} |")
        lines.append("")

    lines.append("## 三、差距分析与改进建议")
    lines.append("")
    lines.append("按差距压力排序（压力 = 竞品渗透率 × 维度权重）：")
    lines.append("")
    lines.append("| 优先级 | 维度 | 竞品渗透率 | 紧迫度 | 分析 |")
    lines.append("|--------|------|-----------|--------|------|")
    for i, s in enumerate(suggestions[:6], 1):
        urgency_icon = "🔴" if s["urgency"] == "high" else "🟡" if s["urgency"] == "medium" else "🟢"
        lines.append(
            f"| {i} | {s['dimension']} "
            f"| {s['competitors_with_feature']}/{len(competitors)} ({s['competitor_penetration']:.0%}) "
            f"| {urgency_icon} {s['urgency']} "
            f"| {s['comment']} |"
        )
    lines.append("")

    lines.append("## 四、反思与行动")
    lines.append("")
    lines.append("### 保持优势（差异化护城河）")
    lines.append("")
    for s in suggestions:
        if s["urgency"] == "low":
            lines.append(f"- ✅ **{s['dimension']}**: {s['comment']}")
            lines.append(f"  - 对标头部: {s['top_competitor_with_feature'] or '无'}")
    lines.append("")
    lines.append("### 持续加固（过半竞品已具备）")
    lines.append("")
    for s in suggestions:
        if s["urgency"] == "medium":
            lines.append(f"- 🟡 **{s['dimension']}**: {s['comment']}")
            lines.append(f"  - 头部玩家: {s['top_competitor_with_feature'] or '无'}")
    lines.append("")
    lines.append("### 必须警惕（基础标配，不能丢）")
    lines.append("")
    for s in suggestions:
        if s["urgency"] == "high":
            lines.append(f"- 🔴 **{s['dimension']}**: {s['comment']}")
            lines.append(f"  - 最高 Star 竞品: {s['top_competitor_with_feature'] or '无'} ({s['top_competitor_stars']:,} ★)")
    lines.append("")

    lines.append("---")
    lines.append(f"*本报告由 FlowWiki AI Self-Benchmark Engine 自动生成*")
    lines.append("")

    return "\n".join(lines)


def main():
    output_json = sys.argv[1] if len(sys.argv) > 1 else None
    output_md = sys.argv[2] if len(sys.argv) > 2 else None

    token = os.environ.get("GITHUB_TOKEN", os.environ.get("GH_TOKEN", ""))

    print("=" * 60)
    print("  FlowWiki 竞品对标分析引擎")
    print(f"  时间: {datetime.now().isoformat()}")
    print("=" * 60)

    print("\n[1/4] 拉取竞品数据...")
    competitors = []
    seen = set()

    for full_name in COMPETITOR_WHITELIST:
        if full_name in seen:
            continue
        seen.add(full_name)
        print(f"  -> {full_name}")
        detail = get_repo_detail(full_name, token)
        if not detail:
            continue
        readme = get_readme(full_name, token)
        dimensions = analyze_dimensions(readme, detail.get("description", ""))
        competitors.append({
            "full_name": full_name,
            "description": detail.get("description", ""),
            "stars": detail.get("stargazers_count", 0),
            "forks": detail.get("forks_count", 0),
            "language": detail.get("language", ""),
            "created_at": detail.get("created_at", ""),
            "updated_at": detail.get("updated_at", ""),
            "open_issues": detail.get("open_issues_count", 0),
            "license": (detail.get("license") or {}).get("spdx_id", ""),
            "dimensions": dimensions,
            "readme_length": len(readme),
        })

    print(f"  -> 成功获取 {len(competitors)} 个竞品")

    competitors.sort(key=lambda x: -x["stars"])

    print("\n[2/4] 九维度能力分析...")
    for dim in NINE_DIMENSIONS:
        dk = dim["key"]
        dn = dim["name"]
        count = sum(1 for c in competitors if c["dimensions"][dk]["has_feature"])
        print(f"  -> {dn}: {count}/{len(competitors)} 竞品具备")

    print("\n[3/4] 生成差距分析...")
    suggestions = compute_gap_analysis(competitors)
    print(f"  -> 生成 {len(suggestions)} 条改进建议")
    for s in suggestions[:3]:
        print(f"     [{s['urgency']}] {s['dimension']}: {s['comment']}")

    print("\n[4/4] 生成报告...")
    md_report = generate_markdown_report(competitors, suggestions)

    result = {
        "timestamp": datetime.now().isoformat(),
        "competitor_count": len(competitors),
        "competitors": competitors,
        "nine_dimensions": [
            {k: v for k, v in d.items() if k != "signals"}
            for d in NINE_DIMENSIONS
        ],
        "gap_suggestions": suggestions,
    }

    if output_json:
        out = Path(output_json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  -> JSON 报告: {output_json}")

    if output_md:
        out = Path(output_md)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(md_report, encoding="utf-8")
        print(f"  -> Markdown 报告: {output_md}")

    print("\n" + "=" * 60)
    print("  对标完成")
    print("=" * 60)

    return result


if __name__ == "__main__":
    main()
