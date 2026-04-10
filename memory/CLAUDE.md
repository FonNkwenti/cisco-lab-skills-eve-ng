# Cisco Lab Skills — Shared Memory

> This file is imported by every cert project's CLAUDE.md.
> It provides Claude Code with awareness of all available skills and shared lab standards.

## Available Skills

@skills/chapter-builder/SKILL.md
@skills/chapter-topics-creator/SKILL.md
@skills/lab-workbook-creator/SKILL.md
@skills/fault-injector/SKILL.md
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

Every lab directory MUST contain:
- `workbook.md` — student workbook with 9+ sections
- `initial-configs/` — per-device .cfg files
- `solutions/` — per-device .cfg files
- `topology.drawio` — Cisco-icon diagram (`.drawio` only; no PNG required)
- `setup_lab.py` — Netmiko automation (accepts `--host <eve-ng-ip>` argument)

Every workbook MUST include:
- At least 3 troubleshooting scenarios (Section 9)
- Solutions wrapped in `<details>` spoiler blocks (Section 8)
- Console Access Table (ports populated from EVE-NG web UI after lab creation)
- `scripts/fault-injection/` with `inject_scenario_0N.py` + `apply_solution.py`

## Diagram Standards

- White connection lines: `strokeColor=#FFFFFF`
- Cisco icons from `mxgraph.cisco` shape library
- Device labels: hostname + role + loopback IP
- Legend box: black fill, white text, bottom-right corner
- IP last-octet labels near each interface endpoint

## Automation Standards

- Primary: Netmiko `device_type="cisco_ios_telnet"` to EVE-NG host IP + dynamic port
- Alternative: Netmiko `device_type="cisco_ios"` via SSH to node management interface
- Target `host="<eve-ng-ip>"`, `port=<dynamic-port>` (not `127.0.0.1`)
- `setup_lab.py` reads from `initial-configs/*.cfg` and accepts `--host <eve-ng-ip>`
- Fault injection scripts in `scripts/fault-injection/`
- Port discovery: EVE-NG REST API `GET /api/labs/<lab>/nodes` or check EVE-NG web UI
