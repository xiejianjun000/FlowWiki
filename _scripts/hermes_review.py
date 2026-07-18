#!/usr/bin/env python3
"""
通用知识库 Hermes 评估脚本。
支持任意目录：FlowWiki 行业知识库（有 industry.yaml）或 Obsidian vault（有 .obsidian/）。

Usage:
    python _scripts/hermes_review.py --kb /path/to/kb              # 任意知识库
    python _scripts/hermes_review.py --industry root-cause          # FlowWiki 行业
    python _scripts/hermes_review.py --kb /path --output report.md # 输出报告

依赖：配置文件 config.toml [hermes] 段 或 环境变量 DEEPSEEK_API_KEY
"""

# macOS locale workaround
import locale
if not hasattr(locale, 'normalize'):
    locale.normalize = lambda x: x.replace('_','-').lower()

import argparse
import datetime
import json
import logging
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = PROJECT_ROOT / "ops" / "monitoring"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", stream=sys.stderr)
logger = logging.getLogger("hermes-review")

# ── Hermes config ──
def _load_hermes_config() -> dict[str, str]:
    """Read Hermes config: config.toml (primary) → .llm-wiki (fallback, 只补未设) → env (最高)."""
    cfg = {"api_url": "https://api.deepseek.com/v1/chat/completions", "api_key": "", "model": "deepseek-chat"}

    def _try_load(path: Path):
        try:
            import tomllib
        except ImportError:
            try: import tomli as tomllib
            except ImportError: return {}
        try: return tomllib.loads(path.read_text(encoding="utf-8")).get("hermes", {})
        except Exception: return {}

    # Primary: config.toml
    p = _try_load(PROJECT_ROOT / "config.toml")
    if v := p.get("api_url"): cfg["api_url"] = v
    if v := p.get("api_key"): cfg["api_key"] = v
    if v := p.get("model"): cfg["model"] = v

    # Fallback: .llm-wiki — 不覆盖主配置的 URL
    f = _try_load(PROJECT_ROOT / ".llm-wiki" / "config.toml")
    if not cfg["api_key"] and f.get("api_key"): cfg["api_key"] = f["api_key"]

    # Env vars (highest)
    if v := os.environ.get("HERMES_API_URL"): cfg["api_url"] = v
    if v := os.environ.get("HERMES_API_KEY"): cfg["api_key"] = v
    elif not cfg["api_key"]:
        if v := os.environ.get("DEEPSEEK_API_KEY"): cfg["api_key"] = v
    if v := os.environ.get("HERMES_MODEL"): cfg["model"] = v

    return cfg


# ── Knowledge base discovery ──
LINK_RE = re.compile(r"\[\[([^\]|#]+)(?:\|[^\]]*)?\]\]")


def discover_kb(kb_path: Path, industry_slug: str = None) -> dict[str, Any]:
    """自动发现知识库结构，收集上下文。
    FlowWiki 三层架构: raw/{slug}/ + wiki/{slug}/ + storage/{slug}/industry.yaml
    """
    # Support passing slug via function attribute (from main())
    if industry_slug is None:
        industry_slug = getattr(discover_kb, '__industry_slug__', None)
    
    info: dict[str, Any] = {
        "path": str(kb_path),
        "name": industry_slug or kb_path.name,
        "type": "unknown",
        "file_count": 0,
        "README": "",
        "SCHEMA": "",
        "index": "",
        "graph_stats": "",
        "industry_yaml": None,
    }

    # Determine scope: project root with industry OR external directory
    if industry_slug and (kb_path / "storage" / industry_slug / "industry.yaml").exists():
        info["type"] = "flowwiki_industry"
        info["name"] = industry_slug
        wiki_scope = kb_path / "wiki" / industry_slug
        raw_scope = kb_path / "raw" / industry_slug
        # Count only industry-specific files
        info["file_count"] = len([f for f in wiki_scope.rglob("*.md")] if wiki_scope.exists() else []) + \
                             len([f for f in raw_scope.rglob("*.md")] if raw_scope.exists() else [])
    elif (kb_path / ".obsidian").exists():
        info["type"] = "obsidian_vault"
        info["file_count"] = len([f for f in kb_path.rglob("*.md")
                                  if ".obsidian" not in str(f) and ".git" not in str(f)])
        wiki_scope = kb_path
        raw_scope = kb_path / "raw"
    elif (kb_path / "storage").exists() and (kb_path / "wiki").exists():
        info["type"] = "flowwiki"
        info["file_count"] = len([f for f in kb_path.rglob("*.md")
                                  if ".obsidian" not in str(f) and ".git" not in str(f)])
        wiki_scope = kb_path / "wiki"
        raw_scope = kb_path / "raw"
    else:
        info["file_count"] = len([f for f in kb_path.rglob("*.md")
                                  if ".obsidian" not in str(f) and ".git" not in str(f)])
        wiki_scope = kb_path
        raw_scope = kb_path / "raw"

    # README — from kb_path root
    for name in ["README.md", "readme.md"]:
        p = kb_path / name
        if p.exists():
            info["README"] = p.read_text(encoding="utf-8")[:3000]
            break

    # SCHEMA — from kb_path root
    for name in ["SCHEMA.md", "schema.md"]:
        p = kb_path / name
        if p.exists():
            info["SCHEMA"] = p.read_text(encoding="utf-8")[:2000]
            break

    # Index — from wiki_scope (check meta/index.md too)
    for name in ["index.md", "meta/index.md"]:
        p = wiki_scope / name if wiki_scope != kb_path else kb_path / name
        if p.exists():
            info["index"] = p.read_text(encoding="utf-8")[:2000]
            break

    # Industry yaml — from storage/{slug}/industry.yaml
    if industry_slug:
        iy = kb_path / "storage" / industry_slug / "industry.yaml"
        if iy.exists():
            try:
                import yaml
                info["industry_yaml"] = yaml.safe_load(iy.read_text(encoding="utf-8"))
            except Exception:
                pass

    # Graph stats — use wiki_scope (industry subdir or wiki root)
    graph_out = _run_graph_stats(wiki_scope)
    if not graph_out:
        graph_out = _run_flowwiki_graph(wiki_scope)
    if graph_out:
        info["graph_stats"] = graph_out[:3000]

    return info


def _run_graph_stats(kb_path: Path) -> str:
    """尝试运行目标知识库自己的 _scripts/graph.py --format stats。"""
    for script in ["_scripts/graph.py", "_scripts/graph_stats.py", "scripts/graph.py"]:
        p = kb_path / script
        if p.exists():
            try:
                proc = subprocess.run(
                    [sys.executable, str(p), "--format", "stats"],
                    capture_output=True, text=True, timeout=30, cwd=str(kb_path),
                )
                if proc.returncode == 0:
                    return proc.stdout.strip()
                # 部分 graph.py 不支持 --format stats，试无参数
                proc2 = subprocess.run(
                    [sys.executable, str(p)],
                    capture_output=True, text=True, timeout=30, cwd=str(kb_path),
                )
                if proc2.returncode == 0:
                    return proc2.stdout.strip()[:3000]
            except Exception:
                pass
    return ""


def _run_flowwiki_graph(kb_path: Path) -> str:
    """用 FlowWiki 的 graph.py 分析目标目录的 wikilink 图谱。"""
    # 如果 kb_path 有 wiki/ 子目录，从 wiki/ 提取
    wiki_path = kb_path / "wiki" if (kb_path / "wiki").exists() else kb_path
    md_files = [f for f in wiki_path.rglob("*.md")]
    nodes: dict[str, set[str]] = {}
    all_titles: set[str] = set()

    for f in md_files:
        title = f.stem
        all_titles.add(title)

    for f in md_files:
        title = f.stem
        try:
            text = f.read_text(encoding="utf-8")
        except Exception:
            continue
        links = set()
        for m in LINK_RE.finditer(text):
            target = m.group(1).split("|")[0].strip().split("#")[0].strip()
            if target in all_titles and target != title:
                links.add(target)
        nodes[title] = links

    total_edges = sum(len(v) for v in nodes.values())
    isolated = [t for t, links in nodes.items() if len(links) == 0
                and sum(1 for _, v in nodes.items() if t in v) == 0]

    return (
        f"节点: {len(nodes)} | 边: {total_edges} | 孤立: {len(isolated)} "
        f"({len(isolated) / max(len(nodes), 1) * 100:.0f}%) | "
        f"密度: {total_edges / max(len(nodes), 1):.2f}"
    )


# ── Hermes call ──
def call_hermes(kb_info: dict[str, Any], hermes_cfg: dict[str, str]) -> dict[str, Any]:
    """调用 Hermes API 对知识库做质量评审。"""
    api_key = hermes_cfg["api_key"]
    if not api_key:
        return {"mode": "local-fallback", "status": "pending",
                "message": "No API key configured. Set DEEPSEEK_API_KEY or HERMES_API_KEY."}

    name = kb_info["name"]
    kb_type = kb_info["type"]
    file_count = kb_info["file_count"]

    # 行业配置（如果有）
    industry_section = ""
    if kb_info.get("industry_yaml"):
        iy = kb_info["industry_yaml"]
        industry_section = (
            f"\n### 行业配置 (industry.yaml)\n"
            f"- 名称: {iy.get('name', '?')}\n"
            f"- 领域: {iy.get('domain', '?')} / {iy.get('subdomain', '?')}\n"
            f"- 概念: {iy.get('wiki_structure', {}).get('concepts', [])}\n"
            f"- 场景: {[s.get('name', '') for s in iy.get('scenarios', [])]}\n"
        )

    prompt = f"""你是知识库质量评审专家。请全面评审以下知识库。

## 知识库概况
- 名称: {name}
- 类型: {kb_type}
- 文件数: {file_count} 个 .md
{industry_section}

## README
{kb_info['README'][:2500] or '(无)'}

## SCHEMA / 元数据
{kb_info['SCHEMA'][:1500] or '(无)'}

## 索引
{kb_info['index'][:1500] or '(无)'}

## 图谱统计
{kb_info['graph_stats'][:2000] or '(无)'}

请从以下维度评审（1-10 分），用 JSON 格式回复：

1. **结构**: 目录分层、标签体系、frontmatter 是否规范
2. **内容**: 是否覆盖核心领域，深度和广度如何
3. **图谱**: 节点/边数、连通性、枢纽页、断链/孤立情况
4. **操作**: SOP/清单/工作流是否可直接用于实战
5. **时效**: 是否有版本管理、时间敏感内容标注
6. **维护**: 模板/脚本/元文档是否齐全
7. **整体**: 综合评分

只输出 JSON:
```json
{{"scores": {{"结构": x, "内容": x, "图谱": x, "操作": x, "时效": x, "维护": x, "整体": x}}, "verdict": "pass|needs_attention", "strengths": ["优势"], "top_issues": ["问题"], "recommendations": ["建议"]}}
```"""

    api_url = hermes_cfg["api_url"]
    model = hermes_cfg["model"]

    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": "你是知识库评审专家。只输出有效 JSON。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3, "max_tokens": 1500,
    }).encode("utf-8")

    try:
        req = urllib.request.Request(api_url, data=payload,
                                     headers={"Content-Type": "application/json",
                                              "Authorization": f"Bearer {api_key}"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = json.loads(resp.read())
            content = raw["choices"][0]["message"]["content"]
            json_start = content.find("{")
            json_end = content.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                result = json.loads(content[json_start:json_end])
                result["mode"] = "llm"
                result["model_used"] = model
                return result
            else:
                return {"mode": "llm", "status": "parse_error", "raw": content[:500]}
    except Exception as e:
        return {"mode": "llm", "status": "api_error", "error": str(e)[:300]}


# ── Report ──
def save_report(kb_info: dict[str, Any], review: dict[str, Any], output_path: str | None = None) -> str:
    """生成 Markdown 报告并保存。"""
    today = datetime.date.today().isoformat()
    name = kb_info["name"]
    scores = review.get("scores", {})

    if not output_path:
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        safe_name = name.replace(" ", "-").replace("/", "-")
        output_path = str(REPORT_DIR / f"hermes-{safe_name}-{today}.md")

    lines = [
        f"# Hermes {name} 评审 — {today}",
        f"",
        f"**时间**: {datetime.datetime.now().isoformat()} | **模型**: {review.get('model_used', '?')}",
        f"**文件数**: {kb_info['file_count']}",
        f"",
        "## 评分",
        "",
        "| 维度 | 得分 |",
        "|------|------|",
    ]
    for dim, score in scores.items():
        lines.append(f"| {dim} | {score} |")
    lines += [
        f"| **整体** | **{scores.get('整体', '?')}** |",
        f"",
        f"**结论**: {review.get('verdict', '?')}",
        f"",
    ]

    if review.get("strengths"):
        lines.append("## 优势")
        for s in review["strengths"]:
            lines.append(f"- {s}")

    if review.get("top_issues"):
        lines.append("\n## 问题")
        for i in review["top_issues"]:
            lines.append(f"- {i}")

    if review.get("recommendations"):
        lines.append("\n## 建议")
        for r in review["recommendations"]:
            lines.append(f"- {r}")

    if review.get("error"):
        lines.append(f"\n## 错误\n- {review['error']}")

    lines += ["", "---", f"*Hermes 自动评审生成*"]

    content = "\n".join(lines)
    Path(output_path).write_text(content, encoding="utf-8")
    logger.info("报告: %s", output_path)
    return output_path


# ── Main ──
def main() -> None:
    parser = argparse.ArgumentParser(description="通用知识库 Hermes 评估")
    parser.add_argument("--kb", type=str, help="知识库目录路径")
    parser.add_argument("--industry", type=str, help="FlowWiki 行业名（root-cause/compliance-review/...）")
    parser.add_argument("--output", type=str, help="报告输出路径（可选）")
    parser.add_argument("--json", action="store_true", help="输出 JSON 到 stdout")
    args = parser.parse_args()

    # 确定目标
    if args.industry:
        industry_slug = args.industry
        # FlowWiki 三层架构: raw/{slug}/ + wiki/{slug}/ + storage/{slug}/industry.yaml
        kb_path = PROJECT_ROOT
        # Verify industry exists
        if not (PROJECT_ROOT / "storage" / industry_slug / "industry.yaml").exists():
            logger.error("FlowWiki 行业 '%s' 不存在", industry_slug)
            sys.exit(1)
        # Pass slug through for discovery
        discover_kb.__industry_slug__ = industry_slug
    elif args.kb:
        kb_path = Path(args.kb).resolve()
        if not kb_path.exists():
            logger.error("目录 '%s' 不存在", args.kb)
            sys.exit(1)
    else:
        logger.error("需要 --kb 或 --industry 参数")
        sys.exit(1)

    logger.info("发现知识库: %s (类型: %s)", kb_path.name, "FlowWiki" if args.industry else "external")

    hermes_cfg = _load_hermes_config()
    if not hermes_cfg["api_key"]:
        logger.error("未配置 API key（DEEPSEEK_API_KEY 或 HERMES_API_KEY）")
        sys.exit(1)

    logger.info("收集知识库上下文...")
    kb_info = discover_kb(kb_path)
    logger.info("  类型: %s | 文件: %d | 图谱: %s",
                kb_info["type"], kb_info["file_count"],
                "有" if kb_info["graph_stats"] else "无")

    logger.info("调用 Hermes (%s)...", hermes_cfg["model"])
    review = call_hermes(kb_info, hermes_cfg)

    if args.json:
        print(json.dumps({"kb_info": {k: v for k, v in kb_info.items() if k not in ("README", "SCHEMA", "index")},
                          "review": review}, ensure_ascii=False, indent=2))
    else:
        report_path = save_report(kb_info, review, args.output)
        scores = review.get("scores", {})
        logger.info("评审完成: %s — 整体 %.1f/10",
                    review.get("verdict", "?"),
                    scores.get("整体", scores.get("整体", 0)))

    # Exit code
    if review.get("verdict") == "needs_attention":
        sys.exit(1)
    elif review.get("status") in ("api_error", "parse_error"):
        sys.exit(2)


if __name__ == "__main__":
    main()
