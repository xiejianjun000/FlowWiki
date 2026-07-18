#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# FlowWiki 安装脚本 — 自动检测区域 + 生成本地化目录
# ─────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "╔══════════════════════════════════════════╗"
echo "║       FlowWiki 安装向导 v0.2.0          ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# ── Step 1: 检测 Python ──
PYTHON=""
for candidate in python3.13 python3.12 python3.11 python3; do
    if command -v "$candidate" &>/dev/null; then
        PYTHON="$candidate"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    echo "❌ 需要 Python 3.11+，但系统中未找到。请安装后重试。"
    exit 1
fi
echo "✅ Python: $($PYTHON --version)"

# ── Step 2: 检测区域 ──
echo ""
echo "📍 正在检测区域..."

LANG_CODE="$($PYTHON -c "
import sys; sys.path.insert(0, '$PROJECT_ROOT')
from _scripts.locale import detect_locale
print(detect_locale())
" 2>/dev/null || echo "en")"

if [ "$LANG_CODE" = "zh" ]; then
    echo "   检测到：中国大陆 🇨🇳 → 使用中文目录名"
    DISPLAY_DIR="原始资料/ 知识库/ 首页/"
else
    echo "   检测到：海外 🌍 → 使用英文目录名"
    DISPLAY_DIR="raw/ wiki/ 00_首页/"
fi

# ── Step 3: 写入 config.toml ──
CONFIG_FILE="$PROJECT_ROOT/config.toml"
if [ -f "$CONFIG_FILE" ]; then
    # 检查是否已有 locale 配置
    if grep -q '\[locale\]' "$CONFIG_FILE" 2>/dev/null; then
        echo "   config.toml 已有 locale 配置，跳过"
    else
        echo "" >> "$CONFIG_FILE"
        echo "[locale]" >> "$CONFIG_FILE"
        echo "lang = \"$LANG_CODE\"" >> "$CONFIG_FILE"
        echo "auto_detect = true" >> "$CONFIG_FILE"
        echo "✅ locale 配置已写入 config.toml"
    fi
fi

# .llm-wiki/config.toml 同步
LLM_WIKI_CONFIG="$PROJECT_ROOT/.llm-wiki/config.toml"
if [ -f "$LLM_WIKI_CONFIG" ]; then
    if ! grep -q '\[locale\]' "$LLM_WIKI_CONFIG" 2>/dev/null; then
        echo "" >> "$LLM_WIKI_CONFIG"
        echo "[locale]" >> "$LLM_WIKI_CONFIG"
        echo "lang = \"$LANG_CODE\"" >> "$LLM_WIKI_CONFIG"
        echo "auto_detect = true" >> "$LLM_WIKI_CONFIG"
        echo "✅ locale 配置已同步到 .llm-wiki/config.toml"
    fi
fi

# ── Step 4: 生成本地化目录入口 ──
if [ "$LANG_CODE" != "en" ]; then
    echo ""
    echo "📁 正在生成本地化目录入口..."

    CREATED=$($PYTHON -c "
import sys; sys.path.insert(0, '$PROJECT_ROOT')
from _scripts.locale import generate_locale_dirs
from pathlib import Path
created = generate_locale_dirs(Path('$PROJECT_ROOT'), '$LANG_CODE')
for c in created[-5:]:
    print(f'   {c}')
" 2>&1)

    if [ $? -eq 0 ]; then
        echo "✅ 本地化目录已生成"
        echo "$CREATED"
    else
        echo "⚠️  本地化目录生成失败（不影响核心功能）"
    fi
fi

# ── Step 5: 检查依赖 ──
echo ""
echo "🔧 检查依赖..."

if $PYTHON -c "import yaml" 2>/dev/null; then
    echo "   ✅ PyYAML"
else
    echo "   ⚠️  PyYAML 未安装（可选：pip install pyyaml）"
fi

if $PYTHON -c "import mcp" 2>/dev/null; then
    echo "   ✅ MCP SDK"
else
    echo "   ⚠️  MCP SDK 未安装（可选：pip install mcp 以启用 MCP Server）"
fi

# ── Step 6: Git 初始化（如果是全新 clone） ──
if [ -d "$PROJECT_ROOT/.git" ]; then
    echo "   ✅ Git 仓库已就绪"
fi

# ── 完成 ──
echo ""
echo "╔══════════════════════════════════════════╗"
echo "║          安装完成！                      ║"
echo "╠══════════════════════════════════════════╣"
echo "║  语言:  $LANG_CODE                                  ║"
echo "║  目录:  $DISPLAY_DIR"
echo "╠══════════════════════════════════════════╣"
echo "║  快速开始:                               ║"
echo "║    mkdir -p raw/articles                 ║"
echo "║    echo '# 测试' > raw/articles/test.md  ║"
echo "║    在 AI Agent 中说: 请按 ingest skill   ║"
echo "║    把 raw/articles/test.md 入库           ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "📖 完整文档: https://github.com/xiejianjun000/FlowWiki"
echo "🐛 反馈问题: https://github.com/xiejianjun000/FlowWiki/issues"

# ── 可选：打开 Obsidian ──
if command -v open &>/dev/null && [ -d "/Applications/Obsidian.app" ]; then
    echo ""
    read -p "❓ 是否用 Obsidian 打开 FlowWiki？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        open -a Obsidian "$PROJECT_ROOT"
    fi
fi
