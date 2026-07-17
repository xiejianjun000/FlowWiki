#!/usr/bin/env python3
"""
重建 wiki/index.md — 扫描 wiki/ 目录，从 frontmatter 提取信息，
生成紧凑的机器索引（按类型分组）。
幂等：内容未变则不写入。
"""

import logging
import re
import yaml
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

WIKI_DIR = Path("wiki")
INDEX_FILE = WIKI_DIR / "index.md"

# 扫描的子目录及其类型标签
CATEGORIES = {
    "concepts": "概念",
    "playbooks": "操作手册",
    "comparisons": "对比分析",
    "criteria": "判据体系",
    "cases": "案例",
    "meta": "元文档",
}


def extract_frontmatter(filepath: Path) -> dict:
    """提取 Markdown 文件的 YAML frontmatter。"""
    text = filepath.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if match:
        try:
            return yaml.safe_load(match.group(1)) or {}
        except yaml.YAMLError:
            logger.warning(f"YAML 解析失败: {filepath}")
    return {}


def scan_wiki() -> dict[str, list[dict]]:
    """扫描 wiki/ 各子目录，收集页面信息。"""
    result: dict[str, list[dict]] = {}
    for category, label in CATEGORIES.items():
        cat_dir = WIKI_DIR / category
        if not cat_dir.is_dir():
            continue
        pages = []
        for md_file in sorted(cat_dir.glob("*.md")):
            fm = extract_frontmatter(md_file)
            title = fm.get("title", md_file.stem)
            rel_path = str(md_file.relative_to(WIKI_DIR))
            pages.append({"title": title, "path": rel_path})
        if pages:
            result[category] = pages
    return result


def build_index(structure: dict[str, list[dict]]) -> str:
    """根据扫描结果生成 index.md 内容。"""
    lines = [
        "# Wiki 索引",
        "",
        "## 机器索引 — 紧凑、结构化",
        "",
    ]

    labels = {
        "concepts": "核心概念",
        "playbooks": "操作手册",
        "comparisons": "对比分析",
        "criteria": "判据体系",
        "cases": "案例",
        "meta": "元文档",
    }

    for category in ["concepts", "playbooks", "comparisons", "criteria", "cases", "meta"]:
        pages = structure.get(category, [])
        if not pages:
            continue
        label = labels.get(category, category)
        lines.append(f"### {label}")
        for p in pages:
            lines.append(f"- [{p['title']}]({p['path']})")
        lines.append("")

    return "\n".join(lines) + "\n"


def main():
    logger.info("开始重建 wiki/index.md...")

    structure = scan_wiki()
    new_content = build_index(structure)

    # 幂等：内容未变则不写入
    if INDEX_FILE.exists():
        old_content = INDEX_FILE.read_text(encoding="utf-8")
        if old_content == new_content:
            logger.info("index.md 内容未变，跳过写入")
            return
    else:
        INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)

    INDEX_FILE.write_text(new_content, encoding="utf-8")
    counts = {k: len(v) for k, v in structure.items()}
    logger.info(f"index.md 已重建，含: {counts}")


if __name__ == "__main__":
    main()
