---
name: lab-assembler
description: Assembles a complete lab package - workbook, initial-configs, solutions, topology diagram, setup_lab.py, meta.yaml, and fault-injection scripts - for a single lab. Inner builder called by lab-builder (topic orchestrator) during Phase 3 of the workflow (exam-planner -> spec-creator -> lab-builder -> lab-assembler). Use when the user asks to "create a lab", "generate lab N", "build [technology] lab", "assemble a lab package", or when building one lab directly from a topic spec.
---

# Lab Assembler Skill

Converts a single lab entry from `baseline.yaml` into a full lab package (workbook,
configs, solutions, topology, automation, fault-injection). Inner builder invoked by
`lab-builder` (the topic-level orchestrator) during Phase 3 of the three-phase
workflow: exam-planner -> spec-creator -> lab-builder -> **lab-assembler**. Can also be
invoked directly to build a single lab without the orchestrator's review-gate loop.
Labs within a topic are built chronologically so each progressive lab continues from the
previous one.

-# Instructions

--# Step 1: Read Inputs

Before generating anything, read in parallel:
1. `labs/<topic>/baseline.yaml` — active devices, IPs, console ports, lab objectives
2. `labs/<topic>/spec.md` — exam bullet context, lab progression, and blueprint coverage

Then, using the baseline you just read:
3. Check `baseline.yaml labs[N].type` — if `capstone_i` or `capstone_ii`, set `clean_slate: true` for this lab
4. Previous lab's `solutions/` (if `type: progressive` and not the first lab) — becomes
   this lab's `initial-configs/`. If `type: standalone` or `clean_slate: true`, generate
   from `baseline.yaml core_topology` IP addressing only.

Identify which devices are active for this lab number from `baseline.yaml labs[N].devices`.

--# Step 2: Generate & Verify Solutions

Generate complete solution configs for all active devices, verify every command
against live routers, then write verified configs to disk.

### 2a — Draft solutions

Draft the full IOS config for each active device in memory, implementing all lab
objectives. Do not write files yet.

### 2b — Extract commands by context

Parse the draft configs and collect unique (command, context) pairs:
- Lines at global config level → `global`
- Under `interface X` → `interface`
- Under `router eigrp [NAME]` (named string) → `router-eigrp-named`
- Under `router eigrp [N]` (numeric AS) → `router-eigrp`
- Under `address-family ipv4 unicast` → `af-ipv4-unicast`
- Under `router ospf N` → `router-ospf`
- Under `router bgp N` → `router-bgp`

### 2c — Check compatibility record

Read `.agent/skills/reference-data/ios-compatibility.yaml`. For each (command, context) pair:
- `pass` on target platform → OK, proceed
- `fail` on target platform → go to 2e
- `unknown` → add to verification list for 2d

### 2d — Verify unknowns (if any)

Write unknown commands to `_verify_input.yaml` in project root:

```yaml
commands:
  - command: "..."
    context: "..."
```

Run: `python3 .agent/skills/scripts/verify_ios_commands.py _verify_input.yaml`

Re-read `.agent/skills/reference-data/ios-compatibility.yaml`. Delete `_verify_input.yaml`.

### 2e — Resolve failures

For any command that is `fail` on the target platform:
- If `pass` on `ios-xe` (CSR1000v): switch the affected device to `csr1000v` in the draft config.
  Log the platform change as a note in `decisions.md`. Proceed.
- If `fail` on all platforms: do not use the command. Remove it from the draft
  and adjust the lab objective to use a supported alternative. Alert the user.
  Log the dropped command and affected blueprint bullet to `memory/decisions.md`.
  Verify the remaining lab objectives still cover all `baseline.yaml labs[N].objectives` entries —
  if any objective loses its only implementing command, STOP and escalate to the user.

### 2f — Write solutions/ to disk

Only after all commands are `pass` on their target platform: write one `.cfg` file
per active device to `solutions/`. Do not write partial or unverified configs.

--# Step 3: Generate workbook.md

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
11. [Appendix: Script Exit Codes](#11-appendix-script-exit-codes)

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
3. **Hardware & Environment Specifications** — Device Inventory table, cabling table, Console Access Table
4. **Base Configuration** — what is pre-configured in `initial-configs/` (see IS/NOT format below)
5. **Lab Challenge: Core Implementation** — objectives for the student (see format below)
6. **Verification & Analysis** — expected `show` command outputs per objective, with inline `!` comments marking the specific lines or values the student must confirm
7. **Verification Cheatsheet** — quick-reference commands for the entire lab (see format below)
8. **Solutions (Spoiler Alert!)** — solution configs for lab objectives only, wrapped in `<details>` blocks
9. **Troubleshooting Scenarios** — fault injection workflow + symptom-based tickets with `<details>` spoilers
10. **Lab Completion Checklist** — two groups: Core Implementation and Troubleshooting
11. **Appendix: Script Exit Codes** — exit code table for `setup_lab.py`, inject scripts, and `apply_solution.py`

**Section 3 — Device Inventory table (REQUIRED):**

Every workbook must include a Device Inventory table immediately before the cabling table in Section 3:

```markdown
| Device | Role | Platform | Image |
|--------|------|----------|-------|
| R1 | Hub Router | IOSv | vios-adventerprisek9-m.SPA.156-2.T |
| R2 | Branch A | IOSv | vios-adventerprisek9-m.SPA.156-2.T |
```

Use the platform and image from `baseline.yaml core_topology.devices[N].platform` and `.image`. If not specified, use the EVE-NG default for that platform.

**Section 4 — IS/NOT pre-loaded format (REQUIRED):**

Section 4 must use an explicit two-column list — not prose — to describe what the student starts with:

```markdown
## 4. Base Configuration

The following is **pre-loaded** via `setup_lab.py`:

**IS pre-loaded:**
- Hostnames
- Interface IP addressing (all routed links and loopbacks)
- `no ip domain-lookup`

**IS NOT pre-loaded** (student configures this):
- EIGRP routing process
- Subnet advertisement
- Neighbour authentication
```

Rules:
- "IS pre-loaded" items describe features or concepts in plain English — never raw IOS syntax
- "IS NOT pre-loaded" items describe the lab objectives at concept level — align with Section 5 tasks
- Never mix IOS commands into either list (e.g. ❌ "`router eigrp 100`", ✅ "EIGRP routing process")

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

**Section 11 — Appendix: Script Exit Codes (REQUIRED):**

```markdown
## 11. Appendix: Script Exit Codes

| Code | Meaning | Applies to |
|------|---------|------------|
| 0 | Success | All scripts |
| 1 | Partial failure | `apply_solution.py` only |
| 2 | `--host` not provided | All scripts |
| 3 | EVE-NG connectivity error | All scripts |
| 4 | Pre-flight check failed | Inject scripts only |
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
| R1 | (see EVE-NG UI) | `telnet <eve-ng-ip> <port>` |
| R2 | (see EVE-NG UI) | `telnet <eve-ng-ip> <port>` |

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

--# Step 4: Generate initial-configs/

- **First progressive lab (number 0):** Generate base IP addressing from `baseline.yaml core_topology` (IP config only — no routing protocol config).
- **Subsequent progressive labs (N > 0):** Copy exactly from Lab (N-1) `solutions/`. Do not modify.
- **Standalone labs (`type: standalone`):** Generate from `baseline.yaml core_topology` IP addressing only — not chained from previous lab.
- **Capstone I or Capstone II (`clean_slate: true`):** Generate from `baseline.yaml core_topology` IP addressing only — do NOT copy previous lab solutions. All routing protocol config is absent; the student configures everything from scratch.
- One `.cfg` file per active device, named `[Device].cfg`.

--# Step 5: Generate topology.drawio

Dispatch a **single subagent** (general-purpose) to write the topology diagram. This isolates the 328-line drawio/SKILL.md read from main context.

Fill in all [bracketed] placeholders before dispatching.

---SUBAGENT: Topology Diagram (general-purpose)---

Prompt:

You are generating a topology.drawio diagram for a Cisco certification EVE-NG lab.

## Task
Write Draw.io XML to:
  labs/<topic>/lab-NN-<slug>/topology/topology.drawio

Create the `topology/` subdirectory if it does not exist. The drawio file MUST
live inside `topology/`, not at the lab root. Sibling file in the same folder:
`topology/README.md` (written in Step 5b).

## MANDATORY FIRST ACTION
Read .agent/skills/drawio/SKILL.md in full — especially §4.2–§4.7.
Use the §4.7 reference XML snippets as your starting template.
Never write topology XML from scratch.

## Read After drawio/SKILL.md
1. labs/<topic>/baseline.yaml — devices (IPs, roles, loopbacks) and links (subnets)
2. labs/<topic>/lab-NN-<slug>/workbook.md — Section 2 ASCII diagram as layout reference

## Active Devices
[fill from baseline.yaml labs[N].devices — e.g. R1 (Hub), R2 (Branch A), R3 (Branch B)]

## Links
[fill from baseline.yaml core_topology.links — e.g. L1: R1 Fa0/0 ↔ R2 Fa0/0, 10.12.0.0/30]

## Layout
[fill: e.g. Triangle — R1 top center, R2 bottom-left, R3 bottom-right]

## Pre-Write Checklist
- [ ] drawio/SKILL.md §4.2-§4.7 read; §4.7 XML snippets in context
- [ ] Router shape: mxgraph.cisco.routers.router — NOT a rectangle
- [ ] Device labels: separate text cells — NOT embedded in router cell value=
- [ ] Connection lines: strokeColor=#FFFFFF — NOT default black
- [ ] IP last-octet labels: separate edgeLabel cells parented to "1"
- [ ] Legend box: fillColor=#000000, fontColor=#FFFFFF, bottom-right

## Post-Write Checklist (fix before confirming done)
- [ ] File written to `labs/<topic>/lab-NN-<slug>/topology/topology.drawio` — NOT to the lab root
- [ ] Every router cell uses mxgraph.cisco.routers.router shape
- [ ] Every router has a separate label cell
- [ ] Every edge has strokeColor=#FFFFFF
- [ ] Every interface endpoint has a standalone .N octet cell
- [ ] Legend present at bottom-right with black fill

## Output Confirmation
File path, line count, number of router cells, number of edge cells,
confirmation both checklists pass.

--# Step 5b: Generate topology/README.md

After the drawio subagent completes, write `labs/<topic>/lab-NN-<slug>/topology/README.md`.
This file documents the EVE-NG .unl import/export process for this specific lab — it is NOT
auto-generated as part of the build; the .unl file is created manually in EVE-NG.

Required content:
1. **Lab topology summary** — brief description of the topology (device count, links, topology type)
2. **EVE-NG import instructions** — step-by-step: navigate to File > Import, select the `.unl` file, where to find it
3. **Node configuration reference** — table listing each device, its EVE-NG template (e.g. `Cisco IOSv`), RAM, and image name from `baseline.yaml`
4. **Starting the lab** — start all nodes, wait for boot, note console port assignments
5. **Exporting the lab** — how to export `.unl` after making topology changes in EVE-NG

Keep the README concise — it supplements the EVE-NG web UI, not replaces it.

--# Step 6: Generate setup_lab.py

Use `assets/setup_lab_template.py` as the base template. Customise it for this lab's active devices. Ports are discovered at runtime via `discover_ports()` — do NOT hardcode ports.

The script must:
1. Call `require_host(args.host)` to validate the `--host` argument
2. Call `discover_ports(host, args.lab_path)` to get the device→port map via EVE-NG REST API
3. For each active device, call `connect_node()` and push `initial-configs/[Device].cfg`
4. Log progress clearly per device; return exit code 0 on full success, 1 on partial failure

**Validate:** Syntax-check without writing cache files. Preferred:
```bash
python3 -c "import ast; ast.parse(open('setup_lab.py').read(), 'setup_lab.py')"
```
If you use `python3 -m py_compile setup_lab.py` instead, you MUST follow it
with `rm -rf __pycache__` — never leave `__pycache__/` in the lab package.
Fix any SyntaxError before proceeding.

--# Step 6b: Generate root README.md

Write `labs/<topic>/lab-NN-<slug>/README.md` — a quick-reference card for the lab.

Required sections:
1. **Lab title and one-line description**
2. **Blueprint coverage** — list the `baseline.yaml labs[N].blueprint_refs` exam objectives
3. **Prerequisites** — lab number this one chains from (if progressive), Python deps
4. **Quick start** — three commands: import .unl, run setup_lab.py, open workbook.md
5. **Files** — brief directory tree showing the key files in this lab package

Keep it under 60 lines — it is a navigation aid, not documentation. Full detail lives in `workbook.md`.

--# Step 7: Generate fault injection scripts

Dispatch a **single subagent** (general-purpose) to generate the fault injection scripts. This isolates the fault-injector/SKILL.md read and all Python script generation from main context.

Fill in all [bracketed] placeholders before dispatching.

---SUBAGENT: Fault Injection Scripts (general-purpose)---

Prompt:

You are generating fault injection scripts for a Cisco certification lab.

## Task
Generate all fault injection scripts and supporting files in:
  labs/<topic>/lab-NN-<slug>/scripts/fault-injection/

## MANDATORY FIRST ACTION
Read .agent/skills/fault-injector/SKILL.md in full.
Follow it exactly — especially the template locations in assets/.

## Read After fault-injector/SKILL.md
1. labs/<topic>/lab-NN-<slug>/workbook.md — Section 9 (troubleshooting scenarios)

## Lab Context
- Chapter: [chapter]
- Lab path: [lab-path]  ← used for DEFAULT_LAB_PATH in scripts (REST API port discovery)
- Active devices: [list from baseline.yaml labs[N].devices — e.g. R1, R2, R3]
- Number of troubleshooting scenarios: [count from workbook.md Section 9]

Note: Console ports are discovered at runtime via discover_ports() — do NOT hardcode ports.
The lab .unl must be ALREADY IMPORTED and nodes started before running the scripts.

## Pre-Write Checklist
- [ ] fault-injector/SKILL.md read in full
- [ ] Each scenario's fault type, target device, and fault/solution markers identified from Section 9
- [ ] DEFAULT_LAB_PATH set to "[topic]/[lab-slug].unl" in all scripts
- [ ] Template files in assets/ read before writing any inject script

## Output Confirmation
List all files created, py_compile result for each .py file, and fault-injector/SKILL.md Step 5 checklist completion status.

--# Step 8: Write meta.yaml

After the fault-injector subagent completes, lab-assembler owns meta.yaml.
The fault-injector does NOT write meta.yaml (see fault-injector/SKILL.md Step 6).
Collect the fault-injection file paths from the subagent's Output
Confirmation and include them in `created.files` below.

1. Get `skill_version`: run `git -C .agent/skills log --format="%ci" -1` and take the date portion (YYYY-MM-DD).
2. Get today's date (YYYY-MM-DD).
3. Glob all files created in this lab directory (recursive, relative paths).
   Exclude `__pycache__/` and `*.pyc` artifacts.
4. Write `labs/<topic>/lab-NN-<slug>/meta.yaml`:

```yaml
# Auto-generated — do not edit manually. Use /tag-lab to stamp external agent runs.
lab: [lab-dir-name]
chapter: [chapter]
exam: [exam-code]           # e.g. 300-410, 350-401
devices:                    # active devices for this lab (from baseline.yaml labs[N].devices)
  - name: [DEVICE_NAME]
    platform: [iosv|iosvl2|csr1000v|xrv9000]
    role: [Hub Router|Branch A|etc.]
created:
  date: "[YYYY-MM-DD]"
  agent: [CURRENT_AGENT_ID]   # e.g. claude-sonnet-4-6, claude-opus-4-7, claude-haiku-4-5-20251001
  skill: lab-assembler
  skill_version: "[YYYY-MM-DD]"
  files:
    - workbook.md
    - topology/topology.drawio
    - topology/README.md
    - setup_lab.py
    - README.md
    - initial-configs/[Device].cfg   # one entry per device
    - solutions/[Device].cfg          # one entry per device
    - scripts/fault-injection/inject_scenario_01.py
    - scripts/fault-injection/inject_scenario_02.py
    - scripts/fault-injection/inject_scenario_03.py
    - scripts/fault-injection/apply_solution.py
    - scripts/fault-injection/README.md
updated: []
```

List every file actually created — adjust device names and inject script count to match the lab.

--# Step 9: Update Progress & Mindmap

After `meta.yaml` is written:
1. Update `memory/progress.md` — set the status row for this lab to "Review Needed".
2. Update the `README.md` mindmap — set the lab node to `◉ Lab NN <name>`.

-# Common Issues

--# baseline.yaml not found
- **Cause:** Topic has not been through spec-creator yet.
- **Solution:** Stop. Ask the user to run the spec-creator skill first to generate `labs/<topic>/baseline.yaml` and `labs/<topic>/spec.md`.

--# No previous lab solutions to chain from (Lab N > 1)
- **Cause:** Lab (N-1) has not been generated yet.
- **Solution:** Stop. Labs must be generated in sequence. Generate Lab (N-1) first, or ask the user whether to generate from the baseline instead (treating it as Lab 01 style).

--# Device in baseline.yaml has no console port defined
- **Cause:** Incomplete baseline.yaml.
- **Solution:** Ask the user to populate console ports from the EVE-NG web UI. There is no static fallback — EVE-NG ports are dynamic.

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

User: "Generate the next lab for EIGRP" (lab-03-summarization is next per spec.md)

Actions:
1. Read `labs/eigrp/baseline.yaml` — identify lab-03 devices, objectives, blueprint_refs.
2. Read `labs/eigrp/spec.md` — confirm lab-03-summarization is `type: progressive`,
   extends lab-02.
3. Copy `labs/eigrp/lab-02-named-mode/solutions/` as `initial-configs/` for lab-03.
4. Draft solution configs; verify against `reference-data/ios-compatibility.yaml`;
   write to `solutions/`.
5. Write `workbook.md` with all 11 required sections (including Section 11 Appendix).
6. Dispatch drawio subagent to write `topology/topology.drawio` (inside the `topology/` subfolder).
7. Write `topology/README.md` with EVE-NG import/export instructions.
8. Generate `setup_lab.py` using eve_ng.py shared library.
9. Write root `README.md` quick-reference card.
10. Invoke `fault-injector` skill to generate `scripts/fault-injection/`.
11. Write `meta.yaml` listing all created files (including `exam` and `devices` fields).
12. Final cleanup — remove any `__pycache__/` directories and `*.pyc` files from the lab package:
    ```bash
    find labs/<topic>/lab-NN-<slug> -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
    find labs/<topic>/lab-NN-<slug> -type f -name '*.pyc' -delete 2>/dev/null
    ```
    Verify with `find labs/<topic>/lab-NN-<slug> -name '__pycache__'` — must return empty.
12. Pause for review before proceeding to lab-04.
