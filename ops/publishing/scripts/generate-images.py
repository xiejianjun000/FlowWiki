#!/usr/bin/env python3
"""Generate FlowWiki article images using Pillow."""

from PIL import Image, ImageDraw, ImageFont
import os

ASSETS = "/Users/mac/Desktop/FlowWiki/ops/publishing/articles/v0.1.0-launch/assets"
os.makedirs(ASSETS, exist_ok=True)

# Try to get a good font
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

# ============================================================
# 1. COVER IMAGE (1536x864 → resize to 800x420 for Juejin)
# ============================================================
def make_cover():
    w, h = 1536, 864
    img = Image.new("RGB", (w, h), (10, 15, 35))
    draw = ImageDraw.Draw(img)

    # Gradient background effect using rectangles
    for i in range(h):
        r = int(10 + (i / h) * 15)
        g = int(15 + (i / h) * 20)
        b = int(35 + (i / h) * 40)
        draw.line([(0, i), (w, i)], fill=(r, g, b))

    # Decorative circles (knowledge graph nodes)
    import random
    random.seed(42)
    for _ in range(20):
        x = random.randint(50, w - 50)
        y = random.randint(50, h - 50)
        r = random.randint(2, 6)
        alpha = random.randint(30, 80)
        draw.ellipse([x - r, y - r, x + r, y + r],
                     fill=(60, 180, 220, alpha), outline=None)

    # Connecting lines
    nodes = [(random.randint(50, w - 50), random.randint(50, h - 50)) for _ in range(15)]
    for i in range(len(nodes)):
        for j in range(i + 1, min(i + 3, len(nodes))):
            draw.line([nodes[i], nodes[j]], fill=(40, 120, 160, 20), width=1)

    # Title
    font_title = get_font(120)
    font_sub = get_font(36)
    font_gh = get_font(28)

    title = "FlowWiki"
    subtitle = "Knowledge compounds like code. FlowWiki is the compiler."
    github = "github.com/xiejianjun000/FlowWiki"

    # Centered text
    bbox = draw.textbbox((0, 0), title, font=font_title)
    tw = bbox[2] - bbox[0]
    draw.text(((w - tw) // 2, h // 2 - 120), title, fill=(80, 210, 240), font=font_title)

    bbox2 = draw.textbbox((0, 0), subtitle, font=font_sub)
    sw = bbox2[2] - bbox2[0]
    draw.text(((w - sw) // 2, h // 2 + 20), subtitle, fill=(180, 200, 220), font=font_sub)

    bbox3 = draw.textbbox((0, 0), github, font=font_gh)
    gw = bbox3[2] - bbox3[0]
    draw.text(((w - gw) // 2, h - 80), github, fill=(100, 140, 160), font=font_gh)

    # Bottom line accent
    draw.line([(w // 2 - 200, h - 60), (w // 2 + 200, h - 60)], fill=(80, 210, 240), width=3)

    out = f"{ASSETS}/cover.png"
    img.save(out)
    print(f"  ✅ cover.png ({w}x{h})")
    return out

# ============================================================
# 2. ARCHITECTURE DIAGRAM (7 layers)
# ============================================================
def make_arch():
    w, h = 1200, 900
    img = Image.new("RGB", (w, h), (20, 22, 35))
    draw = ImageDraw.Draw(img)

    layers = [
        ("L7", "场景层", "7 通用场景 · 业务外壳可插拔", (120, 200, 255)),
        ("L6", "多 Agent 层", "CLAUDE.md + AGENTS.md + CODEX.md + WORKBUDDY.md", (100, 180, 240)),
        ("L5", "Skill 化层", "4 操作 skill + 高频任务自动抽象 ★", (80, 160, 225)),
        ("L4", "Agent 记忆层 ★", "A-MEM 卡片 + ACE 三 agent 反思循环", (60, 140, 210)),
        ("L3", "Spec-Driven 层", "spec/ 设计 + openspec/changes/ 变更追溯", (50, 120, 195)),
        ("L2", "检索增强层", "BM25 → nano-graphrag → LightRAG 自适应", (40, 100, 180)),
        ("L1", "知识编译层", "raw/ (只读) + wiki/ (AI编译) + 首页/ (人类UX)", (30, 85, 165)),
    ]

    font_num = get_font(28)
    font_name = get_font(32)
    font_desc = get_font(22)

    title_font = get_font(40)
    draw.text((w // 2 - 120, 30), "FlowWiki 7 层架构", fill=(200, 220, 240), font=title_font)

    y_start = 100
    box_h = 95
    gap = 12
    margin = 100

    for i, (num, name, desc, color) in enumerate(layers):
        y = y_start + i * (box_h + gap)
        x = margin

        # Box
        draw.rectangle([x, y, w - margin, y + box_h], fill=color, outline=(255, 255, 255, 30),
                       width=2)

        # Layer number
        draw.text((x + 20, y + 10), num, fill=(255, 255, 255), font=font_num)

        # Layer name
        draw.text((x + 80, y + 10), name, fill=(255, 255, 255), font=font_name)

        # Description
        draw.text((x + 80, y + 48), desc, fill=(240, 245, 255), font=font_desc)

        # Arrow between layers
        if i < len(layers) - 1:
            ny = y + box_h
            arrow_x = w - margin - 40
            draw.polygon([
                (arrow_x - 10, ny), (arrow_x + 10, ny),
                (arrow_x, ny + 12)
            ], fill=(100, 150, 200))

    # Legend
    legend_y = y_start + 7 * (box_h + gap) + 30
    draw.text((margin, legend_y), "★ = FlowWiki 独有创新", fill=(255, 220, 100), font=font_desc)

    out = f"{ASSETS}/arch-diagram.png"
    img.save(out)
    print(f"  ✅ arch-diagram.png ({w}x{h})")
    return out

# ============================================================
# 3. ACE CYCLE DIAGRAM
# ============================================================
def make_ace():
    w, h = 1100, 700
    img = Image.new("RGB", (w, h), (20, 22, 35))
    draw = ImageDraw.Draw(img)

    title_font = get_font(36)
    agent_font = get_font(30)
    desc_font = get_font(20)
    arrow_font = get_font(26)

    draw.text((w // 2 - 180, 30), "ACE 反思循环", fill=(200, 220, 240), font=title_font)
    draw.text((w // 2 - 180, 75), "Generator → Reflector → Curator  三 agent 交叉审查", fill=(140, 160, 180), font=desc_font)

    # Three boxes in a cycle
    cx, cy = w // 2, h // 2 + 20
    r = 200

    agents = [
        ("Generator", "生成摘要\n读 raw → 写 wiki 初稿", (80, 210, 130), -90),
        ("Reflector", "批判审查\n找矛盾/幻觉/过时", (220, 160, 80), 30),
        ("Curator", "最终决策\n通过 / 标待核 / 触发冲突", (80, 160, 220), 150),
    ]

    import math
    positions = []
    for name, desc, color, angle in agents:
        rad = math.radians(angle)
        x = cx + int(r * math.cos(rad)) - 80
        y = cy + int(r * math.sin(rad)) - 50
        positions.append((x, y))

        draw.rounded_rectangle([x, y, x + 200, y + 120], radius=15,
                               fill=color, outline=(255, 255, 255, 40), width=2)
        draw.text((x + 100, y + 15), name, fill=(255, 255, 255), font=agent_font,
                  anchor="ma")

        lines = desc.split("\n")
        for li, line in enumerate(lines):
            draw.text((x + 100, y + 55 + li * 22), line, fill=(240, 245, 255),
                      font=desc_font, anchor="ma")

    # Arrows between agents
    arrow_color = (200, 200, 200)
    for i in range(3):
        j = (i + 1) % 3
        x1, y1 = positions[i][0] + 200, positions[i][1] + 60
        x2, y2 = positions[j][0], positions[j][1] + 60
        draw.line([(x1, y1), (x2, y2)], fill=arrow_color, width=2)

        # Arrow head
        if i == 0:
            draw.polygon([(x2, y2), (x2 + 10, y2 - 6), (x2 + 10, y2 + 6)],
                         fill=arrow_color)
        elif i == 1:
            draw.polygon([(x2, y2), (x2 - 8, y2 - 6), (x2 - 8, y2 + 6)],
                         fill=arrow_color)
        else:
            draw.polygon([(x2, y2), (x2 + 8, y2 - 10), (x2 + 8, y2 + 10)],
                         fill=arrow_color)

    # Ingest trigger
    draw.text((cx - 100, cy + r + 80), "← 每次 ingest 触发", fill=(200, 200, 200),
              font=desc_font, anchor="ma")
    draw.text((cx + 100, cy + r + 80), "错误知识不入 wiki →", fill=(255, 220, 100),
              font=desc_font, anchor="ma")

    out = f"{ASSETS}/ace-cycle.png"
    img.save(out)
    print(f"  ✅ ace-cycle.png ({w}x{h})")
    return out

# ============================================================
# 4. COMPARISON VISUALIZATION
# ============================================================
def make_comparison():
    w, h = 1200, 750
    img = Image.new("RGB", (w, h), (20, 22, 35))
    draw = ImageDraw.Draw(img)

    title_font = get_font(36)
    hdr_font = get_font(20)
    cell_font = get_font(18)

    draw.text((w // 2 - 150, 20), "竞品能力矩阵对比", fill=(200, 220, 240), font=title_font)

    projects = ["FlowWiki", "llm-wiki-\nagent", "claude-\nobsidian", "llm-wiki-\ncompiler", "synthadoc"]
    dimensions = [
        ("防幻觉", [3, 1, 0, 0, 2]),
        ("跨会话记忆", [3, 0, 1, 0, 0]),
        ("多Agent兼容", [3, 2, 1, 1, 2]),
        ("人类UX", [3, 0, 3, 2, 2]),
        ("知识→能力", [3, 0, 0, 0, 0]),
        ("变更追溯", [3, 0, 0, 0, 0]),
        ("自适应检索", [3, 0, 2, 1, 2]),
    ]

    # Table layout
    col_w = 180
    row_h = 60
    table_x = 80
    table_y = 80
    name_w = 140

    # Headers
    for ci, proj in enumerate(projects):
        x = table_x + name_w + ci * col_w
        lines = proj.split("\n")
        draw.rectangle([x, table_y, x + col_w, table_y + 50],
                       fill=(40, 50, 70), outline=(80, 100, 130))
        for li, line in enumerate(lines):
            draw.text((x + col_w // 2, table_y + 8 + li * 22), line,
                      fill=(200, 220, 240), font=hdr_font, anchor="ma")

    draw.rectangle([table_x, table_y, table_x + name_w, table_y + 50],
                   fill=(30, 35, 50), outline=(80, 100, 130))
    draw.text((table_x + name_w // 2, table_y + 25), "维度",
              fill=(180, 200, 220), font=hdr_font, anchor="ma")

    # Data rows
    for ri, (dim, scores) in enumerate(dimensions):
        ry = table_y + 50 + ri * row_h

        # Dimension name
        draw.rectangle([table_x, ry, table_x + name_w, ry + row_h],
                       fill=(30, 35, 50) if ri % 2 == 0 else (35, 40, 55),
                       outline=(60, 80, 100))
        draw.text((table_x + name_w // 2, ry + row_h // 2), dim,
                  fill=(200, 220, 240), font=hdr_font, anchor="ma")

        for ci, score in enumerate(scores):
            x = table_x + name_w + ci * col_w
            bg = (50, 60, 80)
            if score == 3:
                bg = (30, 80, 50)
            elif score == 2:
                bg = (60, 90, 30)
            elif score == 1:
                bg = (80, 70, 30)
            elif score == 0:
                bg = (60, 40, 40)

            draw.rectangle([x, ry, x + col_w, ry + row_h],
                           fill=bg, outline=(80, 100, 130))

            label = {3: "★★★", 2: "★★", 1: "★", 0: "✗"}[score]
            color = (255, 255, 255) if score >= 2 else (220, 220, 220)
            draw.text((x + col_w // 2, ry + row_h // 2), label,
                      fill=color, font=cell_font, anchor="ma")

    # Footer
    footer_y = table_y + 50 + 7 * row_h + 30
    draw.text((table_x, footer_y),
              "★ = FlowWiki 是唯一同时覆盖以上 7 个维度的项目",
              fill=(255, 220, 100), font=cell_font)
    draw.text((table_x, footer_y + 30),
              "数据来源：GitHub 仓库分析 (2026-07-17) · 完整对比见 docs/competitor-analysis.md",
              fill=(140, 160, 180), font=get_font(16))

    out = f"{ASSETS}/comparison.png"
    img.save(out)
    print(f"  ✅ comparison.png ({w}x{h})")
    return out


if __name__ == "__main__":
    print("🎨 生成 FlowWiki 文章配图...")
    make_cover()
    make_arch()
    make_ace()
    make_comparison()
    print(f"\n📁 全部图片已保存到: {ASSETS}")
