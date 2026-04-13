---
name: drawio
description: Visual style guide and workflow for creating Cisco network topology diagrams in Draw.io. Use when generating a topology diagram, creating or updating a topology.drawio file, exporting a PNG, or when any other skill needs to produce or validate a network diagram.
---

# Draw.io Diagram Skill

-# Instructions

--# 1. Locations

Store diagrams in the following directories based on their type:

- **Topology Diagrams**: `labs/<topic>/lab-NN-<slug>/topology.drawio`
  - Use for network topologies, physical cabling, and logical connectivity.
- **Flow Diagrams**: `labs/<topic>/lab-NN-<slug>/flow-[description].drawio`
  - Use for packet flows, process charts, and logic flows.

--# 2. File Formats & Deliverables

The only required deliverable is:

1.  **Source File (`.drawio`)**: The editable XML format. This is the canonical diagram file.

--# 3. Naming Conventions

- Use **kebab-case** for all filenames.
- **Pattern**: `[lab-name]-[diagram-type].extension`
- **Examples**:
  - `eigrp-basic-adjacency-topology.drawio`
  - `packet-flow-vlan-routing.drawio`

--# 4. Visual Style Guide

This section defines the canonical visual style for all topology diagrams. Every generated `.drawio` file **must** follow these rules.

### 4.1 Canvas & Layout

- **Background**: Default Draw.io canvas (assumed dark-theme friendly).
- **Title**: Positioned at the **top center** of the canvas. Bold, 16pt.
- **Legend Box**: Required in every diagram. Positioned at the **bottom-right** corner. Black fill (`#000000`) with white text (`#FFFFFF`), rounded corners, 10pt font.

### 4.2 Device Icons

- Use the **Cisco 19** icon set (`mxgraph.cisco19`).
- **Shape pattern**: All network devices share the base shape `mxgraph.cisco19.rect` with a `prIcon=` attribute selecting the icon. Workstations/PCs use a dedicated shape `mxgraph.cisco19.workstation`.
- **Size**: Network devices **60×60** (square, `aspect=fixed`). Workstations **50×40**.
- **Colors**: `fillColor=#FAFAFA;strokeColor=#005073` for all network devices. `fillColor=#005073;strokeColor=none` for workstations.

| Device | `prIcon` / shape | Full style string |
|--------|-----------------|-------------------|
| **Router** | `prIcon=router` | `sketch=0;points=[[0.5,0,0],[1,0.5,0],[0.5,1,0],[0,0.5,0],[0.145,0.145,0],[0.8555,0.145,0],[0.855,0.8555,0],[0.145,0.855,0]];verticalLabelPosition=bottom;html=1;verticalAlign=top;aspect=fixed;align=center;pointerEvents=1;shape=mxgraph.cisco19.rect;prIcon=router;fillColor=#FAFAFA;strokeColor=#005073;` |
| **L3 / Distribution Switch** | `prIcon=l3_switch` | `sketch=0;points=[[0.015,0.015,0],[0.985,0.015,0],[0.985,0.985,0],[0.015,0.985,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0.25,0],[1,0.5,0],[1,0.75,0],[0.75,1,0],[0.5,1,0],[0.25,1,0],[0,0.75,0],[0,0.5,0],[0,0.25,0]];verticalLabelPosition=bottom;html=1;verticalAlign=top;aspect=fixed;align=center;pointerEvents=1;shape=mxgraph.cisco19.rect;prIcon=l3_switch;fillColor=#FAFAFA;strokeColor=#005073;` |
| **L2 / Access Switch** | `prIcon=workgroup_switch` | Same `points=` as L3 switch above, `prIcon=workgroup_switch` |
| **Firewall** | `prIcon=firewall` | Same `points=` as L3 switch above, `prIcon=firewall` |
| **Cloud / Internet** | `prIcon=generic_cloud` | Same `points=` as L3 switch above, `prIcon=generic_cloud` |
| **PC / Workstation** | `shape=mxgraph.cisco19.workstation` | `points=[[0.03,0.03,0],[0.5,0,0],[0.97,0.03,0],[1,0.4,0],[0.97,0.745,0],[0.5,1,0],[0.03,0.745,0],[0,0.4,0]];verticalLabelPosition=bottom;sketch=0;html=1;verticalAlign=top;aspect=fixed;align=center;pointerEvents=1;shape=mxgraph.cisco19.workstation;fillColor=#005073;strokeColor=none;` |

### 4.3 Device Labels

- **Content**: Three lines — hostname, role, loopback IP.
- **Style**: `text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=top;whiteSpace=wrap;rounded=0;fontSize=11;fontStyle=1`
- **Example**: `R1\nHub/ABR\n10.1.1.1/32`

#### 4.3.1 Smart Label Placement — Empty Side Rule

Labels **must not overlap any connection lines**. Place the label on the side that has **no connections** exiting the device icon:

| Condition | Placement |
|-----------|-----------|
| All physical neighbors are to the **LEFT** (`nx < device_x`) | Place label **RIGHT**: `label_x = device_x + 65` |
| All physical neighbors are to the **RIGHT** (`nx > device_x`) | Place label **LEFT**: `label_x = device_x - 105` |
| Neighbors on both sides (or same-column only) | Default **LEFT**: `label_x = device_x - 105` |

- Y offset (all cases): `label_y = device_y - 7`
- Label width: `100`, height: `60`

> **Note:** Offsets above are for the standard 60×60 Cisco 19 icon. Right offset (+65) places the label just past the right edge of the icon with a 5px gap.

**Examples from EIGRP Lab 08 (updated for Cisco 19 sizing):**
- **R2** is at x=500. All neighbors (R1 at x=400, R3 at x=400) are to the LEFT → label goes **RIGHT** (`label_x = 565`).
- **R6** is at x=200. Its neighbor R1 is at x=400, which is to the RIGHT → label goes **LEFT** (`label_x = 95`).

### 4.4 Connection Lines

Every link must have a **type** that determines its color, thickness, and dash pattern. Never use black. Use `endArrow=none` on all links — Cisco topology diagrams show connectivity, not direction.

#### 4.4.1 Link Type Reference Table

| Link Type | Color | Hex | Width | Dash | Typical use |
|-----------|-------|-----|-------|------|-------------|
| **Routed / physical (default)** | White | `#FFFFFF` | 2 | solid | Router-to-router, routed SVIs |
| **Access port** | White | `#FFFFFF` | 1 | solid | Switch Gi → end host / VPC |
| **Trunk (802.1Q)** | Gold | `#FFD700` | 2 | solid | Switch-to-switch trunk |
| **EtherChannel bundle** | White | `#FFFFFF` | 5 | solid | Po1, LACP, PAgP, static |
| **WAN serial / leased line** | Orange | `#FF8C00` | 2 | solid | Serial, T1, E1, leased WAN |
| **Management / OOB** | Gray | `#888888` | 1 | long-dash `8 4` | Console, OOB mgmt network |
| **OSPF virtual link** | Lavender | `#CE93D8` | 1 | dash `4 4` | Backbone continuity link |
| **OSPF sham link** | Lavender | `#CE93D8` | 1 | dot-dash `1 4 4 4` | OSPF across MPLS VPN |

#### 4.4.2 Style Strings

```
Routed (default):    endArrow=none;html=1;strokeWidth=2;strokeColor=#FFFFFF;
Access port:         endArrow=none;html=1;strokeWidth=1;strokeColor=#FFFFFF;
Trunk (802.1Q):      endArrow=none;html=1;strokeWidth=2;strokeColor=#FFD700;
EtherChannel bundle: endArrow=none;html=1;strokeWidth=5;strokeColor=#FFFFFF;
WAN serial:          endArrow=none;html=1;strokeWidth=2;strokeColor=#FF8C00;
Management/OOB:      endArrow=none;html=1;strokeWidth=1;strokeColor=#888888;dashed=1;dashPattern=8 4;
OSPF virtual link:   endArrow=none;html=1;strokeWidth=1;strokeColor=#CE93D8;dashed=1;dashPattern=4 4;
OSPF sham link:      endArrow=none;html=1;strokeWidth=1;strokeColor=#CE93D8;dashed=1;dashPattern=1 4 4 4;
```

#### 4.4.3 EtherChannel / Dual-Link Pairs

When two or more parallel physical links exist between the same pair of devices (EtherChannel members, redundant trunks), draw them as **two offset lines** that merge into one thick bundle line:

- Draw individual member links first (stroke=1, white, offset by ±5px in the perpendicular axis) using explicit waypoints.
- Then draw the PortChannel/bundle line (stroke=5, white) overlapping them in the center.
- Label the bundle line with the PortChannel number and protocol: `Po1 (LACP)\nSW1 Gi0/1,Gi0/2 active\nSW2 Gi0/1,Gi0/2 passive`.

When member links are too close to draw separately, use the thick bundle line alone (stroke=5) with the member interfaces listed in the label.

#### 4.4.4 Edge Labels

All links must carry an edge label. Label content varies by link type:

| Link Type | Label content |
|-----------|---------------|
| Routed P2P | `IntfA - IntfB\n10.x.x.0/30` |
| Trunk | `IntfA - IntfB\nTrunk (VLANs 10,20,99)` |
| EtherChannel | `Po1 (LACP)\nSW1: Gi0/1,Gi0/2 active\nSW2: Gi0/1,Gi0/2 passive` |
| Access port | `IntfA - IntfB\nAccess VLAN 10` |
| WAN serial | `IntfA - IntfB\n10.x.x.0/30` |
| Tunnel/overlay | See §4.9 |

Label style: `edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;points=[];fontSize=10;fontColor=#FFFFFF;fillColor=none;strokeColor=none;`

For switch-to-switch links also add a **per-end interface label** at each device (source and destination separately), using `edgeLabel` cells with `x="-0.7"` (near source) and `x="0.7"` (near target).

### 4.5 IP Last Octet Labels

- **Required**: Every router interface endpoint must have a small label showing the **last octet** of its IP address (e.g., `.1`, `.2`).
- **Position**: Near the router's side of the connection line, close to the interface.
  - Use the router's X + ~50px (to the right of the icon edge).
  - Y coordinate near the interface exit point on the router.
- **Style**: `edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;points=[];fontSize=10;`
- **Purpose**: Allows instant identification of which IP belongs to which router without reading the full subnet label.

### 4.6 Legend Box

Every diagram must include a legend box with the following properties:

- **Position**: Bottom-right area of the canvas.
- **Fill**: Black (`#000000`).
- **Font Color**: White (`#FFFFFF`).
- **Border**: Rounded, white stroke.
- **Style**: `rounded=1;whiteSpace=wrap;html=1;fillColor=#000000;strokeColor=#FFFFFF;fontColor=#FFFFFF;fontSize=10;align=left;verticalAlign=top;spacingLeft=8;spacingTop=8;`
- **Content**: Always include every visual encoding used in the diagram. Minimum set:
  - **Link types**: list each color/thickness used (e.g. `─── Trunk (gold)`, `═══ EtherChannel`, `--- GRE+IPsec (orange)`)
  - **Tunnel types**: one line per overlay color with label (e.g. `....... GRE/IPsec (orange)`)
  - **Zone / site colors**: one line per zone or site type present
  - **Protocol identifiers**: OSPF process ID, EIGRP AS number, BGP AS, VLANs defined
  - **Cost / metric annotations** if present

### 4.7 Reference XML Snippets

**Title Cell:**
```xml
<mxCell id="title" value="Lab N: Title Here" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=16;fontStyle=1" vertex="1" parent="1">
  <mxGeometry x="200" y="40" width="400" height="40" as="geometry" />
</mxCell>
```

**Device Icon — Router (Cisco 19):**
```xml
<mxCell id="R1" value="" style="sketch=0;points=[[0.5,0,0],[1,0.5,0],[0.5,1,0],[0,0.5,0],[0.145,0.145,0],[0.8555,0.145,0],[0.855,0.8555,0],[0.145,0.855,0]];verticalLabelPosition=bottom;html=1;verticalAlign=top;aspect=fixed;align=center;pointerEvents=1;shape=mxgraph.cisco19.rect;prIcon=router;fillColor=#FAFAFA;strokeColor=#005073;" vertex="1" parent="1">
  <mxGeometry x="400" y="200" width="60" height="60" as="geometry" />
</mxCell>
```

**Device Icon — L3/Distribution Switch (Cisco 19):**
```xml
<mxCell id="SW1" value="" style="sketch=0;points=[[0.015,0.015,0],[0.985,0.015,0],[0.985,0.985,0],[0.015,0.985,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0.25,0],[1,0.5,0],[1,0.75,0],[0.75,1,0],[0.5,1,0],[0.25,1,0],[0,0.75,0],[0,0.5,0],[0,0.25,0]];verticalLabelPosition=bottom;html=1;verticalAlign=top;aspect=fixed;align=center;pointerEvents=1;shape=mxgraph.cisco19.rect;prIcon=l3_switch;fillColor=#FAFAFA;strokeColor=#005073;" vertex="1" parent="1">
  <mxGeometry x="400" y="350" width="60" height="60" as="geometry" />
</mxCell>
```

**Device Icon — L2/Access Switch (Cisco 19):**
```xml
<mxCell id="SW2" value="" style="sketch=0;points=[[0.015,0.015,0],[0.985,0.015,0],[0.985,0.985,0],[0.015,0.985,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0.25,0],[1,0.5,0],[1,0.75,0],[0.75,1,0],[0.5,1,0],[0.25,1,0],[0,0.75,0],[0,0.5,0],[0,0.25,0]];verticalLabelPosition=bottom;html=1;verticalAlign=top;aspect=fixed;align=center;pointerEvents=1;shape=mxgraph.cisco19.rect;prIcon=workgroup_switch;fillColor=#FAFAFA;strokeColor=#005073;" vertex="1" parent="1">
  <mxGeometry x="250" y="500" width="60" height="60" as="geometry" />
</mxCell>
```

**Device Icon — PC / Workstation (Cisco 19):**
```xml
<mxCell id="PC1" value="" style="points=[[0.03,0.03,0],[0.5,0,0],[0.97,0.03,0],[1,0.4,0],[0.97,0.745,0],[0.5,1,0],[0.03,0.745,0],[0,0.4,0]];verticalLabelPosition=bottom;sketch=0;html=1;verticalAlign=top;aspect=fixed;align=center;pointerEvents=1;shape=mxgraph.cisco19.workstation;fillColor=#005073;strokeColor=none;" vertex="1" parent="1">
  <mxGeometry x="260" y="660" width="50" height="40" as="geometry" />
</mxCell>
```

**Device Label (left of icon):**
```xml
<mxCell id="R1_lbl" value="R1&#10;Hub/ABR&#10;10.1.1.1/32" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=top;whiteSpace=wrap;rounded=0;fontSize=11;fontStyle=1" vertex="1" parent="1">
  <mxGeometry x="300" y="193" width="100" height="60" as="geometry" />
</mxCell>
```

**White Connection Line:**
```xml
<mxCell id="link_R1_R2" value="" style="endArrow=none;html=1;strokeWidth=2;strokeColor=#FFFFFF;fillColor=#f5f5f5;" edge="1" parent="1" source="R1" target="R2">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

**IP Last Octet Label:**
```xml
<mxCell id="R1_Fa1_0_octet" value=".1" style="edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;points=[];fontSize=10;" vertex="1" connectable="0" parent="1">
  <mxGeometry x="450" y="260" as="geometry" />
</mxCell>
```

**Legend Box:**
```xml
<mxCell id="legend" value="Legend&#10;--- Physical Link&#10;- - - Tunnel Link&#10;OSPF Process ID: 1&#10;Area 0 (Backbone)" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#000000;strokeColor=#FFFFFF;fontColor=#FFFFFF;fontSize=10;align=left;verticalAlign=top;spacingLeft=8;spacingTop=8;" vertex="1" parent="1">
  <mxGeometry x="600" y="700" width="180" height="100" as="geometry" />
</mxCell>
```

### 4.8 Layout Rules — Avoiding Link Overlap

**Critical Rule**: A connection line must NEVER visually cross through an intermediate device. This happens when three or more devices share the same X coordinate in a vertical chain and a "bypass" link connects non-adjacent devices.

**Problem Pattern** (DO NOT USE when bypass links exist):
```
  R1 (400, 200)    ← bypass link R1→R3 draws a straight
  |                   vertical line through R2
  R2 (400, 400)
  |
  R3 (400, 600)
```

**Solution**: When a bypass link exists between two devices that have intermediate devices at the same X coordinate, **offset the intermediate device(s) horizontally** to create a triangle or staggered layout.

**Correct Pattern** — Offset R2 to create a clear triangle:
```
       R1 (400, 200)
      / \
     /   \              R1→R3 link has clear path on the left
    /     \
  R2 (500, 400)        R2 shifted right by ~100px
    \
     \
      R3 (400, 600)
```

**General Rules**:
1. **Detect bypass links**: Before placing devices, check if any link connects two devices that skip over intermediate devices in the vertical chain.
2. **Offset intermediate devices**: Shift the intermediate device(s) horizontally by at least 100px to create visual separation.
3. **Preferred offset direction**: Shift RIGHT (increase X) unless the right side is occupied by another device (R4, R7), in which case shift LEFT.
4. **Label adjustment**: When a device is offset, its label position must follow — labels go to the LEFT of the device icon, or ABOVE if the left side is crowded.
5. **Octet label adjustment**: IP last-octet labels must be repositioned to remain near their respective interface endpoints after any coordinate changes.

**When bypass links are NOT present** (pure linear chain R1→R2→R3 with no R1→R3 link), the standard vertical column layout at the same X is fine.

### 4.9 Overlay / Tunnel Lines

Tunnel overlays represent **logical connections** that run on top of the physical topology. They must be visually distinct from physical links.

#### 4.9.1 Style Rules

| Property | Value |
|----------|-------|
| Stroke width | `1` (thinner than physical `2`) |
| Dash pattern | `dashed=1;dashPattern=1 4;` (tiny dots, wide gaps) |
| Arrow | `endArrow=none;` |
| Exit point | Top center of source: `exitX=0.5;exitY=0;exitDx=0;exitDy=0;` |
| Entry point | Top center of target: `entryX=0.5;entryY=0;entryDx=0;entryDy=0;` |
| Curve | `curved=1;` |

#### 4.9.2 Color Coding by Tunnel/Overlay Type

All overlay lines use `strokeWidth=1` (thinner than physical `2`), `dashed=1;dashPattern=1 4;` (tiny dots, wide gaps), `curved=1`, and `endArrow=none`. They arc above the physical topology (see §4.9.3).

| Tunnel / Overlay | Color | Hex | Notes |
|-----------------|-------|-----|-------|
| **GRE (bare)** | White | `#FFFFFF` | Plain GRE, no encryption |
| **IPsec (tunnel or transport mode)** | Red | `#F44336` | Encrypted, no GRE wrapper |
| **GRE over IPsec** | Orange | `#FF6D00` | Most common site VPN — GRE for routing + IPsec for encryption |
| **DMVPN (hub-to-spoke / spoke-to-spoke)** | Orange | `#FF6D00` | Same color as GRE/IPsec; label distinguishes (DMVPN Phase I/II/III) |
| **MPLS LSP** | Amber | `#FF6600` | Label-switched path in provider core |
| **VXLAN** | Cyan | `#00AAFF` | Overlay in DC fabrics |
| **L2TP** | Purple | `#AA00FF` | L2 tunnel |
| **SD-WAN / vEdge overlay** | Teal | `#00BCD4` | Cisco SD-WAN data plane |
| **Other / Unknown** | Yellow | `#FFFF00` | Temporary; replace once type is known |

> **GRE vs GRE+IPsec distinction**: White dashed arc = pure GRE (unencrypted, lab/internal). Orange dashed arc = GRE+IPsec (production VPN, encrypted). This is a common CCNP scenario — always label arcs with tunnel interface names and the encapsulation type so the legend can be read unambiguously.

#### 4.9.3 Arc Routing — Curving Over Intermediate Devices

Tunnel lines must arc **above** the physical topology, not route through intermediate devices.

**Algorithm**: Use two waypoints that position the line above both endpoints:
- `arc_y = min(source_y, target_y) - 100` (100px above the higher device)
- Waypoint 1: `(source_x + 39, arc_y)` — above source icon center
- Waypoint 2: `(target_x + 39, arc_y)` — above target icon center

**Example XML** (GRE tunnel R1→R6, R1 at 400,200 and R6 at 200,200):
```xml
<mxCell id="tunnel_R1_R6" value="" style="endArrow=none;html=1;strokeWidth=1;strokeColor=#FFFFFF;fillColor=none;dashed=1;dashPattern=1 4;curved=1;exitX=0.5;exitY=0;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;" edge="1" parent="1" source="R1" target="R6">
  <mxGeometry relative="1" as="geometry">
    <Array as="points">
      <mxPoint x="439" y="100"/>
      <mxPoint x="239" y="100"/>
    </Array>
  </mxGeometry>
</mxCell>
<mxCell id="tunnel_R1_R6_lbl" value="Tunnel8 - Tunnel8&#10;172.16.16.0/30&#10;[GRE]" style="edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;points=[];fontSize=10;" vertex="1" connectable="0" parent="tunnel_R1_R6">
  <mxGeometry relative="1" as="geometry"><mxPoint as="offset"/></mxGeometry>
</mxCell>
```

#### 4.9.4 Tunnel Endpoint Octet Labels

Each tunnel arc endpoint must have a small `.1` / `.2` last-octet label placed **near the top of the device**, at the point where the arc exits/enters.

- **Source device** gets `.1`: position `(source_x + 44, source_y - 15)`
- **Target device** gets `.2`: position `(target_x + 44, target_y - 15)`
- **Style**: `edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;points=[];fontSize=10;`
- **Parent**: `"1"` (canvas root — same as physical octet labels, NOT parented to the tunnel edge)

**Example XML** (R1 at 400,200 → R6 at 200,200):
```xml
<mxCell id="tunnel_R1_R6_0_src_octet" value=".1"
  style="edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;points=[];fontSize=10;"
  vertex="1" connectable="0" parent="1">
  <mxGeometry x="444" y="185" as="geometry" />
</mxCell>
<mxCell id="tunnel_R1_R6_0_dst_octet" value=".2"
  style="edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;points=[];fontSize=10;"
  vertex="1" connectable="0" parent="1">
  <mxGeometry x="244" y="185" as="geometry" />
</mxCell>
```

#### 4.9.5 Legend Requirements

The legend box must list each tunnel type present in the diagram:
```
Legend
--- Physical Link
....... GRE Tunnel (white)
....... IPsec VPN (red)
....... MPLS (orange)
EIGRP AS 100
```

#### 4.9.6 Baseline YAML Structure

Tunnel overlays are defined in the `tunnel_overlays` top-level section of `baseline.yaml`, keyed by lab number:

```yaml
tunnel_overlays:
  - lab: 8
    type: gre
    source: R1:Tunnel8
    target: R6:Tunnel8
    subnet: 172.16.16.0/30
    description: GRE Tunnel for EIGRP over VPN
```

### 4.10 Protocol Domain Zones (Area / AS Overlays)

Domain zones represent logical groupings of devices and links that share a routing boundary — OSPF areas, BGP autonomous systems, VRFs, MPLS domains, etc. They are drawn as **dashed, semi-transparent colored ellipses** that sit visually behind all routers and links.

#### 4.10.1 Drawing Order — Zones First

Zone shapes **must be placed before** (earlier in the XML than) all router cells and link cells. Draw.io renders cells in document order; placing zones first ensures they appear behind devices and lines.

#### 4.10.2 Zone Shape Style

All zone shapes share the same base style pattern:

```
ellipse;whiteSpace=wrap;html=1;dashed=1;strokeWidth=2;opacity=35;
fontSize=12;fontStyle=1;fontColor=#ffffff;
strokeColor=<COLOR>;fillColor=<DARK_FILL>;
verticalAlign=<top|bottom>;
```

- `dashed=1` — boundary is always dashed (never solid)
- `opacity=35` — semi-transparent so routers and links show through
- `fontColor=#ffffff` — white text so label reads against dark canvas
- `fillColor` — a dark-tinted version of the stroke color (see table below)
- `verticalAlign` — place label at `top` if devices occupy the bottom of the ellipse, `bottom` if devices are near the top

#### 4.10.3 Color Table by Domain Type

| Domain Type            | strokeColor | fillColor | Label example              |
|------------------------|-------------|-----------|----------------------------|
| OSPF Area 0 (Backbone) | `#1565C0`   | `#1a3a5c` | `Area 0 (Backbone)`        |
| OSPF Area N (Normal)   | `#2E7D32`   | `#1b3d27` | `Area 1`                   |
| OSPF Stub              | `#E65100`   | `#4a1e00` | `Area 2 (Stub)`            |
| OSPF Totally Stubby    | `#E65100`   | `#4a1e00` | `Area 2 (Totally Stubby)`  |
| OSPF NSSA              | `#6A1B9A`   | `#2e0d40` | `Area 3 (NSSA)`            |
| BGP AS (first/local)   | `#00838F`   | `#003d45` | `AS 65001 (iBGP)`          |
| BGP AS (peer 2)        | `#F57F17`   | `#4a2700` | `AS 65002`                 |
| BGP AS (peer 3)        | `#AD1457`   | `#45072a` | `AS 65003`                 |
| BGP AS (peer 4+)       | `#558B2F`   | `#243d13` | `AS 65004`                 |
| VRF instance           | `#4527A0`   | `#1a0f40` | `VRF CUSTOMER-A`           |
| MPLS domain            | `#37474F`   | `#1a2226` | `MPLS Core`                |

> **Rule:** Each distinct domain gets a unique color from the table. When multiple OSPF areas are present, Area 0 is always blue; assign subsequent normal areas green; assign stub/NSSA areas orange/purple. For BGP, assign one color per AS — rotate through the BGP rows in order.

#### 4.10.4 Zone Sizing and Positioning

- The ellipse must **fully enclose** all devices and links that belong to the zone, with at least 20–30px of padding around the outermost device edges.
- Zones that **share a device** (e.g., an ABR in Area 0 and Area 1) will **overlap** — this is correct and expected. The semi-transparent fills stack and show the shared boundary visually.
- Zones for larger areas (backbone Area 0) are typically wider and taller; peripheral areas (stub, NSSA) are smaller ellipses containing only their few devices.

#### 4.10.5 Zone Label Placement

- The label text inside the ellipse identifies the zone name and type.
- Use `verticalAlign=top` to place the label at the top of the ellipse when devices sit in the lower portion.
- Use `verticalAlign=bottom` to place the label at the bottom when devices sit near the top of the ellipse.
- Never center the label vertically if it would overlap a router icon.

#### 4.10.6 Reference XML Snippet — Zone Shapes

**OSPF Area 0 (Backbone) — blue:**
```xml
<!-- Draw zones FIRST — before any router or link cells -->
<mxCell id="area0_shape" value="Area 0&#xa;(Backbone)"
  style="ellipse;whiteSpace=wrap;html=1;dashed=1;strokeColor=#1565C0;strokeWidth=2;
         fillColor=#1a3a5c;opacity=35;fontSize=12;fontStyle=1;
         verticalAlign=top;fontColor=#ffffff;"
  vertex="1" parent="1">
  <mxGeometry x="20" y="55" width="540" height="380" as="geometry" />
</mxCell>
```

**OSPF Area 1 (Normal) — green:**
```xml
<mxCell id="area1_shape" value="Area 1"
  style="ellipse;whiteSpace=wrap;html=1;dashed=1;strokeColor=#2E7D32;strokeWidth=2;
         fillColor=#1b3d27;opacity=35;fontSize=12;fontStyle=1;
         verticalAlign=bottom;fontColor=#ffffff;"
  vertex="1" parent="1">
  <mxGeometry x="20" y="380" width="520" height="180" as="geometry" />
</mxCell>
```

**OSPF Stub / Totally Stubby Area — orange:**
```xml
<mxCell id="area2_shape" value="Area 2&#xa;(Totally Stubby)"
  style="ellipse;whiteSpace=wrap;html=1;dashed=1;strokeColor=#E65100;strokeWidth=2;
         fillColor=#4a1e00;opacity=35;fontSize=12;fontStyle=1;
         verticalAlign=top;fontColor=#ffffff;"
  vertex="1" parent="1">
  <mxGeometry x="448" y="335" width="310" height="125" as="geometry" />
</mxCell>
```

**BGP Autonomous System — teal (local AS) and orange (peer AS):**
```xml
<!-- Local AS -->
<mxCell id="as65001_shape" value="AS 65001&#xa;(iBGP)"
  style="ellipse;whiteSpace=wrap;html=1;dashed=1;strokeColor=#00838F;strokeWidth=2;
         fillColor=#003d45;opacity=35;fontSize=12;fontStyle=1;
         verticalAlign=top;fontColor=#ffffff;"
  vertex="1" parent="1">
  <mxGeometry x="20" y="55" width="420" height="340" as="geometry" />
</mxCell>

<!-- Peer AS -->
<mxCell id="as65002_shape" value="AS 65002"
  style="ellipse;whiteSpace=wrap;html=1;dashed=1;strokeColor=#F57F17;strokeWidth=2;
         fillColor=#4a2700;opacity=35;fontSize=12;fontStyle=1;
         verticalAlign=top;fontColor=#ffffff;"
  vertex="1" parent="1">
  <mxGeometry x="500" y="55" width="280" height="240" as="geometry" />
</mxCell>
```

#### 4.10.7 Legend Requirements for Zones

When zone shapes are present, the legend box must list each zone with its color. Format:

```
Legend
--- Physical Link
[blue dashed] Area 0 (Backbone)
[green dashed] Area 1 (Normal)
[orange dashed] Area 2 (Totally Stubby)
OSPF Process ID: 1
```

Since Draw.io legend cells are plain text, describe colors in words or use Unicode colored indicators where possible. At minimum, name each zone and its type.

#### 4.10.8 When to Apply Zone Shapes

| Lab type                          | Zones to draw                                           |
|-----------------------------------|---------------------------------------------------------|
| OSPF single-area                  | One Area 0 ellipse enclosing all devices                |
| OSPF multi-area                   | One ellipse per area; ABRs sit inside overlapping zones |
| OSPF stub / totally stubby / NSSA | Area 0 + any normal areas + stub/NSSA area (orange/purple) |
| BGP single-AS                     | One AS ellipse around all iBGP peers                    |
| BGP multi-AS (eBGP)               | One ellipse per AS; eBGP links cross zone boundaries    |
| EIGRP                             | One ellipse per AS number if multiple ASes present      |
| VRF / MPLS                        | One ellipse per VRF or MPLS domain if topologically relevant |
| Single-protocol flat topology     | Zone shapes optional but recommended for clarity        |

### 4.11 Site / Location Containers

Site containers group devices by **physical or organizational location** — HQ, branch, data center, ISP network, internet. They are distinct from protocol domain zones (§4.10): zones show routing boundaries, containers show where equipment lives. Both can be present simultaneously.

#### 4.11.1 Drawing Order

Site containers must appear **before** zone ellipses and **before** all device cells in the XML. Draw.io renders in document order — deepest background first:

```
XML order (top to bottom):
  1. Site containers (§4.11)  ← background layer
  2. Protocol domain zones (§4.10)
  3. Device cells + link cells
```

#### 4.11.2 Container Style

Site containers use a **solid-border rounded rectangle** (vs the dashed ellipse used for zones):

```
Base style:
rounded=1;whiteSpace=wrap;html=1;
strokeWidth=2;opacity=20;
fontSize=13;fontStyle=1;fontColor=#FFFFFF;
verticalAlign=top;spacingTop=6;
```

`opacity=20` keeps the fill subtle so devices inside remain readable.

#### 4.11.3 Color Table by Site Type

| Site Type | strokeColor | fillColor | Label example |
|-----------|-------------|-----------|---------------|
| **HQ / Headquarters** | `#1565C0` | `#0D2137` | `HQ — Chicago` |
| **Branch / Remote site** | `#2E7D32` | `#0D2110` | `Branch — Dallas` |
| **Data Center** | `#6A1B9A` | `#1A0933` | `Data Center` |
| **Service Provider / MPLS cloud** | `#00695C` | `#00201C` | `ISP — MPLS Core` |
| **Internet / WAN cloud** | `#546E7A` | `#1A2226` | `Internet` |
| **Campus / Building** | `#E65100` | `#2D1200` | `Campus A` |

#### 4.11.4 Reference XML Snippets

**HQ site container:**
```xml
<mxCell id="site_hq" value="HQ — Chicago"
  style="rounded=1;whiteSpace=wrap;html=1;strokeColor=#1565C0;strokeWidth=2;
         fillColor=#0D2137;opacity=20;fontSize=13;fontStyle=1;
         fontColor=#FFFFFF;verticalAlign=top;spacingTop=6;"
  vertex="1" parent="1">
  <mxGeometry x="20" y="40" width="500" height="400" as="geometry"/>
</mxCell>
```

**Branch / Remote site container:**
```xml
<mxCell id="site_branch" value="Branch — Dallas"
  style="rounded=1;whiteSpace=wrap;html=1;strokeColor=#2E7D32;strokeWidth=2;
         fillColor=#0D2110;opacity=20;fontSize=13;fontStyle=1;
         fontColor=#FFFFFF;verticalAlign=top;spacingTop=6;"
  vertex="1" parent="1">
  <mxGeometry x="600" y="40" width="400" height="300" as="geometry"/>
</mxCell>
```

**Internet / WAN cloud container:**
```xml
<mxCell id="site_internet" value="Internet"
  style="rounded=1;whiteSpace=wrap;html=1;strokeColor=#546E7A;strokeWidth=2;
         fillColor=#1A2226;opacity=20;fontSize=13;fontStyle=1;
         fontColor=#FFFFFF;verticalAlign=top;spacingTop=6;dashed=1;dashPattern=8 4;"
  vertex="1" parent="1">
  <mxGeometry x="300" y="200" width="300" height="200" as="geometry"/>
</mxCell>
```

> The Internet/WAN container uses a long-dash border (`8 4`) to signal it is outside the operator's control, unlike solid-border managed sites.

#### 4.11.5 When to Apply Site Containers

| Diagram scenario | Containers to draw |
|------------------|--------------------|
| Hub-and-spoke WAN / DMVPN | HQ + one container per spoke site |
| SD-WAN topology | HQ, branches, data center, internet |
| Campus + DC | Campus container + Data Center container |
| Single flat lab (all devices co-located) | None — omit containers, keep diagram clean |
| Multi-site OSPF / BGP | One container per site; zone ellipses overlay them |

--# 5. Workflow

### Creating a New Diagram
1.  Open Draw.io (Desktop or Web).
2.  Create the diagram following the Visual Style Guide (Section 4).
3.  **Validation Checklist**:
    - [ ] Title is at the top center, bold, 16pt.
    - [ ] Device labels are on the **empty side** of the icon (no connection lines on that side). See §4.3.1.
    - [ ] Every device has a hostname, role, and Loopback IP.
    - [ ] Every link uses the correct **type, color, and thickness** from §4.4.1:
      - [ ] Trunk links are gold (`#FFD700`), stroke=2.
      - [ ] EtherChannel bundles are white, stroke=5.
      - [ ] Access ports are white, stroke=1.
      - [ ] Management/OOB links are gray dashed.
      - [ ] OSPF virtual links are lavender dashed.
    - [ ] Every link has interface names on BOTH ends.
    - [ ] Every router interface has a **last octet** label (`.1`, `.2`) near the device. See §4.5.
    - [ ] Subnet ID is visible on every routed link.
    - [ ] **No link visually crosses through an intermediate device**. See §4.8.
    - [ ] **Tunnel overlays** arc above physical topology, use thin colored dotted lines. See §4.9.
      - [ ] GRE+IPsec is orange (`#FF6D00`), not the same white as bare GRE.
      - [ ] Tunnel endpoint octets (`.1`/`.2`) are placed near the top of source/target devices.
    - [ ] **Protocol domain zones** (OSPF areas, BGP AS, VRFs) are dashed semi-transparent ellipses placed FIRST in XML. See §4.10.
      - [ ] Each zone uses the correct color from §4.10.3.
      - [ ] Zone ellipses fully enclose members with ≥20px padding; ABR/ASBR overlaps are expected.
    - [ ] **Site containers** (HQ, branch, DC, internet) are solid rounded rectangles placed BEFORE zone ellipses in XML. See §4.11.
    - [ ] **Legend box** is present (black fill, white text, bottom-right) and lists: link type colors, tunnel colors, zone/site key. See §4.6.
4.  Save the editable file as `.drawio` in the appropriate subdirectory.

### Updating a Diagram
1.  Open the existing `.drawio` file.
2.  Make necessary modifications.
3.  Validate against the checklist above.
4.  Save the `.drawio` file.

-# Common Issues

--# Zone ellipses cover (obscure) routers and links

- **Cause:** Zone shape cells were placed after router and link cells in the XML, causing them to render on top of everything.
- **Solution:** Move all zone `mxCell` elements to appear before the first router cell in the XML. Draw.io renders in document order — zones must come first.

--# Zone ellipse does not enclose all member devices

- **Cause:** Ellipse geometry was sized for the routers but did not account for labels or link endpoints extending beyond the icon bounds.
- **Solution:** Extend the ellipse by at least 20–30px beyond the outermost device icon on every side. Check that interface octet labels near the zone boundary are also inside the ellipse.

--# Connection lines are black instead of white
- **Cause:** Default Draw.io line color was used without applying the style guide.
- **Solution:** Select all connection lines and apply `strokeColor=#FFFFFF;strokeWidth=2` from Section 4.4. Run `scripts/generate_topo.py` to auto-generate a compliant diagram from `baseline.yaml`.

--# Link visually crosses through an intermediate device
- **Cause:** Three or more devices share the same X coordinate and a bypass link connects non-adjacent ones.
- **Solution:** Offset the intermediate device(s) horizontally by at least 100px to create a triangle or staggered layout. See Section 4.8 for the full rule and example.

--# Device label overlaps a connection line
- **Cause:** Label was placed on the same side as one or more connected links.
- **Solution:** Apply the Empty Side Rule (Section 4.3.1) — place the label on the side with no connections exiting the icon.

--# generate_topo.py produces incorrect output
- **Cause:** `baseline.yaml` is missing required fields (`links`, device coordinates, or interface definitions).
- **Solution:** Verify `baseline.yaml` has complete `core_topology.links` with `source`, `target`, and `subnet` for every link. Check for missing `loopback0` values on devices.
