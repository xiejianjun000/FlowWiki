#!/usr/bin/env python3
"""
规范化 wiki/**/*.md 的 frontmatter — 确保每页包含所有必填字段，
缺失字段自动补充默认值，已有字段原样保留。
幂等：多次运行结果一致。
"""

import logging
import re
import yaml
from datetime import date
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

WIKI_DIR = Path("wiki")

REQUIRED_FIELDS = {
    "type": "concept",
    "title": "",           # 从文件名推断或使用第一个 h1
    "created": str(date.today()),
    "updated": str(date.today()),
    "confidence": "medium",
    "sources": [],
    "tags": ["flow-wiki"],
    "status": "draft",
}


def parse_md_parts(text: str) -> tuple[str | None, str, str]:
    """将 Markdown 文本拆分为 (frontmatter_raw, body)。"""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if match:
        fm_raw = match.group(1)
        body = text[match.end():]
        return fm_raw, body
    return None, text


def dump_frontmatter(data: dict) -> str:
    """将 dict 序列化为 YAML frontmatter 块（保持顺序）。"""
    # 按规范字段顺序输出
    field_order = ["type", "title", "created", "updated", "confidence", "sources", "tags", "status"]
    ordered = {}
    for key in field_order:
        if key in data:
            ordered[key] = data[key]
    # 附加其他未知字段
    for key, val in data.items():
        if key not in ordered:
            ordered[key] = val

    yaml_str = yaml.dump(ordered, allow_unicode=True, default_flow_style=None, sort_keys=False).strip()
    return f"---\n{yaml_str}\n---\n"


def extract_title_from_body(body: str) -> str:
    """从 body 中提取第一个 h1 标题。"""
    match = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return ""


def normalize_file(filepath: Path) -> bool:
    """规范化单个文件。返回 True 表示做了修改。"""
    text = filepath.read_text(encoding="utf-8")
    fm_raw, body = parse_md_parts(text)

    if fm_raw is None:
        # 无 frontmatter，全部用默认值
        fm_data = dict(REQUIRED_FIELDS)
    else:
        try:
            fm_data = yaml.safe_load(fm_raw) or {}
        except yaml.YAMLError:
            logger.warning(f"YAML 解析失败，将重建: {filepath}")
            fm_data = {}

    changed = False

    # 补充缺失字段
    for field, default in REQUIRED_FIELDS.items():
        if field not in fm_data or fm_data[field] is None:
            fm_data[field] = default
            changed = True

    # 如果 title 为空，尝试从正文提取或从文件名推断
    if not fm_data.get("title"):
        title = extract_title_from_body(body)
        if not title:
            title = filepath.stem
        fm_data["title"] = title
        changed = True

    # 确保 tags 包含 flow-wiki
    if "flow-wiki" not in fm_data.get("tags", []):
        fm_data["tags"] = fm_data.get("tags", []) + ["flow-wiki"]
        changed = True

    if not changed:
        return False

    new_fm = dump_frontmatter(fm_data)
    new_text = new_fm + body
    filepath.write_text(new_text, encoding="utf-8")
    logger.info(f"归一化: {filepath.relative_to(WIKI_DIR)}")
    return True


def main():
    logger.info("开始规范化 frontmatter...")

    if not WIKI_DIR.is_dir():
        logger.error(f"wiki 目录不存在: {WIKI_DIR}")
        return

    total = 0
    changed = 0
    for md_file in sorted(WIKI_DIR.rglob("*.md")):
        # 跳过特殊文件
        if md_file.name in ("index.md", "log.md", "README.md"):
            continue
        total += 1
        if normalize_file(md_file):
            changed += 1

    logger.info(f"完成: 共 {total} 个文件，修改了 {changed} 个")


if __name__ == "__main__":
    main()
