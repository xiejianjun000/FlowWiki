#!/usr/bin/env python3

import os
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def build_match_index(raw_dir: Path, wiki_dir: Path):
    index = {
        "version": "1.0",
        "timestamp": "2026-07-17T00:00:00Z",
        "matches": [],
        "raw_files": [],
        "wiki_pages": []
    }

    for raw_file in raw_dir.rglob("*"):
        if raw_file.is_file():
            index["raw_files"].append(str(raw_file.relative_to(raw_dir)))

    for wiki_file in wiki_dir.rglob("*.md"):
        if wiki_file.is_file():
            index["wiki_pages"].append(str(wiki_file.relative_to(wiki_dir)))

    index_file = Path(".memory") / "match_index.json"
    index_file.parent.mkdir(exist_ok=True)
    with open(index_file, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    logger.info(f"Built match index with {len(index['raw_files'])} raw files and {len(index['wiki_pages'])} wiki pages")

def main():
    logger.info("Building match index...")

    raw_dir = Path("raw")
    wiki_dir = Path("wiki")

    build_match_index(raw_dir, wiki_dir)

    logger.info("Match index built successfully")

if __name__ == "__main__":
    main()