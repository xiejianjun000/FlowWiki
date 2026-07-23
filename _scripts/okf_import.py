#!/usr/bin/env python3
"""
OKF（Open Knowledge Format）导入器 — 将外部 OKF bundle 导入 FlowWiki wiki/。

导入流程：
  1. 验证 SHA256SUMS 完整性
  2. 检查 okf.json 格式兼容性
  3. 确认不会覆盖已有页面（冲突检测）
  4. 将 pages/ 写入 wiki/ 对应目录
  5. 更新 wiki/index.md
  6. 追加 wiki/log.md

安全机制：
  - 默认写入审核队列（--trusted 可跳过）
  - 冲突时自动重命名（--force 可覆盖）
  - 只接受 OKF v1.x 兼容的 bundle

用法：
  python _scripts/okf_import.py --input ./okf_export
  python _scripts/okf_import.py --input ./bundle --trusted
  python _scripts/okf_import.py --input ./bundle --force --trusted
"""

import argparse
import hashlib
import json
import logging
import shutil
import yaml
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

WIKI_DIR = Path("wiki")
QUARANTINE_DIR = WIKI_DIR / "_quarantine"


def sha256_file(filepath: Path) -> str:
    """计算文件 SHA-256 哈希。"""
    h = hashlib.sha256()
    h.update(filepath.read_bytes())
    return h.hexdigest()


def verify_integrity(bundle_dir: Path) -> tuple[bool, list[str]]:
    """验证 OKF bundle 的 SHA256SUMS 完整性。"""
    sums_file = bundle_dir / "SHA256SUMS"
    if not sums_file.exists():
        return False, ["缺少 SHA256SUMS 文件"]

    errors = []
    for line in sums_file.read_text(encoding="utf-8").strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        parts = line.split("  ", 1)
        if len(parts) != 2:
            errors.append(f"SHA256SUMS 格式错误: {line}")
            continue
        expected_hash, rel_path = parts
        file_path = bundle_dir / rel_path
        if not file_path.exists():
            errors.append(f"文件缺失: {rel_path}")
            continue
        actual_hash = sha256_file(file_path)
        if actual_hash != expected_hash:
            errors.append(f"哈希不匹配: {rel_path} (期望 {expected_hash[:8]}..., 实际 {actual_hash[:8]}...)")

    return len(errors) == 0, errors


def load_manifest(bundle_dir: Path) -> dict:
    """加载并验证 OKF manifest。"""
    manifest_path = bundle_dir / "okf.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"缺少 okf.json: {manifest_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    okf_version = manifest.get("okf_version", "0.0.0")
    if not okf_version.startswith("1."):
        raise ValueError(f"不支持的 OKF 版本: {okf_version}（需要 1.x）")

    return manifest


def detect_conflicts(manifest: dict, wiki_dir: Path) -> list[str]:
    """检测即将写入的页面是否与现有页面冲突。"""
    conflicts = []
    for page_id, page in manifest.get("pages", {}).items():
        target = wiki_dir / page["path"]
        if target.exists():
            conflicts.append(str(page["path"]))
    return conflicts


def import_pages(manifest: dict, bundle_dir: Path, wiki_dir: Path,
                 trusted: bool = False, force: bool = False) -> dict:
    """将 OKF pages 导入 wiki/ 目录。"""
    pages_dir = bundle_dir / "pages"
    imported = []
    skipped = []
    quarantined = []

    for page_id, page in manifest.get("pages", {}).items():
        source_file = pages_dir / (page_id + ".md")
        target_path = wiki_dir / page["path"]

        # 冲突检测
        if target_path.exists() and not force:
            skipped.append({
                "page": page_id,
                "reason": "目标已存在（使用 --force 覆盖）",
            })
            continue

        if not source_file.exists():
            skipped.append({
                "page": page_id,
                "reason": f"源文件不存在: {source_file}",
            })
            continue

        # 非 trusted 模式 → 写入隔离区审核
        if not trusted:
            q_dir = QUARANTINE_DIR / "okf_import"
            q_dir.mkdir(parents=True, exist_ok=True)
            q_target = q_dir / target_path.name
            target_path.parent.mkdir(parents=True, exist_ok=True)

            # 先复制到隔离区
            shutil.copy2(source_file, q_target)

            # 写入验证报告
            report = {
                "imported_at": datetime.now().isoformat(),
                "page_id": page_id,
                "source_bundle": str(bundle_dir),
                "okf_version": manifest.get("okf_version"),
                "page_metadata": page,
                "status": "pending_review",
            }
            report_path = q_dir / (target_path.stem + ".review.json")
            report_path.write_text(
                json.dumps(report, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            quarantined.append({
                "page": page_id,
                "path": str(q_target),
                "reason": "已放入隔离区等待审核（使用 --trusted 直接导入）",
            })
            continue

        # Trusted 模式 → 直接写入
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_file, target_path)
        imported.append(page_id)

    return {
        "imported": imported,
        "skipped": skipped,
        "quarantined": quarantined,
    }


def update_index(wiki_dir: Path, manifest: dict):
    """更新 wiki/index.md 索引。"""
    index_path = wiki_dir / "index.md"
    existing_entries = set()

    if index_path.exists():
        content = index_path.read_text(encoding="utf-8")
        for line in content.split("\n"):
            if line.startswith("- [["):
                existing_entries.add(line)

    new_entries = []
    for page_id, page in manifest.get("pages", {}).items():
        title = page.get("title", page_id)
        entry = f"- [[{title}]] ({page.get('type', '')}) — {page.get('confidence', '')}"
        if entry not in existing_entries:
            new_entries.append(entry)

    if new_entries:
        with index_path.open("a", encoding="utf-8") as f:
            f.write("\n## OKF 导入 ({})\n\n".format(datetime.now().strftime("%Y-%m-%d")))
            for entry in new_entries:
                f.write(entry + "\n")


def append_log(wiki_dir: Path, result: dict):
    """追加 wiki/log.md 日志。"""
    log_path = wiki_dir / "log.md"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    entry = (
        f"\n## [{timestamp}] OKF 导入\n"
        f"- 导入页面: {len(result['imported'])}\n"
        f"- 隔离审核: {len(result['quarantined'])}\n"
        f"- 跳过: {len(result['skipped'])}\n"
    )
    with log_path.open("a", encoding="utf-8") as f:
        f.write(entry)


def main():
    parser = argparse.ArgumentParser(description="FlowWiki OKF 导入器")
    parser.add_argument(
        "--input", "-i", type=str, required=True,
        help="OKF bundle 目录路径",
    )
    parser.add_argument(
        "--trusted", action="store_true",
        help="跳过隔离区审核，直接写入 wiki/",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="覆盖已有页面（默认跳过冲突）",
    )
    parser.add_argument(
        "--wiki-dir", type=str, default="wiki",
        help="目标 wiki 目录（默认: wiki）",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="只检查不写入",
    )

    args = parser.parse_args()
    bundle_dir = Path(args.input)
    wiki_dir = Path(args.wiki_dir)

    if not bundle_dir.is_dir():
        logger.error(f"bundle 目录不存在: {bundle_dir}")
        return

    # Step 1: 完整性验证
    logger.info("验证 bundle 完整性...")
    ok, errors = verify_integrity(bundle_dir)
    if not ok:
        for err in errors:
            logger.error(f"  完整性错误: {err}")
        logger.error("验证失败，拒绝导入")
        return

    # Step 2: 加载 manifest
    logger.info("加载 OKF manifest...")
    try:
        manifest = load_manifest(bundle_dir)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
        logger.error(f"manifest 无效: {e}")
        return

    logger.info(f"  OKF 版本: {manifest.get('okf_version')}")
    logger.info(f"  页面数: {manifest['stats']['page_count']}")
    logger.info(f"  关系数: {manifest['stats']['relation_count']}")

    # Step 3: 冲突检测
    conflicts = detect_conflicts(manifest, wiki_dir)
    if conflicts and not args.force:
        logger.warning(f"检测到 {len(conflicts)} 个冲突:")
        for c in conflicts:
            logger.warning(f"  - {c}")
        logger.warning("使用 --force 覆盖，或手动解决冲突")

    # Step 4: 导入
    if args.dry_run:
        print("\n📋 模拟导入 (dry-run)")
        print(f"   将导入: {manifest['stats']['page_count']} 页")
        print(f"   冲突: {len(conflicts)} 个")
        if not args.trusted:
            print("   模式: 隔离区审核（非 trusted）")
        return

    result = import_pages(manifest, bundle_dir, wiki_dir, args.trusted, args.force)

    # Step 5: 更新索引和日志
    if result["imported"] or result["quarantined"]:
        update_index(wiki_dir, manifest)
        append_log(wiki_dir, result)

    # 输出结果
    print(f"\n✅ OKF 导入完成")
    print(f"   已导入: {len(result['imported'])} 页")
    print(f"   隔离审核: {len(result['quarantined'])} 页")
    print(f"   跳过: {len(result['skipped'])} 页")

    if result["quarantined"]:
        print(f"\n⚠️  {len(result['quarantined'])} 个页面已放入隔离区：")
        for q in result["quarantined"]:
            print(f"   - {q['page']} → {q['path']}")
        print(f"\n   审查通过后执行: python _scripts/okf_import.py --input {args.input} --trusted")

    if result["skipped"]:
        for s in result["skipped"]:
            logger.warning(f"  跳过: {s['page']} — {s['reason']}")


if __name__ == "__main__":
    main()
