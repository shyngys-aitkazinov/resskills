#!/usr/bin/env python3
"""Generate SKILL.md files from .tmpl templates using Jinja2.

Pipeline:
    1. Load shared blocks from blocks/*.md
    2. Find all */SKILL.md.tmpl files
    3. Render templates with Jinja2 (blocks injected as variables)
    4. Write generated SKILL.md files

Usage:
    uv run resskills-gen              # Generate all
    uv run resskills-gen --dry-run    # Check freshness (exit 1 if stale)
"""

from __future__ import annotations

import sys
from pathlib import Path

from jinja2 import Environment, BaseLoader, Undefined


class SilentUndefined(Undefined):
    """Leave unknown variables as-is instead of raising errors."""

    def __str__(self) -> str:
        return f"{{{{{self._undefined_name}}}}}"


def find_root() -> Path:
    """Find the resskills skills root (directory containing blocks/)."""
    # Walk up from this script to find the blocks/ directory
    current = Path(__file__).resolve().parent
    for _ in range(5):
        if (current / "blocks").is_dir():
            return current
        current = current.parent
    raise FileNotFoundError("Cannot find resskills root (no blocks/ directory found)")


def load_blocks(root: Path) -> dict[str, str]:
    """Load all shared blocks from blocks/*.md.

    Block names are derived from filenames:
        preamble.md -> PREAMBLE
        python-standards.md -> PYTHON_STANDARDS
    """
    blocks: dict[str, str] = {}
    blocks_dir = root / "blocks"
    if not blocks_dir.exists():
        return blocks

    for f in sorted(blocks_dir.glob("*.md")):
        key = f.stem.upper().replace("-", "_")
        blocks[key] = f.read_text()

    return blocks


def discover_templates(root: Path) -> list[Path]:
    """Find all SKILL.md.tmpl files (in subdirs and root).

    Skips directories that don't belong to resskills (reference repos,
    hidden dirs, venv, Python package dir).
    """
    # Directories to skip (reference repos, tooling, hidden)
    skip_dirs = {
        ".git",
        ".venv",
        ".claude",
        "__pycache__",
        "node_modules",
        "resskills",  # Python package dir, not a skill
        # Reference repos (cloned for study, not part of the skills pack)
        "gstack",
        "autoresearch",
        "ugodeka",
        "AI-Research-SKILLs",
        "Auto-claude-code-research-in-sleep",
        "academic-research-skills",
        "claude-scientific-skills",
    }

    templates: list[Path] = []
    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue
        if child.name in skip_dirs or child.name.startswith("."):
            continue
        tmpl = child / "SKILL.md.tmpl"
        if tmpl.exists():
            templates.append(tmpl)

    root_tmpl = root / "SKILL.md.tmpl"
    if root_tmpl.exists():
        templates.append(root_tmpl)

    return templates


def render_template(
    tmpl_path: Path,
    root: Path,
    blocks: dict[str, str],
    env: Environment,
) -> str:
    """Render a single SKILL.md.tmpl file with Jinja2."""
    raw = tmpl_path.read_text()

    # Determine skill name from directory
    skill_name = tmpl_path.parent.name if tmpl_path.parent != root else "resskills"

    # Build template variables: all blocks + SKILL_NAME
    variables = {**blocks, "SKILL_NAME": skill_name}

    # Render with Jinja2
    template = env.from_string(raw)
    rendered = template.render(**variables)

    header = (
        "<!-- AUTO-GENERATED from SKILL.md.tmpl -- do not edit directly -->\n"
        "<!-- Regenerate: uv run resskills-gen -->\n\n"
    )
    return header + rendered


def main() -> None:
    """Entry point for resskills-gen command."""
    dry_run = "--dry-run" in sys.argv

    root = find_root()
    blocks = load_blocks(root)
    templates = discover_templates(root)

    if not templates:
        print("No SKILL.md.tmpl files found.")
        sys.exit(1)

    # Configure Jinja2: use {{ }} delimiters, leave unknown vars as-is
    env = Environment(
        loader=BaseLoader(),
        undefined=SilentUndefined,
        keep_trailing_newline=True,
        # Use block_start/end that won't conflict with YAML frontmatter
        block_start_string="{%",
        block_end_string="%}",
        variable_start_string="{{",
        variable_end_string="}}",
        comment_start_string="{#",
        comment_end_string="#}",
    )

    stale: list[str] = []
    generated_count = 0

    for tmpl in templates:
        rendered = render_template(tmpl, root, blocks, env)
        out = tmpl.parent / "SKILL.md"

        if dry_run:
            if not out.exists() or out.read_text() != rendered:
                stale.append(str(out.relative_to(root)))
        else:
            out.write_text(rendered)
            generated_count += 1
            rel = out.relative_to(root)
            print(f"  Generated {rel}")

    if dry_run:
        if stale:
            print(f"STALE: {', '.join(stale)}")
            sys.exit(1)
        else:
            print(f"All {len(templates)} SKILL.md files are fresh.")
    else:
        print(f"\nGenerated {generated_count} SKILL.md files.")


if __name__ == "__main__":
    main()
