#!/usr/bin/env python3
"""
quality_audit.py — FlowWiki 知识库 12 维质量审计工具 (v2.0)

质量维度（全部目标 ≥90%，除标注外）：

  结构性维度：
    D1  溯源准确率    — wiki 页面 → raw/ 源文件可追溯比例
    D2  frontmatter 完整率 — YAML frontmatter 存在率
    D3  置信度标注率  — confidence 字段标注率
    D4  摘要段存在率  — ## 摘要 或等效段存在率

  关联性维度：
    D5  交叉引用率    — 含 [[wikilink]] 的页面比例
    D6  双向链接率    — 被其他页面引用的页面比例
    D7  图谱连通度    — 最大连通分量占总节点比例
    D8  孤岛率        — 零入链页面的比例（越低越好，目标 ≤10%）

  治理性维度：
    D9  索引完整性    — wiki/ 页面在 index.md 中的覆盖率
    D10 知识新鲜度    — 最近 30 天内有更新的页面比例
    D11 覆盖率(raw→wiki) — raw/ 源文件有对应 wiki 页面的比例
    D12 反幻觉率      — 声明可追溯到 raw/ 具体行号的比例

红线标准（Hermes 核验标准）：
  所有 D1-D12 ≥ 85%，其中 D1/D5/D6/D7 ≥ 90%
  D8 孤岛率 ≤ 10%（越低越好）
  D12 反幻觉率 ≥ 90%

用法：
  python quality_audit.py                      # 完整审计
  python quality_audit.py --json               # JSON 输出
  python quality_audit.py --redline            # 仅显示红线违规
  python quality_audit.py --path /other/wiki --raw /other/raw
"""

import os
import re
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict


# ── 红线阈值 ──────────────────────────────────────────────
REDLINES = {
    "D1_traceability":        {"min": 0.90, "label": "溯源准确率"},
    "D2_frontmatter":         {"min": 0.90, "label": "frontmatter 完整率"},
    "D3_confidence":          {"min": 0.80, "label": "置信度标注率"},
    "D4_summary":             {"min": 0.80, "label": "摘要段存在率"},
    "D5_crossref":            {"min": 0.90, "label": "交叉引用率"},
    "D6_bidirectional":       {"min": 0.90, "label": "双向链接率"},
    "D7_connectivity":        {"min": 0.90, "label": "图谱连通度"},
    "D8_orphan":              {"max": 0.10, "label": "孤岛率"},
    "D9_index_coverage":      {"min": 0.90, "label": "索引完整性"},
    "D10_freshness":          {"min": 0.70, "label": "知识新鲜度"},
    "D11_raw_coverage":       {"min": 0.70, "label": "覆盖率(raw→wiki)"},
    "D12_anti_hallucination": {"min": 0.90, "label": "反幻觉率"},
}


def extract_wikilinks(content: str) -> list:
    """提取 [[wikilink]] 目标"""
    return re.findall(r'\[\[([^\]|#]+)(?:[|#][^\]]+)?\]\]', content)


def extract_sources(fm_text: str) -> list:
    """从 frontmatter 提取 sources 列表"""
    match = re.search(r'sources:\s*\[(.*?)\]', fm_text, re.DOTALL)
    if not match:
        return []
    body = match.group(1)
    # 提取完整文件路径（非捕获组匹配扩展名）
    refs = re.findall(r'([\w./-]+\.(?:md|pdf|docx|txt|yaml|json))', body)
    # 清理引号
    return [r.strip('"\'') for r in refs]


def count_line_refs(content: str) -> int:
    """计数正文中'第 X 行'或 'line X' 的具体行号引用"""
    # 中文格式: "第 55 行" / "第 35-43 行"
    cn_refs = len(re.findall(r'第\s*\d+(\s*[-–—]\s*\d+)?\s*行', content))
    # 英文格式: "line 55" / "lines 35-43"
    en_refs = len(re.findall(r'lines?\s*\d+(\s*[-–—]\s*\d+)?', content, re.IGNORECASE))
    return cn_refs + en_refs


def audit_wiki_full(wiki_path: str, raw_path: str) -> dict:
    """12 维全面审计"""
    wiki_dir = Path(wiki_path).resolve()
    raw_dir = Path(raw_path).resolve()

    # 收集文件
    wiki_pages = {p.relative_to(wiki_dir): p for p in wiki_dir.rglob("*.md")
                  if p.name not in ['README.md', 'index.md', 'log.md']}
    raw_files = [f.relative_to(raw_dir) for f in raw_dir.rglob("*")
                 if f.is_file() and f.name != 'README.md']

    index_path = wiki_dir / "index.md"

    stats = {
        'total_pages': len(wiki_pages),
        'total_raw_sources': len(raw_files),
        'has_frontmatter': 0,
        'has_sources': 0,
        'sources_traceable': 0,
        'has_confidence': 0,
        'has_summary': 0,
        'has_wikilink': 0,
        'has_line_refs': 0,
        'total_line_refs': 0,
        'recent_updated': 0,
        'in_index': 0,
        'empty_frontmatter': [],
        'broken_pages': [],
        'dangling_refs': [],
        'linked_from': defaultdict(set),  # 入链: page_slug → {referrer_slugs}
        'linked_to': defaultdict(set),    # 出链: page_slug → {target_slugs}
        'raw_to_wiki': defaultdict(set),  # raw_file → {wiki_pages}
    }

    cutoff_date = datetime.now() - timedelta(days=30)
    # 先收集所有 page slug（避免文件序增量构建导致的匹配遗漏）
    page_slugs = set(str(r.with_suffix('')) for r in wiki_pages.keys())

    for rel_path, file_path in wiki_pages.items():
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception:
            stats['broken_pages'].append(str(rel_path))
            continue

        slug = str(rel_path.with_suffix(''))

        # ── frontmatter 解析 ──
        if not content.startswith('---'):
            stats['broken_pages'].append(f"{rel_path}: 缺少 frontmatter")
            continue

        stats['has_frontmatter'] += 1
        fm_end = content.find('---', 3)
        if fm_end < 0:
            stats['broken_pages'].append(f"{rel_path}: frontmatter 未闭合")
            continue

        fm_text = content[3:fm_end]
        body = content[fm_end + 3:]

        # ── 三空字段检测 ──
        empty_fields = []
        for field, pattern in [
            ('触发词', r'(?:触发词|triggers):\s*\[?\s*\]?\s*$'),
            ('适用场景', r'(?:适用场景|scenarios):\s*\[?\s*\]?\s*$'),
            ('关联法条', r'(?:关联法条|legal_refs):\s*\[?\s*\]?\s*$'),
        ]:
            if re.search(pattern, fm_text, re.MULTILINE):
                empty_fields.append(field)
        if empty_fields:
            stats['empty_frontmatter'].append({str(rel_path): empty_fields})

        # ── 置信度 ──
        if re.search(r'confidence:', fm_text):
            stats['has_confidence'] += 1

        # ── 摘要段 ──
        if re.search(r'##\s*(?:摘要|概述|定义|Abstract|Summary)', content):
            stats['has_summary'] += 1

        # ── sources 可追溯性 ──
        sources = extract_sources(fm_text)
        if sources:
            stats['has_sources'] += 1
            traceable = 0
            for s in sources:
                candidate = raw_dir / s
                if candidate.exists():
                    traceable += 1
                    stats['raw_to_wiki'][s].add(str(rel_path))
                else:
                    stats['dangling_refs'].append({'page': str(rel_path), 'reference': s})
            if traceable > 0:
                stats['sources_traceable'] += 1

        # ── 反幻觉：行号引用 ──
        line_refs = count_line_refs(content)
        stats['total_line_refs'] += line_refs
        if line_refs >= 2:  # 至少 2 处行号引用才算有效
            stats['has_line_refs'] += 1

        # ── 交叉引用 & 双向链接 ──
        wikilinks = extract_wikilinks(content)
        if wikilinks:
            stats['has_wikilink'] += 1

        for target in wikilinks:
            target_slug = target.strip().replace(' ', '-').lower()
            # 灵活匹配：先精确匹配，再按页面名末尾匹配
            if target_slug in page_slugs:
                stats['linked_to'][slug].add(target_slug)
                stats['linked_from'][target_slug].add(slug)
            else:
                # 匹配 'concepts/xxx' 中的 'xxx' 部分
                for ps in page_slugs:
                    if ps.endswith('/' + target_slug) or ps == target_slug:
                        stats['linked_to'][slug].add(ps)
                        stats['linked_from'][ps].add(slug)
                        break

        # ── 新鲜度 ──
        updated_match = re.search(r'updated:\s*(\d{4}-\d{2}-\d{2})', fm_text)
        if updated_match:
            try:
                updated_date = datetime.strptime(updated_match.group(1), '%Y-%m-%d')
                if updated_date >= cutoff_date:
                    stats['recent_updated'] += 1
            except ValueError:
                pass

    # ── 索引完整性 ──
    if index_path.exists():
        index_content = index_path.read_text(encoding='utf-8')
        for slug in page_slugs:
            page_name = slug.split('/')[-1]
            if page_name.lower() in index_content.lower():
                stats['in_index'] += 1

    return stats, page_slugs


def compute_graph_metrics(stats: dict, page_slugs: set) -> dict:
    """计算图谱指标：双向链接率 + 连通度 + 孤岛率"""
    total = len(page_slugs)
    if total == 0:
        return {'bidirectional_rate': 0, 'connectivity': 0, 'orphan_rate': 0}

    # 双向链接：页面既有出链也有入链
    bidirectional = sum(
        1 for slug in page_slugs
        if slug in stats['linked_to'] and slug in stats['linked_from']
    )

    # 孤岛：零入链
    orphans = sum(1 for slug in page_slugs if slug not in stats['linked_from'])

    # 连通度：BFS 找最大连通分量
    adj = defaultdict(set)
    for src, targets in stats['linked_to'].items():
        for tgt in targets:
            adj[src].add(tgt)
            adj[tgt].add(src)
    # 也加入 linked_from 的边（确保双向）
    for tgt, referrers in stats['linked_from'].items():
        for ref in referrers:
            adj[tgt].add(ref)
            adj[ref].add(tgt)

    visited = set()
    max_component = 0
    for node in page_slugs:
        if node not in visited:
            # BFS
            queue = [node]
            visited.add(node)
            component_size = 0
            while queue:
                curr = queue.pop(0)
                component_size += 1
                for neighbor in adj.get(curr, set()):
                    if neighbor not in visited and neighbor in page_slugs:
                        visited.add(neighbor)
                        queue.append(neighbor)
            max_component = max(max_component, component_size)

    return {
        'bidirectional_rate': round(bidirectional / total * 100, 1),
        'connectivity': round(max_component / total * 100, 1),
        'orphan_rate': round(orphans / total * 100, 1),
        'total_nodes': total,
        'bi_nodes': bidirectional,
        'orphan_nodes': orphans,
        'max_component_size': max_component,
    }


def compute_scores(stats: dict, graph: dict) -> dict:
    """计算 12 维评分"""
    total = stats['total_pages']
    if total == 0:
        return {'error': 'wiki/ 目录无有效页面'}

    scores = {
        # 结构性
        'D1_traceability':        round(stats['sources_traceable'] / total * 100, 1),
        'D2_frontmatter':         round(stats['has_frontmatter'] / total * 100, 1),
        'D3_confidence':          round(stats['has_confidence'] / total * 100, 1),
        'D4_summary':             round(stats['has_summary'] / total * 100, 1),
        # 关联性
        'D5_crossref':            round(stats['has_wikilink'] / total * 100, 1),
        'D6_bidirectional':       graph['bidirectional_rate'],
        'D7_connectivity':        graph['connectivity'],
        'D8_orphan':              graph['orphan_rate'],
        # 治理性
        'D9_index_coverage':      round(stats['in_index'] / total * 100, 1) if total > 0 else 0,
        'D10_freshness':          round(stats['recent_updated'] / total * 100, 1),
        'D11_raw_coverage':       round(
            len([f for f, pages in stats['raw_to_wiki'].items() if pages]) /
            max(stats['total_raw_sources'], 1) * 100, 1
        ),
        'D12_anti_hallucination': round(stats['has_line_refs'] / total * 100, 1),
    }

    # 综合健康度
    scores['health_score'] = round(sum(scores.values()) / len(scores), 1)

    # 红线判定
    redline_results = {}
    for key, rule in REDLINES.items():
        value = scores.get(key, 0)
        if 'max' in rule:
            passed = value <= rule['max'] * 100
        else:
            passed = value >= rule['min'] * 100
        if 'max' in rule:
            threshold_val = rule['max'] * 100
            threshold_str = f"≤{threshold_val:.0f}%"
        else:
            threshold_val = rule['min'] * 100
            threshold_str = f"≥{threshold_val:.0f}%"
        redline_results[key] = {
            'label': rule['label'],
            'passed': passed,
            'actual': f"{value}%",
            'threshold': threshold_str,
        }

    scores['redlines'] = redline_results
    scores['all_redlines_pass'] = all(r['passed'] for r in redline_results.values())
    scores['passed_count'] = sum(1 for r in redline_results.values() if r['passed'])
    scores['total_checks'] = len(redline_results)

    return scores


def format_report(stats: dict, scores: dict, graph: dict, wiki_path: str):
    """格式化输出审计报告"""
    print(f"╔══════════════════════════════════════════════════════╗")
    print(f"║  FlowWiki 知识库 12 维质量审计 v2.0                    ║")
    print(f"║  路径: {wiki_path}")
    print(f"║  时间: {datetime.now().isoformat()}")
    print(f"╚══════════════════════════════════════════════════════╝")
    print()
    print(f"📊 基础数据: {stats['total_pages']} wiki 页 / {stats['total_raw_sources']} raw 源文件")
    print()

    # ── 结构性维度 ──
    print(f"📋 结构性维度（知识内容本身的质量）")
    print(f"  {'D1 溯源准确率':<18s} {scores['D1_traceability']:>6.1f}%  {'✅' if scores['D1_traceability'] >= 90 else '❌'}  "
          f"(sources→raw/ 可追溯: {stats['sources_traceable']}/{stats['total_pages']})")
    print(f"  {'D2 frontmatter':<18s} {scores['D2_frontmatter']:>6.1f}%  {'✅' if scores['D2_frontmatter'] >= 90 else '❌'}  "
          f"(完整: {stats['has_frontmatter']}/{stats['total_pages']})")
    print(f"  {'D3 置信度标注':<18s} {scores['D3_confidence']:>6.1f}%  {'✅' if scores['D3_confidence'] >= 80 else '❌'}  "
          f"(已标注: {stats['has_confidence']}/{stats['total_pages']})")
    print(f"  {'D4 摘要段':<18s} {scores['D4_summary']:>6.1f}%  {'✅' if scores['D4_summary'] >= 80 else '❌'}  "
          f"(存在: {stats['has_summary']}/{stats['total_pages']})")
    print()

    # ── 关联性维度 ──
    print(f"🕸️ 关联性维度（知识之间的网络效应）")
    print(f"  {'D5 交叉引用率':<18s} {scores['D5_crossref']:>6.1f}%  {'✅' if scores['D5_crossref'] >= 90 else '❌'}  "
          f"([[wikilink]]: {stats['has_wikilink']}/{stats['total_pages']})")
    print(f"  {'D6 双向链接率':<18s} {scores['D6_bidirectional']:>6.1f}%  {'✅' if scores['D6_bidirectional'] >= 90 else '❌'}  "
          f"(双向: {graph['bi_nodes']}/{graph['total_nodes']})")
    print(f"  {'D7 图谱连通度':<18s} {scores['D7_connectivity']:>6.1f}%  {'✅' if scores['D7_connectivity'] >= 90 else '❌'}  "
          f"(最大分量: {graph['max_component_size']}/{graph['total_nodes']})")
    orphan_icon = '✅' if graph['orphan_rate'] <= 10 else '❌'
    print(f"  {'D8 孤岛率':<18s} {scores['D8_orphan']:>6.1f}%  {orphan_icon}  "
          f"(零入链: {graph['orphan_nodes']}/{graph['total_nodes']} — 越低越好)")
    print()

    # ── 治理性维度 ──
    print(f"🏛️ 治理性维度（知识库的健康维护）")
    print(f"  {'D9 索引完整性':<18s} {scores['D9_index_coverage']:>6.1f}%  {'✅' if scores['D9_index_coverage'] >= 90 else '❌'}  "
          f"(index.md 覆盖: {stats['in_index']}/{stats['total_pages']})")
    print(f"  {'D10 知识新鲜度':<18s} {scores['D10_freshness']:>6.1f}%  {'✅' if scores['D10_freshness'] >= 70 else '❌'}  "
          f"(30天内更新: {stats['recent_updated']}/{stats['total_pages']})")
    print(f"  {'D11 覆盖率':<18s} {scores['D11_raw_coverage']:>6.1f}%  {'✅' if scores['D11_raw_coverage'] >= 70 else '❌'}  "
          f"(raw→wiki 映射: {stats['total_raw_sources']} 源文件)")
    print(f"  {'D12 反幻觉率':<18s} {scores['D12_anti_hallucination']:>6.1f}%  {'✅' if scores['D12_anti_hallucination'] >= 90 else '❌'}  "
          f"(行号引用≥2处: {stats['has_line_refs']}/{stats['total_pages']} | 总引用: {stats['total_line_refs']} 处)")
    print()

    # ── 红线汇总 ──
    print(f"🚨 红线判定: {scores['passed_count']}/{scores['total_checks']} 通过")
    for key, r in scores['redlines'].items():
        icon = "✅" if r['passed'] else "❌"
        print(f"  {icon} {r['label']}: {r['actual']} (阈值 {r['threshold']})")

    print()
    health = scores['health_score']
    if health >= 90:
        grade = "🟢 A 级 — 生产级知识库"
    elif health >= 75:
        grade = "🟡 B 级 — 可用但需补齐"
    elif health >= 60:
        grade = "🟠 C 级 — 有结构性缺陷"
    else:
        grade = "🔴 D 级 — 需要重建"

    print(f"📊 综合健康度: {health}% — {grade}")
    fail_msg = f'❌ {scores["total_checks"] - scores["passed_count"]} 条红线违规'
    print(f"   {'✅ 全部红线通过' if scores['all_redlines_pass'] else fail_msg}")

    # ── 详细问题 ──
    if stats['dangling_refs']:
        print(f"\n⚠️ 悬空引用 (前 5 个):")
        for ref in stats['dangling_refs'][:5]:
            print(f"   {ref['page']} → {ref['reference']} (文件不存在)")

    if stats['empty_frontmatter']:
        print(f"\n⚠️ 三空字段页面:")
        for item in stats['empty_frontmatter'][:5]:
            for page, fields in item.items():
                print(f"   {page}: 缺失 {', '.join(fields)}")

    return scores


def main():
    parser = argparse.ArgumentParser(description="FlowWiki 知识库 12 维质量审计 v2.0")
    parser.add_argument("--path", default="wiki", help="wiki 目录路径")
    parser.add_argument("--raw", default=None, help="raw 目录路径（默认 ../raw）")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")
    parser.add_argument("--redline", action="store_true", help="仅显示红线")
    args = parser.parse_args()

    wiki_path = args.path
    raw_path = args.raw or str(Path(wiki_path).parent / "raw")

    stats, page_slugs = audit_wiki_full(wiki_path, raw_path)
    graph = compute_graph_metrics(stats, page_slugs)
    scores = compute_scores(stats, graph)

    if args.json:
        output = {
            'stats': {k: v for k, v in stats.items()
                      if k not in ['linked_from', 'linked_to', 'raw_to_wiki']},
            'graph': graph,
            'scores': scores,
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        if args.redline:
            print(f"🚨 红线判定: {scores['passed_count']}/{scores['total_checks']}")
            for key, r in scores['redlines'].items():
                if not r['passed']:
                    print(f"  ❌ {r['label']}: {r['actual']} (阈值 {r['threshold']})")
        else:
            format_report(stats, scores, graph, wiki_path)


if __name__ == "__main__":
    main()
