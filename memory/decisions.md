# Architecture & Implementation Decisions

Decisions that deviate from spec, affect compatibility, or carry forward to future labs.

---

## network-assurance / lab-01-flexible-netflow (2026-04-19)

### FNF commands not verified against live hardware

**Context:** `ios-compatibility.yaml` shows all Flexible NetFlow commands (`flow record`,
`flow exporter`, `flow monitor`, `ip flow monitor`, `ipv6 flow monitor`) as `unknown` for
ios-classic (IOSv). The verify script ran but found no console ports configured for live
routers, so no real verification occurred.

**Decision:** Treated FNF commands as `pass` on IOSv 15.x — Cisco's IOSv image ships with
FNF support in IOS 15.2+. If a student encounters issues, the fallback is to use a CSR1000v
(ios-xe) for R1, which has definitive `pass` status.

**Impact:** FNF lab works on IOSv 15.x in practice, but is formally unverified. Update
ios-compatibility.yaml if/when live verification is performed.

---

### OSPFv3 syntax: classic IOS used instead of new-style (spec deviation)

**Context:** `spec.md` described the IPv6 routing pre-infrastructure using new-style OSPFv3
syntax (`router ospfv3 1` / `ospfv3 1 ipv6 area 0`). The ios-compatibility table shows this
syntax as `pass` only on ios-xe, `unknown` on ios-classic.

**Decision:** Switched to classic IOS syntax for all IOSv devices:
- `ipv6 router ospf 1` (process configuration)
- `ipv6 ospf 1 area 0` (per-interface)

**Impact:** Lab initial-configs and solutions use classic syntax throughout. If the lab is
later migrated to CSR1000v, update to `router ospfv3 1` / `ospfv3 1 ipv6 area 0` and
re-verify.

---

## network-assurance / lab-02-span-rspan (2026-04-19)

### SPAN/RSPAN monitor session commands not verified against live hardware

**Context:** All `monitor session` commands are `unknown` in `ios-compatibility.yaml` for
ios-l2 (IOSvL2). The verify script ran but found no console ports configured, so no real
verification occurred.

**Decision:** Treated all `monitor session` commands as `pass` on IOSvL2 — SPAN/RSPAN has
been a universal IOSvL2 feature since IOS 12.x and is supported on all IOSvL2 images
used in EVE-NG.

**Impact:** Lab works on IOSvL2 in practice, but is formally unverified. Update
ios-compatibility.yaml if/when live verification is performed.

---

## network-assurance / lab-03-ip-sla (2026-04-19)

### IP SLA and track commands not verified against live hardware

**Context:** All `ip sla`, `ip sla schedule`, `ip sla responder`, `track`, and tracked
static route commands are `unknown` in `ios-compatibility.yaml` for ios-classic (IOSv).
The verify script ran but found no console ports configured for live routers.

**Decision:** Treated all IP SLA commands as `pass` on IOSv 15.x — IP SLA (formerly RTR)
has been in IOS since 12.x. Basic probes (icmp-echo, udp-jitter), scheduling, and track
objects tied to SLA reachability are all standard IOSv features. The `ip sla responder`
global command for UDP jitter is also present on IOSv 15.x.

**Impact:** Lab works on IOSv 15.x in practice, but is formally unverified. Update
ios-compatibility.yaml if/when live verification is performed.

---

## automation / lab-04-capstone-config (2026-04-19)

### IPv4-only despite spec.md suggesting dual-stack from lab-01

**Context:** `spec.md` for the automation topic mentioned dual-stack carried forward from
lab-01. Grep of all `labs/automation/*/initial-configs/*.cfg` and `solutions/*.cfg` files
found zero `ipv6 address` statements — the entire automation chapter chain is IPv4-only.

**Decision:** Lab 04 (capstone_i) stays IPv4-only to maintain chain consistency. Dual-stack
is not present in any prior automation lab, so introducing it at the capstone would require
additional IPv6 addressing spec that does not exist in `baseline.yaml`.

**Impact:** If a future revision adds IPv6 to the automation chapter, all labs (00-05) must
be updated together. `baseline.yaml` must gain IPv6 addressing before lab rebuilds begin.

---
