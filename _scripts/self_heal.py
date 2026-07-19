#!/usr/bin/env python3
"""
FlowWiki AI 自愈引擎
读取 self_check.py 输出的自检报告，自动修复可修复的问题。

可自动修复的问题类型：
  ✅ frontmatter 缺失 → 自动补全默认 frontmatter
  ✅ frontmatter 字段缺失 → 补充缺失字段
  ✅ confidence 无效 → 修正为 medium
  ✅ status 无效 → 修正为 draft
  ✅ tags 缺少 flow-wiki → 添加
  ✅ 缺少目录 → 创建目录
  ✅ 缺少首页板块 README → 创建模板
  ✅ 双索引不同步 → 调用 sync_dual_index.py

不可自动修复（需人工）：
  ❌ 悬空链接
  ❌ sources 为空
  ❌ 内容矛盾/幻觉
  ❌ 低置信度过高
  ❌ 孤立页面
"""

import json
import sys
import re
import os
import yaml
import subprocess
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WIKI_DIR = PROJECT_ROOT / "wiki"
HOME_DIR = PROJECT_ROOT / "00_首页"

DEFAULT_TYPE_MAP = {
    "concepts": "concept",
    "playbooks": "playbook",
    "criteria": "criteria",
    "comparisons": "comparison",
    "entities": "entity",
    "sources": "source",
    "synthesis": "synthesis",
    "cases": "case",
}


def load_report(report_path: str) -> dict:
    return json.loads(Path(report_path).read_text(encoding="utf-8"))


def parse_frontmatter(filepath: Path):
    text = filepath.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)", text, re.DOTALL)
    if not match:
        return None, "缺少 frontmatter", text
    try:
        data = yaml.safe_load(match.group(1))
        if data is None:
            data = {}
        return data, None, match.group(2)
    except yaml.YAMLError as e:
        return None, f"YAML 解析错误: {e}", ""


def write_frontmatter(filepath: Path, data: dict, body: str):
    fm = yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False).rstrip()
    content = f"---\n{fm}\n---\n\n{body.lstrip()}"
    filepath.write_text(content, encoding="utf-8")


def infer_type(filepath: Path) -> str:
    parts = filepath.relative_to(WIKI_DIR).parts
    if len(parts) >= 2:
        category = parts[0]
        if category in DEFAULT_TYPE_MAP:
            return DEFAULT_TYPE_MAP[category]
    return "concept"


def fix_frontmatter(filepath: Path, fix_log: list) -> bool:
    filepath = Path(filepath) if not isinstance(filepath, Path) else filepath
    abs_path = PROJECT_ROOT / filepath if not filepath.is_absolute() else filepath

    if not abs_path.exists():
        fix_log.append({"file": str(filepath), "action": "skip", "reason": "文件不存在"})
        return False

    data, err, body = parse_frontmatter(abs_path)

    if err and "缺少 frontmatter" in err:
        now = datetime.now().strftime("%Y-%m-%d")
        new_data = {
            "type": infer_type(abs_path),
            "title": abs_path.stem,
            "created": now,
            "updated": now,
            "confidence": "medium",
            "sources": [],
            "tags": ["flow-wiki"],
            "status": "draft",
        }
        write_frontmatter(abs_path, new_data, body)
        fix_log.append({"file": str(filepath), "action": "create_frontmatter", "result": "已补全默认 frontmatter"})
        return True

    if data is None:
        fix_log.append({"file": str(filepath), "action": "skip", "reason": "无法解析 frontmatter"})
        return False

    changed = False
    now = datetime.now().strftime("%Y-%m-%d")

    required_fields = ["type", "title", "created", "updated", "confidence", "sources", "tags", "status"]
    for field in required_fields:
        if field not in data or data[field] is None:
            if field == "type":
                data[field] = infer_type(abs_path)
            elif field == "title":
                data[field] = abs_path.stem
            elif field in ("created", "updated"):
                data[field] = now
            elif field == "confidence":
                data[field] = "medium"
            elif field == "sources":
                data[field] = []
            elif field == "tags":
                data[field] = ["flow-wiki"]
            elif field == "status":
                data[field] = "draft"
            changed = True
            fix_log.append({"file": str(filepath), "action": f"add_field_{field}", "result": f"补充字段 {field} = {data[field]}"})

    valid_confidence = {"low", "medium", "high"}
    if data.get("confidence") and data["confidence"] not in valid_confidence:
        old = data["confidence"]
        data["confidence"] = "medium"
        changed = True
        fix_log.append({"file": str(filepath), "action": "fix_confidence", "result": f"confidence: {old} → medium"})

    valid_status = {"draft", "reviewed", "archived", "active"}
    if data.get("status") and data["status"] not in valid_status:
        old = data["status"]
        data["status"] = "draft"
        changed = True
        fix_log.append({"file": str(filepath), "action": "fix_status", "result": f"status: {old} → draft"})

    if isinstance(data.get("tags"), list) and "flow-wiki" not in data["tags"]:
        data["tags"].append("flow-wiki")
        changed = True
        fix_log.append({"file": str(filepath), "action": "add_tag", "result": "添加 flow-wiki 标签"})

    if changed:
        data["updated"] = now
        write_frontmatter(abs_path, data, body)

    return changed


def fix_missing_dir(dir_path: str, fix_log: list) -> bool:
    target = PROJECT_ROOT / dir_path
    if not target.exists():
        target.mkdir(parents=True, exist_ok=True)
        fix_log.append({"file": dir_path, "action": "create_dir", "result": f"创建目录 {dir_path}"})
        return True
    return False


def fix_missing_home_section(section: str, fix_log: list) -> bool:
    readme = HOME_DIR / section / "README.md"
    if readme.exists():
        return False
    readme.parent.mkdir(parents=True, exist_ok=True)
    section_name = section.split("_", 1)[1] if "_" in section else section
    content = f"""---
type: moc
title: "{section_name}"
created: {datetime.now().strftime('%Y-%m-%d')}
updated: {datetime.now().strftime('%Y-%m-%d')}
tags: ["flow-wiki", "moc"]
status: active
---

# {section_name}

> 本板块由 AI 自愈引擎自动初始化，需人工补充内容。

## 待完善

- [ ] 添加 {section_name} 概览
- [ ] 添加核心页面链接
- [ ] 配置 Dataview 查询

---
*此文件由 AI Self-Healing Engine 自动生成于 {datetime.now().isoformat()}*
"""
    readme.write_text(content, encoding="utf-8")
    fix_log.append({"file": f"00_首页/{section}/README.md", "action": "create_home_section", "result": f"创建首页板块 {section}"})
    return True


def fix_dual_index_sync(fix_log: list) -> bool:
    sync_script = PROJECT_ROOT / "_scripts" / "sync_dual_index.py"
    if not sync_script.exists():
        fix_log.append({"file": "sync_dual_index.py", "action": "skip", "reason": "同步脚本不存在"})
        return False

    try:
        result = subprocess.run(
            [sys.executable, str(sync_script)],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            timeout=60,
        )
        if result.returncode == 0:
            fix_log.append({"file": "双索引", "action": "sync_index", "result": "双索引已同步"})
            return True
        else:
            fix_log.append({"file": "双索引", "action": "sync_failed", "result": result.stderr[:200]})
            return False
    except Exception as e:
        fix_log.append({"file": "双索引", "action": "sync_error", "result": str(e)[:200]})
        return False


def fix_filename(filepath: str, fix_log: list) -> bool:
    abs_path = PROJECT_ROOT / filepath
    if not abs_path.exists():
        return False

    old_name = abs_path.name
    new_name = re.sub(r'[^\w\u4e00-\u9fff\u3400-\u4dbf\-\.]', '-', old_name)
    new_name = re.sub(r'-+', '-', new_name).strip('-')

    if new_name == old_name:
        return False

    new_path = abs_path.parent / new_name
    if new_path.exists():
        fix_log.append({"file": filepath, "action": "skip_rename", "result": f"目标文件已存在: {new_name}"})
        return False

    abs_path.rename(new_path)
    fix_log.append({"file": filepath, "action": "rename", "result": f"{old_name} → {new_name}"})
    return True


def generate_benchmark_report(fix_log: list) -> bool:
    benchmark_script = PROJECT_ROOT / "_scripts" / "benchmark_competitors.py"
    if not benchmark_script.exists():
        fix_log.append({"file": "竞品对标", "action": "skip", "reason": "对标脚本不存在"})
        return False

    meta_dir = PROJECT_ROOT / "wiki" / "meta"
    meta_dir.mkdir(parents=True, exist_ok=True)
    report_md = meta_dir / "competitor-benchmark.md"
    report_json = meta_dir / "competitor-benchmark.json"

    try:
        result = subprocess.run(
            [
                sys.executable,
                str(benchmark_script),
                str(report_json),
                str(report_md),
            ],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(PROJECT_ROOT),
        )

        if result.returncode != 0:
            fix_log.append({
                "file": "竞品对标",
                "action": "benchmark_failed",
                "reason": f"执行失败: {result.stderr[:200]}",
            })
            return False

        fix_log.append({
            "file": str(report_md.relative_to(PROJECT_ROOT)),
            "action": "generate_benchmark",
            "result": "生成竞品对标分析报告",
        })
        return True

    except subprocess.TimeoutExpired:
        fix_log.append({"file": "竞品对标", "action": "skip", "reason": "超时 (120s)"})
        return False
    except Exception as e:
        fix_log.append({"file": "竞品对标", "action": "skip", "reason": f"异常: {str(e)[:100]}"})
        return False


def heal_report(report: dict) -> dict:
    issues = report.get("issues", [])
    fix_log = []

    fixable_issues = [i for i in issues if i.get("fixable")]
    print(f"待修复问题: {len(fixable_issues)}/{len(issues)}")

    files_to_fix_fm = set()
    dirs_to_create = set()
    home_sections = set()
    files_to_rename = set()
    needs_sync = False

    for issue in fixable_issues:
        cat = issue.get("category", "")
        file = issue.get("file", "")
        msg = issue.get("message", "")

        if cat == "lint" and ("缺少" in msg or "frontmatter" in msg or "confidence" in msg or "status" in msg or "tags" in msg):
            if file.endswith(".md") and file.startswith("wiki/"):
                files_to_fix_fm.add(file)

        if cat == "structure" and "缺少目录" in msg:
            dirs_to_create.add(file)

        if cat == "structure" and "首页板块缺失" in msg:
            m = re.search(r'首页板块缺失: (\S+)', msg)
            if m:
                home_sections.add(m.group(1))

        if cat == "lint" and "文件名不规范" in msg:
            files_to_rename.add(file)

        if cat == "sync" and ("索引" in msg or "同步" in msg):
            needs_sync = True

    print(f"\n修复计划:")
    print(f"  - frontmatter 修复: {len(files_to_fix_fm)} 个文件")
    print(f"  - 创建目录: {len(dirs_to_create)} 个")
    print(f"  - 首页板块: {len(home_sections)} 个")
    print(f"  - 重命名文件: {len(files_to_rename)} 个")
    print(f"  - 双索引同步: {'是' if needs_sync else '否'}")

    fixed_count = 0

    for d in sorted(dirs_to_create):
        if fix_missing_dir(d, fix_log):
            fixed_count += 1

    for sec in sorted(home_sections):
        if fix_missing_home_section(sec, fix_log):
            fixed_count += 1

    for f in sorted(files_to_rename):
        if fix_filename(f, fix_log):
            fixed_count += 1

    for f in sorted(files_to_fix_fm):
        if fix_frontmatter(f, fix_log):
            fixed_count += 1

    if needs_sync:
        if fix_dual_index_sync(fix_log):
            fixed_count += 1

    benchmark_issues = [i for i in issues if i.get("category") == "benchmark"]
    needs_benchmark = len(benchmark_issues) > 0 and not os.environ.get("FLOW_WIKI_SKIP_BENCHMARK", "0") == "1"
    if needs_benchmark:
        print(f"\n[额外] 生成竞品对标报告...")
        if generate_benchmark_report(fix_log):
            fixed_count += 1

    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_issues": len(issues),
        "fixable_issues": len(fixable_issues),
        "fixed_items": len(fix_log),
        "changes": fix_log,
    }

    return summary


def main():
    if len(sys.argv) < 2:
        print("用法: python self_heal.py <自检报告.json> [输出修复报告.json]")
        print("示例: python self_heal.py self_check_report.json heal_report.json")
        sys.exit(1)

    report_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    print("=" * 60)
    print("  FlowWiki AI 自愈引擎")
    print(f"  时间: {datetime.now().isoformat()}")
    print("=" * 60)

    print(f"\n读取自检报告: {report_path}")
    report = load_report(report_path)
    health = report.get("health", {})
    print(f"  健康评分: {health.get('score', '?')}/100 ({health.get('level', '?')})")
    print(f"  问题总数: {health.get('total_issues', 0)}")

    print("\n开始自愈...")
    result = heal_report(report)

    print("\n" + "=" * 60)
    print("  自愈结果汇总")
    print("=" * 60)
    print(f"  总问题数: {result['total_issues']}")
    print(f"  可修复数: {result['fixable_issues']}")
    print(f"  实际修复项: {result['fixed_items']}")

    if result["changes"]:
        print(f"\n  变更明细:")
        for change in result["changes"]:
            msg = change.get("result") or change.get("reason", "")
            icon = "✅" if "skip" not in change["action"] else "⏭️"
            print(f"    {icon} [{change['action']}] {change['file']}: {msg}")

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(
            json.dumps(result, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"\n  修复报告已保存: {output_path}")

    if result["fixed_items"] > 0:
        print(f"\n  👉 已修复 {result['fixed_items']} 项，建议人工审核后合并")
    else:
        print("\n  ✅ 无需修复，知识库健康")

    sys.exit(0)


if __name__ == "__main__":
    main()
