# Cisco Lab Skills — Shared Memory

> This file is imported by every cert project's CLAUDE.md.
> It provides Claude Code with awareness of all available skills and shared lab standards.

## Available Skills

@skills/chapter-builder/SKILL.md
@skills/chapter-topics-creator/SKILL.md
@skills/lab-workbook-creator/SKILL.md
@skills/fault-injector/SKILL.md
@skills/drawio/SKILL.md
@skills/gns3/SKILL.md
@skills/cisco-troubleshooting-1/SKILL.md

## Platform Constraints (GNS3 / Apple M1)

- **Emulation only**: Dynamips. No VirtualBox, VMware, or Containerlab.
- **Router platforms**: c7200 (hub/core/ABR) and c3725 (branch/spoke) only.
- **Console ports**: Base port 5000. R1=5001, R2=5002, R3=5003, R4=5004 ...
- **c7200 interfaces**: fa0/0, fa1/0, fa1/1, s2/0–s2/3, gi3/0
- **c3725 interfaces**: fa0/0, fa0/1, fa1/0–fa1/15 (switch), s2/0–s2/3

## Lab Standards (DeepSeek Standard)

Every lab directory MUST contain:
- `workbook.md` — student workbook with 9+ sections
- `initial-configs/` — per-device .cfg files
- `solutions/` — per-device .cfg files
- `topology.drawio` — Cisco-icon diagram (`.drawio` only; no PNG required)
- `setup_lab.py` — Netmiko telnet automation

Every workbook MUST include:
- At least 3 troubleshooting scenarios (Section 8)
- Solutions wrapped in `<details>` spoiler blocks (Section 9)
- Console Access Table with telnet port per device
- `scripts/fault-injection/` with `inject_scenario_0N.py` + `apply_solution.py`

## Diagram Standards

- White connection lines: `strokeColor=#FFFFFF`
- Cisco icons from `mxgraph.cisco` shape library
- Device labels: hostname + role + loopback IP
- Legend box: black fill, white text, bottom-right corner
- IP last-octet labels near each interface endpoint

## Automation Standards

- Netmiko `device_type="cisco_ios_telnet"` for all GNS3 console access
- Target `host="127.0.0.1"`, `port=[console_port]`
- `setup_lab.py` reads from `initial-configs/*.cfg`
- Fault injection scripts in `scripts/fault-injection/`
