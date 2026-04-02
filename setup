#!/usr/bin/env bash
# resskills setup — register skills with Claude Code
set -e

RESSKILLS_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS_DIR="$(dirname "$RESSKILLS_DIR")"

echo "resskills setup"
echo "==============="
echo ""
echo "Skills pack: $RESSKILLS_DIR"
echo "Skills root: $SKILLS_DIR"
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

# 2. Create symlinks for each skill in the parent directory
# This makes Claude Code discover /experiment, /review, etc. as top-level commands
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
    # Update existing symlink
    ln -snf "$source" "$target"
    ((created++))
  elif [ -e "$target" ]; then
    # Real directory exists, don't overwrite
    echo "  SKIP: $skill (real directory exists at $target)"
    ((skipped++))
  else
    ln -snf "$source" "$target"
    ((created++))
  fi
done

echo "  Created/updated $created symlinks"
[ "$skipped" -gt 0 ] && echo "  Skipped $skipped (real directories exist)"

echo ""
echo "Done! Available skills:"
echo ""
for skill in "${SKILL_DIRS[@]}"; do
  echo "  /$skill"
done
echo ""
echo "Try: /experiment, /review, /deep-research, /hypothesis"
