#!/usr/bin/env python3
"""
扫描并报告 wiki/**/*.md 中的悬空内部链接。
支持 [text](path.md) 和 [[text]] / [[text|alias]] 格式。
可选 --fix 将悬空链接标为 "⚠️ 待补充"。
幂等：多次扫描结果一致。
"""

import argparse
import logging
import re
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

WIKI_DIR = Path("wiki")

# 匹配 [text](relative/path.md) 格式
MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
# 匹配 [[text]] 或 [[text|alias]] 格式
WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")


def resolve_wikilink(target: str, source_file: Path) -> Path | None:
    """
    解析 Wikilink 目标为实际文件路径。
    例如 [[数据溯源链路]] → wiki/concepts/数据溯源链路.md
    """
    # 如果已有扩展名，直接使用
    if target.endswith(".md"):
        name = target
    else:
        name = target + ".md"

    # 如果包含路径分隔符，那是相对路径
    if "/" in name:
        resolved = (source_file.parent / name).resolve()
        return resolved if resolved.exists() else None

    # 否则在所有 wiki 子目录中搜索
    for cat_dir in sorted(WIKI_DIR.iterdir()):
        if not cat_dir.is_dir():
            continue
        candidate = cat_dir / name
        if candidate.exists():
            return candidate
    return None


def resolve_mdlink(path: str, source_file: Path) -> Path | None:
    """解析 [text](path.md) 的相对路径。"""
    # 只处理相对路径（不以 http:// 或 / 开头）
    if path.startswith(("http://", "https://", "/")):
        return None  # 外部链接，不检查
    base = source_file.parent
    resolved = (base / path).resolve()
    if not resolved.is_relative_to(WIKI_DIR.resolve()):
        return None  # 不在 wiki 目录内，跳过
    return resolved if resolved.exists() else None


def scan_dangling(dry_run: bool = True) -> list[dict]:
    """扫描所有 wiki 文件，返回悬空链接列表。"""
    dangling: list[dict] = []

    for md_file in sorted(WIKI_DIR.rglob("*.md")):
        # 跳过特殊文件
        if md_file.name in ("index.md", "log.md", "README.md"):
            continue

        text = md_file.read_text(encoding="utf-8")

        # 检查 [text](path) 格式
        for match in MD_LINK_RE.finditer(text):
            link_text = match.group(1)
            link_path = match.group(2)
            resolved = resolve_mdlink(link_path, md_file)
            if resolved is None and not link_path.startswith(("http://", "https://", "/")):
                # 检查是否可能是 wiki 内部链接
                if link_path.endswith(".md") or "/" in link_path:
                    dangling.append({
                        "file": str(md_file.relative_to(WIKI_DIR)),
                        "type": "mdlink",
                        "text": link_text,
                        "target": link_path,
                        "line_hint": text[:match.start()].count("\n") + 1,
                    })

        # 检查 [[wikilink]] 格式
        for match in WIKILINK_RE.finditer(text):
            target = match.group(1).strip()
            resolved = resolve_wikilink(target, md_file)
            if resolved is None:
                dangling.append({
                    "file": str(md_file.relative_to(WIKI_DIR)),
                    "type": "wikilink",
                    "text": match.group(0),
                    "target": target,
                    "line_hint": text[:match.start()].count("\n") + 1,
                })

    return dangling


def suggest_alternatives(target: str) -> list[str]:
    """为悬空链接目标建议可能的替代文件。"""
    target_lower = target.lower().replace(".md", "")
    suggestions = []

    for md_file in WIKI_DIR.rglob("*.md"):
        if md_file.name in ("index.md", "log.md", "README.md"):
            continue
        stem_lower = md_file.stem.lower()
        # 简单相似度：包含关系
        if target_lower in stem_lower or stem_lower in target_lower:
            suggestions.append(str(md_file.relative_to(WIKI_DIR)))

    return suggestions[:5]


def fix_dangling(source_file: Path, target: str, link_type: str) -> bool:
    """将悬空链接标记为 ⚠️ 待补充。不对 [[wikilink]] 做修改。"""
    if link_type == "wikilink":
        return False  # Wikilink 不自动修改

    text = source_file.read_text(encoding="utf-8")
    new_text = re.sub(
        rf"\[([^\]]*)\]\({re.escape(target)}\)",
        rf"[\1 ⚠️ 待补充]({target})",
        text,
        count=1,
    )
    if new_text != text:
        source_file.write_text(new_text, encoding="utf-8")
        return True
    return False


def main():
    parser = argparse.ArgumentParser(description="扫描并修复 wiki/ 中的悬空链接")
    parser.add_argument("--fix", action="store_true", help="尝试标记悬空链接")
    parser.add_argument("--json", action="store_true", help="以 JSON 格式输出")
    args = parser.parse_args()

    logger.info("扫描悬空链接...")

    dangling = scan_dangling()

    if not dangling:
        logger.info("未发现悬空链接")
        return

    if args.json:
        import json
        print(json.dumps(dangling, ensure_ascii=False, indent=2))
        return

    print(f"\n发现 {len(dangling)} 个悬空链接:\n")
    for d in dangling:
        source = WIKI_DIR / d["file"]
        print(f"  {d['file']}:{d['line_hint']}  [{d['type']}] {d['text']} → {d['target']}")
        suggestions = suggest_alternatives(d["target"])
        if suggestions:
            for s in suggestions:
                print(f"    建议: {s}")

    if args.fix:
        fixed = 0
        for d in dangling:
            if d["type"] == "mdlink":
                source = WIKI_DIR / d["file"]
                if fix_dangling(source, d["target"], d["type"]):
                    fixed += 1
        logger.info(f"已标记 {fixed} 个悬空链接为 ⚠️ 待补充")


if __name__ == "__main__":
    main()
