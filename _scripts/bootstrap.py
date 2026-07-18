#!/usr/bin/env python3
"""
FlowWiki 全自动引导流水线
用法: python _scripts/bootstrap.py --source /path/to/source --slug enforcement-review

流程:
  Step 1  入仓    复制源文件到 raw/{slug}/
  Step 2  设计    LLM 分析 raw/ → 生成 industry.yaml
  Step 3  入库    LLM 从 raw 生成 wiki 页面(concepts/playbooks/criteria/comparisons/meta)
  Step 4  一验    lint 检查 (frontmatter/sources/links)
  Step 5  自修复  断链修正 + 交叉引用 + 反链补全
  Step 6  二验    graph 检查 (孤立/密度/双向率)
  Step 7  三验    hermes_review 终验
  Step 8  注册    更新 00_首页/03_实战场景/ 入口 + 写 ops_log
"""

# macOS locale workaround
import locale
if not hasattr(locale, 'normalize'):
    locale.normalize = lambda x: x.replace('_','-').lower()

import argparse, json, os, re, shutil, subprocess, sys, urllib.request
from datetime import datetime
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from _scripts.ops_log import ops_log

# ── Config ──
API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
API_URL = "https://api.deepseek.com/v1/chat/completions"
if not API_KEY:
    print("错误: 未设置 DEEPSEEK_API_KEY", file=sys.stderr)
    sys.exit(1)

LINK_RE = re.compile(r"\[\[([^\]|#]+)(?:\|[^\]]*)?\]\]")


def step_header(n, name):
    print(f"\n{'='*60}\n  Step {n}: {name}\n{'='*60}", flush=True)


def llm(prompt, system="你是 FlowWiki 知识库架构师。", max_tok=3000):
    """Call DeepSeek API."""
    payload = json.dumps({
        "model": "deepseek-chat",
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
        "temperature": 0.3, "max_tokens": max_tok,
    }).encode()
    req = urllib.request.Request(API_URL, data=payload,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())["choices"][0]["message"]["content"]


def parse_json(text):
    """Extract JSON from LLM output (handles markdown fences)."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:])
        if text.rstrip().endswith("```"):
            text = text[:text.rfind("```")].strip()
    s, e = text.find("{"), text.rfind("}") + 1
    return json.loads(text[s:e]) if s >= 0 and e > s else None


# ══════════════════════════════════════════════════════════
# Step 1: 入仓
# ══════════════════════════════════════════════════════════

def step_ingest(source_dir, slug):
    step_header(1, f"入仓: {Path(source_dir).name} → raw/{slug}/")
    raw_dir = PROJECT_ROOT / "raw" / slug
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")

    files = [f for f in Path(source_dir).rglob("*.md")
             if ".obsidian" not in str(f) and ".git" not in str(f)]

    raw_dir.mkdir(parents=True, exist_ok=True)
    copied = 0
    new_files = []
    for f in files:
        rel = f.relative_to(source_dir)
        dst = raw_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists():
            shutil.copy2(f, dst)
            copied += 1
            new_files.append(str(rel))
            # Add ingest timestamp to frontmatter
            text = dst.read_text(encoding="utf-8")
            if text.strip().startswith("---"):
                fm_end = text.find("---", 3)
                if fm_end > 0:
                    fm = text[3:fm_end]
                    if "ingested:" not in fm:
                        text = text[:3] + f"\ningested: {now.isoformat()}\n" + text[3:]
                        dst.write_text(text, encoding="utf-8")
            else:
                text = f"---\ningested: {now.isoformat()}\n---\n\n{text}"
                dst.write_text(text, encoding="utf-8")

    # Write daily ingest report
    record_dir = PROJECT_ROOT / "00_首页" / "05_采集记录" / slug
    record_dir.mkdir(parents=True, exist_ok=True)
    if new_files:
        report = f"# {slug} 入仓记录 · {today}\n\n"
        report += f"**入仓时间**: {now.isoformat()}\n"
        report += f"**新增文件**: {len(new_files)} 篇\n\n"
        report += "## 文件清单\n\n"
        for nf in new_files:
            report += f"- `{nf}`\n"
        (record_dir / f"{today}.md").write_text(report, encoding="utf-8")

    ops_log("ingest", f"raw/{slug}/ 入仓 {copied} 篇 ({today})", {"files": copied, "date": today}, slug)
    print(f"  入仓: {copied} 篇 ({len(files)} 已有) | 记录: 00_首页/05_采集记录/{slug}/{today}.md", flush=True)
    return raw_dir, copied


# ══════════════════════════════════════════════════════════
# Step 1.5: raw 质量检测 + 自动清洗 + 退回重入
# ══════════════════════════════════════════════════════════

# Known navigation/site-chrome junk patterns (from Chinese gov websites)
JUNK_PATTERNS = [
    re.compile(r'^\s*\[大\]\s*$', re.M),
    re.compile(r'^\s*\[中\]\s*$', re.M),
    re.compile(r'^\s*\[小\]\s*$', re.M),
    re.compile(r'^\s*\[打印\]\s*$', re.M),
    re.compile(r'^\s*仅打印内容\s*$', re.M),
    re.compile(r'^教育部\s*$', re.M),
    re.compile(r'^国家民族事务委员会\s*$', re.M),
    re.compile(r'^公安部\s*$', re.M),
    re.compile(r'^民政部\s*$', re.M),
    re.compile(r'^司法部\s*$', re.M),
    re.compile(r'^财政部\s*$', re.M),
    re.compile(r'^人力资源和社会保障部\s*$', re.M),
    re.compile(r'^自然资源部\s*$', re.M),
    re.compile(r'^住房和城乡建设部\s*$', re.M),
    re.compile(r'^交通运输部\s*$', re.M),
    re.compile(r'^水利部\s*$', re.M),
    re.compile(r'^农业农村部\s*$', re.M),
    re.compile(r'^商务部\s*$', re.M),
    re.compile(r'^文化和旅游部\s*$', re.M),
    re.compile(r'^国家卫生健康委员会\s*$', re.M),
    re.compile(r'^应急管理部\s*$', re.M),
    re.compile(r'^中国人民银行\s*$', re.M),
    re.compile(r'^审计署\s*$', re.M),
    re.compile(r'^相关链接：\s*$', re.M),
    re.compile(r'^【更多】\s*$', re.M),
    re.compile(r'^\s*[\[【].*?[\】\]]\s*$', re.M),  # [xx] 【xx】 single-line labels
    re.compile(r'打印本页\s*$', re.M),
    re.compile(r'^关闭窗口\s*$', re.M),
    # Deep gov site junk — agencies below header
    re.compile(r'^(退役军人事务部|国家语言文字工作委员会|国家航天局|国家原子能机构|国家核安全局|海关总署|国家税务总局|国家市场监督管理总局|国家金融监督管理总局|中国证券监督管理委员会|国家广播电视总局|国家体育总局|国家统计局|国家国际发展合作署|国务院研究室|国家信访局|国家能源局|国家国防科技工业局|国家烟草专卖局|国家林业和草原局|中国民用航空局|国家文物局|国家中医药管理局|国家矿山安全监察局|国家外汇管理局|国家药品监督管理局|国家知识产权局)\s*$', re.M),
    # Very short standalone Chinese chars (archived nav fragments)
    re.compile(r'^[\u4e00-\u9fff]{1,2}\s*$', re.M),
]

# Known bad empty-field replacements for frontmatter
FM_FIXUPS = {
    "doc_number: ": "doc_number: 未标注",
    "doc_number:\n": "doc_number: 未标注\n",
}

CONTENT_JUNK_LINES = [
    "国家机关", "党委", "党组", "党中央", "国务院",  # non-content nav
    "字型", "字号", "扫一扫", "手机打开",  # rendering hints
]


def check_and_clean_raw(raw_dir, slug):
    """Detect and auto-clean contaminated raw files. Returns cleaned count."""
    step_header("1.5", "raw 质量检测 + 自动清洗")

    cleaned = 0
    flagged = []
    errors = []

    for f in raw_dir.rglob("*.md"):
        text = f.read_text(encoding="utf-8")
        original = text
        issues = []

        # ── Check 1: frontmatter quality ──
        if text.strip().startswith("---"):
            fm_end = text.find("---", 3)
            if fm_end > 0:
                fm = text[3:fm_end]
                # Fix frontmatter: ensure fields have values
                for bad, good in FM_FIXUPS.items():
                    if bad in fm:
                        text = text.replace(bad, good)
                        issues.append(f"fm_fix: empty doc_number")

        # ── Check 2: strip URL navigation junk ──
        lines = text.split("\n")
        clean_lines = []
        junk_found = 0
        for line in lines:
            stripped = line.strip()
            if not stripped:
                clean_lines.append(line)
                continue
            # Check against all junk patterns
            is_junk = False
            for pat in JUNK_PATTERNS:
                if pat.match(stripped):
                    is_junk = True
                    junk_found += 1
                    break
            if not is_junk:
                # Also check content junk
                if len(stripped) < 20 and any(cj in stripped for cj in CONTENT_JUNK_LINES):
                    junk_found += 1
                else:
                    clean_lines.append(line)

        if junk_found > 0:
            text = "\n".join(clean_lines)
            issues.append(f"stripped {junk_found} junk lines")

        # ── Check 3: empty content ──
        content_start = text.find("---", 3) + 3 if text.count("---") >= 2 else 0
        body = text[content_start:].strip()
        meaningful = [l for l in body.split("\n") if len(l.strip()) > 20]
        if len(meaningful) < 3:
            issues.append(f"thin_content: only {len(meaningful)} meaningful lines")

        # ── Check 4: LLM routability (trigger word completeness) ──
        fm_end = text.find("---", 3) if text.startswith("---") else -1
        fm = text[3:fm_end] if fm_end > 0 else ""
        empty_fields = []
        for field in ["触发词", "适用场景", "关联法条"]:
            if field not in fm or "[]" in fm.split(f"{field}:")[1].split("\n")[0] if f"{field}:" in fm else True:
                empty_fields.append(field)
        if len(empty_fields) >= 2:
            issues.append(f"low_routability: missing {empty_fields}")

        # ── Act: rewrite if issues found ──
        if issues:
            if "thin_content" in str(issues) and junk_found == 0:
                # Can't auto-fix genuinely empty files
                flagged.append({"file": str(f.relative_to(raw_dir)), "issues": issues, "action": "needs_human"})
                errors.append(f"{f.relative_to(raw_dir)}: 内容过少需人工")
            else:
                # Auto-fixed — rewrite cleaned version
                f.write_text(text, encoding="utf-8")
                cleaned += 1
                flagged.append({"file": str(f.relative_to(raw_dir)), "issues": issues, "action": "auto_cleaned"})

    if cleaned > 0:
        print(f"  ✅ 自动清洗: {cleaned} 篇", flush=True)
    if errors:
        print(f"  ⚠️  需人工: {len(errors)} 篇", flush=True)
        for e in errors[:5]:
            print(f"      {e}", flush=True)

    ops_log("clean", f"raw/{slug}/ 清洗 {cleaned} 篇 | 需人工 {len(errors)} 篇",
            {"cleaned": cleaned, "needs_human": len(errors)}, slug)
    return cleaned, errors


# ── Re-ingest: read raw files, strip junk, re-write ──
def reingest_cleaned(raw_dir, slug):
    """Re-read all raw files after cleaning, verify frontmatter completeness."""
    step_header("1.6", "清洗复核: 验证 raw 文件质量")

    ok, bad_fm, empty = 0, 0, 0
    for f in raw_dir.rglob("*.md"):
        text = f.read_text(encoding="utf-8")
        if not text.strip().startswith("---"):
            # Add minimal frontmatter
            f.write_text(f"---\ntitle: {f.stem}\nstatus: raw\nsources: []\n---\n\n{text}", encoding="utf-8")
            bad_fm += 1
        else:
            fm_end = text.find("---", 3)
            fm = text[3:fm_end] if fm_end > 0 else ""
            body = text[fm_end+3:].strip() if fm_end > 0 else text.strip()
            meaningful = len([l for l in body.split("\n") if len(l.strip()) > 20])
            if meaningful < 3:
                empty += 1
            else:
                ok += 1

    print(f"  frontmatter 完整: {ok} | 补 frontmatter: {bad_fm} | 内容过少: {empty}", flush=True)
    ops_log("reingest", f"raw/{slug}/ 复核: {ok} ok | {bad_fm} fm_fix | {empty} thin",
            {"ok": ok, "fm_fix": bad_fm, "thin": empty}, slug)
    return ok


# ══════════════════════════════════════════════════════════
# Step 2: LLM 设计 industry.yaml
# ══════════════════════════════════════════════════════════

def step_design(slug):
    step_header(2, "LLM 分析 raw/ → 设计 industry.yaml")

    raw_dir = PROJECT_ROOT / "raw" / slug
    iy_path = PROJECT_ROOT / "storage" / slug / "industry.yaml"

    # Collect raw overview
    files_by_dir = {}
    for f in raw_dir.rglob("*.md"):
        d = str(f.relative_to(raw_dir)).split("/")[0]
        files_by_dir.setdefault(d, []).append(f.name)

    overview = [f"## raw/{slug}/ 目录结构 ({sum(len(v) for v in files_by_dir.values())} 篇)"]
    for d in sorted(files_by_dir)[:12]:
        overview.append(f"\n### {d}/ ({len(files_by_dir[d])} 篇)")
        for fn in files_by_dir[d][:5]:
            overview.append(f"  - {fn}")

    # Read key files + sample content from EACH directory
    samples = ""
    for p in ["README.md", "SCHEMA.md", "index.md"]:
        f = raw_dir / p
        if f.exists():
            samples += f"\n### {p}\n{f.read_text(encoding='utf-8')[:1000]}\n"

    # Read first file from each subdirectory for content analysis
    for d in sorted(files_by_dir)[:15]:
        if d in ("README.md", "SCHEMA.md", "index.md"):
            continue
        first_file = raw_dir / d / files_by_dir[d][0]
        if first_file.exists():
            content = first_file.read_text(encoding='utf-8')[:600]
            samples += f"\n### {d}/{files_by_dir[d][0]}\n{content}\n"

    # Also check index.md for concept coverage
    idx_file = raw_dir / "index.md"
    idx_content = ""
    if idx_file.exists():
        idx_content = idx_file.read_text(encoding='utf-8')[:2000]

    prompt = f"""你是 FlowWiki 架构师。基于 raw/ 内容为"{slug}"设计 industry.yaml。

{chr(10).join(overview)}
{samples[:4000]}
## index.md 内容
{idx_content[:1500]}

输出纯 JSON——概念/playbook 名称为中文，覆盖 raw 中出现的所有核心主题（至少 15 个概念）:
{{"name":"名称","slug":"{slug}","domain":"领域","subdomain":"子域","perspective":"视角","raw_sources":{{"laws":[],"standards":[],"datasets":[]}},"wiki_structure":{{"concepts":[],"playbooks":[],"comparisons":[],"criteria":[]}},"scenarios":[{{"id":"","name":"","trigger":"","skills":[]}}],"industry_skills":[{{"name":"","file":".agents/skills/.../SKILL.md"}}]}}"""

    resp = llm(prompt, "你是 FlowWiki 架构师。输出纯 JSON。")
    data = parse_json(resp)
    if not data:
        print("  ❌ LLM 输出解析失败", flush=True)
        return None

    # Write YAML
    iy_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f'name: "{data.get("name", slug)}"',
        f'slug: "{slug}"',
        f'domain: "{data.get("domain", "")}"',
        f'subdomain: "{data.get("subdomain", "")}"',
        f'perspective: "{data.get("perspective", "")}"',
    ]
    for section in ["laws", "standards", "datasets"]:
        items = data.get("raw_sources", {}).get(section, [])
        if items:
            lines.append(f"\n  {section}:")
            for item in items:
                lines.append(f"    - {item}")
    for section in ["concepts", "playbooks", "comparisons", "criteria"]:
        items = data.get("wiki_structure", {}).get(section, [])
        if items:
            lines.append(f"\n  {section}:")
            for item in items:
                lines.append(f"    - {item}")

    iy_path.write_text("\n".join(lines), encoding="utf-8")

    # Quality gate: check raw file coverage
    all_concepts = [c for section in ["concepts", "playbooks", "comparisons", "criteria"]
                    for c in data.get("wiki_structure", {}).get(section, [])
                    if isinstance(c, str)]  # filter dicts from LLM
    raw_files = [f.stem for f in raw_dir.rglob("*.md")]
    uncovered = []
    for rf in raw_files[:30]:  # Check first 30 raw files
        matched = any(kw in rf for kw in all_concepts if len(kw) >= 3)
        if not matched:
            # Check if any raw title keywords match concept keywords
            covered = False
            for kw in all_concepts:
                parts = kw.replace(" ", "").lower()
                if len(parts) >= 3 and parts in rf.lower().replace(" ", "").replace("-", "").replace("_", ""):
                    covered = True
                    break
            if not covered:
                uncovered.append(rf)

    concepts_n = len(data.get("wiki_structure", {}).get("concepts", []))
    if uncovered:
        print(f"  ⚠️  覆盖度缺口: {len(uncovered)}/{min(len(raw_files), 30)} 个 raw 文件未映射", flush=True)
        for uf in uncovered[:5]:
            print(f"      {uf}", flush=True)

    ops_log("design", f"生成 {slug}/industry.yaml", {"concepts": concepts_n, "uncovered": len(uncovered)}, slug)
    print(f"  概念: {concepts_n} | playbook: {len(data.get('wiki_structure',{}).get('playbooks',[]))} | 未覆盖: {len(uncovered)}/{min(len(raw_files), 30)}", flush=True)
    return data


# ══════════════════════════════════════════════════════════
# Step 3: LLM 从 raw 生成 wiki 页面
# ══════════════════════════════════════════════════════════

def step_generate(slug, industry_data):
    step_header(3, "入库: LLM 从 raw 生成 wiki 页面")
    wiki_dir = PROJECT_ROOT / "wiki" / slug
    raw_dir = PROJECT_ROOT / "raw" / slug
    ws = industry_data.get("wiki_structure", {})

    # Read raw context once
    raw_samples = ""
    for sample in list(raw_dir.rglob("*.md"))[:3]:
        t = sample.read_text(encoding="utf-8")[:600]
        raw_samples += f"\n### raw/{sample.relative_to(raw_dir)}\n{t}\n"

    gen_count = 0
    for category, names in [
        ("concepts", ws.get("concepts", [])),
        ("playbooks", ws.get("playbooks", [])),
        ("criteria", ws.get("criteria", [])),
        ("comparisons", ws.get("comparisons", [])),
    ]:
        cat_dir = wiki_dir / category
        cat_dir.mkdir(parents=True, exist_ok=True)
        # Normalize: extract name from dict, filter out non-strings
        def _name(n):
            return n.get('name', str(n)) if isinstance(n, dict) else str(n)
        batch = [n for n in names if not (cat_dir / f"{_name(n)}.md").exists()]
        if not batch:
            continue

        print(f"\n  [{category}] {len(batch)} 篇待生成", flush=True)
        for i, entry in enumerate(batch):
            name = _name(entry)
            prompt = f"""你是生态环境执法案卷评查专家。生成 {category} 页面: "{name}"。

格式: FILENAME: {name}.md 后跟完整 markdown（含 --- frontmatter ---+正文+[[wikilink]]链接+法规引用）。
{raw_samples[:1000]}"""
            try:
                resp = llm(prompt, "输出 format: FILENAME: xxx.md 后跟完整 markdown。", max_tok=1200)
                lines = resp.split("\n")
                fn = None
                for j, line in enumerate(lines):
                    if line.startswith("FILENAME:"):
                        fn = line.replace("FILENAME:", "").strip()
                        body = "\n".join(lines[j+1:]).strip()
                        if not body.startswith("---"):
                            body = f"---\ntitle: {name}\nlayer: {category}\ntype: {category.rstrip('s')}\ntags: []\nstatus: 现行\nsources: [raw/{slug}/README.md]\n---\n\n{body}"
                        (cat_dir / fn).write_text(body, encoding="utf-8")
                        gen_count += 1
                        if (i+1) % 5 == 0:
                            print(f"    [{i+1}/{len(batch)}] {name} ✅", flush=True)
                        break
                if not fn:
                    print(f"    [{i+1}/{len(batch)}] {name} ❌ 解析失败", flush=True)
            except Exception as e:
                print(f"    [{i+1}/{len(batch)}] {name} ❌ {e}", flush=True)

    # Create meta pages
    meta_dir = wiki_dir / "meta"
    meta_dir.mkdir(parents=True, exist_ok=True)
    wiki_files = list(wiki_dir.rglob("*.md"))

    # index.md
    index_parts = [f"# {industry_data.get('name', slug)} 知识库索引\n"]
    for cat in ["concepts", "playbooks", "comparisons", "criteria"]:
        cat_files = list((wiki_dir / cat).glob("*.md")) if (wiki_dir / cat).exists() else []
        if cat_files:
            links = " | ".join(f"[[{f.stem}]]" for f in cat_files)
            index_parts.append(f"\n## {cat} ({len(cat_files)} 篇)\n{links}\n")
    (meta_dir / "index.md").write_text(
        f"---\ntitle: index\nlayer: meta\ntype: index\ntags: [索引]\nstatus: 现行\nsources: [raw/{slug}/README.md]\n---\n\n" + "\n".join(index_parts), encoding="utf-8")

    # ── Generate skills ──
    gen_skills = 0
    skills_dir = PROJECT_ROOT / ".agents" / "skills" / slug
    skills_dir.mkdir(parents=True, exist_ok=True)
    for skill_info in industry_data.get("industry_skills", []):
        skill_name = skill_info.get("name", "")
        skill_file = skill_info.get("file", "")
        if not skill_name:
            continue
        sdir = skills_dir / skill_name
        sdir.mkdir(parents=True, exist_ok=True)
        smd = sdir / "SKILL.md"
        if not smd.exists():
            smd.write_text(f"""---
name: {skill_name}
version: "1.0"
industry: {slug}
tags: [skill, {slug}]
deps: [wiki/{slug}]
---

# {skill_name}

## 输入
- 用户问题
- wiki/{slug}/ 中检索到的相关页面

## 输出
- 结构化回答

## 证据引用
所有结论必须引用 raw/{slug}/ 中的原始证据。
""", encoding="utf-8")
            gen_skills += 1

    # ── Generate prompts ──
    gen_prompts = 0
    prompts_dir = PROJECT_ROOT / "70_Prompt库" / "task" / slug
    prompts_dir.mkdir(parents=True, exist_ok=True)
    for scenario in industry_data.get("scenarios", [])[:3]:
        sid = scenario.get("id", "")
        sname = scenario.get("name", "")
        strigger = scenario.get("trigger", "")
        sskills = ", ".join(scenario.get("skills", []))
        pmd = prompts_dir / f"{sid}.md"
        if not pmd.exists():
            pmd.write_text(f"""---
name: {sname}
trigger: {strigger}
skill: {sskills}
---
# {sname} Prompt

## 触发条件
{strigger}

## 工作流
1. 检索 wiki/{slug}/ 相关知识
2. 对照 raw/{slug}/ 原始证据
3. ACE 反思验证
4. 输出结构化回答

## 依赖
- Skill: {sskills}
- 知识库: wiki/{slug}/ + raw/{slug}/
""", encoding="utf-8")
            gen_prompts += 1

    ops_log("generate", f"wiki/{slug}/ 入库 {gen_count} 篇 | skills {gen_skills} | prompts {gen_prompts}",
            {"wiki": gen_count, "skills": gen_skills, "prompts": gen_prompts}, slug)
    print(f"\n  入库: {gen_count} wiki + {gen_skills} skills + {gen_prompts} prompts → wiki/{slug}/", flush=True)
    return wiki_dir


# ══════════════════════════════════════════════════════════
# Step 4-5: lint + 自修复
# ══════════════════════════════════════════════════════════

def step_lint_and_fix(slug):
    step_header(4, "一验: lint 检查 + 自修复")
    wiki_dir = PROJECT_ROOT / "wiki" / slug

    issues = []
    wiki_files = list(wiki_dir.rglob("*.md"))
    all_titles = {f.stem for f in wiki_files}

    # Check frontmatter
    no_fm, no_sources = [], []
    for f in wiki_files:
        text = f.read_text(encoding="utf-8")
        if not text.strip().startswith("---"):
            no_fm.append(f.name)
        if "sources:" not in text[:text.find("---", 3) if text.count("---") >= 2 else 500]:
            no_sources.append(f.name)

    # Fix missing frontmatter
    for fn in no_fm:
        f = wiki_dir.rglob(fn)
        for ff in f:
            text = ff.read_text(encoding="utf-8")
            ff.write_text(f"---\ntitle: {ff.stem}\nlayer: {ff.parent.name}\ntype: concept\nstatus: 现行\nsources: [raw/{slug}/README.md]\n---\n\n{text}", encoding="utf-8")

    # Fix missing sources
    for fn in no_sources:
        for f in wiki_dir.rglob(fn):
            text = f.read_text(encoding="utf-8")
            f.write_text(text.replace("---", f"---\nsources: [raw/{slug}/README.md]\n", 1), encoding="utf-8")

    # Fix broken wikilinks
    broken_fixed = 0
    for f in wiki_files:
        text = f.read_text(encoding="utf-8")
        original = text
        for m in LINK_RE.finditer(text):
            target = m.group(1).split("|")[0].strip().split("#")[0].strip()
            if target not in all_titles and target != f.stem:
                text = text.replace(m.group(0), m.group(1).split("|")[-1].strip())
        if text != original:
            f.write_text(text, encoding="utf-8")
            broken_fixed += len(LINK_RE.findall(original)) - len(LINK_RE.findall(text))

    # Add cross-references to eliminate isolation
    cross_added = 0
    for f in wiki_files:
        text = f.read_text(encoding="utf-8")
        siblings = [s.stem for s in f.parent.glob("*.md") if s.stem != f.stem]
        existing = set(m.group(1).split("|")[0].strip() for m in LINK_RE.finditer(text))
        new = [s for s in siblings[:2] if s not in existing]
        if new and "## 相关概念" not in text:
            links_md = "\n".join(f"- [[{n}]]" for n in new)
            text += f"\n\n## 相关概念\n{links_md}\n"
            f.write_text(text, encoding="utf-8")
            cross_added += len(new)

    # Add backlinks (bidirectional)
    outlinks = {}
    for f in wiki_files:
        text = f.read_text(encoding="utf-8")
        outlinks[f.stem] = set(m.group(1).split("|")[0].strip() for m in LINK_RE.finditer(text) if m.group(1).split("|")[0].strip() in all_titles)

    backlink_added = 0
    missing_backlinks = {}
    for stem, links in outlinks.items():
        for target in links:
            if stem not in outlinks.get(target, set()):
                missing_backlinks.setdefault(target, set()).add(stem)

    for target, sources in missing_backlinks.items():
        for f in wiki_dir.rglob(f"{target}.md"):
            text = f.read_text(encoding="utf-8")
            if "## 相关引用" not in text:
                blines = "\n".join(f"- [[{s}]]" for s in list(sources)[:3])
                text += f"\n\n## 相关引用\n{blines}\n"
                f.write_text(text, encoding="utf-8")
                backlink_added += len(sources)
                break

    result = f"重写 frontmatter: {len(no_fm)} | 补 sources: {len(no_sources)} | 修断链: {broken_fixed} | 交叉引用: {cross_added} | 反链: {backlink_added}"
    ops_log("lint", result, {"no_fm": len(no_fm), "broken": broken_fixed}, slug)
    print(f"  {result}", flush=True)
    return {"no_fm": len(no_fm), "no_sources": len(no_sources), "broken": broken_fixed}


# ══════════════════════════════════════════════════════════
# Step 6: graph 检查
# ══════════════════════════════════════════════════════════

def step_graph(slug):
    step_header(6, "二验: 图谱质量")
    wiki_dir = PROJECT_ROOT / "wiki" / slug

    all_titles = {f.stem for f in wiki_dir.rglob("*.md")}
    outlinks, inlinks = {}, Counter()
    for f in wiki_dir.rglob("*.md"):
        text = f.read_text(encoding="utf-8")
        outlinks[f.stem] = set()
        for m in LINK_RE.finditer(text):
            t = m.group(1).split("|")[0].strip().split("#")[0].strip()
            if t in all_titles and t != f.stem:
                outlinks[f.stem].add(t)
                inlinks[t] += 1

    total_edges = sum(len(v) for v in outlinks.values())
    isolated = [t for t in all_titles if len(outlinks.get(t, set())) == 0 and inlinks.get(t, 0) == 0]
    bidirectional = sum(1 for a, links in outlinks.items() for b in links if a in outlinks.get(b, set()))
    density = round(total_edges / max(len(all_titles), 1), 2)
    bi_pct = round(bidirectional / max(total_edges, 1) * 100)

    result = f"节点: {len(all_titles)} | 边: {total_edges} | 密度: {density} | 双向率: {bi_pct}% | 孤立: {len(isolated)}"
    ops_log("graph", result, {"nodes": len(all_titles), "edges": total_edges, "density": density, "isolated": len(isolated)}, slug)
    print(f"  {result}", flush=True)

    passed = len(isolated) == 0 and density >= 2.0 and bi_pct >= 50
    return {"nodes": len(all_titles), "edges": total_edges, "density": density, "isolated": len(isolated), "bi_pct": bi_pct, "pass": passed}


# ══════════════════════════════════════════════════════════
# Step 7: hermes_review 终验
# ══════════════════════════════════════════════════════════

def step_hermes_review(slug, graph_result):
    step_header(7, "三验: Hermes 终验")
    wiki_dir = PROJECT_ROOT / "wiki" / slug
    iy = PROJECT_ROOT / "storage" / slug / "industry.yaml"

    # Count pages by category
    cat_counts = {}
    for f in wiki_dir.rglob("*.md"):
        cat_counts[f.parent.name] = cat_counts.get(f.parent.name, 0) + 1

    prompt = f"""你是 FlowWiki 验收专家。评价知识库 "{slug}"。

指标: 节点 {graph_result['nodes']} | 边 {graph_result['edges']} | 密度 {graph_result['density']} | 双向率 {graph_result['bi_pct']}% | 孤立 {graph_result['isolated']}
分类: {json.dumps(cat_counts, ensure_ascii=False)}

输出 JSON: {{"scores":{{"结构":x,"内容":x,"图谱":x,"操作":x,"时效":x,"维护":x,"整体":x}},"verdict":"pass|needs_attention","verification":"一句话验收结论"}}"""

    resp = llm(prompt, "你是验收专家。输出纯 JSON。", max_tok=600)
    review = parse_json(resp)
    if not review:
        review = {"scores": {"整体": 0}, "verdict": "parse_error", "verification": "JSON 解析失败"}

    score = review.get("scores", {}).get("整体", 0)
    verdict = review.get("verdict", "?")
    ops_log("review", f"Hermes: {verdict} ({score}/10)", {"scores": review.get("scores", {})}, slug)
    print(f"  {verdict} — {score}/10 | {review.get('verification', '')}", flush=True)
    return review


# ══════════════════════════════════════════════════════════
# Step 8: 注册到 00_首页/ + 生成可读报告
# ══════════════════════════════════════════════════════════

def step_register(slug, review):
    step_header(8, "注册: 更新 00_首页/ + 生成报告")

    # 1. Update 03_实战场景/
    scene_dir = PROJECT_ROOT / "00_首页" / "03_实战场景"
    slug_dir = scene_dir / slug
    slug_dir.mkdir(parents=True, exist_ok=True)

    score = review.get("scores", {}).get("整体", 0)
    verdict = review.get("verdict", "?")

    (slug_dir / "README.md").write_text(f"""# {slug}

**状态**: {verdict} | **Hermes 评分**: {score}/10

## 快速入口
- [知识库索引](../../wiki/{slug}/meta/index.md)
- [行业配置](../../storage/{slug}/industry.yaml)
- [原始资料](../../raw/{slug}/)

## 验证结果
{review.get('verification', '')}

## 子目录
- concepts → `wiki/{slug}/concepts/`
- playbooks → `wiki/{slug}/playbooks/`
- criteria → `wiki/{slug}/criteria/`
- meta → `wiki/{slug}/meta/`
""", encoding="utf-8")

    # 2. Update 05_采集记录/
    record_dir = PROJECT_ROOT / "00_首页" / "05_采集记录"
    (record_dir / slug).mkdir(parents=True, exist_ok=True)
    raw_files = list((PROJECT_ROOT / "raw" / slug).rglob("*.md"))
    (record_dir / slug / "README.md").write_text(f"""# {slug} 入仓记录

- 入仓时间: {datetime.now().isoformat()}
- 文件数: {len(raw_files)}
- 目录: `raw/{slug}/`
""", encoding="utf-8")

    # 3. Update 04_进化学习/
    ace_dir = PROJECT_ROOT / "00_首页" / "04_进化学习"
    ace_logs = list((PROJECT_ROOT / ".memory" / "ace").glob("*.md"))
    (ace_dir / slug).mkdir(parents=True, exist_ok=True)
    (ace_dir / slug / "README.md").write_text(f"""# {slug} ACE 反思

- ACE 日志: `.memory/ace/` ({len(ace_logs)} 条)
- 缺口卡片: `.memory/gaps/`
""", encoding="utf-8")

    # 4. Generate final report
    ops_dir = PROJECT_ROOT / "ops" / "monitoring"
    ops_dir.mkdir(parents=True, exist_ok=True)

    report = f"""# FlowWiki bootstrap 报告: {slug}

**时间**: {datetime.now().isoformat()}
**状态**: {verdict}

## Hermes 评分

| 维度 | 得分 |
|------|------|
"""
    for k, v in review.get("scores", {}).items():
        report += f"| {k} | {v} |\n"
    report += f"\n**结论**: {review.get('verification', '')}\n"

    # Add ops log summary
    from _scripts.ops_log import get_today_logs
    logs = get_today_logs(limit=50)
    action_counts = Counter(e["action"] for e in logs)
    report += "\n## 操作日志摘要\n\n"
    for action, count in action_counts.most_common():
        report += f"- {action}: {count}\n"

    report_path = ops_dir / f"bootstrap-{slug}-{datetime.now().strftime('%Y-%m-%d')}.md"
    report_path.write_text(report, encoding="utf-8")

    ops_log("register", f"00_首页/ 注册 {slug} | 报告: {report_path.name}", {"verdict": verdict, "score": score}, slug)
    print(f"  00_首页/03_实战场景/{slug}/ ✅", flush=True)
    print(f"  报告: {report_path}", flush=True)


# ══════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="FlowWiki 全自动引导流水线")
    parser.add_argument("--source", required=True, help="源知识库目录")
    parser.add_argument("--slug", required=True, help="行业 slug 名称")
    parser.add_argument("--skip-to", type=int, help="从指定步骤开始 (1-8)")
    args = parser.parse_args()

    slug = args.slug
    start = datetime.now()
    print(f"FlowWiki Bootstrap: {slug}", flush=True)

    try:
        if not args.skip_to or args.skip_to <= 1:
            step_ingest(args.source, slug)

        if not args.skip_to or args.skip_to <= 2:
            check_and_clean_raw(PROJECT_ROOT / "raw" / slug, slug)
            reingest_cleaned(PROJECT_ROOT / "raw" / slug, slug)

        if not args.skip_to or args.skip_to <= 2:
            industry_data = step_design(slug)
            if not industry_data:
                print("❌ 设计失败", file=sys.stderr)
                return 1

        if not args.skip_to or args.skip_to <= 3:
            step_generate(slug, industry_data)

        if not args.skip_to or args.skip_to <= 4:
            step_lint_and_fix(slug)

        if not args.skip_to or args.skip_to <= 6:
            graph_result = step_graph(slug)

        if not args.skip_to or args.skip_to <= 7:
            review = step_hermes_review(slug, graph_result)

        if not args.skip_to or args.skip_to <= 8:
            step_register(slug, review)

        duration = (datetime.now() - start).total_seconds()
        ops_log("bootstrap", f"完成 {slug} 引导 ({duration:.0f}s)", {"duration": duration, "verdict": review.get("verdict")}, slug)

        print(f"\n{'='*60}")
        print(f"  完成: {slug}")
        print(f"  耗时: {duration:.0f}s")
        print(f"  评分: {review.get('scores', {}).get('整体', '?')}/10")
        print(f"  报告: ops/monitoring/bootstrap-{slug}-{datetime.now().strftime('%Y-%m-%d')}.md")
        print(f"{'='*60}")

    except KeyboardInterrupt:
        print("\n中断", file=sys.stderr)
        return 1
    except Exception as e:
        ops_log("bootstrap", f"失败: {e}", {}, slug, "error")
        print(f"\n❌ 失败: {e}", file=sys.stderr)
        return 1

    return 0 if review.get("verdict") == "pass" else 0


if __name__ == "__main__":
    sys.exit(main())
