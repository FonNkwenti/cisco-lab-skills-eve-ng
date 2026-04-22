#!/bin/bash
# bootstrap.sh — Create a new Cisco certification lab project
#
# Usage:
#   ./bootstrap.sh <project-name> <cert-name> <exam-code>
#
# Example:
#   ./bootstrap.sh ccnp-enarsi-labs "CCNP ENARSI" "300-410"

set -e

PROJECT_NAME="${1:?Usage: bootstrap.sh <project-name> <cert-name> <exam-code>}"
CERT_NAME="${2:?Usage: bootstrap.sh <project-name> <cert-name> <exam-code>}"
EXAM_CODE="${3:?Usage: bootstrap.sh <project-name> <cert-name> <exam-code>}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HUB_DIR="$SCRIPT_DIR"
TARGET_DIR="$(dirname "$SCRIPT_DIR")/$PROJECT_NAME"
GITHUB_HUB_URL="$(git -C "$HUB_DIR" remote get-url origin 2>/dev/null || echo 'https://github.com/YOUR_USERNAME/cisco-lab-skills.git')"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Bootstrapping: $PROJECT_NAME"
echo "  Certification: $CERT_NAME ($EXAM_CODE)"
echo "  Target:        $TARGET_DIR"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -d "$TARGET_DIR" ]; then
  echo "ERROR: $TARGET_DIR already exists. Aborting."
  exit 1
fi

echo "→ Creating directory structure..."
mkdir -p "$TARGET_DIR"/{.agent,blueprint/"$EXAM_CODE"/references,specs,conductor/tracks,labs,tests,docs,.prompts}

echo "→ Initializing git repo..."
git -C "$TARGET_DIR" init

echo "→ Adding cisco-lab-skills as submodule at .agent/skills/ ..."
git -C "$TARGET_DIR" submodule add "$GITHUB_HUB_URL" .agent/skills

echo "→ Copying scaffolding..."
cp "$HUB_DIR/scaffolding/gitignore.template"  "$TARGET_DIR/.gitignore"
cp "$HUB_DIR/scaffolding/requirements.txt"    "$TARGET_DIR/requirements.txt"
cp -r "$HUB_DIR/scaffolding/labs-common/"     "$TARGET_DIR/labs/common/"

echo "→ Generating conductor files..."
cp "$HUB_DIR/conductor-template/workflow.md"       "$TARGET_DIR/conductor/workflow.md"
cp "$HUB_DIR/conductor-template/tech-stack.md"     "$TARGET_DIR/conductor/tech-stack.md"
cp -r "$HUB_DIR/conductor-template/code_styleguides" "$TARGET_DIR/conductor/code_styleguides"
cp "$HUB_DIR/conductor-template/tracks.md"         "$TARGET_DIR/conductor/tracks.md"

sed "s/{{CERT_NAME}}/$CERT_NAME/g; s/{{EXAM_CODE}}/$EXAM_CODE/g; s/{{SCOPE}}/TODO: Define scope of coverage/g" \
  "$HUB_DIR/conductor-template/product.md.tmpl" > "$TARGET_DIR/conductor/product.md"

sed "s/{{CERT_NAME}}/$CERT_NAME/g; s/{{EXAM_CODE}}/$EXAM_CODE/g" \
  "$HUB_DIR/conductor-template/product-guidelines.md.tmpl" > "$TARGET_DIR/conductor/product-guidelines.md"

echo "→ Creating CLAUDE.md..."
cat > "$TARGET_DIR/CLAUDE.md" << EOF
# $CERT_NAME ($EXAM_CODE) Lab Project

## Shared Context (Skills + Standards)

@.agent/skills/memory/CLAUDE.md

## This Certification

- **Exam**: $CERT_NAME ($EXAM_CODE)
- **Audience**: Network engineers preparing for the $EXAM_CODE exam
- **Platform**: EVE-NG on Dell Latitude 5540 (Intel/Windows)

## Project Structure

@conductor/product.md
@conductor/workflow.md

## Active Work

- See \`conductor/tracks.md\` for the current chapter plan
- See \`labs/\` for existing lab content
- Run \`git submodule status\` to check skills version

## Three-Phase Workflow

1. **Phase 1 — Plan:** Upload blueprint to \`blueprint/$EXAM_CODE/blueprint.md\`, then run \`exam-planner\` → \`specs/topic-plan.yaml\` + empty \`labs/<topic>/\` folders
2. **Phase 2 — Spec:** Run \`spec-creator\` per topic → \`labs/<topic>/spec.md\` + \`baseline.yaml\` (review after each)
3. **Phase 3 — Build:** Run \`lab-workbook-creator\` one lab at a time → workbook, configs, topology, scripts (review after each)

## Common Commands

\`\`\`bash
# Update skills to latest
git submodule update --remote .agent/skills
git add .agent/skills && git commit -m "chore: sync skills"

# Run lab setup
python3 labs/<topic>/lab-NN-<slug>/setup_lab.py --host <eve-ng-ip>

# Run tests
pytest tests/ -v
\`\`\`
EOF

echo "→ Copying prompt templates..."
if [ -d "$HUB_DIR/scaffolding/prompts" ]; then
  cp -r "$HUB_DIR/scaffolding/prompts/" "$TARGET_DIR/.prompts/"
fi

echo "→ Creating README.md..."
cat > "$TARGET_DIR/README.md" << EOF
# $CERT_NAME ($EXAM_CODE) Lab Series

A comprehensive set of hands-on labs for the $CERT_NAME ($EXAM_CODE) exam.

## Getting Started

1. Clone with submodules: \`git clone --recurse-submodules <repo-url>\`
2. Install Python dependencies: \`pip install -r requirements.txt\`
3. Set up EVE-NG (see \`.agent/skills/eve-ng/SKILL.md\` for constraints)
4. Navigate to a lab and follow the workbook

## Lab Chapters

| Chapter | Description |
|---------|-------------|
| *(Add chapters as they are built)* | |

## Development

Lab creation uses skills in \`.agent/skills/\`. See [CLAUDE.md](CLAUDE.md) for context.
EOF

echo "→ Linking skills into .claude/skills/ for Claude Code discovery..."
bash "$TARGET_DIR/.agent/skills/scripts/link-skills.sh" "$TARGET_DIR"

echo "→ Initial commit..."
git -C "$TARGET_DIR" add -A
git -C "$TARGET_DIR" commit -m "chore: bootstrap $PROJECT_NAME from cisco-lab-skills template"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ Done! Project: $TARGET_DIR"
echo ""
echo "  Next steps:"
echo "  1. Create GitHub repo and push: git remote add origin <url> && git push"
echo "  2. Upload blueprint to blueprint/$EXAM_CODE/blueprint.md, then run exam-planner"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
