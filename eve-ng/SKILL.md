---
name: eve-ng
description: EVE-NG hardware constraints and platform reference for Intel/Windows (QEMU, IOL, Dynamips). Use when generating lab configs, creating baseline.yaml topology definitions, selecting node platforms, assigning interfaces, or any time EVE-NG platform constraints (IOSv, IOSvL2, CSR1000v, IOL, XRv 9000, NX-OSv, ASAv) must be verified for compatibility. Replaces the deprecated gns3 skill.
---

# EVE-NG Lab Skill (Intel / Windows)

Hardware reference and constraint guide for the EVE-NG environment running on Dell Latitude 5540 (i7-1370P, 64 GB RAM) with Windows host. All lab generation must comply with these constraints.

-# Instructions

--# 1. Host Architecture & Constraints

This EVE-NG environment runs on **KVM/QEMU** (full virtualisation). Intel VT-x is active.

- **Platform:** EVE-NG Community/Pro on Ubuntu Server (bare-metal or VMware/Hyper-V guest)
- **Access:** Web UI at `http://<eve-ng-ip>` (default creds: `admin / eve`)
- **Emulation engines available:**
  - **QEMU** — primary engine (IOSv, IOSvL2, CSR1000v, XRv 9000, NX-OSv, ASAv, Catalyst 9kv, Cisco 8000v)
  - **IOL** — lightweight Linux-native IOS (L2 and L3 images)
  - **Dynamips** — legacy only (c7200, c3725 available but deprecated for new labs)
- **No Apple Silicon restrictions:** All Cisco image types are supported.

--# 2. Platform Selection Guide

| Role / Requirement | Primary Platform | Alternative | Notes |
|---|---|---|---|
| General routing (CCNA/CCNP routing) | `iosv` (IOSv) | `iol_l3` (IOL L3) | IOSv is heavier but closest to real IOS 15.x |
| L2 switching (VLANs, STP, EtherChannel, LACP) | `iosvl2` (IOSvL2) | `iol_l2` (IOL L2) | Full RSTP, LACP, BPDU Guard, Rapid PVST+ |
| Advanced IOS-XE (NETCONF, RESTCONF, SD-WAN) | `csr1000v` (CSR1000v) | `c8000v` (Cisco 8000v) | Heavy RAM (~3 GB); use only when IOS-XE needed |
| Service Provider (IS-IS, MPLS, Segment Routing) | `xrv9k` (IOS-XRv 9000) | `xrv` (XRv classic) | XRv 9000 for production parity; IOS-XR CLI |
| Data Centre (VxLAN, NX-OS, EVPN) | `nxosv9k` (NX-OSv 9000) | — | NX-OS CLI only |
| Security (ASA firewall, VPN) | `asav` (ASAv) | — | ASA-specific labs |
| Campus switching / IOS-XE features | `cat9kv` (Catalyst 9000v) | `iosvl2` | Very heavyweight; prefer IOSvL2 for basic switching |
| Lightweight routing (resource-constrained) | `iol_l3` (IOL L3) | `iosv` | Fastest boot, lowest RAM (~256 MB) |
| Lightweight switching | `iol_l2` (IOL L2) | `iosvl2` | Fastest boot for L2 labs |
| Multicast sender / traffic generator | `linux-alpine-3.18.4` (Alpine) | `linux-ubuntu-server-20.04` | Alpine ships `apk` — install `iperf`, `mcjoin`, `smcroute`. VPC cannot generate multicast. |
| Multicast receiver / IGMP joiner | `linux-tinycore-17.0` (TinyCore) | `linux-alpine-3.18.4` | TinyCore is the lightest way to drive `ip maddr add <group> dev eth0` so the PIM-DR sees an `(*,G)` join. |
| Generic Linux end-host (DHCP/DNS/HTTP client) | `linux-alpine-3.18.4` (Alpine) | `linux-tinycore-17.0` | Use when a VPC is not enough (need a real TCP/UDP stack, TLS, or a package manager). |

> **Default rule:** Use `iosv` for routing labs and `iosvl2` for switching labs unless the certification blueprint explicitly requires a different platform (e.g., NX-OS for DC tracks, IOS-XR for SP tracks).

--# 3. Hardware Templates (Source of Truth)

> **Verified 2026-04-10:** Interface names below confirmed against live nodes on this EVE-NG installation. IOSv and IOSvL2 templates are accurate.

### IOSv (vios-adventerprisek9-m.SPA.159-3.M6)

| Interface | Type | Notes |
|-----------|------|-------|
| GigabitEthernet0/0 | GigE | First data interface |
| GigabitEthernet0/1 | GigE | Second data interface |
| GigabitEthernet0/2 | GigE | Third data interface |
| GigabitEthernet0/3 | GigE | Fourth data interface |

- **RAM:** 512 MB recommended
- **IOS Version:** 15.9(3)M6
- **EVE-NG node type:** `vios`
- **Supported features:** Named-mode EIGRP, OSPFv3, BGP, MPLS, IPv6, GRE, IPsec

### IOSvL2 (viosl2-adventerprisek9-m.ssa.high_iron_20200929)

| Interface | Type | Notes |
|-----------|------|-------|
| GigabitEthernet0/0 | GigE | Routed or switchport |
| GigabitEthernet0/1 | GigE | Routed or switchport |
| GigabitEthernet0/2 | GigE | Routed or switchport |
| GigabitEthernet0/3 | GigE | Routed or switchport |
| GigabitEthernet1/0 | GigE | Switchport only |
| GigabitEthernet1/1 | GigE | Switchport only |
| GigabitEthernet1/2 | GigE | Switchport only |
| GigabitEthernet1/3 | GigE | Switchport only |

- **RAM:** 768 MB recommended
- **IOS Version:** 15.x (high_iron_20200929)
- **EVE-NG node type:** `viosl2`
- **Supported features:** VLANs, 802.1Q, RSTP (Rapid PVST+), LACP, PAgP, BPDU Guard, PortFast, VTP, EtherChannel, SVI routing
- **Note:** All 8 interfaces come `up/up` by default at boot — no `no shutdown` needed. IOSv interfaces start `administratively down`.

### CSR1000v (csr1000vng-universalk9.17.03.05)

| Interface | Type | Notes |
|-----------|------|-------|
| GigabitEthernet1 | GigE | First data interface (NOT Gi0/0) |
| GigabitEthernet2 | GigE | Second data interface |
| GigabitEthernet3 | GigE | Third data interface |

> **Note:** CSR1000v interface naming differs from IOSv — uses `GigabitEthernet1/2/3`, not `GigabitEthernet0/0-0/3`.

- **RAM:** 3072 MB minimum (4096 MB recommended)
- **IOS-XE Version:** 17.03.05
- **EVE-NG node type:** `csr1000vng`

### IOL L3 (i86bi_LinuxL3-AdvEnterpriseK9-M2_157_3_May_2018.bin)

| Interface | Type | Notes |
|-----------|------|-------|
| Ethernet0/0 | Ethernet | First data interface |
| Ethernet0/1 | Ethernet | Second data interface |
| Ethernet0/2 | Ethernet | Third data interface |
| Ethernet0/3 | Ethernet | Fourth data interface |
| Ethernet1/0 | Ethernet | Fifth data interface |
| Ethernet1/1 | Ethernet | Sixth data interface |
| Ethernet1/2 | Ethernet | Seventh data interface |
| Ethernet1/3 | Ethernet | Eighth data interface |

- **RAM:** 256 MB
- **IOS Version:** 15.7(3)M
- **EVE-NG node type:** `iol` (requires `iourc` license file)

### IOL L2 (i86bi_linux_l2-adventerprisek9-ms.SSA.high_iron_20190423.bin)

Same interface naming as IOL L3 (`Ethernet0/0` through `Ethernet1/3`), but ports support switchport commands.

- **RAM:** 256 MB
- **EVE-NG node type:** `iol` (requires `iourc` license file)

### IOS-XRv 9000 (xrv9k-fullk9-x.vrr.vga-7.1.1.qcow2)

| Interface | Type | Notes |
|-----------|------|-------|
| GigabitEthernet0/0/0/0 | GigE | IOS-XR naming convention |
| GigabitEthernet0/0/0/1 | GigE | |
| GigabitEthernet0/0/0/2 | GigE | |
| GigabitEthernet0/0/0/3 | GigE | |

- **RAM:** 4096–16384 MB (boot requires 4 GB minimum)
- **IOS-XR Version:** 7.1.1
- **EVE-NG node type:** `xrv9k`
- **Warning:** Long boot time (~10 min). Use only when IOS-XR features are required.

### NX-OSv 9000 (nxosv9k-9500-9.3.5)

| Interface | Type | Notes |
|-----------|------|-------|
| Ethernet1/1 | Ethernet | NX-OS naming — 1-based |
| Ethernet1/2 | Ethernet | |
| Ethernet1/3 | Ethernet | |
| Ethernet1/4 | Ethernet | |
| mgmt0 | Management | Out-of-band management |

- **RAM:** 4096 MB minimum
- **NX-OS Version:** 9.3.5
- **EVE-NG node type:** `nxosv9k`

### ASAv (asav-961-001)

| Interface | Type | Notes |
|-----------|------|-------|
| GigabitEthernet0/0 | GigE | Data (outside/inside) |
| GigabitEthernet0/1 | GigE | |
| GigabitEthernet0/2 | GigE | |
| GigabitEthernet0/3 | GigE | |
| Management0/0 | Management | OOB management |

- **RAM:** 2048 MB
- **ASA Version:** 9.6.1
- **EVE-NG node type:** `asav`

### Alpine Linux (linux-alpine-3.18.4)

| Interface | Type | Notes |
|-----------|------|-------|
| eth0 | Ethernet | First NIC — default |
| eth1 | Ethernet | Add more NICs at node-create time (EVE-NG: *Ethernets* field) |
| ethN | Ethernet | Up to 10 interfaces supported by the generic `linux` template |

- **RAM:** 256 MB recommended (128 MB minimum)
- **vCPU:** 1
- **Disk:** ~150 MB qcow2
- **EVE-NG node type:** `linux` (image = `linux-alpine-3.18.4`)
- **Login:** `root` / `alpine` (or configured at first boot)
- **Why use it:**
  - Full `musl`-based Linux with `apk` package manager — `apk add iperf mcjoin tcpdump socat ethtool iproute2`
  - Real TCP/UDP/IGMP stack — unlike VPC, it can send/receive multicast, run iperf servers, issue IGMPv2/v3 joins
  - Suitable for multicast-sender labs, DHCP client tests, HTTP/S clients, automation targets (Ansible, SSH)
- **Typical multicast role:** source or sender (`iperf -c 239.1.1.1 -u -T 32 -t 60 -b 1M`)

### TinyCore Linux (linux-tinycore-17.0)

| Interface | Type | Notes |
|-----------|------|-------|
| eth0 | Ethernet | First NIC — default |
| ethN | Ethernet | Up to 10 interfaces via the `linux` template |

- **RAM:** 128 MB recommended (64 MB minimum for Core edition)
- **vCPU:** 1
- **Disk:** ~50 MB qcow2
- **EVE-NG node type:** `linux` (image = `linux-tinycore-17.0`)
- **Login:** `tc` (no password by default)
- **Why use it:**
  - Lightest real Linux end-host in the inventory — RAM/disk budget that lets you scatter many receivers across a topology without starving Cisco nodes
  - Packages via `tce-load -wi <pkg>` (e.g. `tce-load -wi iperf`); network tools `ip`, `ping`, `traceroute`, `iperf` available
  - Perfect for "multicast receiver" roles where all you need is an IGMP join and a UDP socket
- **Typical multicast role:** receiver / IGMP joiner (`ip maddr add 239.1.1.1 dev eth0` + `iperf -s -u -B 239.1.1.1`)

--# 4. VPC Nodes (End-Host Simulation)

EVE-NG includes a built-in **VPC** node (Virtual PC) — equivalent to GNS3's VPCS.

### When to use VPC

| Condition | Use VPC |
|-----------|---------|
| Verify routing reachability end-to-end | yes |
| Test DHCP client behaviour | yes |
| Source pings/traceroutes from a host address | yes |
| Simulate a server or application workload | no — use a router loopback or a Linux end-host (§4b) |
| Any L3 routing function | no — VPC has no routing stack |
| Send or receive multicast (IGMP join, iperf UDP to 239.x.x.x) | **no** — VPC has no multicast stack. Use Alpine or TinyCore from §4b. |
| Generate real TCP/UDP traffic (iperf, curl, scripted flows) | no — use a Linux end-host (§4b) |

### VPC hardware profile

| Property | Value |
|----------|-------|
| Node type | VPC (EVE-NG built-in) |
| Interface | `e0` (single Ethernet) |
| IOS image | none |
| RAM | minimal |

### VPC command reference

```
# Assign a static IP
ip <address> <netmask> <gateway>
  Example: ip 192.168.10.2 255.255.255.0 192.168.10.1

# Verify assignment
show

# Ping
ping <destination>

# DHCP
dhcp

# Save config
save
```

> **Note:** EVE-NG VPC syntax differs slightly from GNS3 VPCS. Use `ip <addr> <mask> <gw>` (dotted-decimal mask, not prefix length).

### Referencing VPC in baseline.yaml

```yaml
devices:
  - name: PC1
    type: vpc
    interfaces:
      - name: eth0    # EVE-NG VPCS uses 'eth0', not 'e0' (GNS3-style). Match the EVE-NG name.
        ip: 192.168.10.2/24
        gateway: 192.168.10.1

links:
  - "PC1:eth0 ↔ R1:GigabitEthernet0/1"
```

VPC config files use `.vpc` extension, placed in `initial-configs/PC1.vpc`.

---

--# 4b. Linux End-Host Nodes (Alpine / TinyCore)

Use a Linux end-host whenever a scenario needs a **real IP stack**: multicast senders/receivers, IGMPv2/v3 joiners, iperf traffic generators, DHCP/DNS/HTTP clients, or automation targets (Ansible/Netmiko over SSH). VPC nodes cannot fill these roles.

### When to use which

| Role in the lab | Image | Why |
|-----------------|-------|-----|
| Multicast source / traffic generator | `linux-alpine-3.18.4` | Full `apk` repo; `iperf`, `mcjoin`, `smcroute`, `socat` all one command away |
| Multicast receiver / IGMP joiner | `linux-tinycore-17.0` | 128 MB RAM footprint — scatter 4-6 receivers without starving Cisco nodes |
| DHCP / DNS / HTTP client | either | Alpine if you want `curl`/`wget` + TLS by default; TinyCore if RAM is tight |
| SSH automation target (Ansible/Netmiko) | `linux-alpine-3.18.4` | OpenSSH server via `apk add openssh`; persistent root creds |

### Referencing a Linux end-host in baseline.yaml

```yaml
devices:
  - name: H1
    type: linux                 # EVE-NG generic Linux template
    image: linux-alpine-3.18.4  # folder name under /opt/unetlab/addons/qemu/
    ram: 256                    # MB
    ethernets: 1                # NICs exposed by EVE-NG
    interfaces:
      - name: eth0
        ip: 10.10.10.2/24
        gateway: 10.10.10.1

  - name: H2
    type: linux
    image: linux-tinycore-17.0
    ram: 128
    ethernets: 1
    interfaces:
      - name: eth0
        ip: 10.10.20.2/24
        gateway: 10.10.20.1

links:
  - "H1:eth0 ↔ R1:GigabitEthernet0/1"
  - "H2:eth0 ↔ R3:GigabitEthernet0/1"
```

### Startup configuration (no `.linux` extension)

EVE-NG does not inject Cisco-style text configs into Linux nodes. Two options:

1. **Golden image (preferred):** build the image once with the packages and a boot-time script, re-export as the qcow2 under `/opt/unetlab/addons/qemu/<image>/`. Every node that uses that image starts ready.
2. **Cloud-init / first-boot script:** attach a small CD-ROM ISO per node containing `/etc/network/interfaces` and a `rc.local` that runs the multicast join/send command. Ship the ISO under `initial-configs/<hostname>.iso` and document it in the workbook.

For lab builds where students type commands themselves (recommended for learning multicast), skip startup automation and put the commands in the workbook's verification section.

### Multicast command reference (paste into the workbook)

Commands the workbook should teach students to run on the Linux end-hosts:

```bash
# --- RECEIVER (TinyCore or Alpine) ---
# 1. Join an ASM group via the kernel (IGMPv2/v3 report goes out eth0)
ip maddr add 239.1.1.1 dev eth0
ip maddr show dev eth0                      # verify join is programmed

# 2. Open a UDP socket on the group so datagrams are actually consumed
iperf -s -u -B 239.1.1.1 -i 1               # Alpine: apk add iperf
                                             # TinyCore: tce-load -wi iperf

# 3. Leave the group
ip maddr del 239.1.1.1 dev eth0

# --- SOURCE (Alpine) ---
# 4. Send a 1 Mbps UDP stream to the group, TTL 32 so it crosses PIM hops
iperf -c 239.1.1.1 -u -T 32 -t 60 -b 1M

# --- DIAGNOSTICS ---
tcpdump -ni eth0 igmp or 'udp and dst net 224.0.0.0/4'
ethtool -S eth0 | grep -i multicast
```

On the **router side** the workbook should then verify:

```
show ip igmp groups              # receiver's join populates this
show ip mroute 239.1.1.1         # (*,G) entry appears with OIL pointing toward H2
show ip mroute 239.1.1.1 count   # packet/byte counters increment while iperf runs
```

### Resource budget when scattering Linux hosts

Typical multicast lab = 4-6 routers + 1 source + 2-3 receivers. With Alpine source (256 MB) + three TinyCore receivers (128 MB each), total host overhead is ~640 MB — comfortably inside the 64 GB budget even with 6 IOSv routers (3 GB) and an IOSvL2 (768 MB) in the same lab.

---

--# 5. Console Access Convention

EVE-NG assigns console telnet ports **dynamically** at lab creation — there is no static `500N` convention like GNS3.

### Method 1: EVE-NG REST API (recommended for automation)

Discover ports at runtime before connecting:

```python
import requests

EVE_NG_HOST = "192.168.1.x"   # Your EVE-NG server IP
LAB_PATH    = "your_lab.unl"   # Lab file path on server

def get_node_ports(host, lab_path):
    """Return dict of node_name -> telnet_port."""
    session = requests.Session()
    session.post(f"http://{host}/api/auth/login",
                 json={"username": "admin", "password": "eve"})
    nodes = session.get(f"http://{host}/api/labs/{lab_path}/nodes").json()
    return {
        n["name"]: int(n["url"].split(":")[-1])
        for n in nodes["data"].values()
        if n.get("url")
    }
```

### Method 2: HTML5 Console (browser-based)

Open EVE-NG web UI → click any node → "Console" button. No client software needed. Best for manual lab work.

### Method 3: SecureCRT / PuTTY (telnet client)

1. In EVE-NG web UI, right-click node → "Console" → copy the telnet URI.
2. Connect via `telnet <eve-ng-ip> <port>`.
3. Ports are visible in the EVE-NG web UI per-lab under each node's details.

### Method 4: SSH to Node Management Interface

Configure a management network (`192.168.100.0/24`) on all nodes. Use `device_type="cisco_ios"` with SSH instead of telnet.

### Console Access Table format (workbooks)

Because ports are dynamic, workbooks should use this format:

```
| Device | Console Port | Connection Command |
|--------|-------------|-------------------|
| R1     | (see EVE-NG UI) | `telnet <eve-ng-ip> <port>` |
| R2     | (see EVE-NG UI) | `telnet <eve-ng-ip> <port>` |
```

When automating with `setup_lab.py`, pass `--host <eve-ng-ip>` and the script will discover ports via the REST API.

---

--# 6. Design Rules for Lab Generation

1. **GigabitEthernet is standard:** All IOSv/IOSvL2 interfaces are GigE (`GigabitEthernet0/0`). Do NOT use `FastEthernet` for IOSv/IOSvL2 labs.
2. **Platform-command alignment:** Before generating configs, verify the target platform supports the required syntax. Check `reference-data/ios-compatibility.yaml`. IOSv (IOS 15.9) and IOSvL2 support all IOS 15.x features including named-mode EIGRP, RSTP, LACP, BPDU Guard, OSPFv3.
3. **IOS-XR and NX-OS labs:** Use `xrv9k` and `nxosv9k` only when the lab explicitly requires those OSes. Config syntax is different from IOS — do not mix.
4. **Physical link table:** Always define links explicitly in `baseline.yaml` using the format:
   `Source:Interface ↔ Target:Interface`
5. **Device count:** Minimum 3, maximum 15 routers per chapter topology. VPC nodes do not count toward the router limit.
6. **Resource planning (64 GB host):**
   | Platform | RAM/node | Max nodes (safe) |
   |----------|----------|-----------------|
   | IOSv | 512 MB | 20 |
   | IOSvL2 | 768 MB | 15 |
   | IOL L3/L2 | 256 MB | 40 |
   | CSR1000v | 3072 MB | 8 |
   | XRv 9000 | 4096 MB | 6 |
   | NX-OSv 9000 | 4096 MB | 6 |
   | Alpine Linux | 256 MB | 40 |
   | TinyCore Linux | 128 MB | 60 |
7. **Image permissions:** After uploading any image to EVE-NG, always run:
   ```bash
   /opt/unetlab/wrappers/unl_wrapper -a fixpermissions
   ```
8. **VPC config files use `.vpc` extension** — never `.cfg`. Place in `initial-configs/`.
9. **Ship the EVE-NG `.unl` file.** Every lab MUST include a `topology/` directory
   containing the `.unl` file alongside `topology.drawio` and a `README.md`
   explaining the import process. **The `.unl` is produced by the lab operator
   via EVE-NG's native Export** — not by automation. See Section 7 for the
   shipping standard and the deferred `gen_unl.py` tooling.

--# 7. Shipping EVE-NG Lab Files (`.unl`)

**Every lab MUST ship its EVE-NG `.unl` export.** The `.drawio` diagram is
the *design reference*; the `.unl` is the *exact buildable artifact*. Without
the `.unl`, students must rebuild the topology by hand from the diagram —
error-prone, time-consuming, and produces subtly different link IDs that
break the REST-API port-discovery contract.

### Current policy: operator-provided `.unl`

The **lab operator exports the `.unl` manually** from EVE-NG after building
and smoke-testing the topology. Lab-builder agents do NOT run `gen_unl.py`.

- **Default path:** *Export workflow* below.
- **Deferred:** *Generate workflow* (`gen_unl.py`) is retained for possible
  future refinement but must not be invoked as part of routine lab builds.
  The tooling lives at `labs/common/tools/gen_unl.py` and
  `labs/common/tools/eve_platforms.py`.
- **Why:** generator output drifted from hand-built EVE-NG topologies
  (interface ordering, link IDs, canvas layout); operator export is the
  canonical source of truth.

### Required structure per lab

```
labs/<topic>/lab-NN-<slug>/
  topology/
    topology.drawio                   # conceptual diagram (design)
    lab-NN-<slug>.unl                 # EVE-NG native lab (buildable)
    README.md                         # import instructions + manual fallback
```

Filename convention: `.unl` filename matches the lab folder name exactly
(e.g. `lab-00-vlans-and-trunking.unl`). This becomes the `lab_path` arg for
REST-API port discovery:

```python
discover_ports(host, "switching/lab-00-vlans-and-trunking.unl")
```

### topology/README.md must cover

1. **What's in the folder** (table: `.drawio` vs `.unl` vs `README.md`)
2. **Import steps** — navigate EVE-NG web UI, Add New Lab → Import, upload
   `.unl`, Start all nodes
3. **Lab path expectation** — where in EVE-NG's folder tree the lab should
   live (the path `setup_lab.py` defaults to), and what `--lab-path` to pass
   if the student imports it elsewhere
4. **Manual fallback** — node list with platform types and full link table
   (mirroring `baseline.yaml`) so the student can rebuild if the `.unl` is
   missing, corrupted, or incompatible with their EVE-NG version

### Export workflow (DEFAULT — operator-provided)

The lab operator builds the topology in EVE-NG and exports the `.unl`
manually. Lab-builder agents stop at `topology.drawio` + `topology/README.md`
and wait for the operator to drop the exported `.unl` into
`labs/<topic>/<lab>/topology/`.

1. Build the topology in EVE-NG until all nodes start cleanly
2. EVE-NG web UI: open the lab → **More actions → Export**
3. Save the downloaded `.unl` into `labs/<topic>/<lab>/topology/`
4. Commit `.unl` + `.drawio` + `README.md` together — they must stay in sync
5. Update `meta.yaml` files block to reference all three:
   ```yaml
   files:
     topology:
       diagram: topology/topology.drawio
       eve_ng_lab: topology/<lab-folder-name>.unl
       readme: topology/README.md
   ```

### Generate workflow (DEFERRED — `gen_unl.py`, do not use)

> **Status:** deferred. This tooling is retained for possible future
> refinement but is **not part of the current lab-build workflow**. Do not
> invoke `gen_unl.py` when building a lab. The operator export path above
> is the source of truth. The notes below exist so the generator can be
> picked back up later without re-discovering its contract.

A repo-local generator consumes `labs/<topic>/baseline.yaml` and emits one
`.unl` per lab (plus a `.zip` for EVE-NG import, which only accepts zipped
uploads). Startup configs from `initial-configs/<node>.cfg|.vpc` are
base64-embedded in the `.unl` so `Start all nodes` boots the lab pre-configured.

```bash
# (Deferred — do not run as part of a build)
python labs/common/tools/gen_unl.py switching
python labs/common/tools/gen_unl.py switching --only lab-02-rstp-and-enhancements
python labs/common/tools/gen_unl.py switching --no-embed-configs
```

Outputs (when re-enabled):
- `labs/<topic>/<lab>/topology/<lab>.unl` — buildable lab file
- `labs/<topic>/<lab>/topology/<lab>.zip` — upload this to EVE-NG

Platform → EVE-NG attributes live in `labs/common/tools/eve_platforms.py`.
Add a new platform by exporting one node of that type from EVE-NG and
copying its attributes into the `PLATFORMS` dict.

Node placement on the canvas is computed by `compute_layout()` in
`gen_unl.py` — a tiered default (routers top, switches middle, hosts bottom)
works for most labs. Reposition manually in EVE-NG if the auto-layout is
ugly for a specific topology.

### Never

- Do not ship only the `.drawio` ("students can build it themselves") —
  this is explicitly what this section exists to prevent
- Do not commit the `.unl` without testing that it re-imports and starts
  (zip the file and import via EVE-NG web UI → Add new object → Import)

--# 8. Installed Image Inventory

> **Last verified:** 2026-04-10. This table reflects images confirmed on disk at
> `C:\Users\Nkwenti\Documents\EVE-NG\eve images\Cisco`. Add a row when you upload a new image.

### Installed — Confirmed on Disk

| Platform | Image Filename | Version | EVE-NG Node Type | Status |
|----------|---------------|---------|-----------------|--------|
| IOSv | vios-adventerprisek9-m.SPA.159-3.M6 | 15.9(3)M6 | `vios` | Installed |
| IOSvL2 | viosl2-adventerprisek9-m.ssa.high_iron_20200929 | 15.x (2020) | `viosl2` | Installed |
| CSR1000v | csr1000vng-universalk9.17.03.05-serial | 17.03.05 | `csr1000vng` | Installed |
| IOS-XRv 9000 | xrv9k-fullk9-x.vrr.vga-7.1.1.qcow2 | 7.1.1 | `xrv9k` | Installed |
| IOS-XRv classic | xrv-k9-demo-6.3.1 | 6.3.1 | `xrv` | Installed (demo/limited) |
| NX-OSv 9000 | nxosv9k-9500-9.3.5 | 9.3.5 | `nxosv9k` | Installed |
| ASAv | asav-961-001 | 9.6.1 | `asav` | Installed |
| IOL L3 | i86bi_LinuxL3-AdvEnterpriseK9-M2_157_3_May_2018.bin | 15.7(3)M | `iol` | Installed |
| IOL L2 | i86bi_linux_l2-adventerprisek9-ms.SSA.high_iron_20190423.bin | 15.x (2019) | `iol` | Installed |
| Catalyst 9000v | cat9kv-17.10.01-prd7 | 17.10.01 | `cat9kv` | Installed |
| Cisco 8000v | c8000v-17.06.03 | 17.06.03 | `c8000v` | Installed |
| Linux (Ubuntu Server) | linux-ubuntu-server-20.04 | 20.04 LTS | `linux` | Installed |
| Alpine Linux | linux-alpine-3.18.4 | 3.18.4 | `linux` | Installed — multicast sender, iperf/mcjoin host, general end-host |
| TinyCore Linux | linux-tinycore-17.0 | 17.0 | `linux` | Installed — multicast receiver, IGMP joiner, minimal end-host |

### Not Installed — Commonly Needed

| Image / Tool | Purpose | Notes |
|---|---|---|
| Linux VM (Ubuntu 22.04) | Newer LTS for automation labs | Optional upgrade from 20.04 — 20.04 is sufficient for all current exam objectives |
| SD-WAN (vManage, vBond, vSmart, vEdge) | SD-WAN topology simulation | Heavy (4+ VMs per pod). v20.x+ required for current Cisco SD-WAN exams; v19.2 is outdated |
| WLC (Catalyst Wireless LAN Controller) | Wireless controller labs | EVE-NG does not support RF simulation — wireless labs require physical APs or dedicated wireless lab platforms |
| Catalyst Center (DNA Center) | Campus automation, SD-Access | Requires 56+ GB RAM per instance — impractical in EVE-NG; use dCloud or physical for this feature |
| ISE (Identity Services Engine) | 802.1X, TACACS+, RADIUS, TrustSec | Very heavy (~12 GB RAM). Viable in EVE-NG but not yet installed |

### Image Gap Notes

- **Linux VM** (Ubuntu 20.04) is installed — automation labs (Ansible, Python, NETCONF, YANG, telemetry) are unblocked.
- **Alpine 3.18.4 + TinyCore 17.0** are installed — multicast labs (IGMP joins, PIM-SM/SSM/BIDIR forwarding verification with real source/receiver traffic) are unblocked. Previously these labs could only *configure* multicast; now they can *observe traffic flow*.
- **SD-WAN** requires a dedicated image set; not substitutable with CSR1000v in an SD-WAN topology.
- **Wireless and DNA Center** gaps cannot be closed in EVE-NG — plan to use Cisco dCloud or physical gear for those objectives.
- Exam-specific image requirements (which platforms each exam needs, versions, and quantities) belong in the individual exam repo, not here.

-# Common Issues

--# QEMU node fails to start

- **Cause:** KVM not enabled, or image permissions not fixed.
- **Solution:**
  1. Verify KVM: `kvm-ok` on the EVE-NG host.
  2. Fix permissions: `/opt/unetlab/wrappers/unl_wrapper -a fixpermissions`
  3. Check EVE-NG logs: `/opt/unetlab/data/Logs/`

--# Interface name mismatch in configs

- **Cause:** Config references `FastEthernet0/0` but IOSv only has `GigabitEthernet0/0`.
- **Solution:** Check Section 3 hardware templates. IOSv/IOSvL2 = `Gi0/0`. CSR1000v = `Gi1`. IOL = `Et0/0`. XRv 9000 = `Gi0/0/0/0`.

--# Console connection refused

- **Cause:** Node is not yet started, or EVE-NG assigned a different port.
- **Solution:** Start the node in EVE-NG web UI. Rediscover ports via REST API or check the web UI node details.

--# IOL node fails to start (license error)

- **Cause:** `iourc` license file missing or in wrong location on EVE-NG server.
- **Solution:** Ensure `iourc` is placed at `/opt/unetlab/addons/iol/bin/iourc`. Regenerate with `CiscoIOUKeygen.py` if needed.

--# Too many interfaces needed

- **Cause:** IOSv has only 4 interfaces (`Gi0/0`–`Gi0/3`). IOSvL2 has 8. IOL has 8 per card.
- **Solution:** Use IOL L3 (up to 8 interfaces across 2 cards) or add an EVE-NG unmanaged switch node to extend a single interface into multiple segments.

-# Examples

When generating `baseline.yaml` for an OSPF multi-area lab with 4 routers:
- R1 (ABR, connects Area 0 to Area 1): `iosv` — needs 3 interfaces (`Gi0/0`, `Gi0/1`, `Gi0/2`)
- R2 (Area 0 internal): `iosv` — 2 interfaces
- R3 (ABR, connects Area 0 to Area 2): `iosv` — 3 interfaces
- R7 (Area 2 stub, added Lab 05): `iosv`

When generating `baseline.yaml` for a switching lab (VLANs, STP, EtherChannel):
- SW1 (L2 switch, 6 access + 2 trunk ports): `iosvl2` — use `Gi1/0`–`Gi1/3` for switchports
- SW2 (L2 switch): `iosvl2`
- R1 (default gateway / router-on-a-stick): `iosv`

When a lab requires end-to-end reachability verification:
- PC1 (`vpc` type) — connected to R1 `GigabitEthernet0/1` on `192.168.10.0/24`
- PC2 (`vpc` type) — connected to R3 `GigabitEthernet0/1` on `192.168.30.0/24`
- `initial-configs/PC1.vpc`: `ip 192.168.10.2 255.255.255.0 192.168.10.1`
- Workbook verification step: `PC1> ping 192.168.30.2`
