# Skills Index

Quick reference for all skills in this repository.

| Skill | When to Use | Key Output |
|-------|-------------|------------|
| `chapter-topics-creator` | Starting a new chapter from scratch | `baseline.yaml`, chapter `README.md` |
| `chapter-builder` | Generating multiple labs at once with config chaining | All lab artifacts for a chapter |
| `lab-workbook-creator` | Generating a single lab | `workbook.md`, configs, `setup_lab.py`, `topology.drawio` |
| `fault-injector` | Creating automated troubleshooting scenario scripts | `inject_scenario_0N.py`, `apply_solution.py` |
| `drawio` | Creating or fixing topology diagrams | `topology.drawio` |
| `eve-ng` | Reference for EVE-NG platform capabilities and constraints (QEMU/IOL/Dynamips) | (reference only) |
| `gns3` | **DEPRECATED** — Legacy GNS3/Apple Silicon reference (read-only archive) | (archived) |
| `cisco-troubleshooting-1` | Systematically diagnosing a network fault | Structured resolution report |

## Typical Workflow for a New Chapter

### Prerequisites (exam repo, not skills repo)
Before invoking any skill, the exam repo must have:
- `specs/[chapter]/chapter-spec.md` — **current** blueprint bullets for this chapter, copied
  directly from the official Cisco exam page. Cisco revises blueprints periodically (e.g.,
  ENCOR 350-401 was updated in 2025). If the user has not confirmed the blueprint source,
  stop and ask them to paste the current bullets before proceeding.
- `labs/[chapter]/` directory (created by chapter-topics-creator)

### Step-by-step

```
1. Write specs/[chapter]/chapter-spec.md   (exam blueprint bullets — manual)
        │
        ▼
2. chapter-topics-creator
        │  reads: chapter-spec.md
        │  writes: labs/[chapter]/baseline.yaml
        ▼
3. lab-workbook-creator  (one lab at a time, recommended)
   OR chapter-builder    (all labs at once, for batch generation)
        │  reads: baseline.yaml + chapter-spec.md
        │  writes: workbook.md, initial-configs/, solutions/,
        │          topology.drawio, setup_lab.py
        │  invokes: fault-injector (per lab) → scripts/fault-injection/
        │  invokes: drawio (per lab) → topology.drawio
        ▼
4. EVE-NG: create lab, add nodes (platform from baseline.yaml),
   connect links, start nodes, discover console ports (web UI or REST API)
        │
        ▼
5. python setup_lab.py --host <eve-ng-ip>
        │  pushes initial-configs/ to all devices via Netmiko telnet
        ▼
6. Open workbook.md — work through tasks
   Use scripts/fault-injection/inject_scenario_0N.py for troubleshooting practice
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
