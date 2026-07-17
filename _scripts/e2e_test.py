#!/usr/bin/env python3
"""
FlowWiki 完整端到端测试
覆盖：ingest → ACE → ZK 卡片 → 双索引同步 → lint 体检 → 文件完整性校验
"""

import json
import os
import sys
import subprocess
import yaml
from pathlib import Path
from datetime import datetime

# 测试结果收集
results = []
passed = 0
failed = 0

def test(name, condition, detail=""):
    global passed, failed
    if condition:
        results.append(f"  ✅ {name}" + (f" — {detail}" if detail else ""))
        passed += 1
    else:
        results.append(f"  ❌ {name}" + (f" — {detail}" if detail else ""))
        failed += 1

def section(title):
    results.append(f"\n{'='*60}")
    results.append(f"  {title}")
    results.append(f"{'='*60}")

PYTHON = sys.executable
BASE = Path(__file__).parent.parent

# ============================================================
# 1. 文件结构完整性校验
# ============================================================
section("1. 文件结构完整性校验")

# L1 知识编译层
test("raw/ 目录存在", (BASE / "raw").is_dir())
test("raw/README.md 存在", (BASE / "raw/README.md").exists())
test("wiki/ 目录存在", (BASE / "wiki").is_dir())
test("wiki/index.md 存在", (BASE / "wiki/index.md").exists())
test("wiki/log.md 存在", (BASE / "wiki/log.md").exists())
test("wiki/README.md 存在", (BASE / "wiki/README.md").exists())
test("00_首页/ 目录存在", (BASE / "00_首页").is_dir())
test("00_首页/README.md 存在", (BASE / "00_首页/README.md").exists())

# 6 板块
for i, name in enumerate(["01_知识图谱", "02_判据体系", "03_实战场景", "04_进化学习", "05_采集记录", "06_系统运维"], 1):
    test(f"00_首页/{name}/README.md", (BASE / f"00_首页/{name}/README.md").exists())

# 7 场景
scenarios = ["大气溯源", "执法办案", "排污许可", "企业合规", "督察现场", "案卷评查", "迎检准备"]
test(f"7 场景全齐 ({len(scenarios)} 个)", all(
    (BASE / f"00_首页/03_实战场景/{s}/README.md").exists() for s in scenarios
), f"场景: {', '.join(scenarios)}")

# L2 检索增强层
test("config.toml 存在", (BASE / "config.toml").exists())
test(".llm-wiki/config.toml 存在", (BASE / ".llm-wiki/config.toml").exists())

# L3 Spec-Driven 层
for f in ["design.md", "requirements.md", "structure.md", "tasks.md", "hermes-integration.md"]:
    test(f"spec/{f}", (BASE / f"spec/{f}").exists())
test("openspec/changes/archive/ 存在", (BASE / "openspec/changes/archive").is_dir())

# L4 Agent 记忆层
for d in ["zettelkasten", "episodic", "conflict", "ace"]:
    test(f".memory/{d}/ 目录", (BASE / f".memory/{d}").is_dir())
test(".memory/README.md", (BASE / ".memory/README.md").exists())

# L5 Skill 化层
agents_skills = list((BASE / ".agents/skills").glob("*/SKILL.md"))
claude_skills = list((BASE / ".claude/skills").glob("*/SKILL.md"))
test(f".agents/skills/ SKILL.md 数量", len(agents_skills) == 27, f"实际: {len(agents_skills)}")
test(f".claude/skills/ SKILL.md 数量", len(claude_skills) == 27, f"实际: {len(claude_skills)}")
test("双格式 skill 一致", len(agents_skills) == len(claude_skills) == 27)

# L6 多 agent 接手层
for f in ["CLAUDE.md", "AGENTS.md", "CODEX.md", "WORKBUDDY.md"]:
    test(f".agents/{f}", (BASE / f".agents/{f}").exists())
test("根目录 CLAUDE.md", (BASE / "CLAUDE.md").exists())

# L7 场景层 - industry.yaml
storage_dirs = list((BASE / "storage").iterdir())
yaml_count = sum(1 for d in storage_dirs if (d / "industry.yaml").exists())
test(f"storage/ industry.yaml 数量", yaml_count == 7, f"实际: {yaml_count}")

# 基础设施
test("SCHEMA.md", (BASE / "SCHEMA.md").exists())
test("LICENSE", (BASE / "LICENSE").exists())
test("README.md", (BASE / "README.md").exists())
test(".gitignore", (BASE / ".gitignore").exists())

# 模板
templates = list((BASE / "_templates").glob("*.j2"))
test(f"_templates/ 模板数量", len(templates) >= 7, f"实际: {len(templates)}")

# 脚本
scripts = list((BASE / "_scripts").glob("*.py"))
test(f"_scripts/ 脚本数量", len(scripts) >= 6, f"实际: {len(scripts)}")

# docs
for f in ["getting-started.md", "methodology.md", "comparison.md", "examples.md"]:
    test(f"docs/{f}", (BASE / f"docs/{f}").exists())

# 70_Prompt库
test("70_Prompt库/README.md", (BASE / "70_Prompt库/README.md").exists())

# ============================================================
# 2. industry.yaml 内容校验
# ============================================================
section("2. industry.yaml 内容校验")

for yaml_file in sorted((BASE / "storage").glob("*/industry.yaml")):
    try:
        with open(yaml_file, "r") as f:
            data = yaml.safe_load(f)
        slug = data.get("slug", "?")
        has_name = "name" in data
        has_scenarios = "scenarios" in data and len(data["scenarios"]) > 0
        has_skills = "industry_skills" in data and len(data["industry_skills"]) > 0
        has_raw = "raw_sources" in data
        has_wiki = "wiki_structure" in data
        test(f"{slug}: industry.yaml 完整",
             has_name and has_scenarios and has_skills and has_raw and has_wiki,
             f"scenarios={len(data.get('scenarios',[]))}, skills={len(data.get('industry_skills',[]))}")
    except Exception as e:
        test(f"{yaml_file.parent.name}: industry.yaml 解析", False, str(e))

# ============================================================
# 3. SKILL.md 内容校验
# ============================================================
section("3. SKILL.md 内容校验")

for skill_file in sorted((BASE / ".agents/skills").glob("*/SKILL.md")):
    content = skill_file.read_text(encoding="utf-8")
    name = skill_file.parent.name
    has_function = "## 功能" in content or "## 功能" in content
    has_input = "## 输入" in content or "## 输入" in content
    has_output = "## 输出" in content or "## 输出" in content
    has_constraint = "## 约束" in content or "## 约束" in content
    test(f"skill/{name}: 结构完整",
         has_function and has_input and has_output,
         f"功能={'✅' if has_function else '❌'} 输入={'✅' if has_input else '❌'} 输出={'✅' if has_output else '❌'} 约束={'✅' if has_constraint else '❌'}")

# ============================================================
# 4. .claude/skills vs .agents/skills 内容一致性
# ============================================================
section("4. Skill 双格式一致性")

mismatches = []
for agents_file in sorted((BASE / ".agents/skills").glob("*/SKILL.md")):
    skill_name = agents_file.parent.name
    claude_file = BASE / f".claude/skills/{skill_name}/SKILL.md"
    if not claude_file.exists():
        mismatches.append(f"{skill_name}: .claude/ 缺失")
    else:
        a_content = agents_file.read_text(encoding="utf-8")
        c_content = claude_file.read_text(encoding="utf-8")
        if a_content != c_content:
            mismatches.append(f"{skill_name}: 内容不一致")

test("27 skill 内容完全一致", len(mismatches) == 0,
     f"{'无差异' if not mismatches else '; '.join(mismatches[:5])}")

# ============================================================
# 5. Ingest Pipeline 测试
# ============================================================
section("5. Ingest Pipeline 测试")

# 创建测试 raw 文件
test_raw = BASE / "raw" / "test_e2e.md"
test_raw.write_text("""# 测试文档：EKMA 曲线在 O3 污染溯源中的应用

## 来源
- 文件类型：技术报告
- 发布日期：2026-07-17
- 作者：测试

## 内容摘要
EKMA 曲线是分析 O3 生成敏感性的重要工具。通过绘制 VOCs-NOx 等浓度线，
可以判断 O3 生成处于 VOCs 控制区还是 NOx 控制区。

## 关键参数
- VOCs/NOx 比值阈值：8（分界线）
- O3 最大值出现在比值 = 4-6 区间
""", encoding="utf-8")
test("创建测试 raw 文件", test_raw.exists())

# 运行 ingest_pipeline.py
os.chdir(BASE)
r = subprocess.run([PYTHON, "_scripts/ingest_pipeline.py"], capture_output=True, text=True)
test("ingest_pipeline.py 执行", r.returncode == 0, r.stdout.strip()[:200] if r.returncode == 0 else r.stderr.strip()[:200])

# 验证 wiki/index.md 更新
index_content = (BASE / "wiki/index.md").read_text(encoding="utf-8")
test("wiki/index.md 非空", len(index_content) > 0)
test("wiki/index.md 包含概念索引", "概念" in index_content or "concepts" in index_content.lower())

# ============================================================
# 6. ACE 反思循环测试
# ============================================================
section("6. ACE 反思循环测试")

r = subprocess.run([PYTHON, "_scripts/ace_review.py"], capture_output=True, text=True)
test("ace_review.py 执行", r.returncode == 0, r.stdout.strip()[:200] if r.returncode == 0 else r.stderr.strip()[:200])

# 验证 ACE 日志
ace_logs = list((BASE / ".memory/ace").glob("*.md"))
test("ACE 日志生成", len(ace_logs) >= 1, f"日志数: {len(ace_logs)}")

# 解析最新 ACE 日志
if ace_logs:
    latest_log = max(ace_logs, key=lambda p: p.stat().st_mtime)
    log_content = latest_log.read_text(encoding="utf-8")
    test("ACE 日志含 Generator 输出", "Generator" in log_content)
    test("ACE 日志含 Reflector 审查", "Reflector" in log_content)
    test("ACE 日志含 Curator 决策", "Curator" in log_content)

# ============================================================
# 7. A-MEM 卡片生成测试
# ============================================================
section("7. A-MEM 卡片生成测试")

r = subprocess.run([PYTHON, "_scripts/a_mem_card.py"], capture_output=True, text=True)
test("a_mem_card.py 执行", r.returncode == 0, r.stdout.strip()[:200] if r.returncode == 0 else r.stderr.strip()[:200])

# 验证 ZK 卡片
zk_cards = [f for f in (BASE / ".memory/zettelkasten").glob("*.md") if f.name != "README.md"]
test("ZK 卡片生成", len(zk_cards) >= 1, f"卡片数: {len(zk_cards)}")

# 验证卡片内容
if zk_cards:
    card_content = zk_cards[0].read_text(encoding="utf-8")
    test("ZK 卡片含 frontmatter", card_content.startswith("---"))
    test("ZK 卡片含 id", "id:" in card_content)
    test("ZK 卡片含 关键论点", "关键论点" in card_content)
    test("ZK 卡片含 原始证据", "原始证据" in card_content or "溯源" in card_content)

# ============================================================
# 8. 双索引同步测试
# ============================================================
section("8. 双索引同步测试")

r = subprocess.run([PYTHON, "_scripts/sync_dual_index.py"], capture_output=True, text=True)
test("sync_dual_index.py 执行", r.returncode == 0, r.stdout.strip()[:200] if r.returncode == 0 else r.stderr.strip()[:200])

# 验证机器索引
machine_index = (BASE / "wiki/index.md").read_text(encoding="utf-8")
test("机器索引非空", len(machine_index) > 0)

# 验证人类索引
human_index = (BASE / "00_首页/README.md").read_text(encoding="utf-8")
test("人类索引非空", len(human_index) > 0)
test("人类索引含 6 板块", all(s in human_index for s in ["01_知识图谱", "02_判据体系", "03_实战场景", "04_进化学习", "05_采集记录", "06_系统运维"]))

# ============================================================
# 9. 辅助脚本测试
# ============================================================
section("9. 辅助脚本测试")

r = subprocess.run([PYTHON, "_scripts/build_match_index.py"], capture_output=True, text=True)
test("build_match_index.py 执行", r.returncode == 0, r.stdout.strip()[:200] if r.returncode == 0 else r.stderr.strip()[:200])

r = subprocess.run([PYTHON, "_scripts/gen_criteria_pages.py"], capture_output=True, text=True)
test("gen_criteria_pages.py 执行", r.returncode == 0, r.stdout.strip()[:200] if r.returncode == 0 else r.stderr.strip()[:200])

# ============================================================
# 10. Lint 体检
# ============================================================
section("10. Lint 体检")

# 10.1 悬空链检查
dangling = []
for md_file in (BASE / "wiki").rglob("*.md"):
    content = md_file.read_text(encoding="utf-8")
    import re
    links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
    for text, link in links:
        if link.startswith("http") or link.startswith("#"):
            continue
        # 解析相对路径
        target = (md_file.parent / link).resolve()
        if not target.exists() and not link.startswith("../raw"):
            dangling.append(f"{md_file.name}: [{text}]({link})")

test("悬空链检查", len(dangling) == 0, f"发现 {len(dangling)} 个悬空链" + (f": {'; '.join(dangling[:3])}" if dangling else ""))

# 10.2 frontmatter 检查
no_fm = []
for md_file in (BASE / "wiki").rglob("*.md"):
    if md_file.name in ["README.md", "index.md", "log.md", "lint-report.md"]:
        continue
    if md_file.parent.name == "meta":
        continue
    content = md_file.read_text(encoding="utf-8")
    if not content.startswith("---"):
        no_fm.append(str(md_file.relative_to(BASE)))

test("frontmatter 检查", len(no_fm) == 0, f"{len(no_fm)} 个页面缺 frontmatter" + (f": {', '.join(no_fm[:3])}" if no_fm else ""))

# 10.3 孤儿页检查（wiki 页面是否被 index.md 引用）
orphan_pages = []
index_content = (BASE / "wiki/index.md").read_text(encoding="utf-8")
for md_file in (BASE / "wiki/concepts").glob("*.md"):
    if md_file.name not in index_content:
        orphan_pages.append(md_file.name)
for md_file in (BASE / "wiki/playbooks").glob("*.md"):
    if md_file.name not in index_content:
        orphan_pages.append(md_file.name)
for md_file in (BASE / "wiki/comparisons").glob("*.md"):
    if md_file.name not in index_content:
        orphan_pages.append(md_file.name)

test("孤儿页检查", len(orphan_pages) == 0, f"{len(orphan_pages)} 个孤儿页" + (f": {', '.join(orphan_pages[:3])}" if orphan_pages else ""))

# 10.4 config.toml 校验
try:
    with open(BASE / "config.toml", "r") as f:
        config_content = f.read()
    test("config.toml 含 retrieval 配置", "retrieval" in config_content)
    test("config.toml 含 ace 配置", "ace" in config_content)
    test("config.toml 含 memory 配置", "memory" in config_content)
except Exception as e:
    test("config.toml 读取", False, str(e))

# 10.5 .llm-wiki/config.toml 与根目录一致
root_config = (BASE / "config.toml").read_text(encoding="utf-8")
llm_config = (BASE / ".llm-wiki/config.toml").read_text(encoding="utf-8")
test("config.toml 双路径一致", root_config == llm_config)

# ============================================================
# 11. Git 状态检查
# ============================================================
section("11. Git 状态检查")

r = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, cwd=BASE)
uncommitted = [l for l in r.stdout.strip().split("\n") if l.strip()]
test("Git 工作区干净", len(uncommitted) <= 2, f"{len(uncommitted)} 个未提交文件" + (f": {', '.join(uncommitted[:3])}" if uncommitted else ""))

r = subprocess.run(["git", "log", "--oneline"], capture_output=True, text=True, cwd=BASE)
commits = r.stdout.strip().split("\n")
test("Git 有 commit 历史", len(commits) >= 2, f"commits: {len(commits)}")

r = subprocess.run(["git", "remote", "-v"], capture_output=True, text=True, cwd=BASE)
test("Git remote 已配置", "github.com" in r.stdout, r.stdout.strip()[:100])

# ============================================================
# 清理测试文件
# ============================================================
if test_raw.exists():
    test_raw.unlink()

# ============================================================
# 汇总
# ============================================================
section("测试汇总")
results.append(f"\n  总计: {passed + failed} 项")
results.append(f"  ✅ 通过: {passed}")
results.append(f"  ❌ 失败: {failed}")
results.append(f"  通过率: {passed/(passed+failed)*100:.1f}%")
results.append(f"  时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

print("\n".join(results))

# 输出 JSON 格式结果
report = {
    "total": passed + failed,
    "passed": passed,
    "failed": failed,
    "pass_rate": f"{passed/(passed+failed)*100:.1f}%",
    "timestamp": datetime.now().isoformat(),
    "failures": [r for r in results if "❌" in r]
}

report_path = BASE / "wiki/meta/e2e-test-report.md"
report_path.parent.mkdir(parents=True, exist_ok=True)
report_path.write_text("\n".join(results), encoding="utf-8")

print(f"\n报告已保存: {report_path}")
sys.exit(0 if failed == 0 else 1)
