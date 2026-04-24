# Changelog

All notable changes to the cisco-lab-skills hub are documented here.

---

## [2.1.0] — 2026-04-22

### Automated Claude Code skill discovery

**What changed:** Skills under `.agent/skills/<name>/SKILL.md` are now linked into
`.claude/skills/<name>` so Claude Code can discover them as user-invocable skills.

**New scripts:**
- `scripts/link-skills.sh` — POSIX bash; uses directory junctions on Git Bash / MSYS
  (no admin), symlinks on Linux/macOS. Idempotent.
- `scripts/link-skills.ps1` — PowerShell equivalent using `New-Item -ItemType Junction`.

**Bootstrap integration:**
- `bootstrap.sh` / `bootstrap.ps1` invoke the link script after submodule setup so every
  new exam repo has skills wired up before the initial commit.
- `scaffolding/gitignore.template` now excludes `.claude/skills/` (derived content).

**For existing exam repos:** run `.agent/skills/scripts/link-skills.sh` once, then add
`.claude/skills/` to the repo's `.gitignore`.

---

## [Unreleased]

### Renamed
- `/status` command → `/project-status` to avoid conflict with Claude Code's built-in `/status` command.
- `lab-workbook-creator/` → `lab-assembler/`. The skill always produced the full lab
  package (workbook, initial-configs, solutions, topology, setup_lab.py, meta.yaml,
  fault-injection scripts), not just the workbook. "Assembler" reflects that; "builder"
  is reserved for the topic-level orchestrator (`lab-builder`).

### Added
- `scaffolding/.claude/commands/` — project-scoped slash commands copied into every
  bootstrapped exam repo: `/plan-exam`, `/create-spec`, `/build-lab`, `/build-topic`,
  `/build-capstone`, `/tag-lab`, `/sync-skills`, `/project-status`.
- README auto-update: `plan-exam`, `create-spec`, `build-lab`, `build-topic` commands now
  maintain a `## Lab Chapters` section in the exam repo README. Uses
  `<!-- lab-index-start -->` / `<!-- lab-index-end -->` markers as anchors. Topics appear
  after Phase 1; unchecked lab checklists appear after Phase 2; checkboxes are ticked as
  each lab is approved in Phase 3.
- Three additional supporting commands promoted from ccnp-encor-labs to the hub scaffolding
  (now included in every bootstrapped repo):
  - `/diagram <topic>/<lab-id>` — regenerate a topology diagram independently via `drawio` skill
  - `/inject-faults <topic>/<lab-id>` — regenerate fault-injection scripts via `fault-injector` skill
  - `/troubleshoot <topic>/<lab-id>` — run structured 4-phase diagnosis via `cisco-troubleshooting-1` skill
  - All three use the same advisory-gating pattern as the core 8 commands.

### Migration for existing exam repos
After `git submodule update --remote .agent/skills`, grep each exam repo for
`lab-workbook-creator` and rewrite to `lab-assembler`. Likely hits: `CLAUDE.md`,
any lab `meta.yaml` provenance blocks (the `skill:` field), `.prompts/*`.

---

## [2.0.0] — 2026-04-10

### Skill Restructure — Three-Phase Workflow

**What changed:** Introduced a three-phase lab generation workflow with exam-wide planning,
per-topic spec creation, and pause-and-review lab building.

**New skills:**
- `exam-planner` — reads full blueprint from `blueprint/<exam-code>/blueprint.md`, produces
  `specs/topic-plan.yaml` with technology-based topic breakdown and lab count estimates
- `capstone-creator` scope planned but deferred; per-topic capstones remain in spec-creator

**Renamed skills (directory and skill name):**
- `chapter-topics-creator/` → `spec-creator/` — now reads from `topic-plan.yaml` instead of
  requiring manual `chapter-spec.md`; generates `spec.md` + `baseline.yaml` per topic
- `chapter-builder/` → `lab-builder/` — default is now pause-and-review (not batch);
  pauses after each lab for user approval

**Breaking changes:**
- `baseline.yaml` schema: labs are zero-indexed (`number: 0`), new `folder` field with
  descriptive slugs (`lab-00-introduction`), new `blueprint_refs` field per lab
- Lab directory naming: `lab-NN-[name]/` replaces `labNN/` (e.g., `lab-00-introduction/`
  instead of `lab01/`)
- Blueprint input: now read from `blueprint/<exam-code>/blueprint.md` via exam-planner,
  not manually written into `chapter-spec.md`
- Exam repos using `chapter-spec.md` as the primary input must migrate to the
  `topic-plan.yaml` workflow

**Other changes:**
- `bootstrap.ps1` / `bootstrap.sh`: now scaffold `blueprint/`, `specs/`, `labs/` directories
- `memory/CLAUDE.md`: updated skill list and added three-phase workflow summary
- `memory/skills-index.md`: updated workflow diagram and platform selection table
- `memory/lab-standards.md`: config chaining rules updated for zero-indexed numbering
- EVE-NG inventory: added Linux Ubuntu Server 20.04 to installed images

**Why:** The previous workflow required users to manually write `chapter-spec.md` per chapter
before any labs could be generated. The new workflow reads the full exam blueprint once and
plans the entire exam, reducing manual effort and ensuring complete blueprint coverage.

**Affected projects:** All exam repos need `git submodule update --remote .agent/skills`
and should adopt the new three-phase workflow. Existing labs generated with v1.x continue
to work but new labs should use the v2.0 workflow.

---

## [1.0.0] — 2026-02-20

### Initial Release — Extracted from ccnp-encor-labs-conductor

**Skills included:**
- `chapter-builder` — Multi-lab generation with config chaining
- `chapter-topics-creator` — Chapter planning with `baseline.yaml` generation
- `lab-workbook-creator` — Full lab artifact generation
- `fault-injector` — Automated troubleshooting fault script generation
- `drawio` — Visual style guide + `generate_topo.py` automation
- `gns3` — Apple Silicon GNS3 constraints and hardware reference
- `cisco-troubleshooting-1` — Structured 4-phase troubleshooting methodology

**Memory system introduced:**
- `memory/CLAUDE.md` — Shared Claude Code context (Tier 2)
- `memory/skills-index.md` — Quick reference for all skills
- `memory/gns3-constraints.md` — Hardware platform facts
- `memory/lab-standards.md` — DeepSeek Standard specification

**Key bugs fixed during ENCOR development (see LESSONS_LEARNED.md):**
- Python multiline strings causing `SyntaxError: unterminated string literal`
- Draw.io bypass links crossing through intermediate devices
- GNS3 tunnel overlays requiring top-center exit points to arc correctly
- Netmiko requiring explicit empty string fields (not omitted)

---

<!-- Template for future entries:

## [X.Y.Z] — YYYY-MM-DD

### Skills changed: [skill-name]

**What changed**: Brief description
**Why**: Reason
**Affected projects**: Update submodule ref in all cert repos

-->
