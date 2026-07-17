#!/usr/bin/env python3
"""
知识图谱可视化 — 解析 wiki/**/*.md，提取 [[wikilink]] 和 [text](path) 链接，
构建图谱，输出为 Mermaid mindmap 或 flowchart。
幂等：多次运行结果一致。
"""

import argparse
import logging
import re
from pathlib import Path
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

WIKI_DIR = Path("wiki")

# 页面类型 → 分组标签
CATEGORY_LABELS = {
    "concepts": "概念",
    "playbooks": "操作手册",
    "comparisons": "对比分析",
    "criteria": "判据体系",
    "cases": "案例",
    "meta": "元文档",
}


def resolve_wikilink_id(target: str) -> str | None:
    """
    将 Wikilink 目标解析为 wiki/ 中的相对路径。
    例如: "数据溯源链路" → "wiki/concepts/数据溯源链路.md"
    返回 relative_id 用于节点标识。
    """
    name = target if target.endswith(".md") else target + ".md"
    for cat_dir in sorted(WIKI_DIR.iterdir()):
        if not cat_dir.is_dir():
            continue
        candidate = cat_dir / name
        if candidate.exists():
            return str(candidate.relative_to(WIKI_DIR))
    return None


def resolve_mdlink_id(path: str, source_file: Path) -> str | None:
    """解析 [text](path.md) 为 wiki 相对路径。"""
    if path.startswith(("http://", "https://", "/")):
        return None
    resolved = (source_file.parent / path).resolve()
    try:
        return str(resolved.relative_to(WIKI_DIR.resolve()))
    except ValueError:
        return None


def build_graph() -> dict[str, dict]:
    """
    构建知识图谱。
    返回 {node_id: {"title": str, "category": str, "links": [node_id, ...]}}
    """
    graph: dict[str, dict] = {}

    for md_file in sorted(WIKI_DIR.rglob("*.md")):
        if md_file.name in ("index.md", "log.md", "README.md"):
            continue

        node_id = str(md_file.relative_to(WIKI_DIR))

        # 确定分类
        category = "other"
        for cat_dir in sorted(WIKI_DIR.iterdir()):
            if not cat_dir.is_dir():
                continue
            if md_file.is_relative_to(cat_dir):
                category = cat_dir.name
                break

        # 提取标题（从 frontmatter 或文件名）
        text = md_file.read_text(encoding="utf-8")
        title = md_file.stem
        fm_match = re.search(r"^title:\s*(.+)$", text, re.MULTILINE)
        if fm_match:
            title = fm_match.group(1).strip()

        links = []

        # [[wikilink]]
        for m in re.finditer(r"\[\[([^\]]+)\]\]", text):
            target = m.group(1).split("|")[0].strip()
            resolved = resolve_wikilink_id(target)
            if resolved and resolved != node_id:
                links.append(resolved)

        # [text](path.md)
        for m in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", text):
            resolved = resolve_mdlink_id(m.group(2), md_file)
            if resolved and resolved != node_id:
                if resolved not in links:
                    links.append(resolved)

        graph[node_id] = {
            "title": title,
            "category": category,
            "links": links,
        }

    return graph


def generate_mindmap(graph: dict[str, dict]) -> str:
    """生成 Mermaid mindmap。"""
    lines = ["```mermaid", "mindmap", "  root((Wiki 知识图谱))"]

    groups: dict[str, list[str]] = defaultdict(list)
    for node_id, info in graph.items():
        groups[info["category"]].append(node_id)

    for category in ["concepts", "playbooks", "comparisons", "criteria", "cases", "meta"]:
        nodes = groups.get(category, [])
        if not nodes:
            continue
        label = CATEGORY_LABELS.get(category, category)
        lines.append(f"    {label}")
        for nid in nodes[:20]:  # 限制每类最多 20 个,避免图过大
            title = graph[nid]["title"]
            # 缩略标题（取前 15 个字符）
            short = title[:15] + ("..." if len(title) > 15 else "")
            lines.append(f"      [{short}]")

    lines.append("```")
    return "\n".join(lines)


def generate_flowchart(graph: dict[str, dict], max_edges: int = 50) -> str:
    """生成 Mermaid flowchart（LR 方向）。"""
    lines = ["```mermaid", "flowchart LR"]

    # 生成节点（带样式）
    color_map = {
        "concepts": "#e1f5fe",
        "playbooks": "#e8f5e9",
        "comparisons": "#fff3e0",
        "criteria": "#fce4ec",
        "cases": "#f3e5f5",
        "meta": "#e0e0e0",
    }

    node_ids_used = set()
    edge_count = 0

    # 按引用次数排序，优先显示枢纽节点
    ref_count = {nid: 0 for nid in graph}
    for nid, info in graph.items():
        for link in info["links"]:
            if link in ref_count:
                ref_count[link] += 1

    sorted_nodes = sorted(graph.keys(), key=lambda n: ref_count.get(n, 0), reverse=True)
    top_nodes = sorted_nodes[:20]  # 限制节点数

    # 生成节点定义
    for nid in top_nodes:
        info = graph[nid]
        bg = color_map.get(info["category"], "#f5f5f5")
        safe_id = nid.replace(".md", "").replace("/", "_").replace("-", "_")
        label = info["title"][:20]
        lines.append(f'    {safe_id}["{label}"]')
        lines.append(f"    style {safe_id} fill:{bg}")
        node_ids_used.add(nid)

    # 生成边（只连接都在 top_nodes 中的）
    for nid in top_nodes:
        if edge_count >= max_edges:
            break
        for link in graph[nid]["links"]:
            if edge_count >= max_edges:
                break
            if link in node_ids_used:
                src = nid.replace(".md", "").replace("/", "_").replace("-", "_")
                dst = link.replace(".md", "").replace("/", "_").replace("-", "_")
                lines.append(f"    {src} --> {dst}")
                edge_count += 1

    lines.append("```")
    return "\n".join(lines)


def generate_edgelist(graph: dict[str, dict]) -> str:
    """生成简单的边列表（便于导入 Gephi/Cytoscape 等工具）。"""
    lines = ["source\ttarget\ttype"]
    for node_id, info in graph.items():
        for link in info["links"]:
            lines.append(f"{info['title']}\t{graph.get(link, {}).get('title', link)}\t{info['category']}")
    return "\n".join(lines)


def generate_stats(graph: dict[str, dict]) -> str:
    """生成图谱统计信息。"""
    total_nodes = len(graph)
    total_edges = sum(len(info["links"]) for info in graph.values())
    categories = defaultdict(int)
    for info in graph.values():
        categories[info["category"]] += 1

    # 找出孤立节点（无入边也无出边）
    out_degree = {nid: len(info["links"]) for nid, info in graph.items()}
    in_degree = defaultdict(int)
    for nid, info in graph.items():
        for link in info["links"]:
            in_degree[link] += 1
    isolated = [nid for nid in graph if out_degree[nid] == 0 and in_degree[nid] == 0]

    # 枢纽节点（被引用最多的前 5 个）
    hub_nodes = sorted(in_degree.items(), key=lambda x: x[1], reverse=True)[:5]

    lines = [
        "# 知识图谱统计",
        "",
        f"- 总节点数: {total_nodes}",
        f"- 总边数: {total_edges}",
        f"- 孤立节点: {len(isolated)}",
        "",
        "## 分类分布",
    ]
    for cat in ["concepts", "playbooks", "comparisons", "criteria", "cases", "meta"]:
        count = categories.get(cat, 0)
        label = CATEGORY_LABELS.get(cat, cat)
        lines.append(f"- {label}: {count}")

    if hub_nodes:
        lines.append("")
        lines.append("## 枢纽节点（被引用最多）")
        for nid, count in hub_nodes:
            title = graph.get(nid, {}).get("title", nid)
            lines.append(f"- [{title}]({nid}): 被引用 {count} 次")

    if isolated:
        lines.append("")
        lines.append(f"## 孤立节点（{len(isolated)}）")
        for nid in sorted(isolated):
            title = graph.get(nid, {}).get("title", nid)
            lines.append(f"- [{title}]({nid})")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="知识图谱可视化")
    parser.add_argument("--format", choices=["mindmap", "flowchart", "edgelist", "stats"],
                        default="mindmap", help="输出格式")
    parser.add_argument("--output", type=str, help="输出到文件")
    args = parser.parse_args()

    logger.info("构建知识图谱...")

    graph = build_graph()

    if args.format == "mindmap":
        output = generate_mindmap(graph)
    elif args.format == "flowchart":
        output = generate_flowchart(graph)
    elif args.format == "edgelist":
        output = generate_edgelist(graph)
    elif args.format == "stats":
        output = generate_stats(graph)
    else:
        output = generate_mindmap(graph)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        logger.info(f"图谱已保存到: {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
