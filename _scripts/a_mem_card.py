#!/usr/bin/env python3
"""
A-MEM 卡片生成器
Zettelkasten 卡片自动生成与管理

每个 raw 文件入库时，Generator 生成摘要后，
本脚本负责生成 ZK 卡片并写入 .memory/zettelkasten/
"""

import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from textwrap import dedent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ZKCardGenerator:
    """Zettelkasten 卡片生成器"""

    def __init__(self, memory_dir: str = ".memory"):
        self.memory_dir = Path(memory_dir)
        self.zk_dir = self.memory_dir / "zettelkasten"
        self.zk_dir.mkdir(parents=True, exist_ok=True)

    def generate_card(
        self,
        raw_path: str,
        title: str,
        summary: str,
        key_points: list[str],
        sources: list[str],
        related_cards: list[str] | None = None,
        related_wiki: list[str] | None = None,
        confidence: str = "medium",
        tags: list[str] | None = None,
    ) -> dict:
        """生成一张 ZK 卡片

        Args:
            raw_path: raw 文件相对路径
            title: 卡片标题
            summary: 一句话主旨
            key_points: 关键论点列表
            sources: 原始证据路径列表
            related_cards: 关联卡片 ID 列表
            related_wiki: 关联 wiki 页面列表
            confidence: high | medium | low
            tags: 标签列表

        Returns:
            卡片元数据字典
        """
        date_str = datetime.now().strftime("%Y-%m-%d")
        card_id = self._generate_id(date_str)
        card_file = self.zk_dir / f"{date_str}-{card_id.split('-')[-1]}.md"

        if tags is None:
            tags = ["flow-wiki"]
        if related_cards is None:
            related_cards = []
        if related_wiki is None:
            related_wiki = []

        # 自动查找关联卡片
        auto_related = self._find_related_cards(key_points)
        all_related = list(set(related_cards + auto_related))

        card_content = dedent(f"""\
        ---
        id: {card_id}
        date: {date_str}
        tags: {tags}
        source: {raw_path}
        related: {all_related}
        confidence: {confidence}
        ---

        # {title}

        > {summary}

        ## 关键论点

        """)

        for point in key_points:
            card_content += f"- {point}\n"

        card_content += "\n## 关联知识\n\n"
        for wiki_page in related_wiki:
            card_content += f"- [[{wiki_page}]]\n"

        card_content += "\n## 关联卡片\n\n"
        for card in all_related:
            card_content += f"- [[{card}]]\n"

        card_content += "\n## 原始证据\n\n"
        for src in sources:
            card_content += f"- [[{src}]]\n"

        card_content += f"\n## 入库信息\n\n"
        card_content += f"- 入库时间：{datetime.now().isoformat()}\n"
        card_content += f"- confidence: {confidence}\n"
        card_content += f"- ACE 状态：待审查\n"

        card_file.write_text(card_content, encoding="utf-8")
        logger.info(f"ZK card generated: {card_file}")

        return {
            "card_id": card_id,
            "card_path": str(card_file),
            "title": title,
            "date": date_str,
            "related": all_related,
        }

    def _generate_id(self, date_str: str) -> str:
        """生成卡片 ID：ZK-YYYY-MM-DD-NNN"""
        existing = list(self.zk_dir.glob(f"{date_str}-*.md"))
        seq = len(existing) + 1
        return f"ZK-{date_str}-{seq:03d}"

    def _find_related_cards(self, key_points: list[str], top_k: int = 3) -> list[str]:
        """基于关键词匹配查找关联卡片

        简单实现：扫描已有卡片的 tags 和关键论点，返回匹配度最高的卡片 ID。
        生产环境可替换为 BM25 或向量检索。
        """
        related = []
        keywords = set()
        for point in key_points:
            # 简单分词：按空格和标点切分，取长度 >= 2 的词
            for word in point.replace(",", " ").replace(".", " ").split():
                if len(word) >= 2:
                    keywords.add(word)

        if not keywords:
            return related

        for card_file in self.zk_dir.glob("*.md"):
            if card_file.name == "README.md":
                continue
            try:
                content = card_file.read_text(encoding="utf-8")
                matches = sum(1 for kw in keywords if kw in content)
                if matches > 0:
                    # 从 frontmatter 提取 id
                    for line in content.split("\n"):
                        if line.startswith("id:"):
                            card_id = line.split(":", 1)[1].strip()
                            related.append((card_id, matches))
                            break
            except Exception:
                continue

        # 按匹配度排序，取 top_k
        related.sort(key=lambda x: x[1], reverse=True)
        return [r[0] for r in related[:top_k]]

    def list_cards(self, tag: str | None = None, date: str | None = None) -> list[dict]:
        """列出卡片，支持按标签和日期过滤"""
        cards = []
        for card_file in sorted(self.zk_dir.glob("*.md")):
            if card_file.name == "README.md":
                continue

            if date and not card_file.name.startswith(date):
                continue

            content = card_file.read_text(encoding="utf-8")

            if tag:
                # 简单检查 tags 字段
                in_tags = False
                for line in content.split("\n"):
                    if line.startswith("tags:"):
                        if tag in line:
                            in_tags = True
                        break
                if not in_tags:
                    continue

            # 提取元数据
            meta = {}
            for line in content.split("\n"):
                if line.startswith("---"):
                    continue
                if ":" in line and not line.startswith("#"):
                    key, val = line.split(":", 1)
                    meta[key.strip()] = val.strip()
                if line.startswith("# "):
                    meta["title"] = line[2:].strip()
                    break

            meta["file"] = str(card_file)
            cards.append(meta)

        return cards

    def archive_old_cards(self, days: int = 30):
        """归档超过指定天数的卡片"""
        archive_dir = self.zk_dir / "archive"
        archive_dir.mkdir(exist_ok=True)

        cutoff = datetime.now().timetuple().tm_yday - days
        count = 0

        for card_file in self.zk_dir.glob("*.md"):
            if card_file.name == "README.md":
                continue

            # 从文件名提取日期
            date_part = card_file.stem.split("-")
            if len(date_part) >= 3:
                try:
                    card_date = datetime(
                        int(date_part[0]), int(date_part[1]), int(date_part[2])
                    )
                    age = (datetime.now() - card_date).days
                    if age > days:
                        target = archive_dir / card_file.name
                        card_file.rename(target)
                        count += 1
                        logger.info(f"Archived: {card_file.name} -> {target}")
                except (ValueError, IndexError):
                    continue

        logger.info(f"Archived {count} cards older than {days} days")
        return count


def main():
    """测试：生成一张示例卡片"""
    generator = ZKCardGenerator()

    result = generator.generate_card(
        raw_path="raw/test.md",
        title="测试卡片",
        summary="这是一张测试用的 ZK 卡片",
        key_points=[
            "FlowWiki 采用 Zettelkasten 卡片记忆",
            "每张卡片可追溯到 raw 原始证据",
            "卡片之间通过 related 字段自动关联",
        ],
        sources=["raw/test.md"],
        related_wiki=["wiki/concepts/ekma曲线"],
        confidence="high",
        tags=["flow-wiki", "test"],
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))

    # 列出所有卡片
    cards = generator.list_cards()
    print(f"\n共 {len(cards)} 张卡片")


if __name__ == "__main__":
    main()
