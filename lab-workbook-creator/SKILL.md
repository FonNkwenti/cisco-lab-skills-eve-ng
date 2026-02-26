---
name: lab-workbook-creator
description: Creates a complete CCNP ENARSI lab workbook, initial-configs, solutions, topology diagram, and setup_lab.py automation script for a single lab. Use when the user asks to "create a lab", "generate lab N", "build [technology] lab", "write a workbook", or when chapter-builder invokes it for each lab in a sequence.
---

# Lab Workbook Creator Skill

Converts a lab topic entry from `baseline.yaml` into a full DeepSeek Standard lab package. Prioritises theoretical context, copy-pasteable Cisco IOS configurations, and GNS3 automation scripts.

-# Instructions

--# Step 1: Read Inputs

Before generating anything, read:
1. `labs/[chapter]/baseline.yaml` — active devices, IPs, console ports, lab objectives
2. Check `baseline.yaml labs[N].type` — if `capstone_i` or `capstone_ii`, set `clean_slate: true` for this lab
3. Previous lab's `solutions/` (if this is not Lab 01 AND `clean_slate` is not true) — becomes this lab's `initial-configs/`
4. `specs/[chapter]/chapter-spec.md` — exam bullet context for the lab's objectives

Identify which devices are active for this lab number from `baseline.yaml labs[N].devices`.

--# Step 2: Generate workbook.md

**Table of Contents (required):** Immediately after the workbook title line, insert a TOC block before Section 1. Use Markdown anchor links matching the exact section headings. Required format:

```markdown
## Table of Contents

1. [Concepts & Skills Covered](#1-concepts--skills-covered)
2. [Topology & Scenario](#2-topology--scenario)
3. [Hardware & Environment Specifications](#3-hardware--environment-specifications)
4. [Base Configuration](#4-base-configuration)
5. [Lab Challenge: Core Implementation](#5-lab-challenge-core-implementation)
6. [Verification & Analysis](#6-verification--analysis)
7. [Verification Cheatsheet](#7-verification-cheatsheet)
8. [Solutions (Spoiler Alert!)](#8-solutions-spoiler-alert)
9. [Troubleshooting Scenarios](#9-troubleshooting-scenarios)
10. [Lab Completion Checklist](#10-lab-completion-checklist)

---
```

Rules:
- TOC anchor slugs must match the actual section heading text (lowercase, spaces→hyphens, special chars stripped)
- For capstone labs: update Section 5 link text to match the actual heading (`Full Protocol Mastery` or `Comprehensive Troubleshooting`)
- The `---` horizontal rule after the TOC separates it from Section 1

Write a complete workbook with all required sections:

1. **Section 1 — Concepts & Skills Covered** — structured as follows:
   a. `**Exam Objective:**` line with blueprint bullet(s) and topic name
   b. One short intro paragraph (what the lab covers and why it matters)
   c. Named theory subsections (`### Topic`) — prose, IOS syntax blocks, reference tables
      - Minimum 3 subsections; depth mirrors labs 01/02 style
      - Explain the protocol concept, not just the commands
   d. `**Skills this lab develops:**` table — Skill | Description (2 columns)
2. **Topology & Scenario** — enterprise narrative framing the lab challenge
3. **Hardware & Environment Specifications** — cabling table, Console Access Table
4. **Base Configuration** — what is pre-configured in `initial-configs/`
5. **Lab Challenge: Core Implementation** — objectives for the student (see format below)
6. **Verification & Analysis** — expected `show` command outputs per objective, with inline `!` comments marking the specific lines or values the student must confirm
7. **Verification Cheatsheet** — quick-reference commands for the entire lab (see format below)
8. **Solutions (Spoiler Alert!)** — solution configs for lab objectives only, wrapped in `<details>` blocks
9. **Troubleshooting Scenarios** — fault injection workflow + symptom-based tickets with `<details>` spoilers
10. **Lab Completion Checklist** — two groups: Core Implementation and Troubleshooting

**Section 5 — Tasks format (REQUIRED):**

Section 5 contains Tasks, not Objectives. Each task uses this exact layout:

```markdown
### Task N: [Descriptive Title]

- [Step — what to configure or achieve. May include named values (key names, AS numbers,
  subnet addresses, algorithm names) but never raw IOS command syntax.]
- [Additional steps as needed.]
- [Sub-steps can use nested bullets for multi-part tasks.]

**Verification:** `show ...` command(s) that confirm the task is complete, plus the expected state.

---
```

Rules for task bullet points:
- Describe WHAT to configure in plain English. Named parameters (key-chain names, AS numbers, subnet values, algorithm names) are allowed — they provide necessary precision.
- **Never write raw IOS command syntax** in the task body. No `router eigrp 100`, no `key chain`, no `passive-interface`, no full CLI lines.
- The `**Verification:**` line at the end of each task MUST include the relevant `show` command(s) and the expected outcome. This is the only place where show commands appear in Section 5.

Examples:
- ✅ "Create a key-chain named OSPF_AUTH with key ID 1 and a strong key-string."
- ❌ "Run `key chain OSPF_AUTH` / `key 1` / `key-string <value>`."
- ✅ "Enable EIGRP in Autonomous System 100 on all three routers."
- ❌ "Configure `router eigrp 100` on R1, R2, and R3."
- ✅ **Verification:** "`show ip eigrp neighbors` must show two active neighbors on each router."

**Section 4 — Base Configuration "NOT pre-loaded" list:**

List concepts, not IOS syntax:
- ✅ "EIGRP routing process"
- ❌ "`router eigrp 100`"
- ✅ "Subnet advertisement"
- ❌ "`network` statements"

**Section 7 — Cheatsheet format (REQUIRED):**

The cheatsheet must be broken into named subsections — never one monolithic code block. Required structure:

```markdown
### [Group Name, e.g. "EIGRP Process Configuration"]

​```
[Minimal syntax skeleton showing command structure only]
​```

| Command | Purpose |
|---------|---------|
| `command syntax` | What it does |

### [Next Group, e.g. "Interface Controls"]

​```
[Syntax skeleton]
​```

| Command | Purpose |
|---------|---------|
| ... | ... |

> **Exam tip:** [One high-value exam callout per subsection where relevant]

### Verification Commands

| Command | What to Look For |
|---------|-----------------|
| `show ...` | What the student must confirm |

### Wildcard Mask Quick Reference

| Subnet Mask | Wildcard Mask | Common Use |
|-------------|---------------|------------|

### Common [Protocol] Failure Causes

| Symptom | Likely Cause |
|---------|-------------|
```

Rules:
- Configuration command groups each get: a syntax skeleton code block + a command/purpose table
- Verification commands always go in a `Command | What to Look For` table, never in a code block
- Every cheatsheet ends with a Wildcard/Mask reference table (if applicable) and a Failure Causes table

**Solutions section format (required):**
```markdown
## 8. Solutions (Spoiler Alert!)

> Try to complete the lab challenge without looking at these steps first!

### Objective 1: [Title]

<details>
<summary>Click to view [Device] Configuration</summary>

```bash
! R1
router eigrp ENARSI
 address-family ipv4 unicast autonomous-system 100
  ...
```
</details>

<details>
<summary>Click to view Verification Commands</summary>

```bash
show ip eigrp neighbors
show ip route eigrp
```
</details>
```

**Troubleshooting ticket format (required for each scenario in Section 8):**

Ticket headings MUST describe the **symptom** the student observes — never the fault type or target device. The fault identity is the answer and must only appear inside `<details>` spoiler blocks.

```markdown
### Ticket N — [Observable Symptom Description]

[1-2 sentence scenario context — what the student has been told]

**Success criteria:** [What must be true when fixed]

<details>
<summary>Click to view Diagnosis Steps</summary>
...
</details>

<details>
<summary>Click to view Fix</summary>
...
</details>
```

Examples of correct vs. incorrect headings:
- ❌ `Ticket 1: AS Number Mismatch (Target: R2)` — reveals fault and device
- ✅ `Ticket 1 — R2 Reports No EIGRP Neighbors` — describes symptom only
- ❌ `Scenario 2: Passive Interface on R1` — reveals fault and device
- ✅ `Ticket 2 — Branch-A Loses Reachability Through the Core` — describes impact

**Section 9 format (required):**

Section 9 opens with the inject/restore workflow, then lists each ticket. Each ticket includes its inject command inline so the student knows exactly which script to run without leaving the workbook.

```markdown
## 9. Troubleshooting Scenarios

Each ticket simulates a real-world fault. Inject the fault first, then
diagnose and fix using only show commands.

### Workflow

​```bash
python3 setup_lab.py                                   # reset to known-good
python3 scripts/fault-injection/inject_scenario_01.py  # Ticket 1
python3 scripts/fault-injection/apply_solution.py      # restore
​```

---

### Ticket N — [Observable Symptom]

[1-2 sentence scenario context]

**Inject:** `python3 scripts/fault-injection/inject_scenario_0N.py`

**Success criteria:** [What must be true when fixed]

<details>
<summary>Click to view Diagnosis Steps</summary>
...
</details>

<details>
<summary>Click to view Fix</summary>
...
</details>
```

**`scripts/fault-injection/README.md` format (ops-only — no challenge descriptions):**

The README must only contain: prerequisites, run commands, and a restore command. It must NOT describe what each script injects. Reference `workbook.md` for the challenge. Students discover the fault by running the script and troubleshooting, not by reading the README.

```markdown
# Fault Injection — [Chapter] Lab NN

Each script injects one fault. Work through the corresponding ticket in
`workbook.md` Section 8 before looking at the solution.

## Prerequisites
...

## Inject a Fault
python3 inject_scenario_01.py   # Ticket 1
python3 inject_scenario_02.py   # Ticket 2
python3 inject_scenario_03.py   # Ticket 3

## Restore
python3 apply_solution.py
```

**ASCII Topology Diagram standard (required in Section 2):**

Use Unicode box-drawing characters. Every diagram must include:
- Device box: `┌─┐│└─┘` with hostname, role, and Loopback0 IP inside
- Interface name **and** full IP/mask labeled on each link segment (local side above, remote side below the gap)
- Subnet label on horizontal bottom links
- Do NOT use `/`, `\`, or plain `-` lines — use `│` for vertical links and `─` inside boxes only

Chain (linear) example:
```
                    ┌─────────────────┐
                    │       R1        │
                    │   (Hub Router)  │
                    │ Lo0: 10.0.0.1   │
                    └───────┬─────────┘
                            │ Fa0/0
                            │ 10.12.0.1/30
                            │
                            │ 10.12.0.2/30
                            │ Fa0/0
                    ┌───────┴─────────┐
                    │       R2        │
                    │ (Branch Router) │
                    │ Lo0: 10.0.0.2   │
                    └─────────────────┘
```

Triangle (hub + two branches) example:
```
              ┌─────────────────────────┐
              │           R1            │
              │      (Hub / Core)       │
              │   Lo0: 10.0.0.1/32      │
              └──────┬───────────┬──────┘
           Fa0/0     │           │     Fa1/0
     10.12.0.1/30    │           │   10.13.0.1/30
                     │           │
     10.12.0.2/30    │           │   10.13.0.2/30
           Fa0/0     │           │     Fa0/0
     ┌───────────────┘           └───────────────┐
     │                                           │
┌────┴──────────────┐           ┌────────────────┴────┐
│       R2          │           │       R3            │
│   (Branch A)      │           │   (Branch B)        │
│ Lo0: 10.0.0.2/32  │           │ Lo0: 10.0.0.3/32    │
└─────────┬─────────┘           └─────────┬───────────┘
      Fa0/1│                              │Fa0/1
10.23.0.1/30│                            │10.23.0.2/30
            └────────────────────────────┘
                      10.23.0.0/30
```

**Verification & Analysis format (required in Section 6):**

Every verification code block must use inline `!` comments to mark the exact line(s) or value(s) the student must confirm. Do not rely on prose descriptions alone.

```bash
R1# show ip eigrp neighbors
EIGRP-IPv4 Neighbors for AS(100)
H   Address         Interface       Hold  Uptime   SRTT   RTO  Q  Seq
                                   (sec)           (ms)       Cnt Num
0   10.12.0.2       Fa0/0             12  00:01:43   10   200  0  5   ! ← R2 must appear here
1   10.13.0.2       Fa1/0             11  00:01:40   12   200  0  4   ! ← R3 must appear here

R1# show ip route eigrp
D    10.2.0.0/24 [90/156160] via 10.12.0.2, 00:01:43, Fa0/0   ! ← AD=90, metric correct
D    10.3.0.0/24 [90/156160] via 10.13.0.2, 00:01:40, Fa1/0   ! ← AD=90, metric correct
```

**Console Access Table format (required in Section 3):**

| Device | Port | Connection Command |
|--------|------|--------------------|
| R1 | 5001 | `telnet 127.0.0.1 5001` |
| R2 | 5002 | `telnet 127.0.0.1 5002` |

--# Step 3: Generate initial-configs/

- **Lab 01:** Generate base IP addressing from `baseline.yaml core_topology` (IP config only — no routing protocol config).
- **Lab N (N > 1, not capstone):** Copy exactly from Lab (N-1) `solutions/`. Do not modify.
- **Capstone I or Capstone II (`clean_slate: true`):** Generate from `baseline.yaml core_topology` IP addressing only — do NOT copy previous lab solutions. All routing protocol config is absent; the student configures everything from scratch.
- One `.cfg` file per active device, named `[Device].cfg`.

**Capstone workbook Section 5 format:**

For `capstone_i`, Section 5 heading and opening must be:
```markdown
## 5. Lab Challenge: Full Protocol Mastery

> This is a capstone lab. No step-by-step guidance is provided.
> Configure the complete [Protocol] solution from scratch — IP addressing is pre-configured; everything else is yours to build.
> All blueprint bullets for this chapter must be addressed.
```

For `capstone_ii`, Section 5 heading and opening must be:
```markdown
## 5. Lab Challenge: Comprehensive Troubleshooting

> This is a capstone lab. The network is pre-broken.
> Diagnose and resolve 5+ concurrent faults spanning all blueprint bullets.
> No step-by-step guidance is provided — work from symptoms only.
```

--# Step 4: Generate solutions/

Complete IOS configurations for every active device, implementing all lab objectives. One `.cfg` file per device.

--# Step 5: Generate topology.drawio

**STOP. Before writing a single line of XML, read `.agent/skills/drawio/SKILL.md` §4.2–§4.7 in full.**

Use the §4.7 reference XML snippets as your starting template. Never write topology XML from scratch — always copy and adapt the reference snippets for Device Icon, Device Label, White Connection Line, IP Last Octet Label, and Legend Box.

**Mandatory pre-write checklist (verify against drawio/SKILL.md before writing):**
- [ ] Device shape: `shape=mxgraph.cisco.routers.router;fillColor=#036897;strokeColor=#ffffff;strokeWidth=2;` — not a rectangle
- [ ] Device labels: separate `text` cells positioned on the empty side of the icon (§4.3.1) — not embedded in the router cell value
- [ ] Connection lines: `strokeColor=#FFFFFF;strokeWidth=2` — white, never default black
- [ ] IP last-octet labels: separate `edgeLabel` cells (`.1`, `.2`) near each interface endpoint — not embedded in the edge label string
- [ ] Legend box: black fill `#000000`, white text `#FFFFFF`, bottom-right corner — not colored boxes matching router fills
- [ ] Title: bold, 16pt, top center

**Mandatory post-write validation checklist (run after writing the XML):**
- [ ] Open the file mentally and verify every router cell uses `mxgraph.cisco.routers.router` shape
- [ ] Every router has a separate label cell — no hostname/role/loopback text in the router cell `value=`
- [ ] Every edge has `strokeColor=#FFFFFF` in its style string
- [ ] Every interface endpoint has a standalone `.N` octet cell parented to `"1"` (canvas root)
- [ ] Legend is a single cell with `fillColor=#000000;fontColor=#FFFFFF` at bottom-right
- [ ] The `.drawio` file is the only required diagram artifact — no PNG export needed

If any checklist item fails, fix it before moving to Step 6. Do not mark topology complete with known violations.

--# Step 6: Generate setup_lab.py

Use `assets/setup_lab_template.py` as the base template. Customise it for this lab's active devices and console ports from `baseline.yaml`.

The script must:
1. Use `device_type='cisco_ios_telnet'` to connect via console ports
2. Loop through each active device
3. Load the corresponding `initial-configs/[Device].cfg`
4. Log progress clearly per device

--# Step 7: Invoke fault-injector skill

After generating the workbook, invoke the `fault-injector` skill to create `scripts/fault-injection/` scripts based on the troubleshooting scenarios in the workbook.

Use `assets/troubleshooting_scenarios_template.md` as the template for Section 9 troubleshooting content.

-# Common Issues

--# baseline.yaml not found
- **Cause:** Chapter has not been planned yet.
- **Solution:** Stop. Ask the user to run the `chapter-topics` skill first to generate `labs/[chapter]/baseline.yaml`.

--# No previous lab solutions to chain from (Lab N > 1)
- **Cause:** Lab (N-1) has not been generated yet.
- **Solution:** Stop. Labs must be generated in sequence. Generate Lab (N-1) first, or ask the user whether to generate from the baseline instead (treating it as Lab 01 style).

--# Device in baseline.yaml has no console port defined
- **Cause:** Incomplete baseline.yaml.
- **Solution:** Fall back to default convention (R1=5001, RN=500N). Flag the gap to the user.

--# Solutions section incomplete
- **Cause:** Not all lab objectives have a corresponding solution block.
- **Solution:** Every objective listed in Section 5 (Lab Challenge) must have a `<details>` solution block in Section 8. Go back and complete before finishing.

--# Troubleshooting tickets in wrong section
- **Cause:** Tickets placed inside Section 8 (Solutions) instead of Section 9.
- **Solution:** Section 8 contains only lab objective solution configs. Move all tickets to Section 9 (Troubleshooting Scenarios), which opens with the inject/restore workflow block.

--# Capstone initial-configs incorrectly chain from previous lab
- **Cause:** `clean_slate: true` was not checked before generating initial-configs; previous lab's solutions were copied as usual.
- **Solution:** For any lab with `type: capstone_i` or `type: capstone_ii`, always regenerate initial-configs from `baseline.yaml core_topology` IP addressing only. Never copy from a previous lab's solutions for a capstone.

-# Examples

User: "Generate EIGRP Lab 03 for the ENARSI series."

Actions:
1. Read `labs/eigrp/baseline.yaml` — identify Lab 03 devices, objectives, console ports.
2. Copy `labs/eigrp/lab-02-[name]/solutions/` as `initial-configs/` for Lab 03.
3. Write `workbook.md` with all 10 required sections.
4. Generate `initial-configs/`, `solutions/`, `topology.drawio`, `setup_lab.py`.
5. Invoke `drawio` skill to validate topology diagram style.
6. Invoke `fault-injector` skill to generate `scripts/fault-injection/`.
