---
name: gns3
description: GNS3 hardware constraints and platform reference for Apple Silicon (Dynamips only). Use when generating lab configs, creating baseline.yaml topology definitions, selecting router platforms, assigning interfaces, or any time GNS3 platform constraints (c7200 vs c3725, interface slots, console ports) must be verified for Apple M1/M2/M3 compatibility.
---

# GNS3 Lab Skill (Apple Silicon)

Hardware reference and constraint guide for the GNS3 environment running on Apple M1/M2/M3. All lab generation must comply with these constraints.

-# Instructions

--# 1. Host Architecture & Constraints

This GNS3 environment uses **Dynamips** (Cisco IOS emulation) only.

- **No virtualisation:** Intel VT-x, VMware, and VirtualBox VMs are NOT supported.
- **No NX-OS or IOS-XR:** Strictly limited to classic IOS images.
- **Supported images:** `c7200` and `c3725` only.

--# 2. Platform Selection Guide

| Condition | Use |
|-----------|-----|
| Hub, Core, or ABR role | `c7200` |
| IPsec, GRE crypto features needed | `c7200` |
| More than 3 FastEthernet interfaces needed | `c7200` |
| Branch, Spoke, or Edge role | `c3725` |
| L2 switching ports needed (NM-16ESW) | `c3725` |
| Serial WAN links | either (both support `NM-4T`) |

--# 3. Hardware Templates (Source of Truth)

### c7200

| Slot | Adapter | Interfaces |
|------|---------|------------|
| 0 | `C7200-IO-FE` | fa0/0 |
| 1 | `PA-2FE-TX` | fa1/0, fa1/1 |
| 2 | `PA-4T+` | s2/0–s2/3 |
| 3 | `PA-GE` | gi3/0 |

- **RAM:** 512 MB
- **IOS Image:** `c7200-adventerprisek9-mz.153-3.XB12.image`
- **Idle PC:** `0x60629004`

### c3725

| Slot | Adapter | Interfaces |
|------|---------|------------|
| 0 | `GT96100-FE` | fa0/0, fa0/1 |
| 1 | `NM-16ESW` | fa1/0–fa1/15 (L2 switching) |
| 2 | `NM-4T` | s2/0–s2/3 |

- **RAM:** 256 MB
- **IOS Image:** `c3725-adventerprisek9-mz.124-15.T14.image`
- **Idle PC:** `0x60c09aa0`

--# 4. Console Port Convention

Base port: 5000. Assign sequentially by router number.

| Router | Console Port | Telnet Command |
|--------|-------------|----------------|
| R1 | 5001 | `telnet localhost 5001` |
| R2 | 5002 | `telnet localhost 5002` |
| R3 | 5003 | `telnet localhost 5003` |
| RN | 500N | `telnet localhost 500N` |

--# 5. Design Rules for Lab Generation

1. **No high-speed interfaces:** Do not use `TenGig` or `HundredGig`. Use `FastEthernet` or `GigabitEthernet` (gi3/0 on c7200).
2. **No incompatible technology:** Exclude features requiring IOS-XR, NX-OS, or containerisation.
3. **Physical link table:** Always define links explicitly in `baseline.yaml` using the format:
   `Source:Interface ↔ Target:Interface`
4. **Supported node types (non-IOS):** Unmanaged Switch (generic GNS3), VPCS (ping testing only).
5. **Device count:** Minimum 3 routers, maximum 15 routers per chapter topology (core + optional combined).

-# Common Issues

--# Feature not available on c3725
- **Cause:** c3725 IOS image does not support advanced crypto (IPsec, DMVPN) or advanced BGP features.
- **Solution:** Upgrade the affected router to c7200 in `baseline.yaml`. Update console ports and interface names accordingly (`fa0/0` → `fa0/0` is the same, but `gi3/0` is only on c7200).

--# Interface name mismatch in configs
- **Cause:** Config references `Gi0/0` but the platform only has `Fa0/0`.
- **Solution:** Check the slot table above. c3725 slot 0 = `Fa0/0`/`Fa0/1`. c7200 slot 3 = `Gi3/0`. Never use interface names not listed in the slot tables.

--# Too many interfaces needed
- **Cause:** Lab requires more than 2 FastEthernet on a c3725 (only fa0/0 and fa0/1 in slot 0).
- **Solution:** Switch to c7200 (slot 1 provides fa1/0 and fa1/1, slot 3 provides gi3/0), or use an unmanaged switch to extend a single interface into multiple segments.

-# Examples

When generating `baseline.yaml` for an OSPF multi-area lab with 4 routers:
- R1 (ABR, connects Area 0 to Area 1): `c7200` — needs 3 interfaces
- R2 (Area 0 internal): `c3725` — 2 interfaces sufficient
- R3 (ABR, connects Area 0 to Area 2): `c7200` — needs 3 interfaces
- R7 (Area 2 stub, added in Lab 05): `c3725` — 1 interface sufficient
