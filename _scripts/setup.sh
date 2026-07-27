#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────
# FlowWiki setup.sh — 全局 Skill 部署脚本
# 将 wiki-query 和 wiki-update 安装到所有 Agent 的发现路径，
# 让用户在任何项目中都能操作 FlowWiki 知识库。
#
# 借鉴来源：Ar9av/obsidian-wiki 的 setup.sh
# 创建时间：2026-07-20
# ──────────────────────────────────────────────────────────

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FLOWWIKI_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILLS_SRC="$FLOWWIKI_ROOT/.skills"
CONFIG_DIR="$HOME/.flowwiki"
CONFIG_FILE="$CONFIG_DIR/config"

# ── ANSI 颜色 ──
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}══════════════════════════════════════════${NC}"
echo -e "${CYAN}  FlowWiki 全局 Skill 部署工具${NC}"
echo -e "${CYAN}  FlowWiki 根目录: ${FLOWWIKI_ROOT}${NC}"
echo -e "${CYAN}══════════════════════════════════════════${NC}"
echo ""

# ── 步骤 1：写入配置文件 ──
echo -e "${YELLOW}[1/4]${NC} 写入配置文件 → ${CONFIG_FILE}"
mkdir -p "$CONFIG_DIR"
cat > "$CONFIG_FILE" <<EOF
# FlowWiki 全局配置
# 由 setup.sh 自动生成于 $(date -u +"%Y-%m-%dT%H:%M:%SZ")
flowwiki_root: $FLOWWIKI_ROOT
skills_dir: $SKILLS_SRC

# 行业标识（执法督察评查知识库）
industry: enforcement-review

# 多 vault 支持（使用 @name 前缀切换）
# 格式: vaults.<name>.root
vaults:
  default:
    root: $FLOWWIKI_ROOT
EOF
echo -e "  ${GREEN}✓${NC} 配置已写入"

# ── 步骤 2：符号链接 Skill 到所有 Agent 路径 ──
echo ""
echo -e "${YELLOW}[2/4]${NC} 安装全局 Skill 到 Agent 发现路径..."

# 定义所有 Agent 的 skill 路径 (路径)
AGENT_SKILL_DIRS=(
    "$HOME/.claude/skills"
    "$HOME/.gemini/skills"
    "$HOME/.codex/skills"
    "$HOME/.hermes/skills"
    "$HOME/.openclaw/skills"
    "$HOME/.copilot/skills"
    "$HOME/.kiro/skills"
    "$HOME/.agents/skills"
)

SKILLS=("wiki-query" "wiki-update")
installed_count=0

for skill in "${SKILLS[@]}"; do
    skill_src="$SKILLS_SRC/$skill"
    if [[ ! -d "$skill_src" ]]; then
        echo -e "  ${RED}✗${NC} 技能源缺失: $skill_src"
        continue
    fi

    for target_dir in "${AGENT_SKILL_DIRS[@]}"; do
        mkdir -p "$target_dir"
        target_link="$target_dir/$skill"

        # 如果已存在且是符号链接，先删除
        if [[ -L "$target_link" ]]; then
            rm -f "$target_link"
        elif [[ -d "$target_link" ]]; then
            # 如果是目录而非符号链接，跳过（避免覆盖用户自定义 skill）
            echo -e "  ${YELLOW}⚠${NC}  $(basename "$(dirname "$target_dir")")/$skill 已存在（非符号链接），跳过"
            continue
        fi

        ln -sf "$skill_src" "$target_link"
        installed_count=$((installed_count + 1))
        echo -e "  ${GREEN}✓${NC}  $(basename "$(dirname "$target_dir")")/$skill → .../.skills/$skill/"
    done
done

# ── 步骤 3：同步到项目本地 skills（.claude/skills/ 和 .agents/skills/） ──
echo ""
echo -e "${YELLOW}[3/4]${NC} 同步到项目本地技能目录..."

PROJECT_SKILL_DIRS=(
    "$FLOWWIKI_ROOT/.claude/skills"
    "$FLOWWIKI_ROOT/.agents/skills"
)

for project_dir in "${PROJECT_SKILL_DIRS[@]}"; do
    mkdir -p "$project_dir"
    for skill in "${SKILLS[@]}"; do
        target="$project_dir/$skill"
        skill_src="$SKILLS_SRC/$skill"
        if [[ -L "$target" ]]; then
            rm -f "$target"
        fi
        ln -sf "$skill_src" "$target"
    done
done
echo -e "  ${GREEN}✓${NC} 项目本地技能已同步"

# ── 步骤 4：验证 ──
echo ""
echo -e "${YELLOW}[4/4]${NC} 验证安装..."

errors=0
for skill in "${SKILLS[@]}"; do
    # 检查源文件
    if [[ -f "$SKILLS_SRC/$skill/SKILL.md" ]]; then
        echo -e "  ${GREEN}✓${NC} 技能源: .skills/$skill/SKILL.md"
    else
        echo -e "  ${RED}✗${NC} 技能源缺失: .skills/$skill/SKILL.md"
        errors=$((errors + 1))
    fi
done

# 检查配置文件
if [[ -f "$CONFIG_FILE" ]]; then
    echo -e "  ${GREEN}✓${NC} 配置文件: $CONFIG_FILE"
else
    echo -e "  ${RED}✗${NC} 配置文件缺失: $CONFIG_FILE"
    errors=$((errors + 1))
fi

# 检查至少一个 Agent skill 已安装
claude_skill="$HOME/.claude/skills/wiki-query/SKILL.md"
if [[ -f "$claude_skill" ]]; then
    echo -e "  ${GREEN}✓${NC} Claude Code skill 已就绪"
else
    echo -e "  ${YELLOW}⚠${NC}  Claude Code skill 未安装（可能 Claude Code 未使用）"
fi

echo ""

if [[ $errors -eq 0 ]]; then
    echo -e "${GREEN}══════════════════════════════════════════${NC}"
    echo -e "${GREEN}  部署成功！${NC}"
    echo -e "${GREEN}══════════════════════════════════════════${NC}"
    echo ""
    echo -e "  已安装的 Skill:"
    echo -e "    ${CYAN}wiki-query${NC}  — 从任意项目查询 FlowWiki 知识库"
    echo -e "    ${CYAN}wiki-update${NC} — 将任意项目的知识同步到 FlowWiki"
    echo ""
    echo -e "  支持的 Agent:"
    echo -e "    Claude Code  → ~/.claude/skills/"
    echo -e "    Gemini CLI   → ~/.gemini/skills/"
    echo -e "    Codex        → ~/.codex/skills/"
    echo -e "    Hermes       → ~/.hermes/skills/"
    echo -e "    OpenClaw     → ~/.openclaw/skills/"
    echo -e "    Copilot CLI  → ~/.copilot/skills/"
    echo -e "    OpenCode等   → ~/.agents/skills/"
    echo ""
    echo -e "  使用方法:"
    echo -e "    在任意项目中告诉 Agent:"
    echo -e "    ${YELLOW}  /wiki-query 行政处罚的程序合法性要点${NC}"
    echo -e "    ${YELLOW}  /wiki-update 把这段代码的坑记录到知识库${NC}"
    echo ""
    echo -e "  卸载:"
    echo -e "    bash $SCRIPT_DIR/setup.sh --uninstall"
else
    echo -e "${RED}══════════════════════════════════════════${NC}"
    echo -e "${RED}  部署完成但有 $errors 个错误${NC}"
    echo -e "${RED}══════════════════════════════════════════${NC}"
    exit 1
fi
