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
| 3 | Hardware & Environment Specifications | Must include Console Access Table + Cabling Table. Console ports are dynamic — populate from EVE-NG web UI after lab creation. Format: `telnet <eve-ng-ip> <port>` |
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

**No raw IOS command syntax in task steps or in the Section 4 "NOT pre-loaded" list.**
Named parameters (key-chain names, AS numbers, algorithm names, subnet addresses) are allowed.
The `**Verification:**` line at the end of each task is the only place show commands appear in Section 5.

- ✅ "Create a key-chain named OSPF_AUTH with key ID 1 and a strong key-string."
- ❌ "Run `key chain OSPF_AUTH` / `key 1` / `key-string <value>`."
- ✅ "Enable EIGRP in Autonomous System 100 on all three routers."
- ❌ "Configure `router eigrp 100` on R1, R2, and R3."

## Cheatsheet Formatting (Section 7) — REQUIRED

Never put all commands in one monolithic code block. Always use named subsections:

1. One subsection per logical command group — each with a syntax skeleton code block followed by a `Command | Purpose` table
2. Verification commands in a `Command | What to Look For` table (never a code block)
3. End with a mask/wildcard reference table and a failure-causes table

Reference `lab-workbook-creator/SKILL.md` Section 5/7 format blocks for the exact template.

## Diagram Standards

- White connection lines (`strokeColor=#FFFFFF`) — never black
- Cisco shape library icons (`mxgraph.cisco.routers.router`)
- Device label: hostname + role + loopback IP
- IP last-octet labels near each interface
- Legend box: black fill, white text, bottom-right

## Global Configuration Standards

All Cisco router and switch initial configs must include these global commands immediately after `hostname`:

```
hostname <device-name>
no ip domain-lookup
!
```

These commands are required for all new labs and must appear in every initial config file for Cisco devices.

## Config Chaining Rules

- Lab 00 (first progressive) `initial-configs/` = IP addressing only from `baseline.yaml`
- Lab N (progressive, N > 0) `initial-configs/` = Lab (N-1) `solutions/`
- Standalone labs `initial-configs/` = IP addressing only from `baseline.yaml`
- Capstone I + II `initial-configs/` = IP addressing only from `baseline.yaml` (clean slate)
- **Never remove** a config command between progressive labs — only add

## Overlay Tunnel Design: Unique Loopback per Endpoint Type

When a lab configures multiple tunnel types sharing the same router pair:

- Plain GRE tunnels (`tunnel mode gre ip`, no protection) **must use a different source loopback** than IPsec tunnels (`tunnel mode ipsec ipv4` or `tunnel mode gre ip` + `tunnel protection`).
- A VTI (`tunnel mode ipsec ipv4`) negotiates **wildcard traffic selectors** (`0.0.0.0/0 ↔ 0.0.0.0/0`) for its endpoint pair. Any unencrypted tunnel sharing those endpoints will have packets dropped with `%CRYPTO-4-RECVD_PKT_NOT_IPSEC`.
- **Required loopback allocation when mixing plain and encrypted overlays:**

  | Tunnel type | Source loopback | Address convention |
  |-------------|-----------------|-------------------|
  | Plain GRE (Tunnel0) | Loopback0 (router-id) | `X.X.X.X/32` |
  | IPsec VTI + GRE-over-IPsec | **Loopback10** | `10.10.R.R/32` (R = router number) |

- Reference incident: `labs/virtualization/lab-03-ipsec-and-gre-over-ipsec/troubleshooting-reports/INC-20260421-ticket-002.md`

## Troubleshooting Scenario Requirements

Each of the 3+ scenarios must have:
1. Problem Statement (observable symptoms)
2. Mission (what to diagnose/fix)
3. Success Criteria (measurable checkboxes)
4. Solution in `<details>` spoiler block
5. Reference to `scripts/fault-injection/inject_scenario_0N.py`
