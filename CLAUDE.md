---
description: Foundation CLAUDE.md for the cisco-lab-skills submodule — shared context loaded automatically by Pi in every exam repo that mounts this submodule at .agent/skills/.
---

# cisco-lab-skills

Foundation skill library for Cisco certification lab generation. Mounted as a git submodule
at `.agent/skills/` inside every exam-specific lab repo (e.g., ENARSI, ENCOR, SPCOR).

Fix a skill once here and pull the update into every exam repo via `git submodule update`.

## Before Any Session

Always read at the start of a lab generation session:
1. `memory/progress.md` — current chapter and lab completion status
2. `LESSONS_LEARNED.md` — bugs and patterns from prior development

## Branching

See `BRANCHING.md` for the full rule. Short version:

- **`main` is a published API.** Every downstream exam repo (CCNP SPRI,
  ENARSI, ENCOR, SPCOR, ...) inherits it on `git submodule update --remote`.
- **Default to a branch for speculative or untested changes.** This is
  intentionally the inverse of the trunk-default rule used in exam repos —
  the asymmetry reflects the higher blast radius here.
- **Direct-to-`main` is OK for:** typo/doc fixes, `LESSONS_LEARNED.md`
  entries, `ios-compatibility.yaml` updates, mature skill changes already
  validated downstream.
- **Use a branch for:** new builder behavior, skill-step changes, schema
  changes, anything cross-cutting. Match the parent exam repo's branch name
  so the work is coordinated across both repos.
- **`experiment/` branches require a kill-date in the first commit message.**

## Three-Phase Workflow

1. **exam-planner** — reads full blueprint, creates `topic-plan.yaml` + empty `labs/<topic>/` folders
2. **spec-creator** — creates `spec.md` + `baseline.yaml` per topic (review after each)
3. **lab-builder** — topic-level orchestrator that invokes `lab-assembler` for each lab, pausing for review between them. Invoke `lab-assembler` directly to build one lab without the loop.

Blueprint location: `blueprint/<exam-code>/blueprint.md`

## How Skills Work

Skills live at `.agent/skills/<skill-name>/SKILL.md`. Never discover them by listing
directories — read the specific SKILL.md when a step calls for it.

Skills that generate large output are dispatched as subagents to protect main context:

| Skill | Invoke as |
|---|---|
| `drawio` | Subagent (Step 5 in lab-assembler) |
| `fault-injector` | Subagent (Step 7 in lab-assembler) |
| All other skills | Inline (read SKILL.md, follow instructions) |

## Exam-Agnostic Design

Skills in this repo are platform and exam agnostic. Exam-specific content (blueprint file,
topic-plan.yaml, spec.md, baseline.yaml, labs) lives in the exam repo, not here. When a skill
references a specific exam (e.g., "ENARSI" or "ENCOR") treat it as an example — apply to the
actual exam in context.

## Platform Reference

`eve-ng/SKILL.md` — **Active platform.** EVE-NG constraints (Intel/Windows, QEMU/IOL images: IOSv, IOSvL2, CSR1000v, XRv 9000, NX-OSv, ASAv).
`gns3/SKILL.md` — **DEPRECATED.** GNS3/Dynamips archive (Apple Silicon, c7200/c3725 only). Read-only reference.
