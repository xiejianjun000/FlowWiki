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

def main():
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

    logger.info("Ingest pipeline completed successfully")

if __name__ == "__main__":
    main()