# Lab Standards (DeepSeek Standard)

The canonical quality bar for all labs in this system.

## Required Files Per Lab

```
labs/<topic>/lab-NN-<slug>/
├── workbook.md
├── initial-configs/   R1.cfg, R2.cfg, ...
├── solutions/         R1.cfg, R2.cfg, ...
├── topology.drawio
├── setup_lab.py
└── scripts/fault-injection/
    ├── README.md
    ├── inject_scenario_01.py
    ├── inject_scenario_02.py
    ├── inject_scenario_03.py
    └── apply_solution.py
```

## Workbook Sections (Required)

| # | Section | Notes |
|---|---------|-------|
| 1 | Concepts & Skills Covered | |
| 2 | Topology & Scenario | Narrative enterprise context |
| 3 | Hardware & Environment Specifications | Must include: Device Inventory table, Loopback Address table, cabling table, Advertised Prefixes table (when lab configures network statements), Console Access Table. Console ports are dynamic — populate from EVE-NG web UI after lab creation. Format: `telnet <eve-ng-ip> <port>` |
| 4 | Base Configuration | |
| 5 | Lab Challenge: Core Implementation | Challenge-first, no step hints |
| 6 | Verification & Analysis | |
| 7 | Verification Cheatsheet | |
| 8 | Solutions (Spoiler Alert!) | All in `<details>` blocks |
| 9 | Troubleshooting Scenarios | Min 3, each with fault-injection reference |
| 10 | Lab Completion Checklist | |

## Voice & Tone

- **Narrative-first**: "As the lead network engineer for Acme Corp, you must..."
- **Cisco official terminology**: "Feasible Successor", "Administrative Distance"
- **Challenge-first**: No step-by-step hints until the hidden solution section

## Task Formatting (Section 5) — REQUIRED

Section 5 uses **Tasks**, not Objectives. Each task uses this exact layout:

```markdown
### Task N: [Descriptive Title]

- [Step — what to configure. Named values (key names, AS numbers, subnets) are fine. No raw IOS command syntax.]
- [Additional steps.]

**Verification:** `show ...` command(s) and expected state.

---
```

**No raw IOS/XR command syntax in task steps or in the Section 4 "NOT pre-loaded" list.**
Named parameters (object names, AS numbers, algorithm names, subnet addresses, keyword flags
like `summary-only`) are allowed — they provide precision without handing over the command.
The prohibition covers all CLI forms: global config, sub-commands, route-map clauses, and
exec-mode operational commands (`clear`, `debug`). The `**Verification:**` line is the only
place CLI commands appear in Section 5 (including soft-resets needed to trigger evaluation).

- ✅ "Create a key-chain named OSPF_AUTH with key ID 1 and a strong key-string."
- ❌ "Run `key chain OSPF_AUTH` / `key 1` / `key-string <value>`."
- ✅ "Enable EIGRP in Autonomous System 100 on all three routers."
- ❌ "Configure `router eigrp 100` on R1, R2, and R3."
- ✅ "Install a null-route for 172.16.0.0/16 pointing to Null0 as the aggregate anchor."
- ❌ "Run `ip route 172.16.0.0 255.255.0.0 Null0`."
- ✅ "Originate the 172.16.0.0/16 aggregate on R1. Do not use `summary-only`."
- ❌ "Add `aggregate-address 172.16.0.0 255.255.0.0` under the BGP address-family."
- ✅ "Create route-map `R1_OUT` seq 10: match prefix-list `PFX_EXACT` → prepend AS 65100 three times."
- ❌ "Under seq 10: `match ip address prefix-list PFX_EXACT` / `set as-path prepend 65100 65100 65100`."
- ✅ "Apply `R1_OUT` outbound on R1's R4 neighbor."
- ❌ "Add `neighbor 10.1.14.4 route-map R1_OUT out` under the BGP address-family."

## Cheatsheet Formatting (Section 7) — REQUIRED

Never put all commands in one monolithic code block. Always use named subsections:

1. One subsection per logical command group — each with a syntax skeleton code block followed by a `Command | Purpose` table
2. Verification commands in a `Command | What to Look For` table (never a code block)
3. End with a mask/wildcard reference table and a failure-causes table

Reference `lab-assembler/SKILL.md` Section 5/7 format blocks for the exact template.

## Diagram Standards

- White connection lines (`strokeColor=#FFFFFF`) — never black
- Cisco shape library icons (`mxgraph.cisco.routers.router`)
- Device label: hostname + role + loopback IP
- IP last-octet labels near each interface
- Legend box: black fill, white text, bottom-right

## Config Chaining Rules

- Lab 00 (first progressive) `initial-configs/` = IP addressing only from `baseline.yaml`
- Lab N (progressive, N > 0) `initial-configs/` = Lab (N-1) `solutions/`
- Standalone labs `initial-configs/` = IP addressing only from `baseline.yaml`
- Capstone I + II `initial-configs/` = IP addressing only from `baseline.yaml` (clean slate)
- **Never remove** a config command between progressive labs — only add

## Troubleshooting Scenario Requirements

Each of the 3+ scenarios must have:
1. Problem Statement (observable symptoms)
2. Mission (what to diagnose/fix)
3. Success Criteria (measurable checkboxes)
4. Solution in `<details>` spoiler block
5. Reference to `scripts/fault-injection/inject_scenario_0N.py`
