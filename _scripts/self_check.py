#!/usr/bin/env python3
"""
FlowWiki AI 自检引擎
定时扫描知识库健康度，输出结构化自检报告。
"""

import json
import sys
import re
import os
import yaml
import subprocess
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WIKI_DIR = PROJECT_ROOT / "wiki"
RAW_DIR = PROJECT_ROOT / "raw"
HOME_DIR = PROJECT_ROOT / "00_首页"
MEMORY_DIR = PROJECT_ROOT / ".memory"

IGNORE_DIRS = {
    ".git", "node_modules", "dist", "build",
    ".obsidian", "__pycache__", ".venv", "venv",
}

SEVERITY_SCORE = {"critical": 100, "high": 50, "medium": 20, "low": 5, "info": 1}


def should_skip(path: Path) -> bool:
    return any(part in IGNORE_DIRS for part in path.parts)


def parse_frontmatter(filepath: Path):
    text = filepath.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return None, "缺少 frontmatter"
    try:
        data = yaml.safe_load(match.group(1))
        if data is None:
            data = {}
        return data, None
    except yaml.YAMLError as e:
        return None, f"YAML 解析错误: {e}"


def get_body(filepath: Path) -> str:
    text = filepath.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n.*?\n---\s*\n?(.*)", text, re.DOTALL)
    return match.group(1) if match else text


def add_issue(issues, category, severity, file, message, fixable=False, fix_hint=""):
    issues.append({
        "category": category,
        "severity": severity,
        "file": file,
        "message": message,
        "fixable": fixable,
        "fix_hint": fix_hint,
    })


def check_structure():
    issues = []

    required_dirs = [
        ("raw", "high"),
        ("wiki", "high"),
        ("00_首页", "high"),
        ("spec", "medium"),
        (".memory", "medium"),
        (".agents/skills", "medium"),
    ]
    for d, sev in required_dirs:
        if not (PROJECT_ROOT / d).is_dir():
            add_issue(issues, "structure", sev, d,
                      f"缺少目录: {d}", fixable=True, fix_hint=f"mkdir -p {d}")

    required_files = [
        ("SCHEMA.md", "high"),
        ("README.md", "medium"),
        ("LICENSE", "low"),
        (".gitignore", "medium"),
        ("wiki/index.md", "high"),
        ("wiki/log.md", "medium"),
        ("00_首页/README.md", "high"),
    ]
    for f, sev in required_files:
        if not (PROJECT_ROOT / f).exists():
            add_issue(issues, "structure", sev, f, f"缺少文件: {f}", fixable=False)

    home_sections = [
        "01_知识图谱", "02_判据体系", "03_实战场景",
        "04_进化学习", "05_采集记录", "06_系统运维"
    ]
    for sec in home_sections:
        if not (HOME_DIR / sec / "README.md").exists():
            add_issue(issues, "structure", "medium",
                      f"00_首页/{sec}/README.md",
                      f"首页板块缺失: {sec}",
                      fixable=True, fix_hint=f"创建 00_首页/{sec}/README.md")

    return issues


def check_lint():
    issues = []

    if not WIKI_DIR.is_dir():
        return issues

    required_fields = [
        "type", "title", "created", "updated",
        "confidence", "sources", "tags", "status",
    ]
    valid_confidence = {"low", "medium", "high"}
    valid_status = {"draft", "reviewed", "archived", "active"}
    valid_filename_re = re.compile(r"^[\w\u4e00-\u9fff\u3400-\u4dbf\-]+\.md$")

    for md_file in sorted(WIKI_DIR.rglob("*.md")):
        if should_skip(md_file):
            continue
        if md_file.name in ("index.md", "log.md", "README.md"):
            continue
        if md_file.parent.name == "meta":
            continue

        rel_path = str(md_file.relative_to(PROJECT_ROOT))

        if not valid_filename_re.match(md_file.name):
            add_issue(issues, "lint", "medium", rel_path,
                      f"文件名不规范: {md_file.name}",
                      fixable=True, fix_hint="重命名为合法格式")

        data, err = parse_frontmatter(md_file)
        if err:
            add_issue(issues, "lint", "high", rel_path,
                      f"frontmatter 错误: {err}",
                      fixable=True, fix_hint="补全/修复 frontmatter")
            continue
        if data is None:
            continue

        missing_fields = [
            f for f in required_fields
            if f not in data or data[f] is None
        ]
        if missing_fields:
            add_issue(issues, "lint", "high", rel_path,
                      f"缺少必填字段: {', '.join(missing_fields)}",
                      fixable=True,
                      fix_hint=f"补全字段: {', '.join(missing_fields)}")

        conf = data.get("confidence", "")
        if conf and conf not in valid_confidence:
            add_issue(issues, "lint", "medium", rel_path,
                      f"confidence 无效: '{conf}'",
                      fixable=True, fix_hint="修正为 low/medium/high")

        status = data.get("status", "")
        if status and status not in valid_status:
            add_issue(issues, "lint", "medium", rel_path,
                      f"status 无效: '{status}'",
                      fixable=True, fix_hint="修正为 draft/reviewed/archived/active")

        tags = data.get("tags", [])
        if isinstance(tags, list) and "flow-wiki" not in tags:
            add_issue(issues, "lint", "low", rel_path,
                      "tags 缺少 flow-wiki",
                      fixable=True, fix_hint="添加 flow-wiki 标签")

        sources = data.get("sources", [])
        if isinstance(sources, list) and len(sources) == 0:
            if data.get("confidence") != "low":
                add_issue(issues, "lint", "medium", rel_path,
                          "sources 为空且 confidence 非 low",
                          fixable=False, fix_hint="需人工补充引用来源")

        body = get_body(md_file)
        internal_links = []
        for m in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", body):
            target = m.group(2)
            if not target.startswith(("http://", "https://", "/")):
                internal_links.append(("mdlink", target))
        for m in re.finditer(r"\[\[([^\]]+)\]\]", body):
            target = m.group(1).split("|")[0].strip()
            internal_links.append(("wikilink", target))

        for link_type, target in internal_links:
            resolved = None
            if link_type == "mdlink":
                candidate = (md_file.parent / target).resolve()
                if candidate.exists():
                    resolved = candidate
            elif link_type == "wikilink":
                name = target if target.endswith(".md") else target + ".md"
                for cat_dir in sorted(WIKI_DIR.iterdir()):
                    if not cat_dir.is_dir():
                        continue
                    candidate = cat_dir / name
                    if candidate.exists():
                        resolved = candidate
                        break
            if resolved is None:
                add_issue(issues, "lint", "medium", rel_path,
                          f"悬空链接: {target}",
                          fixable=False, fix_hint="需人工确认链接目标")

    return issues


def check_content_quality():
    issues = []

    if not WIKI_DIR.is_dir():
        return issues

    page_data = {}
    for md_file in sorted(WIKI_DIR.rglob("*.md")):
        if should_skip(md_file) or md_file.name in ("index.md", "log.md", "README.md"):
            continue
        if md_file.parent.name == "meta":
            continue
        data, _ = parse_frontmatter(md_file)
        if data:
            rel = str(md_file.relative_to(PROJECT_ROOT))
            page_data[rel] = {
                "title": data.get("title", md_file.stem),
                "confidence": data.get("confidence", "unknown"),
                "status": data.get("status", "unknown"),
                "sources": data.get("sources", []),
                "body": get_body(md_file),
            }

    if page_data:
        low_conf = sum(1 for v in page_data.values() if v["confidence"] == "low")
        low_conf_ratio = low_conf / len(page_data)
        if low_conf_ratio > 0.5:
            add_issue(issues, "content", "high", "wiki/",
                      f"低置信度页面占比过高: {low_conf_ratio:.0%} ({low_conf}/{len(page_data)})",
                      fixable=False, fix_hint="需人工补充高质量原始资料")

    contradiction_signals = ["不一致", "矛盾", "冲突", "相反"]
    for rel, info in page_data.items():
        body = info["body"]
        hits = [s for s in contradiction_signals if s in body]
        if len(hits) >= 2:
            add_issue(issues, "content", "medium", rel,
                      f"疑似存在矛盾表述（信号: {', '.join(hits)}）",
                      fixable=False, fix_hint="需人工核实内容一致性")

    for rel, info in page_data.items():
        body = info["body"]
        has_link = "[[" in body or "](." in body or "](/" in body
        if not has_link:
            add_issue(issues, "content", "low", rel,
                      "孤立页面（无内部链接）",
                      fixable=False, fix_hint="建议添加相关页面链接")

    return issues


def check_external_benchmark():
    issues = []

    skip_benchmark = os.environ.get("FLOW_WIKI_SKIP_BENCHMARK", "0") == "1"
    if skip_benchmark:
        add_issue(issues, "benchmark", "low", "外部对标",
                  "已跳过竞品对标分析",
                  fixable=False, fix_hint="设置 FLOW_WIKI_SKIP_BENCHMARK=0 启用")
        return issues

    benchmark_script = PROJECT_ROOT / "_scripts" / "benchmark_competitors.py"
    if not benchmark_script.exists():
        add_issue(issues, "benchmark", "high", "外部对标",
                  "竞品对标脚本缺失",
                  fixable=False, fix_hint="检查 _scripts/benchmark_competitors.py")
        return issues

    try:
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            tmp_json = tf.name

        result = subprocess.run(
            [
                sys.executable,
                str(benchmark_script),
                tmp_json,
            ],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(PROJECT_ROOT),
        )

        if result.returncode != 0:
            add_issue(issues, "benchmark", "medium", "外部对标",
                      f"对标分析执行失败: {result.stderr[:200]}",
                      fixable=False, fix_hint="检查 GitHub API 连接或 token")
            return issues

        try:
            with open(tmp_json, encoding="utf-8") as f:
                data = json.load(f)

            suggestions = data.get("gap_suggestions", [])
            competitors_count = data.get("competitor_count", 0)

            add_issue(issues, "benchmark", "info", "外部对标",
                      f"对标 {competitors_count} 个竞品，生成 {len(suggestions)} 条改进建议",
                      fixable=True, fix_hint="生成 wiki/meta/competitor-benchmark.md")

            high_urgency = [s for s in suggestions if s.get("urgency") == "high"]
            for s in high_urgency[:3]:
                add_issue(issues, "benchmark", "medium",
                          f"对标/{s['dimension']}",
                          s["comment"],
                          fixable=False, fix_hint=f"参考竞品: {s.get('top_competitor_with_feature', '无')}")

            benchmark_report_path = PROJECT_ROOT / "wiki" / "meta" / "competitor-benchmark.md"
            benchmark_report_path.parent.mkdir(parents=True, exist_ok=True)

        except Exception as e:
            add_issue(issues, "benchmark", "medium", "外部对标",
                      f"解析对标结果失败: {str(e)[:100]}",
                      fixable=False, fix_hint="检查输出格式")
        finally:
            try:
                os.unlink(tmp_json)
            except Exception:
                pass

    except subprocess.TimeoutExpired:
        add_issue(issues, "benchmark", "low", "外部对标",
                  "竞品对标超时（60s）",
                  fixable=False, fix_hint="网络可能较慢，已跳过")
    except Exception as e:
        add_issue(issues, "benchmark", "low", "外部对标",
                  f"对标分析异常: {str(e)[:100]}",
                  fixable=False, fix_hint="已跳过，不影响核心流程")

    return issues


def check_dual_index_sync():
    issues = []

    wiki_index = PROJECT_ROOT / "wiki" / "index.md"
    home_readme = HOME_DIR / "README.md"

    if not wiki_index.exists():
        add_issue(issues, "sync", "high", "wiki/index.md",
                  "机器索引不存在",
                  fixable=True, fix_hint="运行 sync_dual_index.py")
    if not home_readme.exists():
        add_issue(issues, "sync", "high", "00_首页/README.md",
                  "人类索引不存在",
                  fixable=True, fix_hint="运行 sync_dual_index.py")

    if wiki_index.exists() and WIKI_DIR.is_dir():
        index_content = wiki_index.read_text(encoding="utf-8")
        wiki_pages = [
            f for f in WIKI_DIR.rglob("*.md")
            if f.name not in ("index.md", "log.md", "README.md")
            and f.parent.name != "meta"
            and not should_skip(f)
        ]
        referenced = 0
        for page in wiki_pages:
            if page.stem in index_content or page.name in index_content:
                referenced += 1
        if wiki_pages and referenced / len(wiki_pages) < 0.5:
            add_issue(issues, "sync", "medium", "wiki/index.md",
                      f"索引覆盖率低: {referenced}/{len(wiki_pages)} 页面被索引",
                      fixable=True, fix_hint="运行 sync_dual_index.py 更新索引")

    return issues


def compute_health_score(issues):
    total_penalty = 0
    by_category = {}
    by_severity = {}

    for issue in issues:
        score = SEVERITY_SCORE.get(issue["severity"], 0)
        total_penalty += score
        cat = issue["category"]
        by_category[cat] = by_category.get(cat, 0) + 1
        sev = issue["severity"]
        by_severity[sev] = by_severity.get(sev, 0) + 1

    health_score = max(0, 100 - total_penalty)
    health_level = (
        "excellent" if health_score >= 90
        else "good" if health_score >= 70
        else "fair" if health_score >= 50
        else "poor"
    )

    return {
        "score": health_score,
        "level": health_level,
        "total_issues": len(issues),
        "fixable_count": sum(1 for i in issues if i["fixable"]),
        "by_category": by_category,
        "by_severity": by_severity,
    }


def main():
    output_path = sys.argv[1] if len(sys.argv) > 1 else None

    print("=" * 60)
    print("  FlowWiki AI 自检引擎")
    print(f"  扫描时间: {datetime.now().isoformat()}")
    print("=" * 60)

    all_issues = []

    print("\n[1/5] 检查结构完整性...")
    struct_issues = check_structure()
    all_issues.extend(struct_issues)
    print(f"  -> 发现 {len(struct_issues)} 个结构问题")

    print("\n[2/5] 运行 Lint 检查...")
    lint_issues = check_lint()
    all_issues.extend(lint_issues)
    print(f"  -> 发现 {len(lint_issues)} 个 Lint 问题")

    print("\n[3/5] 评估内容质量...")
    content_issues = check_content_quality()
    all_issues.extend(content_issues)
    print(f"  -> 发现 {len(content_issues)} 个内容质量问题")

    print("\n[4/5] 检查双索引同步...")
    sync_issues = check_dual_index_sync()
    all_issues.extend(sync_issues)
    print(f"  -> 发现 {len(sync_issues)} 个同步问题")

    print("\n[5/5] 外部竞品对标分析...")
    benchmark_issues = check_external_benchmark()
    all_issues.extend(benchmark_issues)
    print(f"  -> 发现 {len(benchmark_issues)} 个对标差距")

    health = compute_health_score(all_issues)

    print("\n" + "=" * 60)
    print("  自检结果汇总")
    print("=" * 60)
    print(f"  健康评分: {health['score']}/100  ({health['level']})")
    print(f"  问题总数: {health['total_issues']}")
    print(f"  可自动修复: {health['fixable_count']}")
    print(f"  按严重程度: {health['by_severity']}")
    print(f"  按类别: {health['by_category']}")

    benchmark_data = None
    if benchmark_issues:
        for issue in benchmark_issues:
            if issue.get("severity") == "info":
                benchmark_data = {"status": "ok", "message": issue["message"]}
                break

    report = {
        "timestamp": datetime.now().isoformat(),
        "project_root": str(PROJECT_ROOT),
        "health": health,
        "issues": all_issues,
        "benchmark": benchmark_data,
    }

    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            json.dumps(report, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"\n  报告已保存: {output_path}")

    if all_issues:
        print("\n  TOP 问题预览:")
        for issue in all_issues[:10]:
            icon = "🔧" if issue["fixable"] else "👤"
            print(f"    {icon} [{issue['severity']}] {issue['file']}: {issue['message']}")

    has_critical = any(i["severity"] == "critical" for i in all_issues)
    sys.exit(1 if has_critical else 0)


if __name__ == "__main__":
    main()
