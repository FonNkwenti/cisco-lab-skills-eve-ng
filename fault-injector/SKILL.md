---
name: fault-injector
description: Generates Python fault-injection scripts for lab troubleshooting scenarios using Netmiko. Use when the user asks to "inject faults", "generate troubleshooting scripts", "create fault scenarios", "add troubleshooting practice", or automatically after lab-workbook-creator generates a workbook.
---

# Fault Injector Skill

Generates Python scripts that inject the troubleshooting scenarios defined in lab workbooks into the live lab environment. Enables students to set up fault conditions for exam-style troubleshooting practice without manual configuration.

-# Instructions

--# Step 1: Parse Inputs

Read from the lab directory:
1. `workbook.md` — extract troubleshooting scenarios from Section 9 and the Console Access Table
2. Console Access Table → device-to-port map: `{"R1": <port>, "R2": <port>, ...}`. Ports are dynamic in EVE-NG — populated from the Console Access Table in the workbook (which is filled in from the EVE-NG web UI after lab creation).
3. From each scenario extract: **Scenario Number**, **Target Device**, **Fault Type**, **Commands to inject**

--# Step 2: Generate Fault Injection Scripts

For each scenario (minimum 3 per lab), generate `scripts/fault-injection/inject_scenario_0N.py`.

Use `assets/inject_scenario_01_template.py` (and `_02`, `_03`) as base templates. Customise:
- `DEVICE_NAME` and `CONSOLE_PORT` from the Console Access Table
- `FAULT_COMMANDS` list from the scenario's solution section
- Docstring describing exactly what fault is injected

Each script must:
1. Connect via Netmiko to EVE-NG host IP + dynamic console port. Two supported modes:
   - **Telnet (default):** `device_type="cisco_ios_telnet"`, `host=EVE_NG_HOST`, `port=<dynamic>`
   - **SSH (alternative):** `device_type="cisco_ios"`, `host=<node-mgmt-ip>`, `port=22`
2. Apply fault commands via `send_config_set()`
3. Print clear progress output (connecting → injecting → done)
4. Handle connection errors gracefully with a non-zero exit

--# Step 3: Generate apply_solution.py

Use `assets/apply_solution_template.py` as the base template. Customise it to restore all affected devices to their correct configuration by pushing the relevant `solutions/[Device].cfg` content.

The template includes a `--reset` flag that erases device configs before pushing the solution (two-phase: Phase 1 erase, Phase 2 push). This mirrors the `--reset` flag in `setup_lab.py` and guarantees a clean slate when stale fault config might otherwise linger after an additive push. Always include this flag — it is optional to the user at runtime but must be present in every generated script.

--# Step 4: Generate scripts/fault-injection/README.md

Use `assets/README_template.md` as the base. Fill in:
- One section per scenario: scenario number, target device, command to run
- **Ops-only — do NOT include fault names or descriptions that reveal what is broken**
- Usage instructions for injecting and restoring
- Prerequisites (EVE-NG lab running with all nodes started, netmiko installed)

--# Step 5: Validate

- [ ] One inject script per scenario
- [ ] `apply_solution.py` restores all affected devices
- [ ] `README.md` lists all available scenarios
- [ ] All scripts are idempotent (safe to run multiple times)
- [ ] Console ports match the workbook's Console Access Table
- [ ] Run `python3 -m py_compile` on every generated `.py` file — fix any SyntaxError before proceeding

--# Step 6: Update meta.yaml

Update provenance tracking for this lab.

- **If `meta.yaml` already exists** (lab-workbook-creator wrote it): append to `updated[]`:
  ```yaml
  updated:
    - date: "[YYYY-MM-DD]"
      agent: claude-sonnet-4-6
      skill: inject-faults
      skill_version: "[date of .agent/skills HEAD]"
      files:
        - scripts/fault-injection/inject_scenario_01.py
        # ... all inject scripts generated
        - scripts/fault-injection/apply_solution.py
        - scripts/fault-injection/README.md
  ```
- **If `meta.yaml` does not exist** (standalone run on a pre-existing lab): create it with `created` fields set to today's date and `agent: unknown` to indicate provenance was not tracked at generation time, then add the fault-injection files to `created.files`.

-# Output Structure

```
labs/<topic>/lab-NN-<slug>/
└── scripts/
    └── fault-injection/
        ├── README.md
        ├── inject_scenario_01.py
        ├── inject_scenario_02.py
        ├── inject_scenario_03.py
        └── apply_solution.py
```

-# Script Structure Reference

```python
#!/usr/bin/env python3
"""
Fault Injection Script: [Scenario Name]

Injects:     [Description of fault]
Target:      [Device name]
Fault Type:  [e.g., AS Mismatch, Passive Interface, Timer Mismatch]
"""

from netmiko import ConnectHandler
import sys

DEVICE_NAME  = "R2"
EVE_NG_HOST  = "192.168.x.x"  # EVE-NG server IP — set to match your environment
CONSOLE_PORT = 32768           # Dynamic port from EVE-NG web UI / Console Access Table

FAULT_COMMANDS = [
    "no router eigrp 100",
    "router eigrp 200",
]

def inject_fault():
    print(f"[*] Connecting to {DEVICE_NAME} on {EVE_NG_HOST}:{CONSOLE_PORT}...")
    try:
        conn = ConnectHandler(
            device_type="cisco_ios_telnet",
            host=EVE_NG_HOST,
            port=CONSOLE_PORT,
            username="", password="", secret="",
            timeout=10,
        )
        print(f"[+] Connected. Injecting fault...")
        conn.send_config_set(FAULT_COMMANDS)
        conn.disconnect()
        print(f"[+] Fault injected on {DEVICE_NAME}.")
    except Exception as e:
        print(f"[!] Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("=" * 50)
    print(f"Fault Injection: [Scenario Name]")
    print("=" * 50)
    inject_fault()
```

-# Common Issues

--# workbook.md has no troubleshooting scenarios
- **Cause:** The workbook was generated without a Section 9, or scenarios were not written.
- **Solution:** Stop. Ask the user to add at least 3 troubleshooting scenarios to `workbook.md` Section 9 before running this skill. Use `assets/troubleshooting_scenarios_template.md` (from the `lab-workbook-creator` assets) as a reference format.

--# Console Access Table not found in workbook
- **Cause:** Workbook was generated with a non-standard structure, or the user hasn't populated dynamic EVE-NG ports yet.
- **Solution:** Ask the user to start the lab in EVE-NG web UI, note the assigned telnet ports per node, and add them to the Console Access Table in `workbook.md` Section 3 before running this skill.

--# Scenario fault commands are unclear
- **Cause:** The solution section in the workbook doesn't clearly show what was misconfigured.
- **Solution:** Derive the fault as the inverse of the solution: if the solution says `ip ospf hello-interval 10`, the fault is `ip ospf hello-interval 30`.

--# apply_solution.py restores wrong state
- **Cause:** `solutions/` configs were updated after the fault scripts were generated.
- **Solution:** Regenerate `apply_solution.py` after any workbook or solutions update.

-# Examples

User: "Generate fault injection scripts for EIGRP Lab 03."

Actions:
1. Read `labs/eigrp/lab-03-[name]/workbook.md` — extract Console Access Table and 3 troubleshooting scenarios.
2. For each scenario, generate an `inject_scenario_0N.py` using the template from `assets/`.
3. Generate `apply_solution.py` to restore all affected devices.
4. Generate `scripts/fault-injection/README.md` with scenario descriptions.
5. Update `meta.yaml` (Step 6).
