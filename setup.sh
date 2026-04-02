#!/usr/bin/env bash
# resskills setup — register skills with Claude Code
#
# Usage:
#   ./setup.sh           Install globally (~/.claude/skills/)
#   ./setup.sh --local   Install for current project only (.claude/skills/)
set -e

RESSKILLS_DIR="$(cd "$(dirname "$0")" && pwd)"

# Parse flags
LOCAL=0
while [ $# -gt 0 ]; do
  case "$1" in
    --local) LOCAL=1; shift ;;
    *) echo "Unknown flag: $1 (use --local for project install)"; exit 1 ;;
  esac
done

if [ "$LOCAL" -eq 1 ]; then
  SKILLS_DIR="$(pwd)/.claude/skills"
  mkdir -p "$SKILLS_DIR"
  MODE="project"
else
  SKILLS_DIR="$HOME/.claude/skills"
  mkdir -p "$SKILLS_DIR"
  MODE="global"
fi

echo "resskills setup ($MODE)"
echo "======================="
echo ""
echo "Skills pack: $RESSKILLS_DIR"
echo "Install to:  $SKILLS_DIR"
echo ""

# 1. Install Python dependencies and generate SKILL.md files
if command -v uv >/dev/null 2>&1; then
  echo "Installing dependencies..."
  (cd "$RESSKILLS_DIR" && uv sync --quiet)
  echo "Generating SKILL.md files..."
  (cd "$RESSKILLS_DIR" && uv run resskills-gen)
else
  echo "Warning: uv not found. Install it: curl -LsSf https://astral.sh/uv/install.sh | sh"
  echo "Skipping dependency install and generation."
  echo ""
fi

# 2. Symlink the resskills directory itself
RESSKILLS_LINK="$SKILLS_DIR/resskills"
if [ -L "$RESSKILLS_LINK" ]; then
  ln -snf "$RESSKILLS_DIR" "$RESSKILLS_LINK"
elif [ ! -e "$RESSKILLS_LINK" ]; then
  ln -snf "$RESSKILLS_DIR" "$RESSKILLS_LINK"
fi

# 3. Create symlinks for each skill
echo ""
echo "Creating skill symlinks..."

SKILL_DIRS=(
  analyze careful checkpoint code-quality debug deep-research
  experiment hypothesis implement integrate learn lit-review
  paper-compile paper-review paper-write pi-review retro review
  second-opinion setup-project
)

created=0
skipped=0
for skill in "${SKILL_DIRS[@]}"; do
  target="$SKILLS_DIR/$skill"
  source="resskills/$skill"

  if [ -L "$target" ]; then
    ln -snf "$source" "$target"
    ((created++))
  elif [ -e "$target" ]; then
    echo "  SKIP: $skill (already exists at $target)"
    ((skipped++))
  else
    ln -snf "$source" "$target"
    ((created++))
  fi
done

echo "  Created/updated $created symlinks"
[ "$skipped" -gt 0 ] && echo "  Skipped $skipped (already exist)"

echo ""
echo "Done! ($MODE install)"
echo ""
if [ "$LOCAL" -eq 1 ]; then
  echo "Skills available in this project only."
  echo "Add .claude/skills/ to .gitignore if you don't want to commit the symlinks."
else
  echo "Skills available in all projects."
fi
echo ""
for skill in "${SKILL_DIRS[@]}"; do
  echo "  /$skill"
done
echo ""
echo "Try: /experiment, /review, /deep-research, /hypothesis"
