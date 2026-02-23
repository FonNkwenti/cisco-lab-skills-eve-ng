# cisco-lab-skills

AI agent skills for Cisco certification lab generation. Used as a **git submodule** at `.agent/skills/` inside every certification lab project.

One repo, shared across all exam series (ENARSI, SPCOR, ENCOR, etc.). Fix a skill once — pull the update into every exam repo.

## Skills

| Skill | What It Does |
|-------|-------------|
| `chapter-topics-creator` | Plans a chapter — generates `baseline.yaml` + backfills `chapter-spec.md` |
| `chapter-builder` | Generates all labs in a chapter with config chaining |
| `lab-workbook-creator` | Generates a single lab (workbook, configs, topology, scripts) |
| `fault-injector` | Creates automated Netmiko fault injection scripts |
| `mega-capstone-creator` | Generates the multi-domain final capstone spanning all chapters |
| `drawio` | Visual style guide + `generate_topo.py` for topology diagrams |
| `gns3` | Apple Silicon GNS3 constraints and hardware selection reference |
| `cisco-troubleshooting-1` | Structured 4-phase network troubleshooting methodology |

## Structure

```
cisco-lab-skills/              ← submodule root (mounted at .agent/skills/)
├── chapter-topics-creator/
│   └── SKILL.md
├── chapter-builder/
│   └── SKILL.md
├── lab-workbook-creator/
│   ├── SKILL.md
│   └── assets/
│       ├── setup_lab_template.py
│       └── troubleshooting_scenarios_template.md
├── fault-injector/
│   ├── SKILL.md
│   └── assets/
│       ├── inject_scenario_0N_template.py
│       ├── apply_solution_template.py
│       └── README_template.md
├── mega-capstone-creator/
│   └── SKILL.md
├── drawio/
│   ├── SKILL.md
│   └── scripts/generate_topo.py
├── gns3/
│   └── SKILL.md
├── cisco-troubleshooting-1/
│   ├── SKILL.md
│   ├── evals/evals.json
│   └── references/
│       ├── diagnostic-commands.md
│       ├── methodologies.md
│       └── resolution-report-template.md
└── scaffolding/
    ├── requirements.txt
    └── labs-common/tools/   (shared Python utilities)
```

## Adding to a new exam repo

```bash
cd /path/to/your-exam-repo
git submodule add file:///Users/fon/Antigravity/cisco-lab-skills .agent/skills
git commit -m "chore: add cisco-lab-skills submodule"
```

> **Using GitHub?** Replace the `file://` URL with your GitHub remote URL after pushing this repo.

## Cloning an exam repo (pulls skills automatically)

```bash
git clone --recurse-submodules /path/to/exam-repo
# OR if already cloned without --recurse-submodules:
git submodule update --init
```

## Updating a skill

### Step 1 — Edit the skill in this repo

```bash
cd /Users/fon/Antigravity/cisco-lab-skills
# edit chapter-topics-creator/SKILL.md, lab-workbook-creator/SKILL.md, etc.
git add .
git commit -m "fix(lab-workbook-creator): capstone clean-slate initial-config logic"
```

### Step 2 — Pull the update into each exam repo

```bash
# ENARSI
cd /Users/fon/Antigravity/ccnp-enarsi-labs-cc
git submodule update --remote .agent/skills
git add .agent/skills
git commit -m "chore: update skills submodule"

# SPCOR (once created)
cd /Users/fon/Antigravity/ccnp-spcor-labs
git submodule update --remote .agent/skills
git add .agent/skills
git commit -m "chore: update skills submodule"
```

Each exam repo pins skills to a **specific commit**. `git submodule update --remote` advances the pin to the latest. This means:
- You can update ENARSI skills without touching SPCOR until you're ready
- If an update breaks something, the other exam repos are unaffected
- `git log .agent/skills` in any exam repo shows the full skills change history

## Checking which commit each repo uses

```bash
# Inside any exam repo
git submodule status
# Output: abc1234 .agent/skills (v1.2.0)
#          ↑ commit hash pinned by this exam repo
```

## Workflow summary

```
cisco-lab-skills (this repo)
    │
    ├── .agent/skills/ ←── ccnp-enarsi-labs-cc  (pinned to commit A)
    ├── .agent/skills/ ←── ccnp-spcor-labs       (pinned to commit A or B)
    └── .agent/skills/ ←── ccnp-labs-template    (pinned to commit A)

Fix a bug in lab-workbook-creator:
  1. Commit fix here          → commit B
  2. Update ENARSI            → pins to commit B
  3. Update SPCOR when ready  → pins to commit B
```

## Scaffolding

`scaffolding/` contains shared Python tools used by generated lab scripts:
- `lab_utils.py` — Netmiko connection helpers
- `fault_utils.py` — fault injection / restoration helpers
- `requirements.txt` — Python dependencies (netmiko, PyYAML, etc.)
