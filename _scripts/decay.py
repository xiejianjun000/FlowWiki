#!/usr/bin/env python3
"""
Decay — FlowWiki 记忆衰减模块（伴侣式记忆 §5.3）

生命力公式:
  vitality = recency_weight + frequency_weight + utility_weight + gravity_weight - wear_penalty

约束:
  - gravity-protected 条目不压缩（即使 vitality < 0）
  - 衰减 → 压缩为摘要，不删除
  - 归档 → 终态（archived），保留墓碑标志
  - 少数派分支（.memory/minority/）中的条目不衰减
  - 每次运行产生最多一个 git commit（CONSOLIDATE 约束）

用法:
  python _scripts/decay.py               # 执行衰减扫描
  python _scripts/decay.py --dry-run     # 预览，不实际修改
  python _scripts/decay.py --threshold N # 设置 vitality 阈值（默认 0）
"""

import argparse
import datetime
import re
import sys
from pathlib import Path
from collections import defaultdict

# ── 配置 ──────────────────────────────────────────────
KB_ROOT = Path(__file__).resolve().parent.parent
WIKI_DIR = KB_ROOT / "wiki"
MEMORY_DIR = KB_ROOT / ".memory"
DECAY_LOG = MEMORY_DIR / "decay" / "log.md"

# 生命力权重（可调）
WEIGHTS = {
    "recency": 0.3,      # 最近更新时间（越新越好）
    "frequency": 0.2,    # 被引用频率（通过 [[wikilink]] 计数）
    "utility": 0.25,     # 用户实际使用反馈（查询命中次数）
    "gravity": 0.25,     # 结构负荷承载（入链数 × 中心性）
    "wear_penalty": 0.15, # 每过 90 天衰减一次
}

# 阈值
VITALITY_FLOOR = 0       # 低于此值 → 标记 decaying
ARCHIVE_THRESHOLD = -3    # 低于此值且 decay 超过 90 天 → 压缩归档
GRAVITY_FLOOR = 0.5       # gravity_weight >= 此值 → 跳过衰减（引力保护）

TODAY = datetime.date.today()

# 确保目录存在
MEMORY_DIR.mkdir(parents=True, exist_ok=True)
(MEMORY_DIR / "decay").mkdir(parents=True, exist_ok=True)


# ── 辅助函数 ──────────────────────────────────────────

def extract_frontmatter(text: str) -> dict:
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).split("\n"):
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip("\"'")
    return fm


def count_inbound_links(wiki_files: dict, target_stem: str) -> int:
    """统计有多少其他页面引用此页面（[[wikilink]] 计数）"""
    count = 0
    for path, content in wiki_files.items():
        if path.stem == target_stem:
            continue
        link_pattern = re.compile(rf"\[\[{re.escape(target_stem)}(\|[^\]]*)?\]\]")
        count += len(link_pattern.findall(content))
    return count


def count_query_hits(page_stem: str) -> int:
    """从操作日志估算查询命中次数（简化版：统计 log.md 中的引用）"""
    log_file = WIKI_DIR / "log.md"
    if not log_file.exists():
        return 0
    try:
        log_text = log_file.read_text(encoding="utf-8")
        pattern = re.compile(rf"\[\[{re.escape(page_stem)}(\||\]\])")
        return len(pattern.findall(log_text))
    except Exception:
        return 0


def days_since(date_str: str) -> int:
    """计算自给定日期以来的天数"""
    try:
        if not date_str or date_str == "unknown":
            return 365  # 无日期 → 视为很旧
        d = datetime.date.fromisoformat(date_str.split("T")[0])
        return (TODAY - d).days
    except Exception:
        return 365


# ── 生命力计算 ────────────────────────────────────────

def calculate_vitality(page_path: Path, wiki_files: dict,
                       inlink_counts: dict = None) -> dict:
    """计算单个页面的生命力分数"""
    try:
        content = page_path.read_text(encoding="utf-8")
    except Exception:
        return {"vitality": -10, "status": "error", "reason": "read error"}

    fm = extract_frontmatter(content)
    stem = page_path.stem

    # 1. Recency（最近更新）
    updated = fm.get("updated") or fm.get("created") or "unknown"
    age_days = days_since(updated)
    recency_score = max(0, 1.0 - (age_days / 365))  # 一年内有效
    recency_weighted = recency_score * WEIGHTS["recency"]

    # 2. Frequency（被引用频率）
    if inlink_counts is not None:
        link_count = inlink_counts.get(stem, 0)
    else:
        link_count = count_inbound_links(wiki_files, stem)
    frequency_score = min(1.0, link_count / 10)  # 10 次引用 → 满分
    frequency_weighted = frequency_score * WEIGHTS["frequency"]

    # 3. Utility（查询命中）
    query_hits = count_query_hits(stem)
    utility_score = min(1.0, query_hits / 5)  # 5 次命中 → 满分
    utility_weighted = utility_score * WEIGHTS["utility"]

    # 4. Gravity（入链数 × 中心性——简化版：入链数归一化）
    gravity_score = min(1.0, link_count / 20)  # 20 个入链 → 满分
    gravity_weighted = gravity_score * WEIGHTS["gravity"]
    is_gravity_protected = gravity_weighted >= GRAVITY_FLOOR

    # 5. Wear penalty（时间磨损）
    wear_cycles = max(0, age_days // 90)  # 每 90 天一个衰减周期
    wear_penalty = min(1.0, wear_cycles * WEIGHTS["wear_penalty"])

    vitality = round(
        recency_weighted + frequency_weighted +
        utility_weighted + gravity_weighted - wear_penalty, 3
    )

    return {
        "path": str(page_path.relative_to(KB_ROOT)),
        "stem": stem,
        "vitality": vitality,
        "is_gravity_protected": is_gravity_protected,
        "age_days": age_days,
        "inbound_links": link_count,
        "query_hits": query_hits,
        "recency": round(recency_weighted, 3),
        "frequency": round(frequency_weighted, 3),
        "utility": round(utility_weighted, 3),
        "gravity": round(gravity_weighted, 3),
        "wear_penalty": round(wear_penalty, 3),
        "frontmatter_status": fm.get("status", "unknown"),
    }


# ── 衰减操作 ──────────────────────────────────────────

def compress_to_summary(page_path: Path, result: dict) -> bool:
    """将页面压缩为摘要形式，不删除原文件"""
    try:
        content = page_path.read_text(encoding="utf-8")
    except Exception:
        return False

    fm = extract_frontmatter(content)
    body_start = content.find("---", 3)
    if body_start < 0:
        body_start = 0
    else:
        body_start += 4  # 跳过后一个 ---\n

    body = content[body_start:].strip()
    # 提取前三段作为摘要
    paragraphs = [p.strip() for p in body.split("\n\n") if p.strip() and not p.strip().startswith("#")]
    summary = "\n\n".join(paragraphs[:3])
    if not summary:
        summary = body[:500]

    # 更新 frontmatter：标记 decaying + 保留原摘要
    new_fm = fm.copy()
    new_fm["status"] = "decaying"
    new_fm["decayed_at"] = TODAY.isoformat()
    new_fm["original_size"] = str(len(body))
    new_fm["summary"] = summary[:200]

    # 重建页面
    fm_lines = []
    for k, v in new_fm.items():
        if isinstance(v, str) and (" " in v or "," in v):
            fm_lines.append(f'{k}: "{v}"')
        else:
            fm_lines.append(f"{k}: {v}")

    new_content = "---\n" + "\n".join(fm_lines) + "\n---\n\n"
    new_content += f"> ⚠️ 此页面已衰减（decayed at {TODAY}）。原内容 已保留在 git 历史中。\n\n"
    new_content += f"## 摘要\n\n{summary}\n"

    page_path.write_text(new_content, encoding="utf-8")
    return True


def archive_page(page_path: Path, tombstone_dir: Path) -> bool:
    """归档页面到 tombstone 目录，保留墓碑标志"""
    try:
        content = page_path.read_text(encoding="utf-8")
    except Exception:
        return False

    fm = extract_frontmatter(content)
    fm["status"] = "archived"
    fm["archived_at"] = TODAY.isoformat()

    # 记录墓碑
    tombstone_dir.mkdir(parents=True, exist_ok=True)
    tombstone_file = tombstone_dir / page_path.name
    tombstone_file.write_text(content, encoding="utf-8")

    # 更新原文件为墓碑引用
    tombstone_content = f"""---
status: archived
archived_at: {TODAY}
tombstone: {tombstone_file.relative_to(KB_ROOT)}
original_title: {fm.get('title', page_path.stem)}
---

# ⚱️ 已归档: {fm.get('title', page_path.stem)}

此页面已归档。完整内容保留在 `{tombstone_file.relative_to(KB_ROOT)}`。

原内容可通过 git 历史恢复：`git log -- {page_path.relative_to(KB_ROOT)}`
"""
    page_path.write_text(tombstone_content, encoding="utf-8")
    return True


# ── 主流程 ────────────────────────────────────────────

def scan_all_wiki_pages() -> dict:
    """扫描 wiki/ 下所有 markdown 文件"""
    files = {}
    if WIKI_DIR.exists():
        for path in WIKI_DIR.rglob("*.md"):
            try:
                files[path] = path.read_text(encoding="utf-8")
            except Exception:
                continue
    return files


def run_decay(dry_run: bool = False, threshold: float = VITALITY_FLOOR):
    """执行衰减扫描"""
    print(f"\n{'='*55}")
    print(f"  FlowWiki 记忆衰减扫描 — {TODAY}")
    print(f"  模式: {'预览 (Dry Run)' if dry_run else '执行'}")
    print(f"  阈值: vitality < {threshold} → 衰减")
    print(f"{'='*55}\n")

    wiki_files = scan_all_wiki_pages()

    # 排除特殊目录
    wiki_pages = {p: c for p, c in wiki_files.items()
                  if ".memory" not in p.parts
                  and "_templates" not in p.parts
                  and p.parent != KB_ROOT
                  and "minority" not in p.parts}

    # 先计算所有入链计数
    inlink_counts = defaultdict(int)
    for path, content in wiki_pages.items():
        for target_path in wiki_pages:
            if target_path == path:
                continue
            link_pattern = re.compile(rf"\[\[{re.escape(target_path.stem)}(\||\]\])")
            inlink_counts[target_path.stem] += len(link_pattern.findall(content))

    # 逐页计算 vitality
    results = []
    for page_path in sorted(wiki_pages.keys()):
        result = calculate_vitality(page_path, wiki_pages, dict(inlink_counts))
        results.append(result)

    # 排序：vitality 从低到高
    results.sort(key=lambda r: r["vitality"])

    # 分类统计
    healthy = [r for r in results if r["vitality"] >= threshold]
    decaying = [r for r in results if r["vitality"] < threshold and r["vitality"] >= ARCHIVE_THRESHOLD]
    to_archive = [r for r in results if r["vitality"] < ARCHIVE_THRESHOLD]

    # 排除引力保护页面
    gravity_protected = [r for r in results if r["is_gravity_protected"]]
    decaying = [r for r in decaying if not r["is_gravity_protected"]]
    to_archive = [r for r in to_archive if not r["is_gravity_protected"]]

    # 输出概览
    print(f"  页面总数: {len(results)}")
    print(f"  ✅ 健康 (vitality ≥ {threshold}): {len(healthy)}")
    print(f"    引力保护（免衰减）: {len(gravity_protected)}")
    print(f"  🟡 建议衰减 (vitality < {threshold}): {len(decaying)}")
    print(f"  🔴 建议归档 (vitality < {ARCHIVE_THRESHOLD}): {len(to_archive)}")
    print()

    # 详细列表
    if decaying:
        print(f"  ── 衰减候选 ──")
        for r in decaying[:10]:
            print(f"  🟡 [{r['vitality']: 5.1f}] {r['stem']:<40s} "
                  f"age={r['age_days']}d links={r['inbound_links']} "
                  f"status={r['frontmatter_status']}")
        if len(decaying) > 10:
            print(f"  ... 及其余 {len(decaying) - 10} 页")
        print()

    if to_archive:
        print(f"  ── 归档候选 ──")
        for r in to_archive[:10]:
            print(f"  🔴 [{r['vitality']: 5.1f}] {r['stem']:<40s} "
                  f"age={r['age_days']}d links={r['inbound_links']}")
        if len(to_archive) > 10:
            print(f"  ... 及其余 {len(to_archive) - 10} 页")
        print()

    if not dry_run:
        # 执行衰减
        actions = 0
        tombstone_dir = MEMORY_DIR / "decay" / "tombstones"

        for r in decaying:
            page_path = KB_ROOT / r["path"]
            if not page_path.exists():
                continue
            success = compress_to_summary(page_path, r)
            if success:
                print(f"  🟡 已衰减: {r['path']}")
                actions += 1

        for r in to_archive:
            page_path = KB_ROOT / r["path"]
            if not page_path.exists():
                continue
            success = archive_page(page_path, tombstone_dir)
            if success:
                print(f"  🔴 已归档: {r['path']} → {tombstone_dir.relative_to(KB_ROOT)}")
                actions += 1

        print(f"\n  共执行 {actions} 个操作。")
        if actions > 0:
            print(f"  建议运行: git add -A && git commit -m \"chore(decay): {actions} pages decayed/archived\"")

    # 写日志
    log_entry = f"\n## [{TODAY}] decay scan\n"
    log_entry += f"- healthy: {len(healthy)}, decaying: {len(decaying)}, archived: {len(to_archive)}\n"
    log_entry += f"- gravity_protected: {len(gravity_protected)}\n"
    log_entry += f"- mode: {'dry_run' if dry_run else 'executed'}\n"

    DECAY_LOG.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if DECAY_LOG.exists() else "w"
    with open(DECAY_LOG, mode, encoding="utf-8") as f:
        if mode == "w":
            f.write("# Decay Log\n\n> 记忆衰减操作日志\n")
        f.write(log_entry)

    # 返回结果以供编程使用
    return {
        "total": len(results),
        "healthy": len(healthy),
        "decaying": len(decaying),
        "to_archive": len(to_archive),
        "gravity_protected": len(gravity_protected),
        "details": results,
    }


def main():
    parser = argparse.ArgumentParser(
        description="FlowWiki 记忆衰减引擎（伴侣式记忆 §5.3）")
    parser.add_argument("--dry-run", action="store_true",
                        help="预览模式，不实际修改文件")
    parser.add_argument("--threshold", type=float, default=VITALITY_FLOOR,
                        help=f"vitality 阈值（默认: {VITALITY_FLOOR}）")
    args = parser.parse_args()

    run_decay(dry_run=args.dry_run, threshold=args.threshold)


if __name__ == "__main__":
    main()
