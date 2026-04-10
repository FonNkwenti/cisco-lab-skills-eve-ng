# Lessons Learned — Cisco Lab Skills

Patterns, bugs, and design decisions from lab development across certifications.
Reference this when starting a new certification or extending a skill.
Newest entries at the top.

---

## Draw.io — Never Write XML from Scratch (ENARSI, 2026-02)

### ❌ Bug: topology.drawio generated as plain rectangles, ignoring drawio skill

**Trigger:** A topology was written from scratch as colored rounded rectangles with embedded
labels and default-black connection lines. The drawio skill was never read. Every visual rule
was violated: no Cisco icons, no white lines, no separate label cells, no last-octet labels.

**Prevention:**
- Before writing any `topology.drawio` XML, read `drawio/SKILL.md` §4.2–§4.7 in full
- Always start from the §4.7 reference XML snippets — never write drawio XML from scratch
- Run both the pre-write and post-write checklists in `lab-workbook-creator/SKILL.md` Step 5

---

## Platform / IOS Version — Verify Before Generating Configs (ENARSI, 2026-02)

### ❌ Bug: Config syntax incompatible with device IOS version

**Trigger:** Named mode EIGRP configs were generated for a device running IOS 12.4.
Named mode requires IOS 15.0+. Result: 70+ configs had to be reverted and regenerated.

**Prevention:**
- Before generating any router config, read `baseline.yaml` → `core_topology.devices[*].ios_image`
- If the lab uses named mode EIGRP, OSPF process variants, or any IOS 15+ feature,
  verify the image version is ≥ 15.0 before writing a single config line
- If image version and config syntax conflict, STOP and surface it — never silently fall back

---

## Network Statements — Cross-Check Against Router Interfaces (ENARSI, 2026-02)

### ❌ Bug: Spurious network statements propagate through all chained labs

**Trigger:** Routers contained `network` statements for links that didn't exist on that router.
These propagated silently because each lab's initial-configs are copied from the previous
lab's solutions/, so the error multiplied across all subsequent labs.

**Prevention:**
- When writing any `network` statement under `router eigrp` or `router ospf`, verify:
  the subnet matches an interface that exists on THIS router in the topology
- The check: `interface IP + wildcard` must match one of the router's own interface addresses
  as declared in `baseline.yaml core_topology`
- After generating initial-configs for lab-01 (or any chain-starting lab),
  manually trace each network statement to a specific interface before proceeding

---

## Optional Devices — Must Be Handled Explicitly at Introduction (ENARSI, 2026-02)

### ❌ Bug: New device introduced mid-chapter with missing configs

**Trigger:** A new device entered mid-chapter. Its initial-configs, solutions, and the
existing devices' updated solutions (with the new link) were all missing.

**Prevention:**
- When a lab's `baseline.yaml available_from` field introduces a new device:
  1. Create `initial-configs/[new_device].cfg` from `baseline.yaml core_topology`
     (not from previous solutions — the device has no prior history)
  2. Add the new link to ALL existing devices' `solutions/` configs in that lab
  3. Carry `solutions/[new_device].cfg` forward into the next lab's `initial-configs/`
- After generating: verify `solutions/` contains one `.cfg` per active device

---

## Fault Scripts — apply_solution.py Must Always Exist (ENARSI, 2026-02)

### ❌ Bug: `apply_solution.py` silently omitted from fault-injection output

**Trigger:** Inject scripts were generated but `apply_solution.py` was missing.

**Prevention:**
- After any fault-injection run, verify these files exist in `scripts/fault-injection/`:
  - `apply_solution.py` — exactly one, always present
  - `inject_scenario_NN.py` — one per troubleshooting ticket in workbook Section 9
  - `README.md` — exactly one, always present
- If `apply_solution.py` is missing: do not mark the lab complete — generate it immediately

---

## Fault Scripts — No Empty Stubs (ENARSI, 2026-02)

### ❌ Bug: Inject scripts with empty function bodies or `pass` statements

**Trigger:** Scripts were syntactically valid Python but functionally useless. File existence
checks passed but the scripts would silently do nothing when run.

**Prevention:**
- A fault script is only complete when it contains: device dict, `ConnectHandler`,
  and `send_config_set()` with actual fault commands
- After generating, spot-check at least one `inject_scenario_NN.py` per lab —
  verify it contains `ConnectHandler` and a non-empty command list
- Scripts with `pass`, `# TODO`, or empty command lists (`[]`) are defects, not drafts

---

## Python Script Generation

### ❌ Bug: `SyntaxError: unterminated string literal` in generated scripts

**Cause**: Fault injection / setup scripts using multiline f-strings with embedded CLI config blocks. The AI generates a string that ends prematurely or contains an unescaped `"""`.

**Fix**:
1. Represent CLI config as a Python `list` of strings, not a heredoc or f-string.
2. After generating any Python script, validate: `python3 -m py_compile script.py`

**Affected skills**: `fault-injector`, `lab-workbook-creator` (setup_lab.py)

---

## Draw.io Diagrams

### ❌ Bug: Link visually crossing through an intermediate device

**When**: Three devices share the same X coordinate and a bypass link connects non-adjacent ones (R1→R3 when R1, R2, R3 are all at x=400).

**Fix**: Offset intermediate devices horizontally by ≥100px. See `skills/drawio/SKILL.md` Section 4.8.

### ❌ Bug: Tunnel overlays routing through devices instead of arcing above

**Fix**: Use `exitX=0.5;exitY=0` (top-center) and add two arc waypoints above both endpoints. See `skills/drawio/SKILL.md` Section 4.9.3.

---

## Netmiko / EVE-NG Automation

### ⚡ Pattern: Telnet connections to EVE-NG consoles

```python
ConnectHandler(
    device_type="cisco_ios_telnet",
    host="<eve-ng-ip>",   # EVE-NG server IP — not 127.0.0.1
    port=32768,           # Dynamic port from EVE-NG web UI / Console Access Table
    username="",          # Must be present but empty — do NOT omit
    password="",          # Same
    secret="",            # Same
    timeout=10,
)
```

Omitting `username`, `password`, or `secret` causes `TypeError` in some Netmiko versions.

**Key difference from GNS3:** EVE-NG ports are dynamic — there is no static `500N` convention. Always read ports from the Console Access Table in `workbook.md` Section 3 or discover via the EVE-NG REST API.

### ⚡ Pattern: EVE-NG interface naming differs from GNS3 Dynamips

| Old (Dynamips) | New (EVE-NG) | Platform |
|----------------|-------------|---------|
| `FastEthernet0/0` | `GigabitEthernet0/0` | IOSv |
| `FastEthernet1/0` | `GigabitEthernet1/0` | IOSvL2 (switchport) |
| `GigabitEthernet3/0` | `GigabitEthernet1` | CSR1000v |
| `FastEthernet0/0` | `Ethernet0/0` | IOL L3 |

Never use `FastEthernet` in new EVE-NG labs unless using a legacy Dynamips image.

---

## Lab Design

### ⚡ Pattern: Config chaining — never remove, only add

Solutions from Lab N become initial configs for Lab N+1. Never `no` a command between labs unless that lab explicitly teaches undoing it.

### ⚡ Pattern: Always run `spec-creator` first

Starting a topic by jumping to `lab-workbook-creator` for Lab 00 causes topology problems in later labs (interface exhaustion, no room for optional devices). `spec-creator` pre-reserves IPs and interfaces for all planned labs via `baseline.yaml`.

### ⚡ Pattern: Console Access Table is required for fault-injector

The `fault-injector` skill parses port mappings from the workbook's Console Access Table (Section 3). Without it, generated scripts use placeholder ports. Always include:

| Device | Port | Connection Command |
|--------|------|--------------------|
| R1 | 5001 | `telnet 127.0.0.1 5001` |

---

## Style Iterations (ENCOR history)

| Version | Change | Reason |
|---------|--------|--------|
| v1 | Black connection lines | Default Draw.io |
| v2 | White lines (`#FFFFFF`) | Invisible on dark backgrounds |
| v3 | Labels below icon | Default position |
| v4 | Labels left/right (empty side rule) | Overlapped connection lines |
| v5 | Added IP last-octet labels | Students couldn't identify interface ownership |
