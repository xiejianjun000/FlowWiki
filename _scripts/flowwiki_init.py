#!/usr/bin/env python3
"""
flowwiki-init — FlowWiki 一键初始化脚本

对标：
- Ar9av/obsidian-wiki: `obsidian-wiki setup --vault /path`
- GBrain: `gbrain init`（2 秒启动）

用法：
    flowwiki init                    # 在当前目录初始化
    flowwiki init /path/to/vault     # 指定路径初始化
    flowwiki doctor                  # 健康检查
    flowwiki status                  # 查看状态
"""

import argparse
import os
import shutil
import sys
import subprocess
from datetime import datetime
from pathlib import Path

FLOWWIKI_VERSION = "0.6.0"

# ── 默认目录结构 ──────────────────────────────────────────────
DEFAULT_DIRS = [
    "raw/",
    "wiki/",
    "00_首页/",
    "spec/",
    "openspec/",
    "_templates/",
    ".memory/zettelkasten/",
    ".memory/episodic/",
    ".memory/conflict/",
    ".memory/ace/",
    ".agents/skills/ingest/",
    ".agents/skills/query/",
    ".agents/skills/lint/",
    ".agents/skills/research/",
    ".claude/skills/ingest/",
    ".claude/skills/query/",
    ".claude/skills/lint/",
    ".claude/skills/research/",
    "storage/",
    "ops/monitoring/",
    "ops/automation/",
    "docs/",
    "70_Prompt库/",
]

DEFAULT_FILES = {
    "SCHEMA.md": """# FlowWiki Schema

## 项目结构
- `raw/` — 不可变的原始数据源（LLM 只读）
- `wiki/` — LLM 编译和维护的知识页面
- `00_首页/` — 运营看板和导航首页
- `spec/` — Spec-Driven 开发规格
- `_templates/` — Jinja2 模板
- `.memory/` — Agent 记忆层
- `.agents/skills/` — Agent Skill 定义
- `.claude/skills/` — Claude Code Skill 副本
- `storage/` — 持久化存储
- `ops/` — 运维和自动化

## 核心操作
- **ingest**: `python _scripts/ingest_pipeline.py --raw <path>`
- **query**: 读 index → 加载相关页 → 合成回答
- **lint**: `python _scripts/lint.py`
- **doctor**: `flowwiki doctor`

## 维护纪律
- raw/ 只读，AI 绝不修改
- wiki/ 写入必须经过 ACE 反思循环
- 所有知识必须可追溯到 raw/ 原始证据
""",

    "wiki/index.md": """# Wiki 索引

> 最后更新: {date}
> 页面总数: 0

## 概念
（待编译）

## 实体
（待编译）

## 对比分析
（待编译）

## 综合分析
（待编译）
""",

    "wiki/log.md": """# Wiki 操作日志

## [{date}] FlowWiki 初始化
- 操作: init
- 版本: {version}
- 状态: 成功
""",

    "config.toml": """[retrieval]
engine = "bm25"
fallback_engines = ["nano-graphrag", "lightrag"]

[ingest]
auto_compile = true
compile_interval = "30m"
max_workers = 4

[ace]
enabled = true
reflector_threshold = 0.8
curator_override = true

[memory]
card_limit = 10000
auto_prune = true
prune_threshold = 0.3

[skill]
cache_enabled = true
cache_ttl = "1h"

[logging]
level = "INFO"
format = "json"
file = "flowwiki.log"

[industry]
default = "general"
switch_enabled = true

[okf]
enabled = true
export_dir = "./okf_export"

[storage]
path = "./storage"
backup_enabled = true
backup_interval = "24h"
""",

    "AGENTS.md": """# AGENTS.md — FlowWiki 通用 Agent Bootstrap

## 身份
你是 FlowWiki 知识库的 AI 管理员。

## 启动协议
1. 读 `SCHEMA.md` → 确认维护纪律
2. 读 `wiki/index.md` → 全库索引
3. 读 `.memory/zettelkasten/` 最新卡片 → 恢复上下文
4. 读 `wiki/log.md` 最近 20 行 → 了解近期变更

## 核心操作
- **ingest**: `python _scripts/ingest_pipeline.py --raw <path>`
- **query**: 读 index → 加载相关页 → 合成回答
- **lint**: `python _scripts/lint.py`

## 输出约束
- 所有回答引用 wiki/ 页
- 写入 wiki 的内容必须经过 ACE 反思循环
- 不确定时明确告知，不编造答案
""",

    ".gitignore": """# FlowWiki .gitignore
__pycache__/
*.pyc
*.pyo
.venv/
env/
venv/
.DS_Store
*.log
.okf_export/
storage/*.db
""",
}


# ── CLI 入口 ──────────────────────────────────────────────────

def init_vault(vault_path: str, force: bool = False):
    """初始化 FlowWiki 知识库结构"""
    root = Path(vault_path).resolve()

    if root.exists() and any(root.iterdir()) and not force:
        print(f"❌ 目录不为空: {root}")
        print(f"   使用 --force 强制覆盖（不会覆盖已有文件）")
        sys.exit(1)

    root.mkdir(parents=True, exist_ok=True)

    # 创建目录结构
    dirs_created = 0
    for d in DEFAULT_DIRS:
        full = root / d
        if not full.exists():
            full.mkdir(parents=True, exist_ok=True)
            dirs_created += 1

    # 创建默认文件
    files_created = 0
    today = datetime.now().strftime("%Y-%m-%d")
    for fname, content in DEFAULT_FILES.items():
        full = root / fname
        if not full.exists():
            full.write_text(
                content.format(date=today, version=FLOWWIKI_VERSION),
                encoding="utf-8"
            )
            files_created += 1

    print(f"✅ FlowWiki v{FLOWWIKI_VERSION} 初始化完成")
    print(f"   路径: {root}")
    print(f"   创建: {dirs_created} 目录 + {files_created} 文件")
    print()
    print(f"📖 下一步:")
    print(f"   flowwiki doctor    — 健康检查")
    print(f"   flowwiki status    — 查看状态")
    print(f"   放入 raw/           — 添加原始资料")
    print(f"   flowwiki-ingest    — 开始编译知识")


def doctor(vault_path: str = "."):
    """健康检查 — 对标 Ar9av obsidian-wiki doctor 和 GBrain brain doctor"""
    root = Path(vault_path).resolve()

    if not root.exists():
        print(f"❌ 目录不存在: {root}")
        sys.exit(1)

    issues = []
    warnings = []
    ok_count = 0

    # 检查核心目录
    for d in ["raw", "wiki", "00_首页", ".memory", ".agents", ".claude"]:
        if (root / d).exists():
            ok_count += 1
        else:
            issues.append(f"缺失目录: {d}/")

    # 检查核心文件
    for f in ["SCHEMA.md", "AGENTS.md", "config.toml", "wiki/index.md", "wiki/log.md"]:
        if (root / f).exists():
            ok_count += 1
        else:
            issues.append(f"缺失文件: {f}")

    # 检查脚本
    scripts_dir = Path(__file__).resolve().parent if Path(__file__).resolve().parent.name == "_scripts" else root / "_scripts"
    if scripts_dir.exists():
        key_scripts = ["ace_review.py", "lint.py", "verify_before_write.py"]
        for s in key_scripts:
            if (scripts_dir / s).exists():
                ok_count += 1
            else:
                warnings.append(f"缺失脚本: _scripts/{s}")

    # 检查 config.toml 可解析性
    config_path = root / "config.toml"
    if config_path.exists():
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib
            except ImportError:
                tomllib = None

        if tomllib:
            try:
                with open(config_path, "rb") as f:
                    tomllib.load(f)
                ok_count += 1
            except Exception as e:
                issues.append(f"config.toml 解析失败: {e}")
        else:
            warnings.append("无法检查 config.toml（缺少 tomli 库）")

    # 报告
    print(f"🏥 FlowWiki Doctor 报告")
    print(f"   路径: {root}")
    print(f"   {ok_count} 项通过")

    if issues:
        print(f"\n🔴 严重问题 ({len(issues)}):")
        for i in issues:
            print(f"   - {i}")

    if warnings:
        print(f"\n🟡 警告 ({len(warnings)}):")
        for w in warnings:
            print(f"   - {w}")

    if not issues and not warnings:
        print("   ✅ 一切正常")

    # 状态统计
    wiki_pages = len(list((root / "wiki").rglob("*.md"))) if (root / "wiki").exists() else 0
    raw_files = len(list((root / "raw").rglob("*"))) if (root / "raw").exists() else 0
    print(f"\n📊 统计:")
    print(f"   Wiki 页面: {wiki_pages}")
    print(f"   原始资料: {raw_files}")

    return 0 if not issues else 1


def status(vault_path: str = "."):
    """查看知识库状态"""
    root = Path(vault_path).resolve()

    if not (root / "config.toml").exists():
        print("❌ 未找到 config.toml，请先运行 flowwiki init")
        sys.exit(1)

    wiki_pages = len(list((root / "wiki").rglob("*.md"))) if (root / "wiki").exists() else 0
    raw_files = len(list((root / "raw").rglob("*"))) if (root / "raw").exists() else 0

    # 读取 log 最近变更
    log_path = root / "wiki" / "log.md"
    last_action = "无记录"
    if log_path.exists():
        lines = log_path.read_text(encoding="utf-8").strip().split("\n")
        for line in reversed(lines):
            if line.startswith("## ["):
                last_action = line.strip("# ")
                break

    print(f"📋 FlowWiki v{FLOWWIKI_VERSION} 状态")
    print(f"   路径: {root}")
    print(f"   Wiki 页面: {wiki_pages}")
    print(f"   原始资料: {raw_files}")
    print(f"   最近操作: {last_action}")


def main():
    parser = argparse.ArgumentParser(
        description="FlowWiki — AI 与人类协同复利的知识库",
        prog="flowwiki"
    )
    sub = parser.add_subparsers(dest="command", help="命令")

    # flowwiki init
    p_init = sub.add_parser("init", help="初始化 FlowWiki 知识库")
    p_init.add_argument("path", nargs="?", default=".", help="知识库路径（默认当前目录）")
    p_init.add_argument("--force", action="store_true", help="强制初始化（不检查空目录）")

    # flowwiki doctor
    p_doctor = sub.add_parser("doctor", help="健康检查")
    p_doctor.add_argument("--path", default=".", help="知识库路径")

    # flowwiki status
    p_status = sub.add_parser("status", help="查看状态")

    # flowwiki version
    sub.add_parser("version", help="显示版本")

    args = parser.parse_args()

    if args.command == "init":
        init_vault(args.path, args.force)
    elif args.command == "doctor":
        sys.exit(doctor(args.path))
    elif args.command == "status":
        status()
    elif args.command == "version":
        from pathlib import Path as _Path
        print(f"FlowWiki v{FLOWWIKI_VERSION}")
        print(f"路径: {_Path(__file__).resolve().parent.parent}")
    else:
        parser.print_help()
        print("\n快速开始: flowwiki init")


if __name__ == "__main__":
    main()
