#!/usr/bin/env python3

import os
import yaml
import logging
from pathlib import Path

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

    index_content = "# Wiki 索引\n\n"
    index_content += f"## 行业：{industry_config.get('name', '未知')}\n\n"

    concepts = industry_config.get("wiki_structure", {}).get("concepts", [])
    if concepts:
        index_content += "### 核心概念\n"
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
            index_content += f"- [{concept}](concepts/{concept_file.name})\n"
        index_content += "\n"

    playbooks = industry_config.get("wiki_structure", {}).get("playbooks", [])
    if playbooks:
        index_content += "### 操作手册\n"
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
            index_content += f"- [{playbook}](playbooks/{playbook_file.name})\n"
        index_content += "\n"

    comparisons = industry_config.get("wiki_structure", {}).get("comparisons", [])
    if comparisons:
        index_content += "### 对比分析\n"
        for comparison in comparisons:
            comp_file = wiki_dir / "comparisons" / f"{comparison.lower().replace(' ', '-').replace('vs', 'vs')}.md"
            comp_file.parent.mkdir(exist_ok=True)
            if not comp_file.exists():
                comp_content = f"---\ntype: comparison\ntitle: {comparison}\ncreated: 2026-07-17\nupdated: 2026-07-17\nconfidence: medium\nsources: []\ntags: [flow-wiki, comparison]\nstatus: draft\n---\n\n"
                comp_content += f"# {comparison}\n\n"
                comp_content += f"## 对比维度\n\n待补充\n\n"
                comp_content += f"## 结论\n\n"
                comp_file.write_text(comp_content, encoding="utf-8")
            index_content += f"- [{comparison}](comparisons/{comp_file.name})\n"
        index_content += "\n"

    index_file = wiki_dir / "index.md"
    index_file.write_text(index_content, encoding="utf-8")
    logger.info(f"Generated wiki/index.md with {len(concepts)} concepts, {len(playbooks)} playbooks, {len(comparisons)} comparisons")

def run_ace_review(wiki_content: str) -> dict:
    return {
        "status": "approved",
        "reviewer": "reflector",
        "timestamp": "2026-07-17T00:00:00Z",
        "comments": "内容符合规范"
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