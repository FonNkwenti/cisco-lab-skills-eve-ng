# Skills Index

Quick reference for all skills in this repository.

| Skill | When to Use | Key Output |
|-------|-------------|------------|
| `exam-planner` | Starting a new exam — reads full blueprint, groups into topics | `specs/topic-plan.yaml`, empty `labs/<topic>/` folders |
| `spec-creator` | Creating specs for a single topic after exam-planner | `labs/<topic>/spec.md`, `baseline.yaml` |
| `lab-builder` | Generating multiple labs at once with config chaining (topic-level orchestrator) | All lab artifacts for a topic |
| `lab-assembler` | Assembling a single lab package from a topic spec (inner builder) | `workbook.md`, configs, `setup_lab.py`, `topology.drawio`, `meta.yaml`, fault-injection scripts |
| `fault-injector` | Creating automated troubleshooting scenario scripts | `inject_scenario_0N.py`, `apply_solution.py` |
| `mega-capstone-creator` | Final cross-topic capstone after all topic labs complete | Multi-domain capstone lab package |
| `drawio` | Creating or fixing topology diagrams | `topology.drawio` |
| `eve-ng` | Reference for EVE-NG platform capabilities and constraints (QEMU/IOL/Dynamips) | (reference only) |
| `gns3` | **DEPRECATED** — Legacy GNS3/Apple Silicon reference (read-only archive) | (archived) |
| `cisco-troubleshooting-1` | Systematically diagnosing a network fault | Structured resolution report |

## Three-Phase Workflow

### Prerequisites (exam repo, not skills repo)
Before invoking any skill, the exam repo must have:
- `blueprint/<exam-code>/blueprint.md` — **current** blueprint bullets, copied directly
  from the official Cisco exam page. Cisco revises blueprints periodically. If the user
  has not confirmed the blueprint source, stop and ask them to paste the current bullets.

### Step-by-step

```
1. Upload blueprint to blueprint/<exam-code>/blueprint.md   (manual)
        │
        ▼
2. exam-planner                              ← Phase 1
        │  reads: blueprint.md
        │  writes: specs/topic-plan.yaml + empty labs/<topic>/ folders
        │  (review once)
        ▼
3. spec-creator  (one topic at a time)       ← Phase 2
        │  reads: topic-plan.yaml + blueprint.md
        │  writes: labs/<topic>/spec.md + baseline.yaml
        │  creates: empty lab-NN-<slug>/ folders
        │  (review after each topic)
        ▼
4. lab-builder        (all labs at once, with review gate) ← Phase 3
   OR lab-assembler   (one lab at a time, no loop)
        │  reads: spec.md + baseline.yaml
        │  writes: workbook.md, initial-configs/, solutions/,
        │          topology.drawio, setup_lab.py
        │  invokes: fault-injector (per lab) → scripts/fault-injection/
        │  invokes: drawio (per lab) → topology.drawio
        │  (review after each lab)
        ▼
5. EVE-NG: create lab, add nodes (platform from baseline.yaml),
   connect links, start nodes, discover console ports (web UI or REST API)
        │
        ▼
6. python setup_lab.py --host <eve-ng-ip>
        │  pushes initial-configs/ to all devices via Netmiko telnet
        ▼
7. Open workbook.md — work through tasks
   Use scripts/fault-injection/inject_scenario_0N.py for troubleshooting practice
        │
        ▼
8. mega-capstone-creator  (after all topics complete)
        │  generates: labs/mega-capstone/ — multi-domain final capstone
```

## Slash Commands — Full Reference

All commands live in `.claude/commands/` inside your exam repo and are advisory (they warn on missing prerequisites but do not block).

### Phase commands (build progression)

| Command | Phase | What it does |
|---------|-------|-------------|
| `/project-status` | Any | Shows current phase, what's been built, and the recommended next command |
| `/plan-exam` | 1 | Reads `blueprint/<code>/blueprint.md` → writes `specs/topic-plan.yaml` + empty `labs/<topic>/` folders |
| `/create-spec <topic>` | 2 | Reads topic plan → writes `labs/<topic>/spec.md` + `baseline.yaml`; review before proceeding |
| `/build-lab <topic>/<lab-id>` | 3 | Builds one complete lab package (workbook, configs, topology, scripts); review before proceeding |
| `/build-topic <topic>` | 3 | Builds every lab in a topic with a review gate between each |
| `/build-capstone <slug>` | 3 | Builds the cross-topic mega-capstone lab |
| `/tag-lab <topic>/<lab-id>` | Post-build | Stamps `meta.yaml` with agent + skill version |
| `/sync-skills` | Any | Runs `git submodule update --remote .agent/skills` and reports what changed |
| `/git-commit [files]` | Any | Stage, commit (conventional format), and optionally push — always use this instead of raw git commands |

### Artifact-level commands (regenerate one thing)

Use these when a skill was updated, a workbook section changed, or a diagram needs fixing — without rebuilding the whole lab.

| Command | Regenerates | When to use |
|---------|-------------|-------------|
| `/diagram <topic>/<lab-id>` | `topology.drawio` | After a drawio skill fix, after topology changes in baseline.yaml, or after `/sync-skills` reveals a style update |
| `/inject-faults <topic>/<lab-id>` | `scripts/fault-injection/*.py` + `README.md` | After adding/editing troubleshooting scenarios in workbook.md Section 9, or after a fault-injector skill fix |
| `/troubleshoot <topic>/<lab-id> <symptom>` | _(no files)_ | When actively debugging a live fault in EVE-NG — runs structured 4-phase diagnosis; not a file generator |

**Typical post-skill-sync workflow:**

```
/sync-skills                                  ← pull latest skill fixes
/diagram ospf/lab-00-single-area-ospfv2       ← regenerate topology with new style
/inject-faults ospf/lab-00-single-area-ospfv2 ← regenerate fault scripts with new template
```

`/build-lab` also dispatches diagram and inject-faults automatically (Steps 5 and 7 of `lab-assembler`). The artifact-level commands let you redo just one piece without touching workbook, configs, or solutions.

### Platform selection from baseline.yaml

| baseline.yaml platform value | EVE-NG node type | Use case |
|---|---|---|
| `iosv` | `vios` | Routing labs (OSPF, EIGRP, BGP, redistribution) |
| `iosvl2` | `viosl2` | Switching labs (VLANs, STP, EtherChannel) |
| `csr1000v` | `csr1000vng` | IOS-XE features (NETCONF, RESTCONF, SD-WAN edge) |
| `xrv9k` | `xrv9k` | SP labs (IS-IS, MPLS, Segment Routing, IOS-XR) |
| `nxosv9k` | `nxosv9k` | DC labs (NX-OS, VxLAN, EVPN) |
| `iol_l3` | `iol` | Lightweight routing (low RAM, fast boot) |
| `iol_l2` | `iol` | Lightweight switching |
