# {{EXAM_SHORT}} ({{EXAM_CODE}}) Lab Series

> Hands-on labs for the {{EXAM_SHORT}} ({{EXAM_CODE}}) exam: *{{EXAM_NAME}}*.
> Built on {{PLATFORM}} using the [cisco-lab-skills](.agent/skills/) toolkit.

**For current build progress, see [`STATUS.md`](STATUS.md).**

## At a Glance

| | |
|---|---|
| **Exam** | {{EXAM_SHORT}} — {{EXAM_NAME}} |
| **Code** | {{EXAM_CODE}} |
| **Blueprint** | [`blueprint/{{EXAM_CODE}}/blueprint.md`](blueprint/{{EXAM_CODE}}/blueprint.md) |
| **Topics** | {{TOPIC_COUNT}} (see [`specs/topic-plan.yaml`](specs/topic-plan.yaml)) |
| **Total labs (planned)** | ~{{TOTAL_LABS}} |
| **Platform** | {{PLATFORM}} |
| **Skill toolkit** | [`.agent/skills/`](.agent/skills/) (git submodule) |

## Quick Start

```bash
git clone --recurse-submodules <repo-url>
cd {{REPO_NAME}}
pip install -r requirements.txt
```

Run the reference lab to verify your EVE-NG setup:

```bash
cd labs/{{REFERENCE_LAB}}/
python setup_lab.py --host <eve-ng-ip>
# then follow workbook.md
```

> First time? Read [`labs/{{REFERENCE_LAB}}/README.md`](labs/{{REFERENCE_LAB}}/) for a full walkthrough.

## Repository Layout

```
{{REPO_NAME}}/
├── blueprint/{{EXAM_CODE}}/    Exam blueprint (source of truth for objectives)
├── specs/topic-plan.yaml       Topic breakdown + build order (Phase 1 output)
├── labs/<topic>/               Per-topic specs (Phase 2) and lab builds (Phase 3)
│   ├── spec.md                 Topic spec — progression and coverage
│   ├── baseline.yaml           Topology + IP plan + lab definitions
│   └── lab-NN-<slug>/          Built lab: workbook, configs, topology, scripts
├── conductor/                  Project workflow docs (product, tracks, workflow)
├── memory/                     Cross-session notes and progress logs
├── tests/                      Repo-level tests
└── .agent/skills/              Lab-generation toolkit (git submodule)
```

## How Labs Are Built

Every topic moves through three sequential phases. The skill toolkit at `.agent/skills/` automates each one.

| Phase | Skill | Input → Output |
|-------|-------|----------------|
| **1. Plan** | `exam-planner` | Blueprint → `specs/topic-plan.yaml` |
| **2. Spec** | `spec-creator` | Topic → `labs/<topic>/spec.md` + `baseline.yaml` |
| **3. Build** | `lab-builder` | Spec → workbook, configs, topology, fault-injection scripts |

Each phase has a review gate — outputs are inspected before the next phase begins.
See [`.agent/skills/README.md`](.agent/skills/) for the full skill catalogue and design.

## Commands

| Command | Phase | Purpose |
|---------|-------|---------|
| `/plan-exam` | 1 | Read blueprint, create `topic-plan.yaml` |
| `/create-spec <topic>` | 2 | Generate `spec.md` + `baseline.yaml` for one topic |
| `/build-lab <topic>/<lab-id>` | 3 | Build a single lab |
| `/build-topic <topic>` | 3 | Build all labs for a topic with review gates |
| `/build-capstone` | 3 | Multi-domain capstone spanning topics |
| `/tag-lab <topic>/<lab-id>` | — | Stamp lab `meta.yaml` with provenance |
| `/sync-skills` | — | Pull latest `.agent/skills/` from upstream |
| `/project-status` | — | Regenerate [`STATUS.md`](STATUS.md) |

For the current state of the project (which labs are built, what's next), run `/project-status` or read [`STATUS.md`](STATUS.md).

## Prerequisites

- Python 3.10+ with `pip install -r requirements.txt`
- EVE-NG accessible on your network (see [`.agent/skills/eve-ng/SKILL.md`](.agent/skills/eve-ng/) for image and hardware constraints)
- Cisco IOSv / IOSvL2 / XRv 9000 images loaded in EVE-NG (per topic requirements in `baseline.yaml`)

## Working on This Project

| If you want to… | Read |
|----|----|
| Understand conventions and project context | [`CLAUDE.md`](CLAUDE.md) |
| See current chapter plan / track | [`conductor/tracks.md`](conductor/tracks.md) |
| See live build progress | [`STATUS.md`](STATUS.md) |
| Learn how the skill toolkit works | [`.agent/skills/README.md`](.agent/skills/) |
| Read the exam blueprint | [`blueprint/{{EXAM_CODE}}/blueprint.md`](blueprint/{{EXAM_CODE}}/blueprint.md) |

---

*This README is generated from `.agent/skills/scaffolding/README_template.md` at project bootstrap. Keep it stable — put live status in [`STATUS.md`](STATUS.md) instead.*
