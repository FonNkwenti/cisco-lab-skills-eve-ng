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

### Fixed: IP addressing not explicitly documented in workbook Section 3

**What changed:** `lab-assembler/SKILL.md` now requires two additional tables in Section 3
of every workbook:

1. **Loopback Address table** — placed immediately after the Device Inventory table.
   Lists every active device's loopback interface(s), address/prefix, and purpose
   (router-id, peering source, prefix source, etc.).

2. **Advertised Prefixes table** — placed after the cabling table. Lists every prefix the
   lab explicitly injects into a routing protocol via a `network` statement or redistribution.
   Omit for pure IGP underlay labs with no advertised user-space prefixes.

**Why:** Previously the only IP reference in the workbook was the cabling table (transit
subnets only) and the ASCII topology diagram (loopback last-octets only). A reviewer or
student had to cross-reference `baseline.yaml` or the solution configs to find all
addresses — there was no single place to verify the full IP plan at a glance.

**`memory/lab-standards.md` updated:** Section 3 row now lists all five required tables.

**Affected labs:** Any lab built before this fix is missing the Loopback Address and
Advertised Prefixes tables in Section 3. Add them manually or regenerate the workbook.

---

### Fixed: drawio SKILL.md vs reference file discrepancies (cisco19 shapes, rounded zones)

**What changed:** Two visual style mismatches between `drawio/SKILL.md` and the canonical
`drawio/references/style-guide-reference.drawio` were found and corrected.

1. **Device icons**: SKILL.md §4.2 had old `mxgraph.cisco.routers.router` shapes (dark-blue
   filled silhouettes). The reference uses `mxgraph.cisco19.rect;prIcon=router` (white fill,
   teal border, modern Cisco19 library). All style strings, XML snippets, and the validation
   checklist updated.

2. **Zone/domain shapes**: SKILL.md §4.10.2 specified `ellipse` (ovals). The reference uses
   `rounded=1;arcSize=5` (near-rectangular boxes with barely-softened corners). All zone
   style strings and XML snippets updated.

**Additional:** Canvas background `#1a1a2e` now explicit in §4.1; label approach in §4.3 updated
to embedded HTML in device cell `value` via `labelPosition=` attributes (matching the reference
pattern, no separate label cells needed).

**Affected labs:** Any `topology.drawio` generated before this fix uses the old shapes. Regenerate
via `/diagram <topic>/<lab-id>` after running `git submodule update --remote .agent/skills`.

---

### Migrated: fault-injector and lab-assembler to eve_ng.py shared library

**What changed:** Replaced hardcoded `EVE_NG_HOST` / `CONSOLE_PORT` constants in all
fault-injection and `setup_lab.py` templates with runtime port discovery via `discover_ports()`
from the `common/tools/eve_ng.py` shared library.

**fault-injector:**
- All three `inject_scenario_0N_template.py` files rewritten: `require_host()`, `discover_ports()`,
  `connect_node()`, pre-flight checks, structured exit codes (0/2/3/4)
- `apply_solution_template.py` rewritten: reads `solutions/[Device].cfg` via `discover_ports()`,
  supports `--reset` flag (`soft_reset_device()`: issues `default interface` + `no router` to clear
  running-config state without a reload) and `--node` to target a single device
- `README_template.md` updated: `--host <eve-ng-ip>` in all commands, exit codes table,
  `.unl` import prerequisite note
- `SKILL.md` updated: Step 1 documents runtime port discovery, Script Structure Reference
  updated to `eve_ng.py` pattern, Exit Codes table added, validate checklist updated

**lab-assembler:**
- `setup_lab_template.py` rewritten: uses `discover_ports()` (`parents[1]` depth to `labs/`)
- `SKILL.md` updated with six additions:
  - Section 3: Device Inventory table format required
  - Section 4: IS/NOT pre-loaded format (concept-level, no IOS syntax)
  - Section 11: Appendix exit codes table added to TOC and section list
  - `meta.yaml` schema: `exam` and `devices` fields added
  - Step 5b: `topology/README.md` generation (EVE-NG import/export docs)
  - Step 6b: root `README.md` quick-reference card generation

**Constraint enforced:** `--lab-path` in all scripts is for REST API port discovery against
an ALREADY-IMPORTED, ALREADY-RUNNING lab. It does not generate `.unl` files.

**Affected projects:** After `git submodule update --remote .agent/skills`, delete and rebuild
any in-progress labs that used the old hardcoded-port pattern (e.g. ccnp-spri ospf/lab-00).

### Renamed
- `/status` command → `/project-status` to avoid conflict with Claude Code's built-in `/status` command.
- `lab-workbook-creator/` → `lab-assembler/`. The skill always produced the full lab
  package (workbook, initial-configs, solutions, topology, setup_lab.py, meta.yaml,
  fault-injection scripts), not just the workbook. "Assembler" reflects that; "builder"
  is reserved for the topic-level orchestrator (`lab-builder`).

### Added
- `scaffolding/tasks/` — two starter templates now generated into every bootstrapped repo:
  - `tasks/lessons.md` — exam-specific correction log; new entries at top; reviewed each session
  - `tasks/todo.md` — session scratchpad only (current plan + outstanding decisions);
    not a build tracker — use `/project-status` or `README.md § Lab Chapters` for that
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
