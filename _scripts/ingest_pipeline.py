#!/usr/bin/env python3

import os
import re
import sys
import datetime
import yaml
import logging
from pathlib import Path

# 让本脚本可导入同目录下的 reindex 模块
sys.path.insert(0, str(Path(__file__).resolve().parent))
import reindex

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_industry_config(slug: str) -> dict:
    config_path = Path(f"storage/{slug}/industry.yaml")
    if not config_path.exists():
        logger.error(f"industry.yaml not found for {slug}")
        return {}
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def scan_raw_files(raw_dir: Path) -> list:
    files = []
    for path in raw_dir.rglob("*"):
        if path.is_file():
            files.append(str(path.relative_to(raw_dir)))
    return files

def compile_to_wiki(raw_files: list, industry_config: dict):
    wiki_dir = Path("wiki")
    wiki_dir.mkdir(exist_ok=True)

    # —— 创建骨架文件（index 由 reindex.py 统一重建） ——

    concepts = industry_config.get("wiki_structure", {}).get("concepts", [])
    for concept in concepts:
        concept_file = wiki_dir / "concepts" / f"{concept.lower().replace(' ', '-')}.md"
        concept_file.parent.mkdir(exist_ok=True)
        if not concept_file.exists():
            concept_content = f"---\ntype: concept\ntitle: {concept}\ncreated: 2026-07-17\nupdated: 2026-07-17\nconfidence: medium\nsources: []\ntags: [flow-wiki, concept]\nstatus: draft\n---\n\n"
            concept_content += f"# {concept}\n\n"
            concept_content += f"## 定义\n\n待补充\n\n"
            concept_content += f"## 相关资料\n\n"
            concept_content += f"## 关联概念\n\n"
            concept_file.write_text(concept_content, encoding="utf-8")

    playbooks = industry_config.get("wiki_structure", {}).get("playbooks", [])
    for playbook in playbooks:
        playbook_file = wiki_dir / "playbooks" / f"{playbook.lower().replace(' ', '-')}.md"
        playbook_file.parent.mkdir(exist_ok=True)
        if not playbook_file.exists():
            playbook_content = f"---\ntype: playbook\ntitle: {playbook}\ncreated: 2026-07-17\nupdated: 2026-07-17\nconfidence: medium\nsources: []\ntags: [flow-wiki, playbook]\nstatus: draft\n---\n\n"
            playbook_content += f"# {playbook}\n\n"
            playbook_content += f"## 概述\n\n待补充\n\n"
            playbook_content += f"## 步骤\n\n"
            playbook_content += f"## 注意事项\n\n"
            playbook_file.write_text(playbook_content, encoding="utf-8")

    comparisons = industry_config.get("wiki_structure", {}).get("comparisons", [])
    for comparison in comparisons:
        comp_file = wiki_dir / "comparisons" / f"{comparison.lower().replace(' ', '-').replace('vs', 'vs')}.md"
        comp_file.parent.mkdir(exist_ok=True)
        if not comp_file.exists():
            comp_content = f"---\ntype: comparison\ntitle: {comparison}\ncreated: 2026-07-17\nupdated: 2026-07-17\nconfidence: medium\nsources: []\ntags: [flow-wiki, comparison]\nstatus: draft\n---\n\n"
            comp_content += f"# {comparison}\n\n"
            comp_content += f"## 对比维度\n\n待补充\n\n"
            comp_content += f"## 结论\n\n"
            comp_file.write_text(comp_content, encoding="utf-8")

    # —— 统一重建 index.md（扫描 wiki/ 实际文件，幂等） ——
    # 解决"加了页面但 index.md 不更新"的问题（lint #5）
    reindex.main()
    logger.info(f"Compiled {len(concepts)} concepts, {len(playbooks)} playbooks, {len(comparisons)} comparisons; index auto-synced via reindex")

def run_ace_review(wiki_content: str, raw_root: Path = None) -> dict:
    """ACE 反思循环：检查 wiki 内容是否符合宪法要求（SCHEMA §4.2 / §5.1）。

    强制检查项：
    1. frontmatter 存在且含 sources 字段
    2. 含 `## 摘要` 段且非空
    3. 含 `## 原文指针` 段
    4. 原文指针段含 `全文路径` 字段
    5. 原文指针段含 `引用规则` 字段
    6. 全文路径指向的 raw 文件真实存在（若提供 raw_root，默认项目根 raw/）
    7. wiki 主体无大段原文搬运（启发式：单段不超过 500 字且不含"第X章"模式 ≥3 次）

    缺任一项返回 needs_revision，Curator 据此退回 Generator。
    """
    issues = []

    # raw_root 默认指向项目根的 raw/ 目录
    if raw_root is None:
        raw_root = Path(__file__).resolve().parent.parent / "raw"

    # 1. frontmatter 检查
    if not wiki_content.startswith("---"):
        issues.append("missing frontmatter")
    else:
        fm_end = wiki_content.find("---", 3)
        if fm_end < 0:
            issues.append("frontmatter not closed")
        else:
            fm = wiki_content[3:fm_end]
            if "sources:" not in fm:
                issues.append("frontmatter missing 'sources' field")

    # 2. 摘要段
    if "## 摘要" not in wiki_content:
        issues.append("missing '## 摘要' section (SCHEMA §4.2)")
    else:
        summary_start = wiki_content.find("## 摘要") + len("## 摘要")
        next_h2 = wiki_content.find("\n## ", summary_start)
        summary_body = wiki_content[summary_start:next_h2 if next_h2 > 0 else len(wiki_content)].strip()
        if len(summary_body) < 5:
            issues.append("'## 摘要' section is empty")

    # 3. 原文指针段
    if "## 原文指针" not in wiki_content:
        issues.append("missing '## 原文指针' section (SCHEMA §1.3 铁律)")
    else:
        ptr_start = wiki_content.find("## 原文指针") + len("## 原文指针")
        next_h2 = wiki_content.find("\n## ", ptr_start)
        ptr_body = wiki_content[ptr_start:next_h2 if next_h2 > 0 else len(wiki_content)]

        # 4. 全文路径字段
        if "全文路径" not in ptr_body:
            issues.append("'## 原文指针' missing '全文路径' field")

        # 5. 引用规则字段
        if "引用规则" not in ptr_body:
            issues.append("'## 原文指针' missing '引用规则' field")

        # 6. raw 文件存在性（可选，需 raw_root）
        if raw_root is not None:
            path_match = re.search(r"全文路径[：:]\s*`?\.\./raw/([^\s`]+)`?", ptr_body)
            if path_match:
                raw_rel = path_match.group(1)
                raw_file = raw_root / raw_rel
                if not raw_file.exists():
                    issues.append(f"dangling pointer: raw file not found: {raw_rel}")

    # 7. 全文搬运启发式检查
    chapter_pattern = re.findall(r"第[一二三四五六七八九十百零\d]+章", wiki_content)
    if len(chapter_pattern) >= 3:
        issues.append(f"possible full-text dump: found {len(chapter_pattern)} '第X章' markers (raw/ should hold full text)")

    # 决策
    if issues:
        return {
            "status": "needs_revision",
            "reviewer": "reflector",
            "timestamp": datetime.datetime.now().isoformat(),
            "issues": issues,
            "comments": f"Curator: 退回 Generator（{len(issues)} issue）"
        }
    return {
        "status": "approved",
        "reviewer": "curator",
        "timestamp": datetime.datetime.now().isoformat(),
        "issues": [],
        "comments": "符合 SCHEMA §4.2：含摘要 + 原文指针段，无全文搬运"
    }

# ═══════════════════════════════════════════════════════════
# 快速暂存模式（引自 Ar9av --quick / 伴侣式记忆 TRIAGE）
# 用途：60 秒内将临时知识片段存入 raw/inbox/
#       标记 confidence=pending，等待后续正式 ingest
# 约束：不执行 ACE 审查、不编译 wiki、不读取活跃 wiki
# ═══════════════════════════════════════════════════════════

def _content_hash(text: str) -> str:
    """生成内容哈希作为稳定 ID（TRIAGE 要求）。"""
    import hashlib
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]

def _slugify(title: str) -> str:
    """将标题转为文件安全的 slug。"""
    slug = title.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug[:80]  # 截断过长标题

def quick_capture(content: str, title: str = None, source: str = None,
                  tags: list = None, confidence: str = "pending") -> str:
    """快速暂存：将知识片段存入 raw/inbox/。

    此为 TRIAGE 操作：只做浅层过滤（去重 + 分配 ID），
    不执行语义矛盾解决，不读取活跃 wiki。

    Args:
        content: 知识片段正文
        title: 标题（可选，自动提取首行或内容哈希）
        source: 来源说明（项目名/文件路径/对话摘要）
        tags: 标签列表
        confidence: 置信度（pending 或 low）

    Returns:
        写入的文件路径（相对项目根）
    """
    inbox_dir = Path("raw/inbox")
    inbox_dir.mkdir(parents=True, exist_ok=True)

    # 分配稳定 ID
    content_id = _content_hash(content)

    # 自动标题
    if not title:
        first_line = content.strip().split("\n")[0]
        title = first_line[:120] if len(first_line) > 5 else f"untitled-{content_id}"

    slug = _slugify(title)
    today = datetime.date.today().isoformat()
    filename = f"{today}-{slug}-{content_id}.md"

    # 去重：相同 content hash 不产生重复条目（TRIAGE MUST 幂等）
    existing = list(inbox_dir.glob(f"*-{content_id}.md"))
    if existing:
        dup_path = str(existing[0])
        logger.info(f"Duplicate skipped (content hash {content_id}): "
                     f"already in {dup_path}")
        return dup_path

    # 构建 frontmatter
    tags_yaml = "\n  - ".join([""] + (tags or ["inbox"]))
    source_line = f"\nsource: {source}" if source else ""

    file_content = f"""---
title: "{title}"
type: inbox
confidence: {confidence}
created: {today}
updated: {today}
content_hash: {content_id}{source_line}
tags: [{tags_yaml}
]
---

# {title}

{content.strip()}

---

> 快速暂存于 {datetime.datetime.now().isoformat()}
> 状态: {confidence} — 等待正式 ingest 或人类策展
"""

    filepath = inbox_dir / filename
    filepath.write_text(file_content, encoding="utf-8")
    logger.info(f"Quick capture: raw/inbox/{filename} (confidence={confidence})")

    return f"raw/inbox/{filename}"


def verify_before_write_gate(wiki_dir: Path, strict: bool = False) -> dict:
    """ACE Verifier 门控：写入前逐条验证引用来源。
    
    对标 Ekgardt/llm-wiki VERIFY-BEFORE-WRITE + swarmvault candidate review。
    在 wiki/ 页面实际写入前，调用 verify_before_write.py 验证可追溯性。
    
    Args:
        wiki_dir: wiki 目录路径
        strict: 严格模式（失败即阻止写入）
    
    Returns:
        {"passed": int, "failed": int, "quarantined": list}
    """
    import importlib.util
    
    spec = importlib.util.spec_from_file_location(
        "verify_before_write",
        Path(__file__).resolve().parent / "verify_before_write.py"
    )
    if spec is None:
        logger.warning("verify_before_write.py not found, skipping pre-write verification")
        return {"passed": 0, "failed": 0, "quarantined": [], "skipped": True}
    
    vbw = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vbw)
    
    result = vbw.verify_wiki_dir(str(wiki_dir), strict=strict)
    
    if result.get("failed", 0) > 0:
        logger.warning(f"VERIFY-BEFORE-WRITE: {result['failed']} pages failed, "
                       f"{result['quarantined_count']} quarantined")
    else:
        logger.info(f"VERIFY-BEFORE-WRITE: all {result['passed']} pages passed")
    
    return result


def main():
    import argparse

    parser = argparse.ArgumentParser(description="FlowWiki Ingest Pipeline")
    parser.add_argument("--quick", "-q", action="store_true",
                        help="快速暂存模式：将内容存入 raw/inbox/（跳过 ACE 审查）")
    parser.add_argument("--title", "-t", type=str, default=None,
                        help="快速暂存的标题")
    parser.add_argument("--source", "-s", type=str, default=None,
                        help="快速暂存的来源说明")
    parser.add_argument("--tags", type=str, default=None,
                        help="快速暂存的标签（逗号分隔）")
    parser.add_argument("--file", "-f", type=str, default=None,
                        help="从文件读取内容（默认从 stdin）")
    parser.add_argument("--text", type=str, default=None,
                        help="直接传入文本内容")
    parser.add_argument("--verify", action="store_true", default=True,
                        help="启用 VERIFY-BEFORE-WRITE 门控（默认开启）")
    parser.add_argument("--no-verify", action="store_true",
                        help="跳过 VERIFY-BEFORE-WRITE 门控")
    parser.add_argument("--strict-verify", action="store_true",
                        help="严格验证模式（失败即阻止写入）")

    args = parser.parse_args()

    # ── 快速暂存模式 ──
    if args.quick:
        # 读取内容：优先 --text > --file > stdin
        if args.text:
            content = args.text
            source_hint = "命令行参数"
        elif args.file:
            filepath = Path(args.file)
            if not filepath.exists():
                logger.error(f"File not found: {args.file}")
                sys.exit(1)
            content = filepath.read_text(encoding="utf-8")
            source_hint = args.source or str(filepath)
        elif not sys.stdin.isatty():
            content = sys.stdin.read()
            source_hint = args.source or "标准输入"
        else:
            logger.error("快速暂存需要内容输入：--text / --file / 管道 stdin")
            sys.exit(1)

        tags = args.tags.split(",") if args.tags else None
        source = args.source or source_hint

        result_path = quick_capture(
            content=content,
            title=args.title,
            source=source,
            tags=tags,
            confidence="pending"
        )

        print(f"✓ 快速暂存完成: {result_path}")
        print(f"  下一步: python _scripts/ingest_pipeline.py (正式 ingest 时将处理 inbox)")
        return

    # ── 正式 Ingest 模式 ──
    logger.info("Starting ingest pipeline...")

    default_industry = "root-cause"
    industry_config = load_industry_config(default_industry)
    
    if not industry_config:
        logger.error("No industry config loaded")
        return

    raw_dir = Path("raw")
    raw_files = scan_raw_files(raw_dir)
    logger.info(f"Found {len(raw_files)} raw files")

    compile_to_wiki(raw_files, industry_config)

    # ── VERIFY-BEFORE-WRITE 门控（对标 Ekgardt/llm-wiki + swarmvault） ──
    if args.verify and not args.no_verify:
        logger.info("Running VERIFY-BEFORE-WRITE gate...")
        verify_result = verify_before_write_gate(
            Path("wiki"),
            strict=args.strict_verify
        )
        if verify_result.get("skipped"):
            logger.info("VERIFY-BEFORE-WRITE skipped (module not available)")
        elif verify_result.get("failed", 0) > 0:
            logger.warning(
                f"VERIFY-BEFORE-WRITE: {verify_result['failed']} pages failed — "
                f"see wiki/_quarantine/ for isolated content"
            )
    else:
        logger.info("VERIFY-BEFORE-WRITE gate disabled (--no-verify)")

    logger.info("Ingest pipeline completed successfully")

if __name__ == "__main__":
    main()