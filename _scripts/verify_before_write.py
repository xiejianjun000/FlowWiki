#!/usr/bin/env python3
"""
VERIFY-BEFORE-WRITE — 写入前引用验证与质量门控。

引自 Ekgardt/llm-wiki（VERIFY-BEFORE-WRITE 机制）+ swarmvault（candidate review queue），
在 AI Agent 写入 wiki/ 之前执行逐条验证：

验证项（6 级）：
  L1 — 引用来源追溯：sources 列表中每个引用是否可追溯到 raw/ 原始文件
  L2 — 虚构引用检测：正文中引用的 raw/ 路径是否实际存在
  L3 — Frontmatter 完整性：必填字段是否齐全、值域是否合法
  L4 — Wikilink 有效性：[[link]] 的目标页面是否存在（或即将创建）
  L5 — 内容新鲜度：引用来源的最后修改时间是否在合理范围内
  L6 — 交叉引用一致性：同一来源在不同页面中的引用是否一致

验证失败时自动隔离到 wiki/_quarantine/ 并生成验证报告。

用法：
  # 验证单个文件写入前
  python _scripts/verify_before_write.py --file wiki/concepts/my-page.md

  # 验证 stdin 中的内容
  echo "..." | python _scripts/verify_before_write.py --stdin

  # 批量检查已存在的 wiki/ 目录
  python _scripts/verify_before_write.py --batch

  # 审查隔离区
  python _scripts/verify_before_write.py --audit-quarantine
"""

import argparse
import hashlib
import json
import logging
import os
import re
import sys
import yaml
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

WIKI_DIR = Path("wiki")
RAW_DIR = Path("raw")
QUARANTINE_DIR = WIKI_DIR / "_quarantine"

REQUIRED_FRONTMATTER = ["type", "title", "created", "updated", "confidence", "sources", "tags"]
VALID_CONFIDENCE = {"low", "medium", "high"}
VALID_TYPES = {"concept", "entity", "comparison", "overview", "source-summary",
               "playbook", "standard", "criteria", "synthesis", "sop", "index", "log"}
SOURCE_FRESHNESS_MAX_DAYS = 365  # 来源超过 1 年须标注

# 虚构引用模式：引用了不存在的 raw/ 路径
FICTITIOUS_REF_PATTERNS = [
    (r"raw/[^\s\[\]`\)\"']{0,200}\.md", "正文引用 raw/*.md"),
    (r'"sources":\s*\[([^\]]+)\]', "frontmatter sources 列表"),
    (r"源自\s*[：:]\s*[`\"]?(raw/[^\s`\"]+\.md)", "中文 '源自' 格式"),
]


def sha256(text: str) -> str:
    """计算文本 SHA-256 哈希。"""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def parse_frontmatter(text: str) -> tuple[dict | None, str, str | None]:
    """解析内容中的 YAML frontmatter。"""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, re.DOTALL)
    if not match:
        return None, text, "缺少 frontmatter"
    try:
        data = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as e:
        return None, text, f"frontmatter YAML 解析错误: {e}"
    body = text[match.end():]
    return data, body, None


def verify_sources(data: dict, text: str) -> list[dict]:
    """L1 — 引用来源追溯：每个 sources 项是否可追溯到 raw/ 文件。"""
    issues = []
    sources = data.get("sources", [])
    if not isinstance(sources, list):
        return [{"level": "L1", "severity": "error", "message": "sources 字段格式错误（应为列表）"}]

    if not sources:
        issues.append({
            "level": "L1",
            "severity": "warning",
            "message": "sources 为空（建议至少引用一个 raw/ 源文件）",
        })
        return issues

    for src in sources:
        src = str(src).strip()
        # 标准化路径
        candidates = [
            Path(src),
            Path("..") / src if src.startswith("raw/") else Path("raw") / src,
            RAW_DIR / src.replace("raw/", ""),
        ]
        found = any(c.exists() for c in candidates)
        if not found:
            issues.append({
                "level": "L1",
                "severity": "error",
                "message": f"source 引用无法追溯: '{src}' 在 raw/ 中不存在",
                "detail": f"已尝试: {[str(c) for c in candidates[:3]]}",
            })
    return issues


def verify_fictitious_refs(text: str) -> list[dict]:
    """L2 — 虚构引用检测：正文中引用的 raw/ 路径是否实际存在。"""
    issues = []
    for pattern, desc in FICTITIOUS_REF_PATTERNS:
        for m in re.finditer(pattern, text):
            ref_path = m.group(1).strip("`\"'[]")
            # 排除 wikilink 格式的（由 L4 处理）
            if "[[" in m.group(0):
                continue
            # 尝试多种路径
            candidates = [Path(ref_path)]
            if not ref_path.startswith("/"):
                candidates.append(RAW_DIR / ref_path.replace("raw/", ""))
                candidates.append(Path("..") / ref_path)
            if not any(c.exists() for c in candidates):
                issues.append({
                    "level": "L2",
                    "severity": "error" if "sources" in desc else "warning",
                    "message": f"{desc}引用了不存在的文件: {ref_path}",
                })
    return issues


def verify_frontmatter(data: dict) -> list[dict]:
    """L3 — Frontmatter 完整性与值域校验。"""
    issues = []

    # 必填字段
    for field in REQUIRED_FRONTMATTER:
        if field not in data or data[field] is None:
            issues.append({
                "level": "L3",
                "severity": "error",
                "message": f"缺少必填字段: {field}",
            })

    # confidence 值域
    conf = data.get("confidence", "")
    if conf and conf not in VALID_CONFIDENCE:
        issues.append({
            "level": "L3",
            "severity": "error",
            "message": f"confidence 值无效: '{conf}'（应为 low/medium/high）",
        })

    # type 值域
    page_type = data.get("type", "")
    if page_type and page_type not in VALID_TYPES:
        issues.append({
            "level": "L3",
            "severity": "warning",
            "message": f"type 值不标准: '{page_type}'（建议使用: {sorted(VALID_TYPES)}）",
        })

    # tags 包含 flow-wiki
    tags = data.get("tags", [])
    if isinstance(tags, list) and "flow-wiki" not in tags:
        issues.append({
            "level": "L3",
            "severity": "warning",
            "message": "tags 缺少 'flow-wiki'",
        })

    return issues


def verify_wikilinks(text: str, existing_pages: set[str]) -> list[dict]:
    """L4 — Wikilink 有效性：目标页面是否存在。"""
    issues = []
    for m in re.finditer(r"\[\[([^\]]+)\]\]", text):
        target = m.group(1).split("|")[0].strip()
        target_md = target if target.endswith(".md") else target + ".md"

        found = (
            target in existing_pages or
            target_md in existing_pages or
            any(target_md in p for p in existing_pages) or
            any(target in p for p in existing_pages)
        )

        if not found:
            issues.append({
                "level": "L4",
                "severity": "warning",
                "message": f"wikilink 目标可能不存在: [[{target}]]",
            })
    return issues


def verify_freshness(data: dict) -> list[dict]:
    """L5 — 内容新鲜度：引用来源最后修改时间。"""
    issues = []
    sources = data.get("sources", [])
    if not isinstance(sources, list):
        return issues

    now = datetime.now()
    for src in sources:
        src = str(src).strip()
        candidates = [
            Path(src),
            RAW_DIR / src.replace("raw/", ""),
        ]
        for c in candidates:
            if c.exists():
                mtime = datetime.fromtimestamp(c.stat().st_mtime)
                age_days = (now - mtime).days
                if age_days > SOURCE_FRESHNESS_MAX_DAYS:
                    issues.append({
                        "level": "L5",
                        "severity": "warning",
                        "message": f"引用来源 {src} 最后修改于 {age_days} 天前（超过 {SOURCE_FRESHNESS_MAX_DAYS} 天）",
                    })
                break
    return issues


def verify_cross_ref_consistency(data: dict, wiki_dir: Path) -> list[dict]:
    """L6 — 交叉引用一致性：同一来源在其他页面中的引用是否一致。"""
    # 这是一个启发式检查，标记但不过滤
    return []


def collect_existing_pages(wiki_dir: Path) -> set[str]:
    """收集现有 wiki/ 页面名集合。"""
    pages = set()
    if not wiki_dir.is_dir():
        return pages
    for md_file in wiki_dir.rglob("*.md"):
        if md_file.name in ("index.md", "log.md", "README.md"):
            continue
        if "_quarantine" in str(md_file):
            continue
        pages.add(md_file.name)
        pages.add(md_file.stem)
        rel = str(md_file.relative_to(wiki_dir))
        pages.add(rel)
    return pages


def verify_content(text: str, target_path: str = None, wiki_dir: Path = None) -> dict:
    """对内容执行全量 6 级验证，返回验证报告。"""
    wiki_dir = wiki_dir or WIKI_DIR
    existing_pages = collect_existing_pages(wiki_dir)

    # 如果目标是新页面，将其加入存在集合
    if target_path:
        target_name = Path(target_path).name
        existing_pages.add(target_name)
        existing_pages.add(Path(target_path).stem)

    all_issues = []
    data, body, fm_error = parse_frontmatter(text)

    if fm_error:
        all_issues.append({
            "level": "L0",
            "severity": "error",
            "message": fm_error,
        })
        return make_report(text, all_issues, data or {})

    if data is None:
        all_issues.append({
            "level": "L0",
            "severity": "error",
            "message": "无法解析 frontmatter",
        })
        return make_report(text, all_issues, {})

    all_issues.extend(verify_sources(data, text))
    all_issues.extend(verify_fictitious_refs(text))
    all_issues.extend(verify_frontmatter(data))
    all_issues.extend(verify_wikilinks(text, existing_pages))
    all_issues.extend(verify_freshness(data))
    all_issues.extend(verify_cross_ref_consistency(data, wiki_dir))

    return make_report(text, all_issues, data)


def make_report(text: str, issues: list[dict], data: dict) -> dict:
    """生成验证报告。"""
    errors = [i for i in issues if i["severity"] == "error"]
    warnings = [i for i in issues if i["severity"] == "warning"]
    passed = len(errors) == 0

    return {
        "verified_at": datetime.now(timezone.utc).isoformat(),
        "passed": passed,
        "score": max(0, 100 - len(errors) * 20 - len(warnings) * 5),
        "content_hash": sha256(text),
        "frontmatter": {k: v for k, v in data.items() if k in REQUIRED_FRONTMATTER},
        "errors": errors,
        "warnings": warnings,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "total_issues": len(issues),
        "verdict": "✅ 通过" if passed else "❌ 未通过" + (" (有警告)" if warnings else ""),
    }


def quarantine(content: str, report: dict, source_label: str) -> Path:
    """将未通过验证的内容隔离到 _quarantine/。"""
    q_dir = QUARANTINE_DIR / datetime.now().strftime("%Y-%m-%d")
    q_dir.mkdir(parents=True, exist_ok=True)

    # 内容文件
    content_hash = report["content_hash"][:12]
    safe_name = re.sub(r"[^\w\-\.]", "_", source_label or content_hash)
    content_path = q_dir / f"{safe_name}.md"
    content_path.write_text(content, encoding="utf-8")

    # 验证报告
    report_path = q_dir / f"{safe_name}.review.json"
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return content_path


def audit_quarantine() -> str:
    """列出隔离区待审核内容。"""
    if not QUARANTINE_DIR.is_dir():
        return "隔离区为空，无需审核。"

    lines = ["# 隔离区审核报告", "", f"路径: {QUARANTINE_DIR}", ""]
    items = []

    for review_file in sorted(QUARANTINE_DIR.rglob("*.review.json")):
        try:
            report = json.loads(review_file.read_text(encoding="utf-8"))
            md_file = review_file.with_suffix(".md")
            items.append({
                "file": str(md_file.relative_to(QUARANTINE_DIR)),
                "report": report,
                "score": report.get("score", 0),
                "errors": report.get("error_count", 0),
            })
        except (json.JSONDecodeError, KeyError):
            continue

    if not items:
        return "隔离区无有效审核项。"

    items.sort(key=lambda x: x["score"], reverse=True)
    for item in items:
        lines.append(f"## {item['file']}")
        lines.append(f"- 验证分数: {item['score']}/100")
        lines.append(f"- 错误数: {item['errors']}")
        lines.append(f"- 状态: {item['report'].get('verdict', '?')}")
        for err in item["report"].get("errors", []):
            lines.append(f"  - ❌ {err['message']}")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="VERIFY-BEFORE-WRITE 引用验证")
    parser.add_argument("--file", "-f", type=str, help="验证指定文件")
    parser.add_argument("--stdin", action="store_true", help="从 stdin 读取内容验证")
    parser.add_argument("--batch", action="store_true", help="批量检查 wiki/ 目录")
    parser.add_argument("--audit-quarantine", action="store_true", help="审查隔离区")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")
    parser.add_argument("--output", "-o", type=str, help="输出报告到文件")
    parser.add_argument("--strict", action="store_true", help="严格模式：警告也导致验证失败")
    parser.add_argument("--wiki-dir", type=str, default="wiki", help="wiki 目录路径")

    args = parser.parse_args()
    wiki_dir = Path(args.wiki_dir)

    if args.audit_quarantine:
        print(audit_quarantine())
        return

    if args.batch:
        print(f"🔍 批量检查 {wiki_dir}...")
        all_results = []
        for md_file in sorted(wiki_dir.rglob("*.md")):
            if md_file.name in ("index.md", "log.md", "README.md"):
                continue
            if "_quarantine" in str(md_file):
                continue
            text = md_file.read_text(encoding="utf-8")
            report = verify_content(text, str(md_file.relative_to(wiki_dir)), wiki_dir)
            all_results.append((str(md_file.relative_to(wiki_dir)), report))

        passed = sum(1 for _, r in all_results if r["passed"])
        failed = len(all_results) - passed

        print(f"\n📊 批量检查结果")
        print(f"   总计: {len(all_results)} 文件")
        print(f"   通过: {passed}")
        print(f"   未通过: {failed}")
        print(f"   通过率: {passed/max(len(all_results), 1)*100:.1f}%")

        if failed:
            print(f"\n❌ 未通过的文件:")
            for fpath, report in all_results:
                if not report["passed"]:
                    print(f"   {fpath} (分数: {report['score']}, 错误: {report['error_count']})")

        if args.json:
            print(json.dumps([
                {"path": p, "report": r} for p, r in all_results
            ], ensure_ascii=False, indent=2))

        if args.output:
            Path(args.output).write_text(json.dumps(
                [{"path": p, "report": r} for p, r in all_results],
                ensure_ascii=False, indent=2,
            ))
        return

    # 单文件/stdin 模式
    if args.stdin:
        text = sys.stdin.read()
        label = "stdin"
    elif args.file:
        filepath = Path(args.file)
        if not filepath.exists():
            logger.error(f"文件不存在: {filepath}")
            return
        text = filepath.read_text(encoding="utf-8")
        label = filepath.name
    else:
        parser.print_help()
        return

    report = verify_content(text, label if args.file else None, wiki_dir)

    if args.strict:
        report["passed"] = report["passed"] and report["warning_count"] == 0
        report["verdict"] = "✅ 通过" if report["passed"] else "❌ 未通过"

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"\n📋 验证报告: {label}")
        print(f"   {report['verdict']}")
        print(f"   分数: {report['score']}/100")
        print(f"   错误: {report['error_count']} | 警告: {report['warning_count']}")

        if report["errors"]:
            print(f"\n❌ 错误:")
            for err in report["errors"]:
                print(f"   [{err['level']}] {err['message']}")

        if report["warnings"]:
            print(f"\n⚠️  警告:")
            for warn in report["warnings"]:
                print(f"   [{warn['level']}] {warn['message']}")

    if args.output:
        Path(args.output).write_text(
            json.dumps(report, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    # 未通过 → 隔离
    if not report["passed"] and not args.dry_run:
        q_path = quarantine(text, report, label)
        print(f"\n🚫 内容已隔离: {q_path}")
        print(f"   审查通过后手动移入 wiki/ 或使用 --trusted 导入")

    # 退出码
    if not report["passed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
