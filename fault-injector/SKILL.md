---
name: fault-injector
description: Generates Python fault-injection scripts for GNS3 lab troubleshooting scenarios using Netmiko. Use when the user asks to "inject faults", "generate troubleshooting scripts", "create fault scenarios", "add troubleshooting practice", or automatically after lab-workbook-creator generates a workbook.
---

# Fault Injector Skill

Generates Python scripts that inject the troubleshooting scenarios defined in lab workbooks into the live GNS3 environment. Enables students to set up fault conditions for exam-style troubleshooting practice without manual configuration.

-# Instructions

--# Step 1: Parse Inputs

Read from the lab directory:
1. `workbook.md` — extract troubleshooting scenarios from Section 8 and the Console Access Table
2. Console Access Table → device-to-port map: `{"R1": 5001, "R2": 5002, ...}`
3. From each scenario extract: **Scenario Number**, **Target Device**, **Fault Type**, **Commands to inject**

--# Step 2: Generate Fault Injection Scripts

For each scenario (minimum 3 per lab), generate `scripts/fault-injection/inject_scenario_0N.py`.

Use `assets/inject_scenario_01_template.py` (and `_02`, `_03`) as base templates. Customise:
- `DEVICE_NAME` and `CONSOLE_PORT` from the Console Access Table
- `FAULT_COMMANDS` list from the scenario's solution section
- Docstring describing exactly what fault is injected

Each script must:
1. Connect via Netmiko `device_type="cisco_ios_telnet"` to `localhost:[console_port]`
2. Apply fault commands via `send_config_set()`
3. Print clear progress output (connecting → injecting → done)
4. Handle connection errors gracefully with a non-zero exit

--# Step 3: Generate apply_solution.py

Use `assets/apply_solution_template.py` as the base template. Customise it to restore all affected devices to their correct configuration by pushing the relevant `solutions/[Device].cfg` content.

--# Step 4: Generate scripts/fault-injection/README.md

Use `assets/README_template.md` as the base. Fill in:
- One section per scenario: name, fault description, target device, command to run
- Usage instructions for injecting and restoring
- Prerequisites (GNS3 running, netmiko installed)

--# Step 5: Validate

- [ ] One inject script per scenario
- [ ] `apply_solution.py` restores all affected devices
- [ ] `README.md` lists all available scenarios
- [ ] All scripts are idempotent (safe to run multiple times)
- [ ] Console ports match the workbook's Console Access Table

-# Output Structure

```
labs/[chapter]/[lab-NN]/
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
CONSOLE_HOST = "127.0.0.1"
CONSOLE_PORT = 5002

FAULT_COMMANDS = [
    "no router eigrp 100",
    "router eigrp 200",
]

def inject_fault():
    print(f"[*] Connecting to {DEVICE_NAME} on port {CONSOLE_PORT}...")
    try:
        conn = ConnectHandler(
            device_type="cisco_ios_telnet",
            host=CONSOLE_HOST,
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
- **Cause:** The workbook was generated without a Section 8, or scenarios were not written.
- **Solution:** Stop. Ask the user to add at least 3 troubleshooting scenarios to `workbook.md` Section 8 before running this skill. Use `assets/troubleshooting_scenarios_template.md` (from the `lab-workbook-creator` assets) as a reference format.

--# Console Access Table not found in workbook
- **Cause:** Workbook was generated with a non-standard structure.
- **Solution:** Fall back to default port convention (R1=5001, RN=500N). Warn the user.

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
