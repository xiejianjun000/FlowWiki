#!/usr/bin/env python3
"""
FlowWiki 每日全量测试 + 4 知识库顺序跑 + Hermes 验证

Usage:
    python _scripts/daily_test.py                     # 完整测试
    python _scripts/daily_test.py --quick              # 快速测试（仅 lint）
    python _scripts/daily_test.py --industry root-cause # 单行业测试

输出：
    ops/monitoring/daily-test-YYYY-MM-DD.md             # 完整报告
    ops/monitoring/daily-test-YYYY-MM-DD.json           # 机器可读结果
"""

import argparse
import datetime
import json
import logging
import re
import subprocess
import sys
import traceback
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
from _scripts.ops_log import ops_log

# Config
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = PROJECT_ROOT / "ops" / "monitoring"

# ── Load Hermes config from config.toml ──
def _load_hermes_config() -> dict[str, str]:
    """Read Hermes API config from config.toml, fallback to env vars."""
    cfg: dict[str, str] = {
        "api_url": "http://localhost:20128/v1/chat/completions",
        "api_key": "sk-omniroute",
        "model": "oc/deepseek-v4-flash-free",
    }
    config_path = PROJECT_ROOT / "config.toml"
    if not config_path.exists():
        config_path = PROJECT_ROOT / ".llm-wiki" / "config.toml"

    if config_path.exists():
        try:
            import tomllib  # Python 3.11+
        except ImportError:
            try:
                import tomli as tomllib  # type: ignore[no-redef]
            except ImportError:
                tomllib = None  # type: ignore[assignment]

        if tomllib:
            try:
                data = tomllib.loads(config_path.read_text(encoding="utf-8"))
                hermes = data.get("hermes", {})
                cfg["api_url"] = hermes.get("api_url", cfg["api_url"])
                cfg["api_key"] = hermes.get("api_key", cfg["api_key"])
                cfg["model"] = hermes.get("model", cfg["model"])
            except Exception:
                pass

    # Env vars override config file
    import os
    if v := os.environ.get("HERMES_API_URL"):
        cfg["api_url"] = v
    if v := os.environ.get("HERMES_API_KEY"):
        cfg["api_key"] = v
    elif not cfg.get("api_key"):
        # Fallback: read DEEPSEEK_API_KEY from env (Hermes main model key)
        if v := os.environ.get("DEEPSEEK_API_KEY"):
            cfg["api_key"] = v
    if v := os.environ.get("HERMES_MODEL"):
        cfg["model"] = v

    return cfg

_hermes_cfg = _load_hermes_config()
HERMES_API_URL = _hermes_cfg["api_url"]
HERMES_API_KEY = _hermes_cfg["api_key"]
HERMES_MODEL = _hermes_cfg["model"]
HERMES_TIMEOUT = 120  # LLM 调用超时（秒）

# 四个需要每日跑的知识库（行业适配器）
INDUSTRIES = [
    {"slug": "root-cause", "name": "根因分析"},
    {"slug": "compliance-review", "name": "合规审查"},
    {"slug": "license-management", "name": "证照管理"},
    {"slug": "enterprise-compliance", "name": "企业合规AI管家"},
    {"slug": "enforcement-review", "name": "执法督察评查（测试用）"},
]

SCRIPTS = [
    {"name": "ingest_pipeline", "path": "_scripts/ingest_pipeline.py"},
    {"name": "ace_review", "path": "_scripts/ace_review.py"},
    {"name": "a_mem_card", "path": "_scripts/a_mem_card.py"},
    {"name": "lint", "path": "_scripts/lint.py"},
    {"name": "graph", "path": "_scripts/graph.py"},
    {"name": "sync_dual_index", "path": "_scripts/sync_dual_index.py"},
    {"name": "reindex", "path": "_scripts/reindex.py"},
    {"name": "normalize", "path": "_scripts/normalize.py"},
    {"name": "build_match_index", "path": "_scripts/build_match_index.py"},
    {"name": "gen_criteria_pages", "path": "_scripts/gen_criteria_pages.py"},
    {"name": "fix_dangling", "path": "_scripts/fix_dangling.py"},
    {"name": "e2e_test", "path": "_scripts/e2e_test.py"},
    {"name": "mcp_server", "path": "_scripts/mcp_server.py"},
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("daily-test")

# ---------------------------------------------------------------------------
# Phase 1: All scripts syntax + import check
# ---------------------------------------------------------------------------

def phase1_script_syntax() -> list[dict[str, Any]]:
    """Verify all Python scripts can be compiled (syntax check)."""
    results = []
    for script in SCRIPTS:
        path = PROJECT_ROOT / script["path"]
        try:
            subprocess.run(
                [sys.executable, "-c",
                 f"import py_compile; py_compile.compile('{path}', doraise=True)"],
                capture_output=True, text=True, check=True, timeout=30,
            )
            results.append({"script": script["name"], "status": "pass"})
        except subprocess.CalledProcessError as e:
            results.append({
                "script": script["name"], "status": "fail",
                "error": e.stderr.strip()[:200],
            })
        except Exception as e:
            results.append({
                "script": script["name"], "status": "error",
                "error": str(e)[:200],
            })
    return results


# ---------------------------------------------------------------------------
# Phase 2: CI lint check
# ---------------------------------------------------------------------------

def phase2_ci_lint() -> dict[str, Any]:
    """Run CI-level lint checks on the wiki structure."""
    errors = []
    stats: dict[str, int] = {"pages": 0, "with_frontmatter": 0, "orphan_pages": 0}

    wiki_dir = PROJECT_ROOT / "wiki"
    home_readme = PROJECT_ROOT / "00_首页" / "README.md"
    schema_file = PROJECT_ROOT / "SCHEMA.md"

    # Key file existence
    for label, path in [
        ("wiki/index.md", wiki_dir / "index.md"),
        ("00_首页/README.md", home_readme),
        ("SCHEMA.md", schema_file),
        (".gitignore", PROJECT_ROOT / ".gitignore"),
    ]:
        if not path.exists():
            errors.append(f"MISSING: {label}")

    # Wiki frontmatter check
    if wiki_dir.exists():
        for md_file in wiki_dir.rglob("*.md"):
            if md_file.name in ("README.md", "index.md", "log.md"):
                continue
            if "meta" in md_file.parts:
                continue
            stats["pages"] += 1
            try:
                if md_file.read_text(encoding="utf-8").startswith("---"):
                    stats["with_frontmatter"] += 1
                else:
                    errors.append(f"No frontmatter: {md_file.relative_to(PROJECT_ROOT)}")
            except Exception:
                pass

    return {
        "status": "pass" if not errors else "warning",
        "errors": errors[:20],
        "stats": stats,
    }


# ---------------------------------------------------------------------------
# Phase 3: 4 知识库顺序跑
# ---------------------------------------------------------------------------

def phase3_industry_run(industry: dict[str, str]) -> dict[str, Any]:
    """Run ingest + lint + query + research on a single industry."""
    slug = industry["slug"]
    name = industry["name"]
    results: dict[str, Any] = {
        "industry": name, "slug": slug, "steps": {}, "overall": "pass",
    }

    # 3a) Verify industry config exists
    config_path = PROJECT_ROOT / "storage" / slug / "industry.yaml"
    if not config_path.exists():
        results["overall"] = "fail"
        results["error"] = f"industry.yaml not found for {slug}"
        return results

    # 3b) Lint the industry-specific wiki pages
    wiki_dir = PROJECT_ROOT / "wiki"
    industry_pages = list(wiki_dir.rglob("*.md"))
    results["steps"]["wiki_count"] = len(industry_pages)

    # 3c) Run lint on the wiki
    try:
        proc = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "_scripts" / "lint.py")],
            capture_output=True, text=True, timeout=60,
            cwd=str(PROJECT_ROOT),
        )
        results["steps"]["lint"] = {
            "status": "pass" if proc.returncode == 0 else "fail",
            "output": proc.stdout.strip()[:500] + proc.stderr.strip()[:500],
        }
    except Exception as e:
        results["steps"]["lint"] = {"status": "error", "error": str(e)[:200]}

    # 3d) Run ingest pipeline for the industry
    try:
        proc = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "_scripts" / "ingest_pipeline.py")],
            capture_output=True, text=True, timeout=120,
            cwd=str(PROJECT_ROOT),
        )
        results["steps"]["ingest"] = {
            "status": "pass" if proc.returncode == 0 else "fail",
            "output": proc.stdout.strip()[:500],
        }
    except Exception as e:
        results["steps"]["ingest"] = {"status": "error", "error": str(e)[:200]}

    return results


# ---------------------------------------------------------------------------
# Phase 4: Hermes 验证
# ---------------------------------------------------------------------------

def phase4_hermes_verify(results_per_industry: list[dict[str, Any]]) -> dict[str, Any]:
    """
    调用本地 Hermes LLM（OmniRoute/DeepSeek）对 4 个知识库做真实 AI 评审。
    读取 config.toml [hermes] 段获取 api_url + api_key + model。
    """
    api_key = HERMES_API_KEY.strip()
    api_url = HERMES_API_URL.strip()
    model = HERMES_MODEL.strip()

    if not api_key:
        return {
            "mode": "local-fallback", "status": "pending",
            "message": "No Hermes API key configured.",
            "fallback_checks": _local_hermes_fallback(results_per_industry),
        }

    # 收集每个行业的 wiki 摘要
    industry_summaries: list[str] = []
    for r in results_per_industry:
        slug = r["slug"]
        name = r["industry"]
        cfg_path = PROJECT_ROOT / "storage" / slug / "industry.yaml"
        cfg_text = cfg_path.read_text(encoding="utf-8")[:1500] if cfg_path.exists() else "(no config)"
        # 收集该行业相关 wiki 页的前 500 字符
        wiki_snippets = ""
        wiki_dir = PROJECT_ROOT / "wiki"
        if wiki_dir.exists():
            for md_file in list(wiki_dir.rglob("*.md"))[:5]:
                try:
                    wiki_snippets += f"\n--- {md_file.name} ---\n{md_file.read_text(encoding='utf-8')[:300]}"
                except Exception:
                    pass
        industry_summaries.append(
            f"## {name} ({slug})\n\n**Config**:\n{cfg_text}\n\n**Wiki samples**:\n{wiki_snippets[:1000]}"
        )

    prompt = f"""你是 FlowWiki 知识库质量评审专家。请评审以下 4 个行业知识库的完整性和质量。

{"".join(industry_summaries)}

请从以下维度评分（每项 1-10 分），并给出简短理由：

1. **结构完整性**：wiki 目录结构是否合理，concepts/playbooks/comparisons 是否齐全
2. **内容准确性**：wiki 内容与 industry.yaml 定义是否一致
3. **关联性**：概念之间是否有合理的交叉引用
4. **可操作性**：playbook 是否可执行，步骤是否清晰
5. **整体质量**：综合评分

请用以下 JSON 格式回复（只输出 JSON，不要其他文字）：
```json
{{
  "reviews": [
    {{"industry": "root-cause", "scores": {{"结构": x, "内容": x, "关联": x, "操作": x, "整体": x}}, "verdict": "pass|needs_attention", "notes": "简要说明"}},
    ...
  ],
  "overall_verdict": "pass|needs_attention",
  "top_issues": ["最严重的问题1", "问题2", ...]
}}
```"""

    try:
        payload = json.dumps({
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a knowledge base quality reviewer. Always respond in Chinese. Only output valid JSON."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
            "max_tokens": 2048,
        }).encode("utf-8")

        req = urllib.request.Request(
            api_url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
        )
        with urllib.request.urlopen(req, timeout=HERMES_TIMEOUT) as resp:
            raw = json.loads(resp.read())
            content = raw["choices"][0]["message"]["content"]

            # Extract JSON from response
            json_start = content.find("{")
            json_end = content.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                result = json.loads(content[json_start:json_end])
                result["mode"] = "llm"
                result["model_used"] = model
                return result
            else:
                return {
                    "mode": "llm", "status": "parse_error",
                    "model_used": model, "raw_response": content[:500],
                    "fallback_checks": _local_hermes_fallback(results_per_industry),
                }

    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:500]
        return {
            "mode": "llm", "status": "api_error",
            "error": f"HTTP {e.code}: {body}",
            "fallback_checks": _local_hermes_fallback(results_per_industry),
        }
    except Exception as e:
        return {
            "mode": "llm", "status": "connection_error",
            "error": str(e)[:300],
            "fallback_checks": _local_hermes_fallback(results_per_industry),
        }


def _local_hermes_fallback(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Local ACE-style verification without Hermes API."""
    checks = {}
    for r in results:
        slug = r["slug"]
        issues = []

        # Check if wiki has content for this industry
        concept_dir = PROJECT_ROOT / "wiki" / "concepts"
        if concept_dir.exists():
            industry_concepts = [
                f for f in concept_dir.glob("*.md")
                if slug in f.read_text(encoding="utf-8").lower()[:500]
            ]
            if not industry_concepts:
                issues.append(f"No concepts found for {slug}")
            checks[slug] = {
                "concept_count": len(industry_concepts),
                "issues": issues,
                "verdict": "ok" if not issues else "needs_attention",
            }
        else:
            checks[slug] = {"concept_count": 0, "issues": ["wiki/concepts/ not found"], "verdict": "needs_attention"}

    return checks


# ---------------------------------------------------------------------------
# Phase 5: Docker check (if installed)
# ---------------------------------------------------------------------------

def phase5_docker_check() -> dict[str, Any]:
    """Verify Docker build succeeds."""
    dockerfile = PROJECT_ROOT / "Dockerfile"
    if not dockerfile.exists():
        return {"status": "skipped", "message": "Dockerfile not found"}

    try:
        proc = subprocess.run(
            ["docker", "build", "--no-cache", "-t", "flowwiki:test", "."],
            capture_output=True, text=True, timeout=300,
            cwd=str(PROJECT_ROOT),
        )
        return {
            "status": "pass" if proc.returncode == 0 else "fail",
            "output": proc.stdout.strip()[-300:] + proc.stderr.strip()[-300:],
        }
    except FileNotFoundError:
        return {"status": "skipped", "message": "Docker not installed"}
    except Exception as e:
        return {"status": "error", "error": str(e)[:200]}


# ---------------------------------------------------------------------------
# Phase 6: 关系图质量检测（4 个知识库的 wikilink 图谱质量）
# ---------------------------------------------------------------------------

# 质量阈值
GRAPH_QUALITY_THRESHOLDS = {
    "min_density": 0.30,          # 边/节点比至少 0.3
    "max_isolation_pct": 40.0,    # 孤立节点不超过 40%
    "max_broken_links": 3,        # 断链不超过 3 个
    "min_coverage_pct": 50.0,     # industry.yaml 概念至少 50% 出现在图中
}

WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
MDLINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def _extract_graph_from_wiki() -> dict[str, dict[str, Any]]:
    """从 wiki/ 所有页面提取 wikilink 图谱。"""
    wiki_dir = PROJECT_ROOT / "wiki"
    graph: dict[str, dict[str, Any]] = {}
    all_pages: set[str] = set()

    if not wiki_dir.exists():
        return graph

    # 收集所有有效页面名
    for md_file in wiki_dir.rglob("*.md"):
        if md_file.name in ("index.md", "log.md", "README.md"):
            continue
        rel = str(md_file.relative_to(wiki_dir))
        page_id = rel.replace(".md", "")
        all_pages.add(page_id)

    # 提取每个页面的链接
    for md_file in wiki_dir.rglob("*.md"):
        if md_file.name in ("index.md", "log.md", "README.md"):
            continue
        rel = str(md_file.relative_to(wiki_dir))
        page_id = rel.replace(".md", "")

        try:
            text = md_file.read_text(encoding="utf-8")
        except Exception:
            continue

        outlinks: list[str] = []
        broken: list[str] = []

        # [[wikilink]]
        for m in WIKILINK_RE.finditer(text):
            target = m.group(1).split("|")[0].strip()
            outlinks.append(target)
            # 检查是否为有效页面
            if target not in all_pages and not target.endswith((".png", ".jpg", ".svg", ".pdf")):
                broken.append(target)

        # markdown links
        for m in MDLINK_RE.finditer(text):
            path = m.group(2)
            if path.startswith(("http://", "https://", "#")):
                continue
            target_basename = path.rsplit("/", 1)[-1] if "/" in path else path
            if target_basename.endswith(".md"):
                target_name = target_basename.replace(".md", "")
                outlinks.append(target_name)
                if target_name not in all_pages:
                    broken.append(target_name)

        graph[page_id] = {
            "file": rel,
            "outlinks": outlinks,
            "broken": broken,
            "out_count": len(outlinks),
            "broken_count": len(broken),
        }

    # 计算入链
    for pid in graph:
        graph[pid]["in_count"] = 0
        graph[pid]["inlinks_from"] = []
    for pid, info in graph.items():
        for target in info["outlinks"]:
            if target in graph:
                graph[target]["in_count"] += 1
                graph[target]["inlinks_from"].append(pid)

    return graph


def _load_industry_yaml_concepts(slug: str) -> list[str]:
    """从 storage/{slug}/industry.yaml 提取概念/playbook/comparison 名称。"""
    config_path = PROJECT_ROOT / "storage" / slug / "industry.yaml"
    if not config_path.exists():
        return []

    concepts: list[str] = []
    try:
        import yaml
        data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        wiki_struct = data.get("wiki_structure", {}) if data else {}
        for section in ("concepts", "playbooks", "comparisons", "criteria"):
            for item in wiki_struct.get(section, []):
                concepts.append(item)
    except Exception:
        pass
    return concepts


def phase6_graph_quality() -> dict[str, Any]:
    """检查 4 个知识库的 wikilink 关系图质量。"""
    graph = _extract_graph_from_wiki()
    if not graph:
        return {"status": "skipped", "message": "No wiki pages found"}

    total_nodes = len(graph)
    total_edges = sum(info["out_count"] for info in graph.values())
    total_broken = sum(info["broken_count"] for info in graph.values())
    isolated = [
        pid for pid, info in graph.items()
        if info["out_count"] == 0 and info["in_count"] == 0
    ]
    isolated_pct = round(len(isolated) / total_nodes * 100, 1) if total_nodes else 0
    density = round(total_edges / total_nodes, 2) if total_nodes else 0

    # 按 industry 分组检查覆盖度
    industry_checks: list[dict[str, Any]] = []
    for ind in INDUSTRIES:
        slug = ind["slug"]
        name = ind["name"]
        expected = _load_industry_yaml_concepts(slug)
        if not expected:
            industry_checks.append({
                "industry": name, "slug": slug,
                "expected_count": 0, "found_count": 0,
                "coverage_pct": 0, "missing": [],
                "verdict": "skipped",
            })
            continue

        found = []
        missing = []
        for c in expected:
            # Match by basename (industry.yaml 概念名 vs graph key 如 "concepts/数据溯源链路")
            matched = False
            for gkey in graph:
                if gkey.endswith(f"/{c}") or gkey == c:
                    found.append(c)
                    matched = True
                    break
            if not matched:
                missing.append(c)
        cov_pct = round(len(found) / len(expected) * 100, 1) if expected else 0

        # 检查 found 概念之间的互联度（需要映射到 graph key）
        found_keys: dict[str, str] = {}  # concept_name → graph_key
        for c in found:
            for gkey in graph:
                if gkey.endswith(f"/{c}") or gkey == c:
                    found_keys[c] = gkey
                    break

        interlinked = 0
        for c, gkey in found_keys.items():
            if gkey in graph:
                out_targets = set(graph[gkey]["outlinks"])
                other_found_keys = {k for name, k in found_keys.items() if name != c}
                interlinked += len(out_targets & other_found_keys)
        inter_density = round(interlinked / len(found), 2) if found else 0

        verdict = "pass"
        if cov_pct < GRAPH_QUALITY_THRESHOLDS["min_coverage_pct"]:
            verdict = "needs_attention"
        if missing:
            verdict = "needs_attention"

        industry_checks.append({
            "industry": name, "slug": slug,
            "expected_count": len(expected), "found_count": len(found),
            "coverage_pct": cov_pct, "missing": missing,
            "inter_density": inter_density,
            "verdict": verdict,
        })

    # 综合评分
    checks = {
        "density": {"value": density, "threshold": GRAPH_QUALITY_THRESHOLDS["min_density"],
                     "pass": density >= GRAPH_QUALITY_THRESHOLDS["min_density"]},
        "isolation": {"value": isolated_pct, "threshold": GRAPH_QUALITY_THRESHOLDS["max_isolation_pct"],
                      "pass": isolated_pct <= GRAPH_QUALITY_THRESHOLDS["max_isolation_pct"]},
        "broken_links": {"value": total_broken, "threshold": GRAPH_QUALITY_THRESHOLDS["max_broken_links"],
                         "pass": total_broken <= GRAPH_QUALITY_THRESHOLDS["max_broken_links"]},
    }
    all_quality_pass = all(c["pass"] for c in checks.values())

    # 结构问题详情
    issues: list[str] = []
    if not checks["density"]["pass"]:
        issues.append(f"图密度过低: {density}（阈值 ≥ {GRAPH_QUALITY_THRESHOLDS['min_density']}），"
                      f"{total_nodes} 节点仅 {total_edges} 条边")
    if not checks["isolation"]["pass"]:
        issues.append(f"孤立节点过多: {isolated_pct}%（阈值 ≤ {GRAPH_QUALITY_THRESHOLDS['max_isolation_pct']}%），"
                      f"{len(isolated)} 个节点无任何连接")
    if not checks["broken_links"]["pass"]:
        broken_list = []
        for pid, info in graph.items():
            for b in info["broken"][:3]:
                broken_list.append(f"{pid} → '[[{b}]]'")
        issues.append(f"断链: {total_broken} 个（阈值 ≤ {GRAPH_QUALITY_THRESHOLDS['max_broken_links']}）: "
                      + "; ".join(broken_list[:5]))

    return {
        "status": "pass" if all_quality_pass else ("needs_attention" if issues else "warning"),
        "total_nodes": total_nodes,
        "total_edges": total_edges,
        "density": density,
        "isolated_nodes": len(isolated),
        "isolated_pct": isolated_pct,
        "broken_links": total_broken,
        "isolated_list": isolated[:20],
        "quality_checks": checks,
        "industry_coverage": industry_checks,
        "issues": issues,
    }


# ---------------------------------------------------------------------------
# Report generator
# ---------------------------------------------------------------------------

def generate_report(
    phase1: list[dict[str, Any]],
    phase2: dict[str, Any],
    phase3: list[dict[str, Any]],
    phase4: dict[str, Any],
    phase5: dict[str, Any],
    phase6: dict[str, Any],
    duration_sec: float,
) -> str:
    """Generate a Markdown report."""
    today = datetime.date.today().isoformat()
    p1_pass = sum(1 for r in phase1 if r["status"] == "pass")
    p1_total = len(phase1)
    p3_pass = sum(1 for r in phase3 if r["overall"] == "pass")
    p3_total = len(phase3)

    lines = [
        f"# FlowWiki 每日全量测试报告 — {today}",
        "",
        f"**执行时间**: {datetime.datetime.now().isoformat()} | **耗时**: {duration_sec:.1f}s",
        "",
        "## 总体结果",
        "",
        f"| 阶段 | 状态 | 详情 |",
        f"|------|------|------|",
        f"| Phase 1: 脚本编译 | {'✅' if p1_pass == p1_total else '⚠️'} | {p1_pass}/{p1_total} 通过 |",
        f"| Phase 2: CI Lint | {'✅' if phase2['status'] == 'pass' else '⚠️'} | {phase2['stats'].get('pages', 0)} 页 wiki |",
        f"| Phase 3: 4 知识库 | {'✅' if p3_pass == p3_total else '⚠️'} | {p3_pass}/{p3_total} 行业通过 |",
        f"| Phase 4: Hermes 验证 | {'✅' if phase4.get('status') in ('pass','ok','pending') else '⚠️'} | {phase4.get('mode', 'unknown')} |",
        f"| Phase 5: Docker | {'✅' if phase5.get('status') == 'pass' else '⏭️' if phase5.get('status') == 'skipped' else '⚠️'} | {phase5.get('message', phase5.get('status', ''))} |",
        f"| Phase 6: 关系图质量 | {'✅' if phase6.get('status') == 'pass' else '⚠️'} | {phase6.get('total_nodes', 0)} 节点 / {phase6.get('total_edges', 0)} 边 / {phase6.get('isolated_pct', 0)}% 孤立 |",
        "",
        "---",
        "",
        "## Phase 1: 脚本编译检查",
        "",
    ]

    # Phase 1 failures
    for r in phase1:
        icon = "✅" if r["status"] == "pass" else "❌"
        detail = f" — {r.get('error', '')}" if r["status"] != "pass" else ""
        lines.append(f"- {icon} {r['script']}{detail}")

    # Phase 2 details
    lines += [
        "",
        "## Phase 2: CI Lint 检查",
        "",
        f"- 状态: {phase2['status']}",
        f"- wiki 页数: {phase2['stats'].get('pages', 0)}",
        f"- frontmatter 完整: {phase2['stats'].get('with_frontmatter', 0)}",
    ]
    if phase2["errors"]:
        lines.append("### 发现问题")
        for e in phase2["errors"]:
            lines.append(f"- {e}")

    # Phase 3 details
    lines += ["", "## Phase 3: 4 知识库顺序跑", ""]
    for r in phase3:
        icon = "✅" if r["overall"] == "pass" else "❌"
        lines.append(f"### {icon} {r['industry']} ({r['slug']})")
        for step, detail in r.get("steps", {}).items():
            if step == "wiki_count":
                lines.append(f"- 页面数: {detail}")
            elif isinstance(detail, dict):
                lines.append(f"- {step}: {detail.get('status', '?')}")

    # Phase 4 details
    lines += ["", "## Phase 4: Hermes 验证", ""]
    lines.append(f"- 模式: {phase4.get('mode', '?')}")
    lines.append(f"- 状态: {phase4.get('status', '?')}")
    if phase4.get("message"):
        lines.append(f"- 备注: {phase4['message']}")
    if "fallback_checks" in phase4:
        for slug, check in phase4["fallback_checks"].items():
            lines.append(f"- {slug}: {check.get('verdict', '?')} ({check.get('concept_count', 0)} concepts)")

    # Phase 5
    lines += ["", "## Phase 5: Docker 构建", ""]
    lines.append(f"- 状态: {phase5.get('status', '?')}")

    # Phase 6 details
    lines += ["", "## Phase 6: 关系图质量检测", ""]
    if phase6.get("status") == "skipped":
        lines.append(f"- 状态: skipped — {phase6.get('message', '')}")
    else:
        lines.append(f"- 状态: {phase6.get('status', '?')}")
        lines.append(f"- 总节点: {phase6.get('total_nodes', 0)} | 总边: {phase6.get('total_edges', 0)}")
        lines.append(f"- 图密度: {phase6.get('density', 0)} | 孤立节点: {phase6.get('isolated_nodes', 0)} ({phase6.get('isolated_pct', 0)}%) | 断链: {phase6.get('broken_links', 0)}")

        # Quality checks
        qc = phase6.get("quality_checks", {})
        if qc:
            lines.append("")
            lines.append("### 质量指标")
            lines.append("")
            lines.append("| 指标 | 值 | 阈值 | 通过 |")
            lines.append("|------|-----|------|------|")
            for metric_name, check in qc.items():
                icon = "✅" if check.get("pass") else "❌"
                label = {"density": "图密度", "isolation": "孤立率", "broken_links": "断链数"}.get(metric_name, metric_name)
                lines.append(f"| {label} | {check.get('value')} | {check.get('threshold')} | {icon} |")

        # Industry coverage
        ic = phase6.get("industry_coverage", [])
        if ic:
            lines.append("")
            lines.append("### 4 知识库覆盖度")
            lines.append("")
            lines.append("| 知识库 | 期望概念 | 已覆盖 | 覆盖率 | 互联密度 | 状态 |")
            lines.append("|--------|----------|--------|--------|----------|------|")
            for item in ic:
                icon = "✅" if item["verdict"] == "pass" else "⚠️"
                lines.append(f"| {item['industry']} | {item['expected_count']} | {item['found_count']} | {item['coverage_pct']}% | {item['inter_density']} | {icon} |")
                if item.get("missing"):
                    lines.append(f"| ↳ 缺失: {', '.join(item['missing'][:5])} | | | | | |")

        # Issues
        if phase6.get("issues"):
            lines.append("")
            lines.append("### 发现的问题")
            for issue in phase6["issues"]:
                lines.append(f"- ❌ {issue}")

        # Isolated nodes list
        if phase6.get("isolated_list"):
            lines.append("")
            lines.append(f"### 孤立节点（{len(phase6['isolated_list'])}）")
            for nid in phase6["isolated_list"][:10]:
                lines.append(f"- `{nid}`")

    lines += [
        "",
        "---",
        f"*自动生成于 {datetime.datetime.now().isoformat()}*",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="FlowWiki Daily Full Test")
    parser.add_argument("--quick", action="store_true", help="Quick mode (lint only)")
    parser.add_argument("--industry", help="Run single industry only")
    args = parser.parse_args()

    start = datetime.datetime.now()
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    logger.info("=" * 60)
    logger.info("FlowWiki Daily Full Test — %s", start.isoformat())
    logger.info("=" * 60)

    # Phase 1
    logger.info("[Phase 1] Script syntax check...")
    phase1 = phase1_script_syntax()
    p1_ok = sum(1 for r in phase1 if r["status"] == "pass")
    logger.info("  %d/%d scripts passed", p1_ok, len(phase1))
    for r in phase1:
        if r["status"] != "pass":
            logger.warning("  FAIL: %s — %s", r["script"], r.get("error", ""))

    # Phase 2
    logger.info("[Phase 2] CI lint check...")
    phase2 = phase2_ci_lint()
    logger.info("  Status: %s | %d pages", phase2["status"], phase2["stats"]["pages"])

    # Phase 3
    industries = INDUSTRIES
    if args.industry:
        industries = [i for i in INDUSTRIES if i["slug"] == args.industry]
        if not industries:
            logger.error("Unknown industry: %s", args.industry)
            sys.exit(1)

    phase3 = []
    for industry in industries:
        logger.info("[Phase 3] Running '%s' (%s)...", industry["name"], industry["slug"])
        result = phase3_industry_run(industry)
        phase3.append(result)
        logger.info("  Overall: %s", result["overall"])

    # Phase 4
    logger.info("[Phase 4] Hermes verification...")
    phase4 = phase4_hermes_verify(phase3)
    logger.info("  Mode: %s | Status: %s", phase4.get("mode"), phase4.get("status"))

    # Phase 5
    if not args.quick:
        logger.info("[Phase 5] Docker build check...")
        phase5 = phase5_docker_check()
    else:
        phase5 = {"status": "skipped", "message": "quick mode"}
    logger.info("  Status: %s", phase5.get("status"))

    # Phase 6
    logger.info("[Phase 6] Relationship graph quality check...")
    phase6 = phase6_graph_quality()
    logger.info("  Status: %s | %d nodes / %d edges / %.1f%% isolated",
                phase6.get("status"), phase6.get("total_nodes", 0),
                phase6.get("total_edges", 0), phase6.get("isolated_pct", 0))

    # Generate report
    duration = (datetime.datetime.now() - start).total_seconds()
    logger.info("Generating reports... (%.1fs total)", duration)

    report_md = generate_report(phase1, phase2, phase3, phase4, phase5, phase6, duration)
    report_json = json.dumps({
        "date": datetime.date.today().isoformat(),
        "duration_sec": duration,
        "phase1": phase1,
        "phase2": phase2,
        "phase3": phase3,
        "phase4": phase4,
        "phase5": phase5,
        "phase6": phase6,
    }, ensure_ascii=False, indent=2)

    today = datetime.date.today().isoformat()
    md_path = REPORT_DIR / f"daily-test-{today}.md"
    json_path = REPORT_DIR / f"daily-test-{today}.json"

    md_path.write_text(report_md, encoding="utf-8")
    json_path.write_text(report_json, encoding="utf-8")

    logger.info("Report saved:")
    logger.info("  Markdown: %s", md_path)
    logger.info("  JSON:     %s", json_path)

    # Exit code
    all_pass = (
        all(r["status"] == "pass" for r in phase1)
        and phase2["status"] == "pass"
        and all(r["overall"] == "pass" for r in phase3)
    )
    if all_pass:
        logger.info("ALL CHECKS PASSED ✅")
        ops_log("daily_test", f"{p1_ok}/{p1_total} scripts, {p3_pass}/{p3_total} industries, {phase6.get('total_nodes',0)} nodes", {"duration": duration}, status="ok")
    else:
        logger.error("SOME CHECKS FAILED ⚠️")
        ops_log("daily_test", f"FAILED: {p1_ok}/{p1_total} scripts, {p3_pass}/{p3_total} industries", {"duration": duration}, status="error")
        sys.exit(1)


if __name__ == "__main__":
    main()
