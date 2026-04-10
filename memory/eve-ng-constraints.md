# EVE-NG Constraints — Intel / Windows (Dell Latitude 5540)

Source of truth for all hardware decisions in EVE-NG lab generation.
Replaces the deprecated `gns3-constraints.md`.

## What Works

| Component | Details |
|-----------|---------|
| QEMU (KVM) | Primary engine — IOSv, IOSvL2, CSR1000v, XRv 9000, NX-OSv 9k, ASAv, Cat9kv, C8000v |
| IOL (IOS on Linux) | Lightweight — IOL L3, IOL L2 (requires `iourc` license on EVE-NG server) |
| Dynamips | Legacy — c7200, c3725 available but deprecated for new labs |
| VPC | Built-in end-host simulation (equivalent to GNS3 VPCS) |
| Unmanaged Switch | EVE-NG generic switch for L2 bridging |

## What Does NOT Work

| Component | Why |
|-----------|-----|
| Apple Silicon images | EVE-NG is Linux/Intel — ARM images incompatible |
| GNS3 project files (.gns3) | EVE-NG uses .unl topology format |
| Static console port 500N | EVE-NG assigns ports dynamically per lab session |

## Primary Platform Interface Reference

### IOSv — `iosv` (routing labs)
| Interface | Notes |
|-----------|-------|
| GigabitEthernet0/0 | First data port |
| GigabitEthernet0/1 | Second data port |
| GigabitEthernet0/2 | Third data port |
| GigabitEthernet0/3 | Fourth data port |
- RAM: 512 MB | IOS: 15.9(3)M6

### IOSvL2 — `iosvl2` (switching labs)
| Interface | Notes |
|-----------|-------|
| GigabitEthernet0/0–0/3 | Routed or switchport |
| GigabitEthernet1/0–1/3 | Switchport only |
- RAM: 768 MB | IOS: 15.x (high_iron_20200929)
- Supports: RSTP, LACP, BPDU Guard, PortFast, VTP, EtherChannel

### CSR1000v — `csr1000v` (IOS-XE / advanced features)
| Interface | Notes |
|-----------|-------|
| GigabitEthernet1 | First data port (NOT Gi0/0) |
| GigabitEthernet2 | Second data port |
| GigabitEthernet3 | Third data port |
- RAM: 3072–4096 MB | IOS-XE: 17.03.05

### IOL L3 — `iol_l3` (lightweight routing)
| Interface | Notes |
|-----------|-------|
| Ethernet0/0–0/3 | First card (4 ports) |
| Ethernet1/0–1/3 | Second card (4 ports) |
- RAM: 256 MB | IOS: 15.7(3)M

### IOL L2 — `iol_l2` (lightweight switching)
Same interface naming as IOL L3. Supports switchport commands.
- RAM: 256 MB

## Console Access (Dynamic Ports)

Unlike GNS3's static `500N` scheme, EVE-NG assigns ports per lab session.

| Method | How |
|--------|-----|
| Web UI | Click node → Console button in EVE-NG browser UI |
| REST API | `GET /api/labs/<lab>/nodes` → parse `url` field per node |
| Manual | Check EVE-NG web UI node details for assigned port |

Automation scripts use `--host <eve-ng-ip>` and discover ports via REST API.

## Resource Planning (64 GB host)

| Platform | RAM/node | Recommended max nodes |
|----------|----------|----------------------|
| IOSv | 512 MB | 20 |
| IOSvL2 | 768 MB | 15 |
| IOL L3/L2 | 256 MB | 40 |
| CSR1000v | 3072 MB | 8 |
| XRv 9000 | 4096 MB | 6 |
| NX-OSv 9000 | 4096 MB | 6 |
| ASAv | 2048 MB | 12 |
