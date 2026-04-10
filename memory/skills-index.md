# Skills Index

Quick reference for all skills in this repository.

| Skill | When to Use | Key Output |
|-------|-------------|------------|
| `exam-planner` | Starting a new exam — reads full blueprint, groups into topics | `specs/topic-plan.yaml`, empty `labs/<topic>/` folders |
| `spec-creator` | Creating specs for a single topic after exam-planner | `labs/<topic>/spec.md`, `baseline.yaml` |
| `lab-workbook-creator` | Generating a single lab from a topic spec | `workbook.md`, configs, `setup_lab.py`, `topology.drawio` |
| `lab-builder` | Generating multiple labs at once with config chaining | All lab artifacts for a topic |
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
4. lab-workbook-creator  (one lab at a time) ← Phase 3
   OR lab-builder        (all labs at once)
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
