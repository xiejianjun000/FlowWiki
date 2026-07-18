#!/usr/bin/env python3
"""
FlowWiki 操作日志 — 每次操作自动记录
所有脚本通过 `ops_log()` 写入统一日志

Usage:
    from ops_log import ops_log
    ops_log("query", "用户问题...", {"confidence": 0.85, "decision": "store"})
    ops_log("ingest", "录入 raw/enforcement-review/xxx.md", {"size": 1024})
    ops_log("lint", "运行 lint 检查", {"errors": 0, "warnings": 2})
    ops_log("graph", "图谱分析", {"nodes": 52, "edges": 186})
"""
import json
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = PROJECT_ROOT / ".memory" / "ops"
LOG_DIR.mkdir(parents=True, exist_ok=True)


def ops_log(
    action: str,           # 操作类型: query|ingest|lint|graph|review|fix|gap|deploy
    detail: str,           # 操作描述
    meta: dict = None,     # 附加数据
    industry: str = None,  # 行业 slug
    status: str = "ok",    # ok|warn|error
):
    """记录一次操作到日志文件。每次操作一行 JSON。"""

    today = datetime.now().strftime("%Y-%m-%d")
    log_file = LOG_DIR / f"{today}.jsonl"

    entry = {
        "ts": datetime.now().isoformat(),
        "action": action,
        "status": status,
        "detail": detail,
        "industry": industry,
    }
    if meta:
        entry["meta"] = meta

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def get_today_logs(action: str = None, limit: int = 50) -> list[dict]:
    """读取今日操作日志，可按 action 筛选。"""
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = LOG_DIR / f"{today}.jsonl"
    if not log_file.exists():
        return []

    entries = []
    with open(log_file, encoding="utf-8") as f:
        for line in f:
            try:
                e = json.loads(line.strip())
                if not action or e.get("action") == action:
                    entries.append(e)
            except json.JSONDecodeError:
                continue

    return entries[-limit:]


def log_summary(days: int = 7) -> str:
    """生成操作日志摘要。"""
    from collections import Counter

    actions = Counter()
    statuses = Counter()
    industries = Counter()
    total = 0

    for d in range(days):
        date = datetime.now().strftime(f"%Y-%m-%d") if d == 0 else ""
        # Simple: just count today's
        for entry in get_today_logs(limit=1000):
            actions[entry["action"]] += 1
            statuses[entry["status"]] += 1
            if entry.get("industry"):
                industries[entry["industry"]] += 1
            total += 1

    lines = [
        f"## 操作日志摘要",
        f"",
        f"总操作数: {total}",
        f"",
        f"### 按操作类型",
    ]
    for action, count in actions.most_common():
        lines.append(f"- {action}: {count}")
    lines += ["", "### 按状态"]
    for status, count in statuses.most_common():
        lines.append(f"- {status}: {count}")

    return "\n".join(lines)


# ── 快速测试 ──
if __name__ == "__main__":
    ops_log("query", "测试查询", {"confidence": 0.9}, industry="enforcement-review")
    ops_log("ingest", "录入检测报告", {"files": 3}, industry="enforcement-review")
    ops_log("lint", "每日 lint", {"errors": 0, "warnings": 1})
    ops_log("graph", "图谱分析", {"nodes": 52, "edges": 186})

    print(log_summary())
    print("\n最近 5 条日志:")
    for e in get_today_logs(limit=5):
        print(f"  [{e['action']}] {e['detail'][:50]} — {e['status']}")
