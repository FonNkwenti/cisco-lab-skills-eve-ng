# cisco-lab-skills

Foundation skill library for Cisco certification lab generation. Mounted as a git submodule
at `.agent/skills/` inside every exam-specific lab repo (e.g., ENARSI, ENCOR, SPCOR).

Fix a skill once here and pull the update into every exam repo via `git submodule update`.

## Before Any Session

Always read at the start of a lab generation session:
1. `memory/progress.md` — current chapter and lab completion status
2. `LESSONS_LEARNED.md` — bugs and patterns from prior development

## Three-Phase Workflow

1. **exam-planner** — reads full blueprint, creates `topic-plan.yaml` + empty `labs/<topic>/` folders
2. **spec-creator** (in `chapter-topics-creator/`) — creates `spec.md` + `baseline.yaml` per topic (review after each)
3. **lab-builder** (in `lab-workbook-creator/`) — builds one lab at a time from the spec (review after each)

Blueprint location: `blueprint/<exam-code>/blueprint.md`

## How Skills Work

Skills live at `.agent/skills/<skill-name>/SKILL.md`. Never discover them by listing
directories — read the specific SKILL.md when a step calls for it.

Skills that generate large output are dispatched as subagents to protect main context:

| Skill | Invoke as |
|---|---|
| `drawio` | Subagent (Step 5 in lab-workbook-creator) |
| `fault-injector` | Subagent (Step 7 in lab-workbook-creator) |
| All other skills | Inline (read SKILL.md, follow instructions) |

## Exam-Agnostic Design

Skills in this repo are platform and exam agnostic. Exam-specific content (blueprint bullets,
IP addressing plans, chapter-spec.md) lives in the exam repo, not here. When a skill
references a specific exam (e.g., "ENARSI") treat it as an example — apply to the actual
exam in context.

## Platform Reference

`eve-ng/SKILL.md` — **Active platform.** EVE-NG constraints (Intel/Windows, QEMU/IOL images: IOSv, IOSvL2, CSR1000v, XRv 9000, NX-OSv, ASAv).
`gns3/SKILL.md` — **DEPRECATED.** GNS3/Dynamips archive (Apple Silicon, c7200/c3725 only). Read-only reference.
