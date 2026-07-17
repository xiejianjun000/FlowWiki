#!/usr/bin/env python3
"""
Wiki 体检工具 — 检查 frontmatter 完整性、断链、文件命名、
必填字段、confidence 值合法性，输出 lint 报告。
幂等：多次运行结果一致。
"""

import argparse
import logging
import re
import yaml
from pathlib import Path
from datetime import datetime, date

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

WIKI_DIR = Path("wiki")
VALID_CONFIDENCE = {"low", "medium", "high"}
VALID_STATUS = {"draft", "reviewed", "archived", "active"}
REQUIRED_FIELDS = ["type", "title", "created", "updated", "confidence", "sources", "tags", "status"]

# 合法文件名: 允许中文、英文、数字、连字符、下划线
VALID_FILENAME_RE = re.compile(r"^[\w\u4e00-\u9fff\u3400-\u4dbf\-]+\.md$")


def parse_frontmatter(filepath: Path) -> tuple[dict | None, str | None]:
    """解析 YAML frontmatter，返回 (data, error)。"""
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


def check_frontmatter(data: dict, filepath: Path) -> list[str]:
    """检查 frontmatter 字段完整性。"""
    issues = []
    for field in REQUIRED_FIELDS:
        if field not in data or data[field] is None:
            issues.append(f"缺少必填字段: {field}")
    return issues


def check_confidence(data: dict) -> list[str]:
    """检查 confidence 值是否合法。"""
    issues = []
    conf = data.get("confidence", "")
    if conf and conf not in VALID_CONFIDENCE:
        issues.append(f"confidence 值无效: '{conf}' (应为 low/medium/high)")
    return issues


def check_status(data: dict) -> list[str]:
    """检查 status 值是否合法。"""
    issues = []
    status = data.get("status", "")
    if status and status not in VALID_STATUS:
        issues.append(f"status 值无效: '{status}' (应为 draft/reviewed/archived/active)")
    return issues


def check_sources(data: dict) -> list[str]:
    """检查 sources 是否为空列表。"""
    issues = []
    sources = data.get("sources", [])
    if isinstance(sources, list) and len(sources) == 0:
        confidence = data.get("confidence", "")
        if confidence != "low":
            issues.append("sources 为空（建议至少引用一个 raw/ 源）")
    return issues


def check_tags(data: dict) -> list[str]:
    """检查 tags 是否包含 flow-wiki。"""
    issues = []
    tags = data.get("tags", [])
    if isinstance(tags, list) and "flow-wiki" not in tags:
        issues.append("tags 缺少 flow-wiki")
    return issues


def check_filename(filepath: Path) -> list[str]:
    """检查文件名是否合法。"""
    issues = []
    if not VALID_FILENAME_RE.match(filepath.name):
        issues.append(f"文件名不规范: {filepath.name}")
    return issues


def find_internal_links(filepath: Path) -> list[tuple[str, str, str]]:
    """查找内部 Markdown 链接和 Wikilink。返回 (type, text, target)。"""
    text = filepath.read_text(encoding="utf-8")
    links = []

    # [text](path.md)
    for m in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", text):
        path = m.group(2)
        if not path.startswith(("http://", "https://", "/")):
            links.append(("mdlink", m.group(1), path))

    # [[wikilink]]
    for m in re.finditer(r"\[\[([^\]]+)\]\]", text):
        target = m.group(1).split("|")[0].strip()
        links.append(("wikilink", m.group(1), target))

    return links


def check_dangling_links(links: list[tuple[str, str, str]], filepath: Path) -> list[str]:
    """检查内部链接是否指向存在的文件。"""
    issues = []
    for link_type, _, target in links:
        resolved = None
        if link_type == "mdlink":
            base = filepath.parent
            resolved = (base / target).resolve()
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
            issues.append(f"悬空链接: {target}")
    return issues


def lint_file(filepath: Path) -> list[str]:
    """对单个文件执行所有检查。"""
    issues = []

    # 文件名检查
    issues.extend(check_filename(filepath))

    # frontmatter 检查
    data, err = parse_frontmatter(filepath)
    if err:
        issues.append(err)
        return issues
    if data is None:
        return issues

    issues.extend(check_frontmatter(data, filepath))
    issues.extend(check_confidence(data))
    issues.extend(check_status(data))
    issues.extend(check_sources(data))
    issues.extend(check_tags(data))

    # 断链检查
    links = find_internal_links(filepath)
    issues.extend(check_dangling_links(links, filepath))

    return issues


def main():
    parser = argparse.ArgumentParser(description="Wiki lint 体检工具")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")
    parser.add_argument("--output", type=str, help="输出报告到文件")
    args = parser.parse_args()

    logger.info("开始 wiki 体检...")

    if not WIKI_DIR.is_dir():
        logger.error(f"wiki 目录不存在: {WIKI_DIR}")
        return

    results: dict[str, list[str]] = {}
    total_issues = 0
    total_files = 0

    for md_file in sorted(WIKI_DIR.rglob("*.md")):
        if md_file.name in ("index.md", "log.md", "README.md"):
            continue
        total_files += 1
        issues = lint_file(md_file)
        if issues:
            rel = str(md_file.relative_to(WIKI_DIR))
            results[rel] = issues
            total_issues += len(issues)

    # 输出报告
    if args.json:
        import json
        report = {
            "total_files": total_files,
            "files_with_issues": len(results),
            "total_issues": total_issues,
            "details": results,
        }
        output = json.dumps(report, ensure_ascii=False, indent=2)
    else:
        lines = [
            f"=== Wiki Lint 报告 ===",
            f"扫描文件数: {total_files}",
            f"有问题的文件: {len(results)}",
            f"问题总数: {total_issues}",
            "",
        ]
        for fpath, issues in results.items():
            lines.append(f"--- {fpath} ---")
            for issue in issues:
                lines.append(f"  ✗ {issue}")
            lines.append("")
        output = "\n".join(lines)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        logger.info(f"报告已保存到: {args.output}")
    else:
        print(output)

    if total_issues > 0:
        logger.warning(f"发现 {total_issues} 个问题")
    else:
        logger.info("lint 通过，未发现问题")


if __name__ == "__main__":
    main()
