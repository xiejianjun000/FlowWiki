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
VALID_STATUS = {"draft", "reviewed", "archived", "active", "现行", "inbox", "deprecated", "已废止"}
REQUIRED_FIELDS = ["type", "title", "created", "updated", "confidence", "sources", "tags", "status"]

# 法典取代映射文件路径
REPEAL_MAP_FILE = Path("storage/enforcement-review/法典取代映射.yaml")

# 旧字段名 → 应迁移到的字段名（残留会让 AI 困惑"用哪个"）
# 合并自 AI 使用反馈 + 历史字段漂移记录
LEGACY_FIELD_MAP = {
    "category": "type",
    "subcategory": "(已废弃)",
    "priority": "风险等级",
    "severity": "风险等级",
    "weight": "(已废弃)",
    "score": "(已废弃)",
    "level": "layer",
    "author": "(已废弃)",
    "version_date": "updated",
    "source": "sources",        # 单数形式 → 复数形式
    "generated": "(已废弃)",
    "last_updated": "updated",
}

# 严格模式：绝对禁止的字段（永不应出现在 frontmatter 中）
FORBIDDEN_FIELDS = {
    "category", "subcategory", "priority", "severity", "weight", "score",
    "source", "generated", "last_updated", "author",
}

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


def check_legacy_fields(data: dict, strict: bool = False) -> list[str]:
    """检查 frontmatter 是否残留旧字段。

    旧字段残留会让 AI 困惑"用哪个"，lint 必须报警。
    strict 模式：旧字段从 warning 升为 error，输出级别标记。

    依据：用户报告"Frontmatter 残留旧字段"问题 + AI 反馈"FI 漂移"。
    """
    issues = []
    prefix = "[禁止字段] " if strict else ""

    for legacy, new_field in LEGACY_FIELD_MAP.items():
        if legacy in data:
            issues.append(f"{prefix}残留旧字段: '{legacy}' → 应迁移到 '{new_field}'")

    # strict 模式：额外检查绝对禁止字段（即使不在 LEGACY_FIELD_MAP 中）
    if strict:
        for field in FORBIDDEN_FIELDS:
            if field in data and field not in LEGACY_FIELD_MAP:
                issues.append(f"[禁止字段] 非法字段 '{field}'（已废止，请删除）")

    return issues


def _load_repeal_map() -> dict | None:
    """加载法典取代映射表。返回 {被废止法律名: {code_location, note, aliases}} 或 None。"""
    if not REPEAL_MAP_FILE.exists():
        return None
    try:
        data = yaml.safe_load(REPEAL_MAP_FILE.read_text(encoding="utf-8"))
        return data.get("repealed_laws", {})
    except Exception as e:
        logger.warning(f"法典取代映射加载失败: {e}")
        return None


def check_obsolete_references(filepath: Path, text: str) -> list[str]:
    """检查 wiki 页面是否引用了已被法典废止的法律。

    依据：用户报告"概念页正文还在引用已废止的法律条文"问题。
    2026.8.15 前为过渡期（warning），之后为 error。
    """
    issues = []
    repeal_map = _load_repeal_map()
    if not repeal_map:
        return issues  # 无映射表则跳过

    # 构建被废止法律名 + 别名的扁平列表
    obsolete_names = {}
    for law_name, info in repeal_map.items():
        obsolete_names[law_name] = info
        for alias in info.get("common_aliases", []):
            obsolete_names[alias] = info

    # 扫描 wikilink [[xxx]]
    for m in re.finditer(r"\[\[([^\]]+)\]\]", text):
        target = m.group(1).split("|")[0].strip()
        # 检查是否匹配已废止法律名或别名
        for obsolete_name, info in obsolete_names.items():
            if obsolete_name in target:
                code_loc = info.get("code_location", "?")
                issues.append(
                    f"时效性引用: [[{target}]] 引用了已废止法律（{obsolete_name}），"
                    f"应改为 [[生态环境法典]] {code_loc}"
                )
                break  # 一个 wikilink 只报一次
    return issues


def check_standard_limits_table(data: dict, text: str) -> list[str]:
    """检查标准页是否含"核心限值表"段且非空。

    依据：用户报告"GB18597-2023 的核心限值表是空的。标准页最刚需的就是限值数值，反而是缺的"。
    标准页 = frontmatter type 含 'standard' 或 '标准'。
    """
    issues = []
    page_type = str(data.get("type", "")).lower()
    is_standard = ("standard" in page_type) or ("标准" in str(data.get("type", "")))

    if not is_standard:
        return issues  # 非标准页不检查

    # 检查 ## 核心限值表 段是否存在
    if "## 核心限值表" not in text:
        issues.append("标准页缺少 '## 核心限值表' 段（lint 强制项）")
        return issues

    # 检查段内容是否为空或全是占位符
    section_start = text.find("## 核心限值表") + len("## 核心限值表")
    next_h2 = text.find("\n## ", section_start)
    section_body = text[section_start:next_h2 if next_h2 > 0 else len(text)].strip()

    # 空内容
    if len(section_body) < 10:
        issues.append("'## 核心限值表' 段为空（标准页必须填写限值数值）")
        return issues

    # 检查是否全是"待补充"占位符
    if "待补充" in section_body and section_body.count("待补充") >= 2:
        issues.append("'## 核心限值表' 段全是占位符（需填写真实限值数值）")

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


def check_coverage(raw_dir: Path = None, wiki_dir: Path = None) -> str:
    """知识缺口发现：raw/ 中完整性高的文件是否被 wiki/ 引用。

    逆方向覆盖检查——不只检"wiki→raw"，还检"raw→wiki"。
    扫描 raw/ 中行数 >100 且有章节结构的文件，检查是否被至少一个 wiki 页引用。
    输出"未被利用的资源"清单。

    依据：AI 反馈——raw/ 有 32 标准、170 文件，多少没被 wiki 覆盖？
    """
    raw_dir = raw_dir or Path("raw")
    wiki_dir = wiki_dir or WIKI_DIR

    # 1. 找 raw/ 中完整性高的文件（行数 > 100）
    high_completeness: list[tuple[Path, int]] = []  # (文件, 行数)
    for raw_file in sorted(raw_dir.rglob("*.md")):
        try:
            lines = raw_file.read_text(encoding="utf-8").split("\n")
            if len(lines) > 100:
                rel = raw_file.relative_to(raw_dir)
                high_completeness.append((rel, len(lines)))
        except Exception:
            continue

    # 2. 收集 wiki/ 中所有对 raw/ 的引用
    referenced_raw: set[str] = set()
    for wiki_file in sorted(wiki_dir.rglob("*.md")):
        if wiki_file.name in ("index.md", "log.md", "README.md"):
            continue
        try:
            text = wiki_file.read_text(encoding="utf-8")
            # 从 frontmatter sources 字段
            fm_match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
            if fm_match:
                try:
                    fm = yaml.safe_load(fm_match.group(1)) or {}
                    sources = fm.get("sources", [])
                    for src in (sources if isinstance(sources, list) else []):
                        src = str(src).strip()
                        referenced_raw.add(src)
                except yaml.YAMLError:
                    pass
            # 从 全文路径 / 旧库权威全文路径 字段（兼容老格式）
            for m in re.finditer(r"全文[路经]径[：:]\s*`?(?:\.\.\/)?(raw/[^\s`]+)`?", text):
                referenced_raw.add(m.group(1))
            for m in re.finditer(r"旧库[^：:\n]*路径[：:]\s*`?(?:\.\.\/)?(raw/[^\s`]+)`?", text):
                referenced_raw.add(m.group(1))
            # 从正文中直接引用的 raw/ 路径（如 [[../raw/xxx]]）
            for m in re.finditer(r"raw/[^\s\[\]`\)]+\.md", text):
                referenced_raw.add(m.group(0))
        except Exception:
            continue

    # 3. 找出未被引用的 raw 文件
    # 宽松匹配（三级）：
    #   L1: 精确路径匹配
    #   L2: 文件名匹配
    #   L3: 词级模糊匹配（source 关键词中的实词是否出现在 raw 文件名中）
    orphaned: list[tuple[str, int]] = []

    # 提取 source 名称中的关键词（拆分为词级片段）
    source_keywords: set[str] = set()
    for ref in referenced_raw:
        # 去除路径前缀和引号
        clean = ref.replace("raw/", "").replace("../", "").strip("`\"'[]")
        # 拆分为关键词片段（非空、长度 > 2、非纯数字）
        parts = re.split(r"[/\\_.\-—]+", clean)
        for part in parts:
            part = part.strip().rstrip(".md")
            # 进一步拆中文词（取 3-4 字以上的连续中文字段）
            chinese_words = re.findall(r"[\u4e00-\u9fff]{3,}", part)
            for cw in chinese_words:
                source_keywords.add(cw)
            # 也保留数字+中文组合（如 "2024"、"GB18597"）
            if re.search(r"[\u4e00-\u9fff]", part) and len(part) >= 3:
                source_keywords.add(part)

    for rel, line_count in high_completeness:
        rel_str = str(rel)
        rel_name = Path(rel_str).name
        rel_stem = Path(rel_str).stem

        # L1 + L2
        direct_match = (
            any(rel_str in ref for ref in referenced_raw) or
            any(ref in rel_str for ref in referenced_raw) or
            rel_name in referenced_raw or
            any(rel_name in ref for ref in referenced_raw)
        )
        # L3: 词级匹配——至少一个 source 实词出现在 raw 文件名中
        fuzzy_match = any(
            kw in rel_stem for kw in source_keywords
            if len(kw) >= 4 and re.search(r"[\u4e00-\u9fff]", kw)
        )

        if not direct_match and not fuzzy_match:
            orphaned.append((rel_str, line_count))

    # 4. 生成报告
    if not orphaned:
        return (
            "# 知识缺口报告\n\n"
            f"raw/ 中完整度 >100 行的文件: {len(high_completeness)}\n"
            "✨ 全部被至少一个 wiki 页引用。\n"
        )

    lines = [
        "# 知识缺口报告（raw→wiki 反向覆盖）",
        "",
        f"## 概要",
        f"- raw/ 中完整度 >100 行的文件: {len(high_completeness)}",
        f"- 被 wiki/ 引用的: {len(high_completeness) - len(orphaned)}",
        f"- ⚠️ 未被引用的: {len(orphaned)}",
        f"- 覆盖率: {(len(high_completeness) - len(orphaned)) / max(len(high_completeness), 1) * 100:.1f}%",
        "",
        "## 未被利用的资源（按完整度降序）",
        "",
    ]
    orphaned.sort(key=lambda x: x[1], reverse=True)
    for path, line_count in orphaned:
        lines.append(f"- `{path}` ({line_count} 行) — 未被任何 wiki 页引用")

    lines.extend([
        "",
        "---",
        "*建议：这些 raw/ 文件已包含较完整的内容，",
        "可创建对应的 wiki 页（概念/操作手册/对比分析）来覆盖。*",
    ])

    return "\n".join(lines) + "\n"


def lint_file(filepath: Path, strict: bool = False) -> list[str]:
    """对单个文件执行所有检查。strict=True 时旧字段检测升为 error 级别。"""
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
    issues.extend(check_legacy_fields(data, strict=strict))

    # 时效性引用检查（扫描已废止法律的 wikilink）
    text = filepath.read_text(encoding="utf-8")
    issues.extend(check_obsolete_references(filepath, text))

    # 标准页限值表检查
    issues.extend(check_standard_limits_table(data, text))

    # 断链检查
    links = find_internal_links(filepath)
    issues.extend(check_dangling_links(links, filepath))

    return issues


def main():
    parser = argparse.ArgumentParser(description="Wiki lint 体检工具")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")
    parser.add_argument("--output", type=str, help="输出报告到文件")
    parser.add_argument("--strict", action="store_true", help="严格模式：旧字段/禁用字段视为错误，非零退出码")
    parser.add_argument("--check-coverage", action="store_true", help="知识缺口发现：raw/ 裸资源检查")

    args = parser.parse_args()

    # 知识缺口检查是独立模式，不走常规 lint 流程
    if args.check_coverage:
        report = check_coverage()
        if args.output:
            Path(args.output).write_text(report, encoding="utf-8")
            logger.info(f"报告已保存到: {args.output}")
        else:
            print(report)
        return

    logger.info("开始 wiki 体检...")

    if not WIKI_DIR.is_dir():
        logger.error(f"wiki 目录不存在: {WIKI_DIR}")
        return

    results: dict[str, list[str]] = {}
    total_issues = 0
    total_files = 0
    strict_violations = 0

    for md_file in sorted(WIKI_DIR.rglob("*.md")):
        if md_file.name in ("index.md", "log.md", "README.md"):
            continue
        total_files += 1
        issues = lint_file(md_file, strict=args.strict)
        if issues:
            rel = str(md_file.relative_to(WIKI_DIR))
            results[rel] = issues
            total_issues += len(issues)
            if args.strict:
                strict_violations += sum(1 for i in issues if "[禁止字段]" in i)

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

    # 严格模式：非法字段 → 非零退出码
    if args.strict and strict_violations > 0:
        logger.error(f"严格模式: {strict_violations} 个禁止字段违规，退出码 1")
        exit(1)


if __name__ == "__main__":
    main()
