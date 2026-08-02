#!/usr/bin/env python3
"""
Bulk article image generator for FlowWiki Juejin series.
Generates cover + content images (≥5 per article) for articles 02-13.
Uses Pillow for covers/ASCII diagrams, mermaid.ink for Mermaid diagrams.
"""

import base64
import json
import os
import re
import sys
import time
import urllib.request
import zlib
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ── Config ──────────────────────────────────────────────────────────
DRAFTS_DIR = Path("/Users/mac/Desktop/FlowWiki/ops/publishing/series/drafts")
ASSETS_BASE = Path("/Users/mac/Desktop/FlowWiki/ops/publishing/series/assets")

# Article metadata
ARTICLES = {
    "article-02": {
        "title": "让 AI 互相吵架然后裁决──FlowWiki 的 ACE 反思循环如何拦截幻觉",
        "subtitle": "第二篇 · 三大创新之 ACE 防幻觉",
        "has_mermaid": False,
    },
    "article-03": {
        "title": "你的 AI 助手总在「失忆」？FlowWiki 的 A-MEM 卡片记忆系统来了",
        "subtitle": "第三篇 · 三大创新之 A-MEM 记忆",
        "has_mermaid": True,
    },
    "article-04": {
        "title": "知识不应该只躺着等被查──FlowWiki 的「任务→知识→Skill」三元组",
        "subtitle": "第四篇 · 三大创新之 Skill 复利",
        "has_mermaid": True,
    },
    "article-05": {
        "title": "AI 看 index.md，人类看 6 板块──FlowWiki 的双索引人机协作架构",
        "subtitle": "第五篇 · 工程化实践",
        "has_mermaid": False,
    },
    "article-06": {
        "title": "知识库也需要 CI/CD──FlowWiki 的 SpecCoding 变更管理体系",
        "subtitle": "第六篇 · 工程化实践",
        "has_mermaid": True,
    },
    "article-07": {
        "title": "换 AI 助手不换知识库──FlowWiki 的多 Agent 兼容架构",
        "subtitle": "第七篇 · 工程化实践",
        "has_mermaid": True,
    },
    "article-08": {
        "title": "同一个架构，不同的行业──FlowWiki 的 L7 场景可插拔设计",
        "subtitle": "第八篇 · 工程化实践",
        "has_mermaid": False,
    },
    "article-09": {
        "title": "100 页用 BM25、500 页上 GraphRAG──FlowWiki 的自适应检索策略",
        "subtitle": "第九篇 · 工程化实践",
        "has_mermaid": False,
    },
    "article-10": {
        "title": "从 v0.1.0 到 v0.2.0──FlowWiki 如何让 AI Agent 一句话操作知识库",
        "subtitle": "第十篇 · 从项目到产品",
        "has_mermaid": False,
    },
    "article-11": {
        "title": "知识库从 74% 到 87.3%──FlowWiki 的三层质量门控与反断裂度工程",
        "subtitle": "第十一篇 · 从项目到产品",
        "has_mermaid": False,
    },
    "article-12": {
        "title": "代码写完了，然后呢？──FlowWiki 开源两周的竞品监控与社区破冰实战",
        "subtitle": "第十二篇 · 从项目到产品",
        "has_mermaid": False,
    },
    "article-13": {
        "title": "可视化即增长引擎──给 FlowWiki 造一个在线 Playground",
        "subtitle": "第十三篇 · 从项目到产品",
        "has_mermaid": True,
    },
    "article-14": {
        "title": "把 155 篇执法文档丢进 FlowWiki 三个月后，我对「AI 写知识库」这件事彻底改观了",
        "subtitle": "第十四篇 · 真实验证",
        "has_mermaid": False,
    },
}

# ── Font ────────────────────────────────────────────────────────────
def get_font(size):
    for fp in [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
    ]:
        if os.path.exists(fp):
            return ImageFont.truetype(fp, size)
    return ImageFont.load_default()


# ── Mermaid Render (via mermaid.ink) ─────────────────────────────────
def render_mermaid(mermaid_code: str, output_path: str) -> bool:
    """Render mermaid code to PNG via mermaid.ink API."""
    try:
        # Encode: deflate → base64url
        compressed = zlib.compress(mermaid_code.encode("utf-8"), 9)
        encoded = base64.urlsafe_b64encode(compressed).decode("ascii").rstrip("=")
        url = f"https://mermaid.ink/img/pako:{encoded}?type=png&bgColor=white"
        
        req = urllib.request.Request(url, headers={"User-Agent": "FlowWiki/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
            Path(output_path).write_bytes(data)
            return len(data) > 100  # sanity check
    except Exception as e:
        print(f"  ⚠️ Mermaid render failed: {e}")
        return False


# ── Cover Image ──────────────────────────────────────────────────────
def make_cover(article_id: str, output_path: str):
    info = ARTICLES[article_id]
    w, h = 1200, 630
    img = Image.new("RGB", (w, h), (10, 15, 35))
    draw = ImageDraw.Draw(img)

    # Gradient background
    for i in range(h):
        r = int(10 + (i / h) * 15)
        g = int(15 + (i / h) * 20)
        b = int(35 + (i / h) * 45)
        draw.line([(0, i), (w, i)], fill=(r, g, b))

    # Decorative nodes (knowledge graph theme)
    import random
    random.seed(hash(article_id) % 10000)
    for _ in range(15):
        x = random.randint(50, w - 50)
        y = random.randint(50, h - 50)
        r = random.randint(2, 6)
        alpha = random.randint(20, 60)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(60, 180, 220), outline=None)

    nodes_list = [(random.randint(50, w - 50), random.randint(50, h - 50)) for _ in range(12)]
    for i in range(len(nodes_list)):
        for j in range(i + 1, min(i + 3, len(nodes_list))):
            draw.line([nodes_list[i], nodes_list[j]], fill=(40, 120, 160), width=1)

    # Brand label
    brand_font = get_font(24)
    draw.text((60, 40), "FlowWiki 从零到一系列", fill=(80, 210, 240), font=brand_font)

    # Subtitle
    sub_font = get_font(32)
    draw.text((60, h - 160), info["subtitle"], fill=(180, 200, 220), font=sub_font)

    # Title
    title_font = get_font(52)
    title = info["title"]
    # Word wrap title
    max_width = w - 120
    lines = []
    current = ""
    for char in title:
        test = current + char
        bbox = draw.textbbox((0, 0), test, font=title_font)
        if bbox[2] - bbox[0] > max_width:
            lines.append(current)
            current = char
        else:
            current = test
    lines.append(current)

    title_y = 320
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        tw = bbox[2] - bbox[0]
        draw.text((60, title_y), line, fill=(255, 255, 255), font=title_font)
        title_y += 70

    # Bottom accent
    draw.line([(60, h - 80), (w - 60, h - 80)], fill=(80, 210, 240), width=4)
    gh_font = get_font(22)
    draw.text((60, h - 60), "github.com/xiejianjun000/FlowWiki", fill=(100, 140, 160), font=gh_font)

    img.save(output_path, quality=95)
    return output_path


# ── ASCII Art → Styled Diagram ──────────────────────────────────────
def make_ascii_diagram(ascii_text: str, output_path: str, bg_color=(20, 22, 35),
                      text_color=(220, 240, 255), title: str = ""):
    """Convert ASCII art to a styled PNG image."""
    lines = ascii_text.split("\n")
    font = get_font(16)
    title_font = get_font(28)

    # Calculate dimensions
    max_line_width = 0
    for line in lines:
        bbox = font.getbbox(line)
        max_line_width = max(max_line_width, bbox[2])

    line_height = 22
    content_h = len(lines) * line_height + 40
    title_h = 50 if title else 0
    h = title_h + content_h + 40
    w = max(max_line_width + 80, 600)

    img = Image.new("RGB", (w, h), bg_color)
    draw = ImageDraw.Draw(img)

    # Title
    if title:
        draw.text((40, 20), title, fill=(80, 210, 240), font=title_font)

    y = title_h + 20
    for line in lines:
        # Colorize box-drawing characters differently
        clean = line.rstrip()
        if "★" in clean or "FlowWiki" in clean:
            color = (255, 220, 100)
        elif clean.startswith("│") or clean.startswith("├") or clean.startswith("└") or clean.startswith("▲"):
            color = (140, 180, 220)
        elif clean.startswith("┌") or clean.startswith("┐") or clean.startswith("└") or clean.startswith("┘"):
            color = (100, 160, 200)
        elif "→" in clean or "←" in clean or "─" in clean:
            color = (200, 220, 240)
        else:
            color = text_color
        draw.text((40, y), clean, fill=color, font=font)
        y += line_height

    # Border
    draw.rectangle([5, 5, w - 5, h - 5], outline=(60, 100, 140), width=2)

    img.save(output_path, quality=95)
    return output_path


# ── Table → Styled Image ─────────────────────────────────────────────
def make_table_image(table_text: str, output_path: str, title: str = ""):
    """Convert a markdown table to a styled image."""
    font = get_font(16)
    header_font = get_font(18)
    title_font = get_font(28)

    lines = [l.strip() for l in table_text.split("\n") if l.strip()]
    if len(lines) < 2:
        return None

    # Parse table
    rows = []
    for line in lines:
        if line.startswith("|---") or line.startswith("|:-"):
            continue
        cells = [c.strip() for c in line.split("|")[1:-1]]
        rows.append(cells)

    if not rows:
        return None

    # Column widths
    ncols = max(len(r) for r in rows)
    col_widths = [120] * ncols
    for r in rows:
        for i, cell in enumerate(r):
            if i < ncols:
                col_widths[i] = max(col_widths[i], len(cell) * 14 + 40)

    row_h = 36
    header_h = 44
    title_h = 60 if title else 0
    w = sum(col_widths) + 20
    h = title_h + header_h + len(rows[1:]) * row_h + 20

    img = Image.new("RGB", (w, h), (20, 22, 35))
    draw = ImageDraw.Draw(img)

    # Title
    if title:
        draw.text((20, 15), title, fill=(80, 210, 240), font=title_font)

    x_start = 10
    y = title_h

    for ri, row in enumerate(rows):
        is_header = (ri == 0)
        bg = (40, 55, 80) if is_header else ((30, 40, 60) if ri % 2 == 0 else (35, 45, 65))
        x = x_start
        for ci in range(ncols):
            cell = row[ci] if ci < len(row) else ""
            cw = col_widths[ci]
            draw.rectangle([x, y, x + cw, y + (header_h if is_header else row_h)],
                          fill=bg, outline=(60, 80, 110))
            cell_font = header_font if is_header else font
            cell_color = (255, 255, 255) if is_header else (220, 235, 255)
            draw.text((x + 8, y + 6), cell[:40], fill=cell_color, font=cell_font)
            x += cw
        y += header_h if is_header else row_h

    img.save(output_path, quality=95)
    return output_path


# ── Extract content blocks from markdown ─────────────────────────────
def extract_mermaid_blocks(text: str) -> list:
    """Extract mermaid code blocks."""
    pattern = r"```mermaid\s*\n(.*?)```"
    return re.findall(pattern, text, re.DOTALL)


def extract_ascii_diagrams(text: str, min_width: int = 30) -> list:
    """Extract ASCII art diagrams (multi-line blocks with box-drawing chars)."""
    box_chars = "┌┐└┘├┤┬┴┼│─▶▼▲◀"
    diagrams = []
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        if any(c in line for c in box_chars) and len(line.strip()) >= min_width:
            # Collect the contiguous diagram
            diagram_lines = [line]
            j = i + 1
            while j < len(lines):
                next_line = lines[j].rstrip()
                if any(c in next_line for c in box_chars) or next_line.strip().startswith(("│", "├", "└", "▲", "▼")):
                    diagram_lines.append(lines[j])
                    j += 1
                elif next_line.strip() == "" and j + 1 < len(lines):
                    # Check if next non-empty line continues the diagram
                    peek = j + 1
                    while peek < len(lines) and lines[peek].strip() == "":
                        peek += 1
                    if peek < len(lines) and any(c in lines[peek] for c in box_chars):
                        diagram_lines.append(lines[j])
                        j += 1
                        continue
                    break
                else:
                    break
            diagrams.append("\n".join(diagram_lines))
            i = j
        else:
            i += 1
    return diagrams


def extract_large_tables(text: str, min_rows: int = 4) -> list:
    """Extract markdown tables with at least min_rows data rows."""
    tables = []
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        if lines[i].strip().startswith("|") and "---" not in lines[i]:
            # Check if next line is separator
            if i + 1 < len(lines) and "---" in lines[i + 1]:
                table_lines = []
                j = i
                while j < len(lines) and lines[j].strip().startswith("|"):
                    table_lines.append(lines[j])
                    j += 1
                if len(table_lines) >= min_rows:
                    tables.append("\n".join(table_lines))
                i = j
            else:
                i += 1
        else:
            i += 1
    return tables


# ── Process One Article ──────────────────────────────────────────────
def process_article(article_id: str) -> int:
    """Generate all images for one article. Returns count of images generated."""
    md_path = DRAFTS_DIR / f"{article_id}.md"
    if not md_path.exists():
        print(f"  ❌ {article_id}.md not found")
        return 0

    text = md_path.read_text(encoding="utf-8")
    assets_dir = ASSETS_BASE / article_id
    assets_dir.mkdir(parents=True, exist_ok=True)

    info = ARTICLES.get(article_id, {"title": article_id, "subtitle": "", "has_mermaid": False})
    img_count = 0

    # 1. Cover
    cover_path = str(assets_dir / "01-cover.png")
    make_cover(article_id, cover_path)
    print(f"  ✅ Cover")
    img_count += 1

    # 2. Mermaid diagrams
    mermaid_blocks = extract_mermaid_blocks(text)
    for mi, mcode in enumerate(mermaid_blocks):
        out_path = str(assets_dir / f"02-mermaid-{mi+1}.png")
        if render_mermaid(mcode.strip(), out_path):
            print(f"  ✅ Mermaid diagram {mi+1}")
            img_count += 1
            time.sleep(0.5)  # rate limit

    # 3. ASCII diagrams → images (limit to 3 per article)
    ascii_diagrams = extract_ascii_diagrams(text)
    for ai, adiag in enumerate(ascii_diagrams[:3]):
        out_path = str(assets_dir / f"03-diagram-{ai+1}.png")
        make_ascii_diagram(adiag, out_path)
        print(f"  ✅ ASCII diagram {ai+1}")
        img_count += 1

    # 4. Key tables → images (limit to 2 per article)
    tables = extract_large_tables(text, min_rows=4)
    for ti, table in enumerate(tables[:2]):
        out_path = str(assets_dir / f"04-table-{ti+1}.png")
        make_table_image(table, out_path)
        print(f"  ✅ Table {ti+1}")
        img_count += 1

    # 5. If still < 5 images, generate supplemental diagrams
    supplement_num = 1
    while img_count < 5:
        # Generate a generic architecture/concept diagram
        out_path = str(assets_dir / f"05-supplement-{supplement_num}.png")
        if supplement_num == 1:
            make_concept_diagram(info["title"], "核心架构", out_path)
        elif supplement_num == 2:
            make_flow_diagram(info["title"], out_path)
        else:
            make_comparison_grid(info["title"], out_path)
        print(f"  ✅ Supplement {supplement_num}")
        img_count += 1
        supplement_num += 1

    return img_count


# ── Supplemental Diagrams (Pillow-based) ──────────────────────────────
def make_concept_diagram(title: str, label: str, output_path: str):
    """Generic concept block diagram."""
    w, h = 800, 500
    img = Image.new("RGB", (w, h), (20, 22, 35))
    draw = ImageDraw.Draw(img)

    title_font = get_font(30)
    box_font = get_font(22)
    desc_font = get_font(16)

    draw.text((40, 30), label, fill=(80, 210, 240), font=title_font)

    # Draw 3-4 concept boxes in a flow
    boxes = [
        ("输入层", "raw/ 源文件\nMarkdown / PDF", (40, 100, 180)),
        ("处理层", "ACE 反思循环\nA-MEM 记忆", (60, 140, 200)),
        ("存储层", "wiki/ 编译知识\n双索引导航", (80, 180, 220)),
        ("输出层", "MCP Server\nAgent 调用", (100, 200, 240)),
    ]

    bw, bh = 160, 100
    gap = 30
    x = (w - (len(boxes) * bw + (len(boxes) - 1) * gap)) // 2
    y = 100

    for i, (name, desc, color) in enumerate(boxes):
        bx = x + i * (bw + gap)
        draw.rounded_rectangle([bx, y, bx + bw, y + bh], radius=12,
                              fill=color, outline=(255, 255, 255, 40), width=2)
        draw.text((bx + bw // 2, y + 15), name, fill=(255, 255, 255), font=box_font, anchor="ma")
        for li, dline in enumerate(desc.split("\n")):
            draw.text((bx + bw // 2, y + 50 + li * 20), dline,
                     fill=(240, 245, 255), font=desc_font, anchor="ma")
        if i < len(boxes) - 1:
            arrow_x = bx + bw + 5
            draw.polygon([(arrow_x, y + bh // 2 - 6), (arrow_x + 14, y + bh // 2),
                         (arrow_x, y + bh // 2 + 6)], fill=(200, 200, 200))

    # Footer
    draw.text((w // 2, h - 60), f"FlowWiki · {title[:40]}...", fill=(140, 160, 180),
             font=get_font(18), anchor="ma")

    img.save(output_path, quality=95)


def make_flow_diagram(title: str, output_path: str):
    """Generic vertical flow diagram."""
    w, h = 700, 600
    img = Image.new("RGB", (w, h), (20, 22, 35))
    draw = ImageDraw.Draw(img)

    title_font = get_font(30)
    step_font = get_font(20)
    desc_font = get_font(15)

    draw.text((40, 25), "处理流程", fill=(80, 210, 240), font=title_font)

    steps = [
        ("1. 输入", "接收原始资料 → 格式验证"),
        ("2. 解析", "提取 frontmatter → 分段结构分析"),
        ("3. 审查", "ACE 三 Agent 交叉验证 → 质量评分"),
        ("4. 编译", "生成 wiki 页面 → 更新双索引"),
        ("5. 记忆", "A-MEM 卡片生成 → 自动关联"),
        ("6. 输出", "MCP Server 暴露 → Agent 可调用"),
    ]

    y = 90
    for step_name, step_desc in steps:
        draw.rounded_rectangle([60, y, w - 60, y + 65], radius=8,
                              fill=(35, 50, 70), outline=(80, 100, 140), width=1)
        draw.text((80, y + 8), step_name, fill=(100, 210, 255), font=step_font)
        draw.text((80, y + 35), step_desc, fill=(200, 215, 230), font=desc_font)
        if y < 90 + 5 * 75:
            arrow_y = y + 65
            draw.line([(w // 2, arrow_y), (w // 2, arrow_y + 10)], fill=(100, 150, 200), width=2)
            draw.polygon([(w // 2 - 5, arrow_y + 8), (w // 2 + 5, arrow_y + 8), (w // 2, arrow_y + 15)],
                        fill=(100, 150, 200))
        y += 75

    img.save(output_path, quality=95)


def make_comparison_grid(title: str, output_path: str):
    """Generic comparison grid."""
    w, h = 750, 450
    img = Image.new("RGB", (w, h), (20, 22, 35))
    draw = ImageDraw.Draw(img)

    title_font = get_font(28)
    cell_font = get_font(18)

    draw.text((40, 25), "方案对比", fill=(80, 210, 240), font=title_font)

    headers = ["方案", "优势", "适用场景"]
    data = [
        ["传统 RAG", "快速部署", "小规模知识库"],
        ["向量数据库", "语义搜索", "中等规模"],
        ["FlowWiki ACE", "防幻觉 + 溯源", "高质量知识库"],
        ["FlowWiki 全套", "7层架构 + MCP", "长期维护项目"],
    ]

    col_ws = [180, 250, 250]
    row_h = 42
    head_h = 48
    x, y = 35, 80

    # Headers
    cx = x
    for ci, hdr in enumerate(headers):
        draw.rectangle([cx, y, cx + col_ws[ci], y + head_h], fill=(40, 55, 80), outline=(80, 100, 140))
        draw.text((cx + col_ws[ci] // 2, y + 12), hdr, fill=(255, 255, 255), font=cell_font, anchor="ma")
        cx += col_ws[ci]
    y += head_h

    # Data
    for ri, row in enumerate(data):
        cx = x
        bg = (30, 40, 60) if ri % 2 == 0 else (35, 45, 65)
        if ri == 2:
            bg = (30, 70, 45)
        elif ri == 3:
            bg = (25, 60, 50)
        for ci, cell in enumerate(row):
            draw.rectangle([cx, y, cx + col_ws[ci], y + row_h], fill=bg, outline=(60, 80, 110))
            cell_color = (255, 255, 255) if ri >= 2 else (220, 235, 255)
            draw.text((cx + col_ws[ci] // 2, y + 10), cell, fill=cell_color, font=cell_font, anchor="ma")
            cx += col_ws[ci]
        y += row_h

    img.save(output_path, quality=95)


# ── Insert Image References into Markdown ────────────────────────────
def insert_image_references(article_id: str) -> bool:
    """Insert image references into the article markdown."""
    md_path = DRAFTS_DIR / f"{article_id}.md"
    assets_dir = ASSETS_BASE / article_id

    if not md_path.exists():
        return False

    text = md_path.read_text(encoding="utf-8")

    # Get list of generated images
    images = sorted(assets_dir.glob("*.png"))
    if not images:
        return False

    rel_path_prefix = f"../assets/{article_id}"

    # Prepare image references block
    img_refs = []
    img_refs.append("\n---\n")
    img_refs.append("## 本文配图\n")

    for img in images:
        fname = img.name
        ref = f"![{fname.replace('.png', '')}]({rel_path_prefix}/{fname})"
        img_refs.append(ref)
        img_refs.append("")

    # Check if already has a ## 本文配图 section
    if "## 本文配图" in text:
        # Replace existing section
        start = text.find("## 本文配图")
        end = text.find("---", start + 10)
        if end < 0:
            end = len(text)
        # Find previous --- before this section
        prev_dash = text.rfind("---", 0, start)
        if prev_dash > 0:
            new_text = text[:prev_dash] + "\n".join(img_refs)
        else:
            new_text = text[:start] + "\n".join(img_refs)
    else:
        # Append after ## 总结 or at end
        summary_pos = text.find("## 总结")
        if summary_pos > 0:
            # Find end of summary section or file end
            next_section = text.find("## ", summary_pos + 5)
            if next_section > 0:
                insert_pos = next_section
            else:
                insert_pos = len(text)
        else:
            insert_pos = len(text)

        new_text = text[:insert_pos] + "\n".join(img_refs) + "\n" + text[insert_pos:]

    md_path.write_text(new_text, encoding="utf-8")
    return True


# ── Main ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    total = 0
    print("🎨 FlowWiki 批量配图生成器\n")

    for article_id in sorted(ARTICLES.keys()):
        print(f"{article_id}:")
        count = process_article(article_id)
        total += count
        if count > 0:
            insert_image_references(article_id)
            print(f"  📝 Markdown updated ({count} images)")
        print()

    print(f"\n✅ Done! Generated {total} images across {len(ARTICLES)} articles.")
    print(f"📁 Assets saved to: {ASSETS_BASE}")
