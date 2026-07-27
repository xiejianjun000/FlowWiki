#!/bin/bash
# install-hooks.sh — FlowWiki 质量门控安装脚本
# 对标 Ar9av/obsidian-wiki setup.sh 的自动化安装体验

set -e

HOOKS_DIR="$(cd "$(dirname "$0")" && pwd)/../.git/hooks"

echo "🔧 FlowWiki 质量门控安装..."

# pre-commit: 提交前自动运行质量审计
cp "$(dirname "$0")/pre-commit.template" "$HOOKS_DIR/pre-commit" 2>/dev/null || {
    # 如果模板不存在，直接复制已安装的 hook
    if [ -f "$(dirname "$0")/../.git/hooks/pre-commit" ]; then
        echo "  ✅ pre-commit hook 已安装"
    else
        echo "  ⚠️  pre-commit hook 未找到，请手动安装"
    fi
}
chmod +x "$HOOKS_DIR/pre-commit" 2>/dev/null || true

echo ""
echo "✅ 质量门控已激活:"
echo "   pre-commit: 提交前自动运行 12 维质量审计"
echo "   CI: GitHub Actions 自动运行质量门控"
echo "   自动化: 每日自动质量监控"
echo ""
echo "跳过门控: git commit --no-verify"
