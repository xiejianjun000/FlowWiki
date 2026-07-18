#!/bin/bash
# 一键生成 FlowWiki 文章配图（4 张）
# 使用方式：bash ops/publishing/scripts/generate-images.sh
# 需要 WorkBuddy 的 ImageGen 工具支持

ARTICLE_DIR="ops/publishing/articles/v0.1.0-launch"
ASSETS_DIR="$ARTICLE_DIR/assets"

mkdir -p "$ASSETS_DIR"

echo "📸 开始生成配图..."

echo "  1/4 封面图 (cover.png)..."
echo "     Prompt: 深色科技风，标题'FlowWiki'，副标题'知识像代码一样复利'，800x420"

echo "  2/4 7 层架构图 (arch-diagram.png)..."
echo "     Prompt: 7 层竖版架构图，Markdown+Git 驱动，1024x768"

echo "  3/4 ACE 反思循环图 (ace-cycle.png)..."
echo "     Prompt: 三 agent 循环流程图，Generator→Reflector→Curator，1024x768"

echo "  4/4 竞品对比图 (comparison.png)..."
echo "     Prompt: 5 项目 9 维对比可视化，雷达图或矩阵，1024x768"

echo ""
echo "✅ 图片生成指令已输出。"
echo ""
echo "在 WorkBuddy 对话中依次执行以上 4 个 ImageGen 请求，"
echo "输出路径设为 $ASSETS_DIR/"
echo "或直接告诉我：'生成 FlowWiki 首发文章的全部配图'"
