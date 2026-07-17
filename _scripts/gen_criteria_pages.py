#!/usr/bin/env python3

import os
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_criteria_page(criteria_name: str, criteria_list: list, output_dir: Path):
    output_file = output_dir / f"{criteria_name.lower().replace(' ', '-')}.md"
    if output_file.exists():
        logger.info(f"Skipped (already exists): {output_file}")
        return
    content = f"---\ntype: criteria\ntitle: {criteria_name}判据集\ncreated: 2026-07-17\nupdated: 2026-07-17\nconfidence: high\nsources: []\ntags: [flow-wiki, criteria]\nstatus: active\n---\n\n"
    content += f"# {criteria_name}判据集\n\n"
    content += f"## 判据数量\n\n{len(criteria_list)} 条\n\n"
    content += "## 判据列表\n\n"

    for i, criterion in enumerate(criteria_list, 1):
        content += f"### {i}. {criterion.get('name', '未命名')}\n\n"
        content += f"- **描述**：{criterion.get('description', '未描述')}\n"
        content += f"- **阈值**：{criterion.get('threshold', '未设定')}\n"
        content += f"- **来源**：{criterion.get('source', '未知')}\n"
        content += f"\n"

    output_file.write_text(content, encoding="utf-8")
    logger.info(f"Generated: {output_file}")

def main():
    logger.info("Generating criteria pages...")

    wiki_dir = Path("wiki")
    criteria_dir = wiki_dir / "criteria"
    criteria_dir.mkdir(parents=True, exist_ok=True)

    mock_criteria_sets = {
        "化学组分": [
            {"name": "PM2.5/PM10比值", "description": "判断细颗粒物污染特征", "threshold": "< 0.5", "source": "HJ 633-2012"},
            {"name": "NO2/SO2比值", "description": "判断移动源贡献", "threshold": "> 2", "source": "研究文献"},
        ],
        "气象条件": [
            {"name": "边界层高度", "description": "判断垂直扩散条件", "threshold": "< 500m", "source": "气象标准"},
            {"name": "风速阈值", "description": "判断水平扩散条件", "threshold": "< 2m/s", "source": "气象标准"},
        ],
    }

    for name, criteria in mock_criteria_sets.items():
        generate_criteria_page(name, criteria, criteria_dir)

    logger.info("Criteria pages generated successfully")

if __name__ == "__main__":
    main()