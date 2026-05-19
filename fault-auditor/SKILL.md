---
name: fault-auditor
description: Retroactively audits existing lab workbooks for fault efficacy. Reads Section 9 troubleshooting tickets, maps topology redundancy, and reports whether each injected fault would actually cause its stated symptom. Produces a dated report file with per-ticket verdicts and fix suggestions. Invoked via /audit-faults <topic>/<lab-slug>.
---

# Fault Auditor Skill

Audits existing lab workbooks to verify that every troubleshooting ticket in
Section 9 will actually cause the symptom it claims — not get silently bypassed
by network redundancy. This is the retroactive version of the Fault Efficacy Gate
(Step 3c) built into the lab-assembler. It does NOT modify the workbook unless
`--fix` is passed; by default it produces a report.

-# Instructions

--# Step 1: Parse Arguments

Arguments format: `<topic>/<lab-slug> [--all] [--fix] [--open]`

Examples:
- `/audit-faults l3vpn-core/lab-01-route-reflector-design`
- `/audit-faults l3vpn-core --all`
- `/audit-faults l3vpn-core/lab-01-route-reflector-design --fix`

Resolution rules:
- `topic` = first path segment (`l3vpn-core`)
- `lab-slug` = second path segment (`lab-01-route-reflector-design`)
- Full lab path: `labs/<topic>/<lab-slug>/`
- `--all` = audit every lab directory under `labs/<topic>/` that has a `workbook.md` with Section 9
- `--fix` = after reporting, apply efficacy notes to workbook tickets and suggest specific fault redesigns. Always ask for confirmation before modifying.
- `--open` = after writing the report, print the report path so the user can open it

If the lab directory cannot be resolved, list available lab directories for that topic and stop.

--# Step 2: Read Inputs

Read in parallel:
1. `labs/<topic>/<lab-slug>/workbook.md` — extract all `### Ticket N — <Symptom>` blocks from Section 9
2. `labs/<topic>/baseline.yaml` — read `core_topology.links` and `labs[N].devices` for topology
3. `labs/<topic>/spec.md` (if it exists) — for protocol context (which protocols are running, RR design, etc.)

For `--all` mode, repeat for each lab directory that contains a workbook with Section 9. Process labs in numeric order.

--# Step 3: Extract Tickets

For each ticket, extract:
- **Ticket number and symptom heading** — the `### Ticket N — ...` line
- **Fault** — derive from the Fix `<details>` block: the inverse of the fix commands is the fault. If the fix *adds* `route-reflector-client`, the fault *omits* it. If the fix *changes* an AS number from 200 to 100, the fault is the wrong AS 200.
- **Expected symptom** — from the ticket heading and scenario context. Be precise: what `show` command on what device should show what?
- **Target device(s)** — which device(s) have their config changed by the inject script
- **Observing device(s)** — which device(s) the student runs `show` commands on to detect the fault

--# Step 4: Map Topology Redundancy

From `baseline.yaml`, build a mental model of:

1. **Physical paths** — every link sequence between any two devices. Identify redundant paths (dual-homed PEs, multiple P-routers, parallel links).
2. **BGP topology** — which devices peer with which. Identify route reflectors, clients, and non-clients. If there's a full-mesh or dual-RR design, note it.
3. **VRF topology** — which PEs import/export which RTs. Which CEs are single-homed vs dual-homed.
4. **IGP topology** — which adjacencies exist, which loopbacks are advertised via which interfaces.
5. **MPLS/LDP topology** — which interfaces have `mpls ip` enabled, which P-routers can build LSPs between which PE loopbacks.

--# Step 5: Redundancy Bypass Analysis (per ticket)

For each ticket, answer these questions:

### 5a — What is the single, precise observable symptom?

Example bad: "network is broken"
Example good: "`show bgp vpnv4 unicast all` on PE3 shows zero remote prefixes (only local RD 5:100 block present)"

### 5b — What are ALL possible paths for the affected traffic/control-plane?

For a VPNv4 route from PE1 to PE3:
- BGP paths: PE1 → P1(RR) → PE3 (primary), PE1 → PE2-XR → P1(RR) → PE3? (if full-mesh residual exists)
- Physical paths for the underlay LSP: PE1→P1→PE3 (via L1+L6), PE1→P2→PE3 (via L2+L7), PE1→P1→P2→PE3 (via L1+L3+L7)

### 5c — For each path: does the fault break it?

Walk every path from 5b and ask: "After the fault commands are applied, is this path still functional?"

- If **all paths are broken** → the fault is ✅ EFFECTIVE
- If **any path survives** → the fault is ❌ INEFFECTIVE — the symptom won't appear

### 5d — For ineffective faults, identify the surviving path

Describe exactly which alternate path bypasses the fault and why. Example:

> Surviving path: PE1→P2→PE3 (via L2+L7). The fault only disabled `mpls ip` on P1 Gi0/1 (L1), but MPLS is still running on P2 Gi0/1 (L2) and P2 Gi0/0 (L7). LDP builds the LSP from PE1 to PE3 via P2 instead.

### 5e — Propose a fix

For each ineffective fault, suggest the minimal change to make it effective:

1. **Compound fault** — also break the surviving path. "Also add `no mpls ip` on P2 Gi0/1 to break the PE1→P2→PE3 LSP."
2. **Retarget** — pick a non-redundant element. "Instead of breaking MPLS on one link, break the BGP session itself: remove `route-reflector-client` for PE3 on P1 — PE3 has no other BGP neighbor."
3. **Change symptom** — if the symptom can be reframed to something that IS observable despite redundancy. "The route still exists but with higher metric / via a different path. Symptom could be 'show ip route shows 172.16.2.0/24 via P2 instead of P1'." But prefer absolute breaks over degraded-state symptoms.

--# Step 6: Write Report

Create `labs/<topic>/<lab-slug>/reports/` if it doesn't exist.

Write `labs/<topic>/<lab-slug>/reports/fault-audit-<YYYY-MM-DD>.md`:

```markdown
# Fault Efficacy Audit — `<topic>/<lab-slug>`

**Date:** <YYYY-MM-DD>
**Auditor:** <agent-id>
**Skill version:** <YYYY-MM-DD from git log>

---

## Summary

| Tickets audited | Effective | Ineffective |
|----------------|-----------|-------------|
| <N>            | <count>   | <count>     |

---

## Topology Context

<brief paragraph describing the topology: device count, P-router count (redundancy),
single/dual RR, PE dual-homing, etc.>

Redundancy factors identified:
- <factor 1, e.g., "All PEs dual-homed to P1 and P2 — LSP has two paths">
- <factor 2, e.g., "Single RR (P1) — no BGP-path redundancy for RR-client routes">
- <factor 3, e.g., "CE1 single-homed to PE1 — no VRF-import redundancy">

---

---

### Ticket 1 — <symptom heading>

**Fault:** <description of what the inject script changes>

**Expected symptom:** <precise observable>

**Analysis:**
<walk through each path — is it broken by the fault?>

**Verdict:** ✅ EFFECTIVE / ❌ INEFFECTIVE

**Explanation:**
<why no path survives / which path survives and why>

<if INEFFECTIVE:>
**Fix suggestion:**
- **Option A:** <compound fault or retarget>
- **Option B:** <alternative>
- **Recommendation:** <which option is better and why>

---

### Ticket 2 — <symptom heading>
...

---

## Overall Assessment

<one paragraph: all clear, or N tickets need fixing. If all effective: "This lab's
troubleshooting scenarios are sound — all faults are guaranteed to cause their
stated symptoms." If any ineffective: "N tickets have redundancy bypasses that
may prevent the fault from being observable. See fix suggestions above.">
```

For `--all` mode, write one report per lab in its own `reports/` directory, then
write a summary at `labs/<topic>/reports/fault-audit-<YYYY-MM-DD>.md` listing all
labs and their pass/fail counts.

--# Step 7: Report to User

Print to the terminal:

```
=== Fault Audit: <topic>/<lab-slug> ===

Ticket 1 — <symptom>  ✅ EFFECTIVE
Ticket 2 — <symptom>  ✅ EFFECTIVE
Ticket 3 — <symptom>  ❌ INEFFECTIVE — PE1→P2→PE3 LSP bypasses the MPLS disable on P1 Gi0/1

Result: 1/3 tickets ineffective
Report: labs/<topic>/<lab-slug>/reports/fault-audit-<YYYY-MM-DD>.md
Exit code: 1
```

Exit codes:
- `0` — all faults effective (audit passed)
- `1` — at least one ineffective fault found (audit failed)

--# Step 8: --fix mode (optional)

If `--fix` was passed:

1. First complete Steps 1-7 (produce the report)
2. For each INEFFECTIVE ticket, present the fix suggestion to the user and ask:
   > "Ticket N is ineffective. Apply fix? [A/B/skip]"
3. When the user selects an option:
   - If **A** or **B**: Edit the workbook's Section 9 ticket to reflect the new fault design (update the symptom description, diagnosis steps, and fix block). Add the `<!-- Efficacy: ... -->` comment. Do NOT touch the inject scripts — that's a separate `/inject-faults` regeneration.
   - If **skip**: Note in the report that the ticket was skipped.
4. After all tickets are processed, update the report with an `## --fix Applied` section listing what was changed.
5. Re-run the audit on the modified tickets to confirm they now pass.
6. Report final exit code.

--# Step 9: --open mode (optional)

If `--open` was passed, after writing the report, print the absolute path to the report file so the user can open it:

```
Report written: C:\Users\...\labs\l3vpn-core\lab-01-route-reflector-design\reports\fault-audit-2026-05-19.md
```

-# Examples

User: `/audit-faults l3vpn-core/lab-01-route-reflector-design`

Actions:
1. Read `labs/l3vpn-core/lab-01-route-reflector-design/workbook.md` Section 9 → 3 tickets
2. Read `labs/l3vpn-core/baseline.yaml` → topology: P1+P2 dual core, single RR on P1, CE1 single-homed, CE2 single-homed
3. Ticket 1: Missing `route-reflector-client` on P1 for 5.5.5.5 → PE3's only BGP neighbor is P1 → ✅ EFFECTIVE
4. Ticket 2: Missing `send-community extended` on P1 for 1.1.1.1 → PE1's only BGP neighbor after migration → ✅ EFFECTIVE
5. Ticket 3: Missing neighbor 5.5.5.5 on P1 → PE3's only BGP neighbor → ✅ EFFECTIVE
6. All 3 pass → write report, exit 0

User: `/audit-faults l3vpn-core --all`

Actions:
1. List `labs/l3vpn-core/` for all `lab-*` directories with workbooks
2. Run audit on each: lab-00, lab-01, lab-02, lab-04 (lab-03 is capstone-config, likely has no Section 9)
3. Write per-lab reports + topic-level summary
4. Report aggregate result

-# Common Issues

--# Lab has no Section 9
- **Cause:** Capstone I (configuration) labs or early progressive labs may not have troubleshooting scenarios.
- **Action:** Report "No troubleshooting scenarios found in this workbook — nothing to audit." Exit 0.

--# baseline.yaml topology is incomplete
- **Cause:** The baseline predates the current topology (e.g., optional devices not yet declared).
- **Action:** Flag this in the report under a `## Limitations` section. Proceed with known topology; note that some redundancy paths may be missed.

--# Ticket Fix block doesn't clearly show the fault
- **Cause:** The Fix block shows resetting the entire BGP config with `no router bgp X` + re-adding everything. The actual fault is unclear.
- **Action:** Flag the ticket as `⚠️ UNCLEAR — cannot determine fault from Fix block`. Include in the report; treat as ineffective for exit code purposes. Suggest the workbook be updated with a clearer fault description in the Diagnosis block.
