#!/usr/bin/env python3
"""
双索引同步脚本
同步 wiki/index.md（机器索引）和 00_首页/（人类索引）
"""

import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DualIndexSync:
    """双索引同步器"""

    def __init__(self, wiki_dir: str = "wiki", home_dir: str = "00_首页"):
        self.wiki_dir = Path(wiki_dir)
        self.home_dir = Path(home_dir)

    def scan_wiki(self) -> dict:
        """扫描 wiki/ 目录结构"""
        structure = {
            "concepts": [],
            "playbooks": [],
            "comparisons": [],
            "entities": [],
            "sources": [],
            "synthesis": []
        }

        for category in structure.keys():
            cat_dir = self.wiki_dir / category
            if cat_dir.exists():
                for file in cat_dir.glob("*.md"):
                    structure[category].append({
                        "name": file.stem,
                        "path": str(file.relative_to(self.wiki_dir))
                    })

        return structure

    def generate_machine_index(self, structure: dict) -> str:
        """生成机器索引（wiki/index.md）"""
        content = "# Wiki 索引\n\n"
        content += "## 机器索引 — 紧凑、结构化\n\n"

        for category, items in structure.items():
            if items:
                content += f"### {category}\n"
                for item in items:
                    content += f"- [{item['name']}]({item['path']})\n"
                content += "\n"

        return content

    def generate_human_index(self, structure: dict) -> str:
        """生成人类索引（00_首页/README.md）"""
        content = "# FlowWiki 首页\n\n"
        content += "## 人类索引 — 认知友好、场景化\n\n"

        # 知识图谱
        content += "### 01_知识图谱\n\n"
        if structure["concepts"]:
            content += "**核心概念**：\n"
            for item in structure["concepts"]:
                content += f"- [{item['name']}](../wiki/{item['path']})\n"
            content += "\n"

        # 操作手册
        content += "### 02_操作手册\n\n"
        if structure["playbooks"]:
            for item in structure["playbooks"]:
                content += f"- [{item['name']}](../wiki/{item['path']})\n"
            content += "\n"

        # 对比分析
        content += "### 03_对比分析\n\n"
        if structure["comparisons"]:
            for item in structure["comparisons"]:
                content += f"- [{item['name']}](../wiki/{item['path']})\n"
            content += "\n"

        return content

    def sync(self):
        """执行同步（幂等：内容未变则不写入）"""
        logger.info("Starting dual index sync...")

        structure = self.scan_wiki()

        # 更新机器索引（幂等）
        machine_index = self.generate_machine_index(structure)
        wiki_index = self.wiki_dir / "index.md"
        if wiki_index.exists():
            existing = wiki_index.read_text(encoding="utf-8")
            if existing != machine_index:
                wiki_index.write_text(machine_index, encoding="utf-8")
                logger.info(f"Updated machine index: {wiki_index}")
            else:
                logger.info(f"Machine index unchanged: {wiki_index}")
        else:
            wiki_index.write_text(machine_index, encoding="utf-8")
            logger.info(f"Created machine index: {wiki_index}")

        # 更新人类索引（幂等）
        human_index = self.generate_human_index(structure)
        home_index = self.home_dir / "README.md"
        if home_index.exists():
            existing = home_index.read_text(encoding="utf-8")
            if "## 机器索引" not in existing:
                existing += "\n\n## 机器索引\n\n"
                existing += "[查看完整机器索引](../wiki/index.md)\n"
                home_index.write_text(existing, encoding="utf-8")
                logger.info(f"Updated human index: {home_index}")
            else:
                logger.info(f"Human index already synced: {home_index}")
        else:
            home_index.write_text(human_index, encoding="utf-8")
            logger.info(f"Created human index: {home_index}")

        logger.info("Dual index sync completed")

def main():
    syncer = DualIndexSync()
    syncer.sync()

if __name__ == "__main__":
    main()