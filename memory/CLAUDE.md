# Cisco Lab Skills — Shared Memory

> This file is imported by every cert project's CLAUDE.md.
> It provides Claude Code with awareness of all available skills and shared lab standards.

## Available Skills

@skills/exam-planner/SKILL.md
@skills/spec-creator/SKILL.md            (Phase 2)
@skills/lab-builder/SKILL.md             (Phase 3 topic orchestrator)
@skills/lab-assembler/SKILL.md           (single lab builder)
@skills/fault-injector/SKILL.md
@skills/mega-capstone-creator/SKILL.md
@skills/tag-lab/SKILL.md
@skills/drawio/SKILL.md
@skills/eve-ng/SKILL.md
@skills/cisco-troubleshooting-1/SKILL.md

## Platform Constraints (EVE-NG / Intel)

- **Emulation:** QEMU (primary), IOL (lightweight), Dynamips (legacy — deprecated for new labs)
- **Primary router platform:** `iosv` (IOSv 15.9) — interfaces: `GigabitEthernet0/0` through `GigabitEthernet0/3`
- **Primary switching platform:** `iosvl2` (IOSvL2 15.x) — interfaces: `Gi0/0`–`Gi0/3` (routed) + `Gi1/0`–`Gi1/3` (switchports)
- **Console access:** Dynamic ports assigned by EVE-NG. Discover via REST API or EVE-NG web UI. No static `500N` convention.
- **All IOS 15.x+ features supported:** Named-mode EIGRP, RSTP, LACP, BPDU Guard, OSPFv3, BGP — all available on IOSv/IOSvL2.

## Lab Standards (DeepSeek Standard)

## Three-Phase Workflow

1. **exam-planner** — reads `blueprint/<exam-code>/blueprint.md`, produces `specs/topic-plan.yaml` + empty `labs/<topic>/` folders
2. **spec-creator** — reads `topic-plan.yaml`, produces `labs/<topic>/spec.md` + `baseline.yaml` per topic, with pause-for-review
3. **lab-builder** — orchestrates all labs for a topic, invoking `lab-assembler` per lab and pausing for review between them. Invoke `lab-assembler` directly to build a single lab without the loop.

Lab directories use descriptive zero-indexed names: `lab-00-introduction`, `lab-01-classic-adjacency`.

Every lab directory MUST contain:
- `workbook.md` — student workbook with 11 sections (Section 11 = Appendix: Script Exit Codes)
- `README.md` — quick-reference card (blueprint coverage, quick-start, file tree)
- `initial-configs/` — per-device .cfg files
- `solutions/` — per-device .cfg files
- `topology/topology.drawio` — Cisco19-icon diagram (`.drawio` only; no PNG required)
- `topology/README.md` — EVE-NG .unl import/export instructions
- `setup_lab.py` — Netmiko automation (accepts `--host <eve-ng-ip>` argument)
- `meta.yaml` — provenance tracking (`exam`, `devices`, `created`, `updated`)

Every workbook MUST include:
- At least 3 troubleshooting scenarios (Section 9)
- Solutions wrapped in `<details>` spoiler blocks (Section 8)
- Device Inventory table in Section 3 (platform, image)
- IS/NOT pre-loaded block in Section 4 (concept-level, no IOS syntax)
- Console Access Table in Section 3 (ports populated from EVE-NG web UI after lab creation)
- `scripts/fault-injection/` with `inject_scenario_0N.py` + `apply_solution.py`

## Diagram Standards

- Canvas background: `#1a1a2e` (dark navy) — set in `<mxGraphModel background="#1a1a2e">`
- White connection lines: `strokeColor=#FFFFFF;strokeWidth=2`
- **Cisco19** icons: `shape=mxgraph.cisco19.rect;prIcon=router` — NOT the old `mxgraph.cisco.routers.router`
- Device labels: embedded HTML in device cell `value` (white bold hostname + gray role/IP)
- Zone/domain overlays: `rounded=1;arcSize=5` dashed semi-transparent boxes — NOT `ellipse`
- Legend box: black fill, white text, bottom-right corner
- IP last-octet labels (`.1`, `.2`) near each interface endpoint

## Automation Standards

- All scripts use `common/tools/eve_ng.py` shared library: `require_host()`, `discover_ports()`, `connect_node()`, `erase_device_config()`
- Port discovery at runtime via EVE-NG REST API — no hardcoded port constants
- `setup_lab.py` at lab root: `sys.path.insert(0, str(SCRIPT_DIR.parents[1] / "common" / "tools"))`
- Fault injection scripts at `scripts/fault-injection/`: `sys.path.insert(0, str(SCRIPT_DIR.parents[3] / "common" / "tools"))`
- All scripts accept `--host <eve-ng-ip>` and `--lab-path <topic>/<slug>.unl` (REST API only — does NOT generate .unl)
- Exit codes: 0=success, 1=partial restore, 2=missing --host, 3=EVE-NG error, 4=preflight fail

## Artifact Regeneration (after skill sync or fixes)

After `/sync-skills`, use these to update individual artifacts without rebuilding the whole lab:

| To regenerate | Command |
|--------------|---------|
| `topology/topology.drawio` | `/diagram <topic>/<lab-id>` |
| `scripts/fault-injection/` | `/inject-faults <topic>/<lab-id>` |
| Active fault diagnosis | `/troubleshoot <topic>/<lab-id> <symptom>` |

See `memory/skills-index.md` for the full slash command reference.
