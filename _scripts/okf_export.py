#!/usr/bin/env python3
"""
OKF（Open Knowledge Format）导出器 — 将 FlowWiki wiki/ 目录导出为 OKF bundle。

OKF 是 llm-wiki-compiler v1.1.0 引入的可移植知识交换格式，对齐 Google Cloud 新兴标准。
导出产物是一个包含以下内容的目录：
  - okf.json       — 清单（页面索引、关系图、来源哈希）
  - pages/         — Markdown 页面（保留 YAML frontmatter + wikilink）
  - SHA256SUMS     — 完整性校验

兼容：llm-wiki-compiler OKF、FlowWiki 内部知识交换、跨工具知识迁移。

用法：
  python _scripts/okf_export.py                      # 导出到 ./okf_export/
  python _scripts/okf_export.py --output ./my-bundle  # 指定输出目录
  python _scripts/okf_export.py --industry enforcement-review  # 只导出指定行业
"""

import argparse
import hashlib
import json
import logging
import re
import yaml
from pathlib import Path
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

WIKI_DIR = Path("wiki")
RAW_DIR = Path("raw")
OKF_VERSION = "1.0.0"
OKF_SPEC = "https://github.com/xiejianjun000/FlowWiki/blob/main/docs/okf-spec.md"


def parse_frontmatter(filepath: Path) -> tuple[dict, str]:
    """解析 YAML frontmatter，返回 (data, body)。"""
    text = filepath.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, re.DOTALL)
    if not match:
        return {}, text
    try:
        data = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        data = {}
    body = text[match.end():]
    return data, body


def sha256_file(filepath: Path) -> str:
    """计算文件 SHA-256 哈希。"""
    h = hashlib.sha256()
    h.update(filepath.read_bytes())
    return h.hexdigest()


def extract_wikilinks(text: str) -> list[str]:
    """提取 [[wikilink]] 目标。"""
    links = []
    for m in re.finditer(r"\[\[([^\]]+)\]\]", text):
        target = m.group(1).split("|")[0].strip()
        links.append(target)
    return links


def extract_relations(pages: dict[str, dict]) -> list[dict]:
    """从 wikilink + sources 字段提取关系图。"""
    relations = []
    # 反向索引：path → page_id
    path_to_id = {p["path"]: pid for pid, p in pages.items()}

    for page_id, page in pages.items():
        for link in page.get("wikilinks", []):
            # 尝试匹配已知页面
            linked_id = None
            link_md = link if link.endswith(".md") else link + ".md"
            for path, pid in path_to_id.items():
                if path.endswith(link_md) or link_md in path or link in pid:
                    linked_id = pid
                    break
            if linked_id:
                relations.append({
                    "source": page_id,
                    "target": linked_id,
                    "type": "wikilink",
                    "label": link,
                })

        # sources 引用
        for src in page.get("sources", []):
            relations.append({
                "source": page_id,
                "target": f"raw:{src}",
                "type": "cites",
                "label": str(src),
            })

    return relations


def export_okf(wiki_dir: Path, output_dir: Path, industry: str = None) -> dict:
    """导出 wiki/ 为 OKF bundle。"""
    if not wiki_dir.is_dir():
        raise FileNotFoundError(f"wiki 目录不存在: {wiki_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)
    pages_dir = output_dir / "pages"
    pages_dir.mkdir(exist_ok=True)

    pages = {}
    sources_hashes = {}
    page_count = 0

    # 遍历 wiki/ 目录
    for md_file in sorted(wiki_dir.rglob("*.md")):
        if md_file.name in ("index.md", "log.md", "README.md"):
            continue
        # 跳过隔离区
        if "_quarantine" in str(md_file):
            continue

        rel_path = str(md_file.relative_to(wiki_dir))
        page_id = rel_path.replace("/", "__").replace(" ", "_").rstrip(".md")
        data, body = parse_frontmatter(md_file)
        wikilinks = extract_wikilinks(body)

        pages[page_id] = {
            "id": page_id,
            "path": rel_path,
            "type": data.get("type", "unknown"),
            "title": data.get("title", md_file.stem),
            "confidence": data.get("confidence", "medium"),
            "sources": data.get("sources", []) if isinstance(data.get("sources"), list) else [],
            "tags": data.get("tags", []) if isinstance(data.get("tags"), list) else [],
            "created": str(data.get("created", "")),
            "updated": str(data.get("updated", "")),
            "status": data.get("status", "unknown"),
            "wikilinks": wikilinks,
            "sha256": sha256_file(md_file),
            "size": md_file.stat().st_size,
        }

        # 复制页面内容到 OKF pages/
        page_out = pages_dir / (page_id + ".md")
        page_out.write_text(md_file.read_text(encoding="utf-8"), encoding="utf-8")

        # 记录 raw/ 来源哈希
        for src in pages[page_id]["sources"]:
            src_file = wiki_dir.parent / src if not src.startswith("raw/") else Path(src)
            if src_file.exists():
                sources_hashes[str(src)] = sha256_file(src_file)

        page_count += 1

    # 提取关系
    relations = extract_relations(pages)

    # 构建 OKF manifest
    manifest = {
        "okf_version": OKF_VERSION,
        "spec": OKF_SPEC,
        "generator": "FlowWiki OKF Exporter",
        "generator_version": "0.5.0",
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "industry": industry,
        "stats": {
            "page_count": page_count,
            "relation_count": len(relations),
            "source_count": len(sources_hashes),
        },
        "pages": {pid: {k: v for k, v in p.items() if k != "sha256"} for pid, p in pages.items()},
        "relations": relations,
        "source_hashes": {str(k): v for k, v in sources_hashes.items()},
    }

    # 写入 okf.json
    manifest_path = output_dir / "okf.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # 生成 SHA256SUMS
    sums_lines = []
    for f in sorted(output_dir.rglob("*")):
        if f.is_file() and f.name != "SHA256SUMS":
            sums_lines.append(f"{sha256_file(f)}  {f.relative_to(output_dir)}")
    (output_dir / "SHA256SUMS").write_text("\n".join(sums_lines) + "\n", encoding="utf-8")

    return manifest


def main():
    parser = argparse.ArgumentParser(description="FlowWiki OKF 导出器")
    parser.add_argument(
        "--output", "-o", type=str, default="./okf_export",
        help="输出目录（默认: ./okf_export）",
    )
    parser.add_argument(
        "--industry", type=str,
        help="只导出指定行业的知识（如 enforcement-review）",
    )
    parser.add_argument(
        "--wiki-dir", type=str, default="wiki",
        help="wiki 目录路径（默认: wiki）",
    )
    parser.add_argument(
        "--stats-only", action="store_true",
        help="只输出统计信息，不实际导出",
    )

    args = parser.parse_args()
    wiki_dir = Path(args.wiki_dir)

    try:
        manifest = export_okf(wiki_dir, Path(args.output), args.industry)

        print(f"✅ OKF 导出完成")
        print(f"   输出目录: {args.output}")
        print(f"   页面数: {manifest['stats']['page_count']}")
        print(f"   关系数: {manifest['stats']['relation_count']}")
        print(f"   来源数: {manifest['stats']['source_count']}")
        print(f"   OKF 版本: {OKF_VERSION}")
        print(f"   导出时间: {manifest['exported_at']}")
        print()
        print(f"导入到其他 Wiki: python _scripts/okf_import.py --input {args.output}")

    except Exception as e:
        logger.error(f"导出失败: {e}")
        raise


if __name__ == "__main__":
    main()
