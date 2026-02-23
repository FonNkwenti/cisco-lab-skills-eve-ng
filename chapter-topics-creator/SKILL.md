---
name: chapter-topics-creator
description: Generates a chapter blueprint and baseline.yaml from CCNP ENARSI exam objectives, ensuring complete blueprint coverage and progressive lab difficulty. Use when the user asks to "plan a chapter", "create chapter topics", "start a new chapter", "what labs should I build for [technology]", "generate baseline.yaml", or "how should I structure the [technology] labs".
---

# Chapter Topics Creator Skill

Generates the strategic plan for a lab chapter, ensuring all exam objectives are covered through a progressive series of labs. Also creates the **baseline.yaml** file that defines shared topology and enables lab chaining continuity.

-# Instructions

--# Step 1: Gather Inputs

Confirm the following before generating:
1. **Technology** — e.g., EIGRP, OSPF, BGP, Redistribution
2. **Exam Objectives** — list the ENARSI blueprint bullets to cover (see `specs/[chapter]/chapter-spec.md`)
3. **Target Lab Count** — determined by blueprint coverage. Minimum labs = what is needed to cover all objectives progressively. The last 2 labs are ALWAYS Capstone I and Capstone II.
4. **Progression** — Foundation → Intermediate → Advanced → Capstone I → Capstone II

--# Step 2: Generate Chapter Blueprint

Design the lab series with:
- Full coverage of all provided exam objectives (no bullet left uncovered)
- Progressive difficulty across labs
- Real-world enterprise scenarios
- Time estimates: 45–120 minutes per lab
- Each lab explicitly declares which devices are active
- **Topology size**: minimum 3 devices, maximum 15 devices total across core + optional

--# Step 2b: Capstone Design Rules

Every chapter ends with exactly 2 capstone labs. These are always the last 2 labs in the series:

**Capstone I — Full Protocol Configuration Challenge**
- `type: capstone_i`
- `clean_slate: true` (initial-configs from `core_topology` IP addressing only, NOT chained from previous lab)
- All blueprint bullets for the chapter must be addressed in a single challenge
- Difficulty: Advanced, time_minutes: 120
- Devices: all core + all optional that have been introduced
- Section 5 (Challenge): "Configure the complete [Protocol] solution from scratch. No step-by-step guidance. All blueprint bullets must be addressed."

**Capstone II — Comprehensive Troubleshooting**
- `type: capstone_ii`
- `clean_slate: true` (initial-configs from `core_topology` IP addressing only, NOT chained from previous lab)
- 5+ concurrent faults spanning all blueprint bullets; students diagnose from a broken network
- Difficulty: Advanced, time_minutes: 120
- Devices: all core + all optional that have been introduced
- Section 5 (Challenge): "The network is pre-broken. Diagnose and resolve 5+ concurrent faults spanning all blueprint bullets."

--# Step 3: Write baseline.yaml

Write `labs/[chapter]/baseline.yaml` using this schema:

```yaml
chapter: [TECHNOLOGY]
version: 1.0

# Core devices — present in ALL labs
core_topology:
  devices:
    - name: R1
      platform: c7200|c3725
      role: [descriptive role]
      loopback0: [IP/mask]
      console_port: 5001
  links:
    - id: L1
      source: [Device:Interface]
      target: [Device:Interface]
      subnet: [network/mask]

# Optional devices — added for specific labs
optional_devices:
  - name: R4
    platform: c7200|c3725
    role: [role]
    loopback0: [IP/mask]
    console_port: 5004
    available_from: [lab number]
    purpose: [why needed]

optional_links:
  - id: L3
    source: [Device:Interface]
    target: [Device:Interface]
    subnet: [network/mask]
    available_from: [lab number]

# Lab progression
labs:
  - number: 1
    title: [Lab Title]
    difficulty: Foundation|Intermediate|Advanced
    time_minutes: [45-120]
    devices: [R1, R2, R3]
    objectives:
      - [objective 1]
      - [objective 2]
  - number: 2
    title: [Lab Title]
    devices: [R1, R2, R3]
    extends: 1
  # ... objective labs ...
  - number: N-1
    title: "[Protocol] Full Protocol Mastery — Capstone I"
    type: capstone_i
    clean_slate: true
    difficulty: Advanced
    time_minutes: 120
    blueprint: all
    devices: [all active devices]
    objectives:
      - [comprehensive config objectives covering all blueprint bullets]
  - number: N
    title: "[Protocol] Comprehensive Troubleshooting — Capstone II"
    type: capstone_ii
    clean_slate: true
    difficulty: Advanced
    time_minutes: 120
    blueprint: all
    devices: [all active devices]
    objectives:
      - [5+ concurrent fault diagnosis objectives spanning all blueprint bullets]
```

--# Step 4: Backfill chapter-spec.md

After generating baseline.yaml, write the plan back into `specs/[chapter]/chapter-spec.md` under the `## Generated Plan` section. Include:
1. **Topology summary** — devices, roles, platforms, link structure (1-3 lines of prose)
2. **Lab Progression table** — number, title, difficulty, time, blueprint bullets, devices
3. **Blueprint Coverage table** — each exam bullet mapped to the lab(s) that cover it

This makes the spec a human-readable record of what was generated. If the user filled in `## Preferences`, note which preferences were honored.

--# Step 5: Validate

Before finishing, confirm:
- [ ] Every exam objective provided is covered by at least one lab
- [ ] Total device count is between 3 (minimum) and 15 (maximum) across core + optional
- [ ] All console ports follow the convention: RN = 500N
- [ ] Platform choices respect Apple Silicon constraints — c7200 or c3725 only (see `gns3` skill)
- [ ] All topology diagrams follow the drawio Visual Style Guide (invoke the `drawio` skill)
- [ ] IP addresses are pre-reserved for all optional devices even if not active in early labs
- [ ] The last 2 labs are Capstone I (`type: capstone_i`) and Capstone II (`type: capstone_ii`), both with `clean_slate: true`

-# Continuity Rules

1. **Core devices** maintain consistent IPs across ALL labs
2. **Optional devices** are pre-reserved with IPs but only activated when declared in `labs[N].devices`
3. **Each lab extends the previous** — solutions become the next lab's initial-configs
4. **Config chaining rule:** only add commands between labs, never remove

-# Common Issues

--# Exam objectives list is incomplete
- **Cause:** User did not provide a full list, or `specs/[chapter]/chapter-spec.md` has unfilled sections.
- **Solution:** Read `specs/exam-blueprint.md` for the full ENARSI 300-410 blueprint and cross-reference the chapter section. Ask the user to confirm before generating.

--# baseline.yaml already exists
- **Cause:** A previous baseline was generated for this chapter.
- **Solution:** Stop and ask the user whether to overwrite or extend the existing file. Do not silently overwrite.

--# Too few labs to cover all objectives
- **Cause:** Target lab count is too low for the number of objectives.
- **Solution:** Propose increasing the count, or explain which objectives will be combined into a single lab and why.

--# Platform selection unclear
- **Cause:** Lab requires features only available on c7200 (crypto, more interfaces) but default is c3725.
- **Solution:** Use c7200 for Hub/Core routers and when IPsec, GRE, or more than 3 FastEthernet interfaces are needed. Use c3725 for Branch/Spoke roles.

-# Examples

User: "Plan the OSPF chapter for ENARSI. Cover all OSPF blueprint topics."

Actions:
1. Read `specs/ospf/chapter-spec.md` for the exam bullets.
2. Design 8–10 labs with Foundation → Advanced progression.
3. Write `labs/ospf/baseline.yaml` with 3 core routers (R1, R2, R3) + optional R4, R7.
4. Write `labs/ospf/README.md` with blueprint coverage matrix.
