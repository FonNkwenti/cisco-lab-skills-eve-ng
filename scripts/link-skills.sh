#!/usr/bin/env bash
# link-skills.sh — Link every skill under .agent/skills/ into .claude/skills/
# so Claude Code can discover them as user-invocable skills.
#
# On Windows (Git Bash / MSYS) this uses directory junctions (mklink /J) —
# no admin rights required. On Linux/macOS this uses regular symlinks.
#
# Idempotent: re-running refreshes stale links without touching real content.
#
# Usage:
#   .agent/skills/scripts/link-skills.sh [project-root]
#
# If project-root is omitted, the script assumes it is being invoked from
# inside a project that already contains .agent/skills/ and resolves the
# project root as three levels up from the script's own directory.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

PROJECT_ROOT="${1:-$(cd "$SCRIPT_DIR/../../.." && pwd)}"

if [ ! -d "$PROJECT_ROOT/.agent/skills" ]; then
  echo "ERROR: $PROJECT_ROOT/.agent/skills not found. Pass the project root as arg 1." >&2
  exit 1
fi

case "$(uname -s)" in
  MINGW*|MSYS*|CYGWIN*) IS_WINDOWS=1 ;;
  *) IS_WINDOWS=0 ;;
esac

CLAUDE_SKILLS="$PROJECT_ROOT/.claude/skills"
mkdir -p "$CLAUDE_SKILLS"

win_path() { cygpath -w "$1"; }

remove_link() {
  local p="$1"
  if [ "$IS_WINDOWS" = "1" ]; then
    # Only remove if it is a reparse point (junction/symlink); otherwise no-op.
    # Using [IO.Directory]::Delete avoids a PS 5.1 bug where Remove-Item on a
    # junction throws NullReferenceException despite successful removal.
    powershell.exe -NoProfile -Command "
      \$i = Get-Item -LiteralPath '$(win_path "$p")' -Force -ErrorAction SilentlyContinue
      if (\$i -and (\$i.LinkType -eq 'Junction' -or \$i.LinkType -eq 'SymbolicLink')) {
        [System.IO.Directory]::Delete('$(win_path "$p")', \$false)
      }
    " >/dev/null 2>&1 || true
  else
    if [ -L "$p" ]; then rm -f "$p"; fi
  fi
}

create_link() {
  local link="$1" target="$2"
  if [ "$IS_WINDOWS" = "1" ]; then
    powershell.exe -NoProfile -Command "New-Item -ItemType Junction -Path '$(win_path "$link")' -Target '$(win_path "$target")' | Out-Null" >/dev/null
  else
    ln -s "$target" "$link"
  fi
}

linked=0
skipped=0
for dir in "$SKILLS_DIR"/*/; do
  name="$(basename "$dir")"
  [ -f "$dir/SKILL.md" ] || continue
  link="$CLAUDE_SKILLS/$name"
  target="$dir"
  target="${target%/}"  # strip trailing slash

  if [ -e "$link" ] || [ -L "$link" ]; then
    remove_link "$link"
  fi

  if [ -e "$link" ] || [ -L "$link" ]; then
    echo "  skip  $name  (exists as non-link directory)"
    skipped=$((skipped + 1))
    continue
  fi

  create_link "$link" "$target"
  echo "  link  $name"
  linked=$((linked + 1))
done

echo ""
echo "Linked $linked skill(s) into .claude/skills/; $skipped skipped."
echo "Ensure .claude/skills/ is in your .gitignore (these are derived from the submodule)."
