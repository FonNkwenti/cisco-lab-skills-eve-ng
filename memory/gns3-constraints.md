> **DEPRECATED:** This file applies to GNS3/Apple Silicon. For EVE-NG on Windows/Intel, see `eve-ng-constraints.md`.

# GNS3 Constraints — Apple Silicon (M1/M2/M3) — ARCHIVED

Source of truth for all hardware decisions in lab generation.

## What Works

| Component | Details |
|-----------|---------|
| Dynamips | Only emulation engine supported |
| c7200 IOS | `c7200-adventerprisek9-mz.153-3.XB12.image`, Idle PC `0x60629004` |
| c3725 IOS | `c3725-adventerprisek9-mz.124-15.T14.image`, Idle PC `0x60c09aa0` |
| VPCS | For ping testing / host simulation |
| Unmanaged Switch | GNS3 generic switch for L2 |

## What Does NOT Work

| Component | Why |
|-----------|-----|
| VirtualBox / VMware VMs | Requires Intel VT-x — not available on M1 |
| IOS-XR / NX-OS | Not supported on c7200/c3725 |
| CSR1000v / Containerlab | Requires x86 VM or Docker |

## Router Interface Reference

### c7200 (Hub/Core/ABR)
| Slot | Adapter | Interfaces |
|------|---------|------------|
| 0 | C7200-IO-FE | fa0/0 |
| 1 | PA-2FE-TX | fa1/0, fa1/1 |
| 2 | PA-4T+ | s2/0–s2/3 |
| 3 | PA-GE | gi3/0 |

### c3725 (Branch/Spoke)
| Slot | Adapter | Interfaces |
|------|---------|------------|
| 0 | GT96100-FE | fa0/0, fa0/1 |
| 1 | NM-16ESW | fa1/0–fa1/15 (L2 labs) |
| 2 | NM-4T | s2/0–s2/3 |

## Console Port Mapping (Base: 5000)

| Router | Port | | Router | Port |
|--------|------|-|--------|------|
| R1 | 5001 | | R5 | 5005 |
| R2 | 5002 | | R6 | 5006 |
| R3 | 5003 | | R7 | 5007 |
| R4 | 5004 | | | |
