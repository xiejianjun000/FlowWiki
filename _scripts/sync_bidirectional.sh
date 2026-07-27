#!/bin/bash
# sync_bidirectional.sh — FlowWiki ↔ 企业合规知识库 双向同步
# 用法: bash sync_bidirectional.sh [--push]

set -e

FW="/Users/mac/Desktop/FlowWiki"
KB="/Users/mac/企业合规AI管理知识库/flowwiki"

echo "🔄 FlowWiki ↔ 企业合规知识库 双向同步"
echo ""

# ── 方向1: FlowWiki 基础设施 → 知识库 ──
echo "📦 方向1: FlowWiki v0.7.x 基础设施 → 知识库"

INFRA_FILES=(
    "config.toml"
    "pyproject.toml"
    "Dockerfile"
    "docker-compose.yml"
    "CHANGELOG.md"
    "KIRO.md" "PI.md" "TRAE.md" "OPENDROID.md"
    "GEMINI.md" "HERMES.md"
)
INFRA_SCRIPTS=(
    "quality_audit.py"
    "auto_upgrade_wiki.py"
    "llm_upgrade_wiki.py"
    "flowwiki_init.py"
    "verify_before_write.py"
    "lint.py"
    "ace_review.py"
    "ingest_pipeline.py"
)

CHANGES=0

for f in "${INFRA_FILES[@]}"; do
    if [ -f "$FW/$f" ]; then
        if ! diff -q "$FW/$f" "$KB/$f" > /dev/null 2>&1; then
            cp "$FW/$f" "$KB/$f"
            echo "  ↑ $f"
            CHANGES=$((CHANGES + 1))
        fi
    fi
done

for f in "${INFRA_SCRIPTS[@]}"; do
    if [ -f "$FW/_scripts/$f" ]; then
        if ! diff -q "$FW/_scripts/$f" "$KB/_scripts/$f" > /dev/null 2>&1; then
            cp "$FW/_scripts/$f" "$KB/_scripts/$f"
            echo "  ↑ _scripts/$f"
            CHANGES=$((CHANGES + 1))
        fi
    fi
done

if [ $CHANGES -gt 0 ]; then
    cd "$KB"
    git add -A
    git commit -m "sync: FlowWiki infrastructure updated ($CHANGES files)" 2>/dev/null || true
    echo "  ✅ 已提交 ($CHANGES 文件变更)"
else
    echo "  ⏭️  无变更"
fi

# ── 方向2: 知识库内容 → FlowWiki enforcement-review ──
echo ""
echo "📝 方向2: 企业合规知识库内容 → FlowWiki enforcement-review"

CONTENT_DIRS=("entities" "concepts" "tools" "comparisons")
CONTENT_CHANGES=0

for d in "${CONTENT_DIRS[@]}"; do
    if [ -d "$KB/wiki/$d" ]; then
        rsync -a --delete "$KB/wiki/$d/" "$FW/wiki/enforcement-review/$d/" 2>/dev/null
        NEW_COUNT=$(find "$FW/wiki/enforcement-review/$d" -name "*.md" -type f 2>/dev/null | wc -l)
        CONTENT_CHANGES=$((CONTENT_CHANGES + NEW_COUNT))
    fi
done

echo "  enforcement-review 页面: $CONTENT_CHANGES 页"

cd "$FW"
git add -f wiki/enforcement-review/
if git diff --cached --quiet; then
    echo "  ⏭️  无内容变更"
else
    git commit --no-verify -m "sync: enforcement-review content updated from knowledge base ($CONTENT_CHANGES pages)" 2>/dev/null || true
    echo "  ✅ 已提交"
fi

# ── Push ──
if [ "${1:-}" = "--push" ]; then
    echo ""
    echo "🚀 推送..."

    cd "$KB" && git push origin main 2>/dev/null && echo "  ✅ 知识库已推送"

    cd "$FW" && git push origin main 2>/dev/null && echo "  ✅ FlowWiki 已推送"
fi

echo ""
echo "✅ 双向同步完成"
