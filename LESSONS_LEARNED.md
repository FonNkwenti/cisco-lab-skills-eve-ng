# Lessons Learned — Cisco Lab Skills

Patterns, bugs, and design decisions from lab development across certifications.
Reference this when starting a new certification or extending a skill.
Newest entries at the top.

---

## 2026-05-13 — IOS-XR SR+LDP coexistence: `show mpls forwarding prefix` shows LDP entry, not SR entry

Confirmed on XRv Classic 6.3.1 during lab-02 SR/LDP coexistence work.

### Two forwarding entries coexist for the same prefix

When both SR-MPLS and LDP are active on IOS-XR, the MPLS forwarding table contains
**two separate entries** for the same IP prefix:

- **SR entry:** keyed by local SR label (SRGB base + prefix-SID index, e.g. 16003).
  Shown by `show mpls forwarding labels 16003 16003 detail` — displays `SR Pfx (idx N)`.
- **LDP entry:** keyed by the IP prefix itself, local label dynamically allocated
  outside the SRGB (e.g. 24008).
  Shown by `show mpls forwarding prefix 10.0.0.3/32 detail` — displays the IP prefix as ID.

`show mpls forwarding prefix <ip>/<len>` **always shows the LDP entry**, not the SR entry.
A student who runs this command will see a dynamic label (24xxx) and conclude LDP is
winning — but this is misleading. The routing table selects SR by default.

**Correct commands to confirm SR wins:**
1. `show route ipv4 <prefix> detail` — look for `labeled SR` and `Local Label: 16003`
2. `show mpls forwarding labels 16003 16003 detail` — shows `SR Pfx (idx N)`, outgoing Pop

**Rule:** In SR+LDP coexistence workbooks, never use `show mpls forwarding prefix` alone
as evidence of SR winning. Always pair it with `show route detail` or
`show mpls forwarding labels <srgb+index>` to show the SR entry explicitly.

---

## 2026-05-13 — IOS-XR MPLS: `show mpls forwarding <prefix>` requires the `prefix` keyword

Confirmed on XRv Classic 6.3.1 during lab-02 SR/LDP coexistence work.

### `show mpls forwarding 10.0.0.3/32` — INVALID on IOS-XR

On IOS-XR, passing a destination prefix directly after `show mpls forwarding` is
rejected with `% Invalid input detected at '^' marker.`. The `prefix` keyword is
mandatory between `forwarding` and the IP address/prefix-length.

**Correct forms:**
- Summary: `show mpls forwarding prefix 10.0.0.3/32`
- Detail:   `show mpls forwarding prefix 10.0.0.3/32 detail`

On IOS-XE / IOSv the prefix can follow `forwarding` directly without the keyword.

**Rule:** Always write `show mpls forwarding prefix <ip>/<len>` in IOS-XR workbooks
and scripts. Never write `show mpls forwarding <ip>/<len>` (no `prefix` keyword).

---

## 2026-05-13 — IOS-XR Pipe Modifiers: `| section` and `| begin` are NOT supported; use `| include` or `| utility`

Confirmed by live probing XRv9k 24.3.1 during SRv6 lab work.

### `| section` — INVALID on all IOS-XR versions

`sh isis fast-reroute | section No FRR backup` is rejected on IOS-XR 24.3.1 with:
`% Invalid input detected at '^' marker.`

The `| section` and `| begin` pipe modifiers are **IOS-XE/IOSv-only features** and
do not exist in the IOS-XR command parser. IOS-XR has a different pipe grammar:

| IOS-XE Modifier | IOS-XR Alternative |
|-----------------|--------------------|
| `\| section <pattern>` | `\| include <pattern>` or `\| utility "sed -n '/<pattern>/,/^[^ ]/p'"` |
| `\| begin <pattern>` | `\| utility "sed -n '/<pattern>/,$ p'"` |
| `\| include <pattern>` | `\| include <pattern>` (same — works on both) |
| `\| exclude <pattern>` | `\| exclude <pattern>` (same — works on both) |
| `\| redirect <file>` | `\| file <file>` |
| `\| append <file>` | `\| file <file> append` |
| `\| count <pattern>` | `\| utility "grep -c <pattern>"` |
| — | `\| utility <command>` (sed, awk, grep, cut, sort, uniq, head, tail) |

### The `| utility` pipe is the IOS-XR superpower

IOS-XR has a unique `| utility <command>` pipe that passes output through
standard Unix utilities. This enables powerful filtering that actually exceeds
IOS-XE's capabilities:

```
# Emulate | section No FRR backup
sh isis fast-reroute | utility "sed -n '/No FRR backup/,/^[^ ]/p'"

# Emulate | begin No FRR backup
sh isis fast-reroute | utility "sed -n '/No FRR backup/,$ p'"

# Count lines matching 'backup'
sh isis fast-reroute | utility "grep -c backup"

# Show first 30 lines
sh isis fast-reroute | utility "head -30"

# Sort unique prefixes
sh route ipv4 | utility "grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+\.[0-9]\+/[0-9]\+'" | utility sort -u
```

### Rule

- Never write `| section` or `| begin` in workbook verification steps targeting
  IOS-XR platforms.
- For simple pattern filtering, use `| include` (works on both XR and XE).
- For section-style multi-line filtering, use `| utility "sed -n '...'"`.
- Update all IOS-XR-targeted workbook verification steps that currently use
  `| section` or `| begin`.

Entries added to `reference-data/ios-compatibility.yaml` with `ios-xr: fail` for
both `| section` and `| begin`. `| utility` documented with `ios-xr: pass`.

---

## 2026-05-13 — IOS-XR TI-LFA: `show isis fast-reroute topology` does not exist; use `detail`

Confirmed by live probing XRv9k on segment-routing lab-01 (TI-LFA).

### `show isis fast-reroute topology ipv4 unicast` — INVALID on all tested XR versions

`show isis fast-reroute topology ipv4 unicast` and `show isis fast-reroute ipv4 <prefix>`
are rejected with `% Invalid input detected at '^' marker.` on IOS-XRv9k 7.1.1 and 24.3.1.
These commands do not exist in the XR show tree.

**Correct commands:**
- All prefixes: `show isis fast-reroute detail`
- Single prefix: `show isis fast-reroute detail <prefix/len>`
- Repair label stack: `show mpls forwarding prefix <prefix/len> detail` — look for the `(!)` backup entry; the label stack is shown under `Label Stack (Top -> Bottom): { ... }`
- Route-level backup: `show route ipv4 <prefix/len> detail` — shows backup NH and imposed label

**Rule:** Never use `show isis fast-reroute topology` or `show isis fast-reroute ipv4 <prefix>`
in workbooks or scripts targeting IOS-XR platforms. Always use `show isis fast-reroute detail`.

### BFD sessions do not form on classic XRv 6.3.1 for IS-IS

On classic IOS-XRv 6.3.1 (software forwarding platform), BFD sessions for IS-IS never
establish even when `bfd minimum-interval` and `bfd multiplier` are correctly configured
on both sides. `show bfd session` returns empty; `show isis adjacency detail` shows
BFD IPv4: None. This is a platform limitation — BFD sub-second timers require hardware
forwarding (XRv9k or physical).

**Workaround:** Use `show isis adjacency detail` to verify TI-LFA protection. When TI-LFA
is active, each adjacency shows its SID as `(protected)` with a backup label stack,
backup interface, and backup next-hop — this confirms the repair path is pre-installed
independent of BFD.

**Rule:** On workbooks targeting classic XRv, note the BFD limitation and direct students
to `show isis adjacency detail` instead of `show bfd session` for protection verification.

### Adjacent PQ-node repair stack is one label, not two

When the TI-LFA PQ-node is R2's immediate next-hop neighbor, IOS-XR imposes only one
repair label (the destination's prefix SID). The outer steering SID is omitted because
the PQ-node is already the next-hop. Example: R2 protecting L2 (R2↔R3), PQ-node = R1
(adjacent on L1) — repair label stack for 10.0.0.3/32 is `{ 16003 }`, not `{ 16001, 16003 }`.
A two-label stack is only needed when the PQ-node is a non-adjacent router.

### Fault injection: must remove `fast-reroute per-prefix` entirely to create observable coverage gap

In ring topologies (e.g., 4-node ring with diagonal), classic LFA already provides 100%
coverage because every neighbor has a shorter alternate path. Removing only
`fast-reroute per-prefix ti-lfa` (leaving `fast-reroute per-prefix` intact) leaves classic
LFA active — `show isis fast-reroute summary` still shows 100% and `show isis fast-reroute
detail` still shows a backup entry. No symptom is observable.

To create an observable FRR coverage gap you must remove `fast-reroute per-prefix` entirely
(which also removes `ti-lfa`). With both commands absent, the router computes no repair path
for that interface's destinations, and the summary shows `Unprotected > 0`.

**Rule:** Fault inject scripts that target FRR coverage must remove `no fast-reroute per-prefix`
(not just `no fast-reroute per-prefix ti-lfa`) when the topology has classic LFA coverage.

### TI-LFA guarantees 100% coverage even without diagonal links — repair paths grow, not coverage

When the L5 diagonal (R1↔R3) is removed from the topology, `show isis fast-reroute summary`
on all routers continues to show 100% coverage. TI-LFA recomputes a 2-label repair stack
(P-node SID + prefix SID) to route around the now-missing shortcut. The observable symptom
of losing the diagonal is: (1) R1's adjacency count drops from 3 to 2, and (2) `show isis
fast-reroute detail` on R2 shows an explicit P-node label in the backup path.

**Rule:** When writing troubleshooting tickets for topology faults on TI-LFA labs, do not
claim coverage drops — it won't. Frame the symptom as: missing IS-IS adjacency + repair
path complexity increase (P-node label added to stack).

---

## 2026-05-12 — IOS-XR Segment-Routing: two LLM-generated syntax bugs confirmed on live nodes

Discovered by live probing XRv Classic 6.3.1 and XRv9k 24.3.1 via Netmiko telnet.
Both bugs affect configs generated by LLMs for IOS-XR segment-routing labs.

### Bug 1: `bfd fast-detect` inside IS-IS address-family (both platforms, all XR versions)

The line `bfd fast-detect` inside `router isis / interface / address-family ipv4 unicast`
is rejected on all IOS-XR versions tested with:
`% Invalid input detected at '^' marker.`

BFD under IS-IS is activated solely by:
```
router isis PROCESS
 interface GigabitEthernet0/0/0/N
  bfd minimum-interval 50
  bfd multiplier 3
```
No additional `bfd fast-detect` command is needed or accepted inside the AF context.

**Rule:** Never emit `bfd fast-detect` inside an IS-IS interface address-family block on
`ios-xr` platform targets. Remove it from any existing config before pushing.

### Bug 2: `index N address ipv4 X.X.X.X` in SR-TE segment-lists (both platforms)

The `address ipv4` form for node-SID addressing inside segment-lists is rejected on all
IOS-XR versions tested. The correct form is `mpls label`:

```
# WRONG — rejected on XRv 6.3.1 and XRv9k 24.3.1:
segment-list EXPLICIT_R4_R3
 index 10 address ipv4 10.0.0.4

# CORRECT — verified pass on XRv9k 24.3.1:
segment-list EXPLICIT_R4_R3
 index 10 mpls label 16004
```

Label value = SRGB base (16000) + prefix-SID index. With SRGB 16000–23999:
R1=16001, R2=16002, R3=16003, R4=16004.

**Rule:** Always use `index N mpls label XXXXX` in SR-TE segment-list entries.
Never use `index N address ipv4 X.X.X.X`.

### XRv Classic 6.3.1 additional limits

Named `segment-list` definitions do not exist at all in IOS-XR 6.3.1 `traffic-eng`.
SR-TE features added in 7.x+ (affinity-map, on-demand color, dynamic metric type,
disjoint-path, PCEP in dynamic paths) are also absent. XRv Classic is suitable only for
labs 00–02 and 05 of the segment-routing topic. Labs 03–04 require XRv9k.

### XRv9k version note

The installed XRv9k image reports **24.3.1**, not 7.1.1 as previously documented.
Updated in `eve-ng/SKILL.md` and `reference-data/ios-compatibility.yaml`.

---

## 2026-05-11 — IS-IS NSF, IS-IS NSR, and BGP NSR are REJECTED on IOSv

Three high-availability commands are not present in the IOSv command set
(vios-adventerprisek9-m.SPA.156-2.T = IOS 15.6(2)T; also confirmed on 15.9(3)M6).
They fail with "% Invalid input" or similar — not merely accepted as no-ops.

### rejected commands

| Command | Context | Error |
|---------|---------|-------|
| `nsf ietf` | `router isis` | rejected (command not present) |
| `nsr` | `router isis` | rejected (command not present) |
| `bgp nsr` | `router bgp` | rejected (command not present) |

### working commands

| Command | Context | Notes |
|---------|---------|-------|
| `bgp graceful-restart` | `router bgp` | works on IOSv |

### Impact on fast-convergence labs

- lab-01 (NSF/NSR): Tasks 1 (IS-IS NSF) and Part A of Task 3 are conceptual
  reference only — no live config possible. Task 2 (BGP GR) works live.
- lab-01 solutions: Must NOT include `nsf ietf`, `nsr`, or `bgp nsr` on any .cfg.
- lab-02, lab-03 initial-configs (which chain from lab-01 solutions): Must also
  exclude these commands. If they leak through, `setup_lab.py` will fail when it
  pushes the configs.

### Propagation rule

Whenever a progressive lab chain introduces a new lab-N, verify that lab-(N-1)'s
solutions contain only commands that pass on the target platform. Run `grep -rn
"nsf ietf\|nsr$\|bgp nsr"` across the topic directory after building solutions.

Entries corrected in `reference-data/ios-compatibility.yaml` from `pass` to `fail`
for `ios-classic` on all three commands.

---

## 2026-05-08 — IOSv MPLS TE command differences vs. physical IOS

Three IOSv-specific behaviours discovered during MPLS lab-03 (RSVP-TE) development.
All apply to IOSv 15.9(3)M6; treat all `ios-classic` MPLS labs as affected.

### 1. `mpls mtu` requires the `override` keyword on IOSv

Physical IOS: `mpls mtu 1508` (accepted)
IOSv: `% Invalid input detected` — the `override` keyword is mandatory.

**Rule:** Always emit `mpls mtu override <size>` in configs targeting IOSv.
Never use bare `mpls mtu <size>`. Check `baseline.yaml platform` before generating
any MPLS interface config with an MTU override.
Entries added to `reference-data/ios-compatibility.yaml` under `mpls mtu override`.

### 2. `show mpls interfaces detail` reports `LSP Tunnel labeling enabled/not enabled`, not `Traffic Engineering: enabled`

Documentation and physical IOS show `Traffic Engineering: enabled`.
IOSv 15.9 shows `LSP Tunnel labeling enabled` (or `not enabled`).

**Rule:** In workbook verification steps and cheatsheets, always use
`LSP Tunnel labeling enabled` as the expected string for IOSv MPLS TE verification —
never `Traffic Engineering: enabled`. This affects troubleshooting tickets that
ask students to compare against a known-good field name.

### 3. `show mpls traffic-eng tunnels <TunnelN> detail` — `detail` keyword rejected on IOSv

On physical IOS, appending `detail` after a named tunnel gives extended output.
On IOSv 15.9, `detail` causes `% Invalid input detected`. Specifying a single
tunnel by name already gives full verbose output — `detail` is redundant and harmful.

**Rule:** Never append `detail` after a specific tunnel name in show commands
targeting IOSv. Use `show mpls traffic-eng tunnels Tunnel10` (no `detail`).
The `detail` keyword is only valid when listing ALL tunnels: `show mpls traffic-eng tunnels detail`.

---

## 2026-05-01 — `no ip prefix-list NAME seq N` (seq-only) is rejected on IOSv

`no ip prefix-list PFX_NAME seq 5` fails on IOSv with `% Incomplete command.`
The insertion of the replacement entry then fails with `%Insertion failed - seq # e`
because seq 5 still exists. Both failures are silent at the Python/Netmiko level —
the script exits 0 but no config change was applied.

**Rule:** Always use `no ip prefix-list NAME` (delete the entire list) when removing or
replacing a prefix-list entry on ios-classic targets, then re-add the correct entry.
This is portable across all IOSv versions and IOS-XE.

**Related:** `clear ip bgp X soft in` triggers a Route Refresh from the neighbor.
Allow ~5 seconds for the re-advertisement cycle to complete before reading
`show ip bgp neighbors X routes` — checking immediately after the command returns
may still show stale adj-RIB-in entries.
Entry added to `reference-data/ios-compatibility.yaml` under `no ip prefix-list NAME seq N`.

---

## 2026-05-01 — BGP peer-group template `activate` is a phantom command on IOSv

**Platform:** IOSv (confirmed 15.6(2)T; treat all `ios-classic` as affected until proven otherwise)

`neighbor PEER-GROUP activate` inside `address-family ipv4` is rejected on IOSv with:

```
% Activation failed : configure "bgp listener range" before activating peergroup
```

IOS treats peer-group template activation as a Dynamic Neighbors feature and requires
`bgp listen range` first — which is not needed for static iBGP.

**Workaround:** Activate each peer-group member individually:

```
address-family ipv4
 neighbor 10.0.0.2 activate
 neighbor 10.0.0.3 activate
```

Members still inherit all peer-group attributes (remote-as, update-source, next-hop-self).
The `neighbor IBGP next-hop-self` line in the address-family is preserved and works.
`neighbor PEER-GROUP activate` works correctly on IOS-XE (CSR1000v 17.03.05).

**Rule:** Never emit `neighbor PEER-GROUP activate` in address-family config blocks for
`ios-classic` platform targets. Always activate members individually.
Entry added to `reference-data/ios-compatibility.yaml` under `neighbor PEER-GROUP activate`.

---

## 2026-04-24 — Three-model comparison surfaced three skill-level bugs

From the OSPF lab-01 three-model build comparison (Haiku / Sonnet / Opus):

1. **Inconsistent drawio placement rule:** `lab-assembler` said drawio at lab
   root, but `topology/README.md` in a subfolder. Haiku followed the letter
   of the rule (wrong folder); Sonnet/Opus inferred the consistent layout.
   **Fix:** Both `drawio/SKILL.md` and `lab-assembler/SKILL.md` now specify
   `topology/topology.drawio` and Step 5 has a path assertion in its
   post-write checklist.

2. **meta.yaml subagent bleed:** `fault-injector/SKILL.md` Step 6 told the
   subagent to write meta.yaml directly, causing it to overwrite the parent's
   provenance with its own identity (Haiku and Sonnet builds both required
   manual overrides post-dispatch).
   **Fix:** Fault-injector no longer touches meta.yaml. lab-assembler owns
   meta.yaml; fault-injector returns its file list via Output Confirmation.

3. **`__pycache__` litter:** Both skills instructed `python3 -m py_compile`
   with no cleanup. Every build left `__pycache__/` directories in
   `scripts/fault-injection/` and sometimes at lab root.
   **Fix:** Syntax-check via `ast.parse` (no filesystem side effect) or
   follow py_compile with explicit `rm -rf __pycache__`. Final-cleanup step
   added to lab-assembler. `.gitignore` entries already present.

Detection path: side-by-side review of three same-spec builds made the
pattern visible. Single-build review would have missed #1 and #3.

---

## Draw.io — Never Write XML from Scratch (ENARSI, 2026-02)

### ❌ Bug: topology.drawio generated as plain rectangles, ignoring drawio skill

**Trigger:** A topology was written from scratch as colored rounded rectangles with embedded
labels and default-black connection lines. The drawio skill was never read. Every visual rule
was violated: no Cisco icons, no white lines, no separate label cells, no last-octet labels.

**Prevention:**
- Before writing any `topology.drawio` XML, read `drawio/SKILL.md` §4.2–§4.7 in full
- Always start from the §4.7 reference XML snippets — never write drawio XML from scratch
- Run both the pre-write and post-write checklists in `lab-assembler/SKILL.md` Step 5

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

**Affected skills**: `fault-injector`, `lab-assembler` (setup_lab.py)

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

Starting a topic by jumping to `lab-assembler` for Lab 00 causes topology problems in later labs (interface exhaustion, no room for optional devices). `spec-creator` pre-reserves IPs and interfaces for all planned labs via `baseline.yaml`.

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
