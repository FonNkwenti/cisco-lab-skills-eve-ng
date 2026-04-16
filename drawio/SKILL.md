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

- **Background**: `#1a1a2e` (dark navy). Set in the `mxGraphModel` attribute: `background="#1a1a2e"`.
- **Title**: Positioned at the **top center** of the canvas. Bold, 17pt, white text.
- **Legend Box**: Required in every diagram. Positioned at the **bottom-right** corner. Black fill (`#000000`) with white text (`#FFFFFF`), rounded corners, 10pt font.

### 4.2 Device Icons — Cisco 19 Shape Library

All devices use the **Cisco 19** shape library. The pattern is:
- Network devices: `shape=mxgraph.cisco19.rect;prIcon=<ICON>` (shared rect base + icon overlay)
- Cloud/Internet: `shape=mxgraph.cisco19.cloud` (dedicated shape — do NOT use `rect+prIcon` for cloud)
- Workstations/VPCs: `shape=mxgraph.cisco19.workstation` (dedicated shape)

#### 4.2.1 Style Strings

**Router:**
```
sketch=0;points=[[0.5,0,0],[1,0.5,0],[0.5,1,0],[0,0.5,0],[0.145,0.145,0],[0.8555,0.145,0],[0.855,0.8555,0],[0.145,0.855,0]];html=1;aspect=fixed;align=center;pointerEvents=1;shape=mxgraph.cisco19.rect;prIcon=router;fillColor=#FAFAFA;strokeColor=#005073;
```

**L3 / Distribution Switch:**
```
sketch=0;points=[[0.015,0.015,0],[0.985,0.015,0],[0.985,0.985,0],[0.015,0.985,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0.25,0],[1,0.5,0],[1,0.75,0],[0.75,1,0],[0.5,1,0],[0.25,1,0],[0,0.75,0],[0,0.5,0],[0,0.25,0]];html=1;aspect=fixed;align=center;pointerEvents=1;shape=mxgraph.cisco19.rect;prIcon=l3_switch;fillColor=#FAFAFA;strokeColor=#005073;
```

**L2 / Access / Workgroup Switch:**
Same `points=` as L3 switch above, with `prIcon=workgroup_switch`.

**Firewall:**
Use `prIcon=firewall` with the router `points=` string.

**Cloud / Internet (standalone icon — NOT a site container):**
```
points=[[0,0.64,0],[0.2,0.15,0],[0.4,0.01,0],[0.79,0.25,0],[1,0.65,0],[0.8,0.86,0],[0.41,1,0],[0.16,0.86,0]];sketch=0;html=1;verticalLabelPosition=bottom;verticalAlign=top;aspect=fixed;align=center;pointerEvents=1;shape=mxgraph.cisco19.cloud;fillColor=#6B6B6B;strokeColor=none;
```
Typical size: `207x124` (wider than tall).

**PC / Workstation / VPC endpoint:**
```
points=[[0.03,0.03,0],[0.5,0,0],[0.97,0.03,0],[1,0.4,0],[0.97,0.745,0],[0.5,1,0],[0.03,0.745,0],[0,0.4,0]];sketch=0;html=1;verticalLabelPosition=bottom;verticalAlign=top;aspect=fixed;align=center;pointerEvents=1;shape=mxgraph.cisco19.workstation;fillColor=#005073;strokeColor=none;
```

#### 4.2.2 Sizes

| Device type | Width | Height |
|-------------|-------|--------|
| Router, L3/L2 switch, firewall | 60 | 60 |
| Workstation / VPC | 50 | 40 |
| Cloud / Internet | ~207 | ~124 |

All network device icons use `aspect=fixed` (square, 1:1 ratio).

### 4.3 Device Labels

Labels are embedded directly in the device cell's `value=` attribute as HTML. Use this format:

```html
<b style="color:#FFFFFF;">HOSTNAME</b><br>
<font color="#CCCCCC" style="font-size:10px;">Role description<br>Lo0: 10.0.0.1/32</font>
```

Separate label cells are NOT used — the label lives inside the icon cell.

#### 4.3.1 Smart Label Placement — Empty Side Rule

**Place the label on the side that has NO connection lines exiting the device.**

Decision process:
1. List all neighbors and their relative position (left, right, above, below).
2. Identify the side with no neighbors — place the label there.
3. If all four sides are occupied (or no clear empty side), **default to bottom**.

| Placement | Style attributes to add to device cell |
|-----------|----------------------------------------|
| **LEFT** | `labelPosition=left;verticalLabelPosition=middle;align=right;verticalAlign=middle;` |
| **RIGHT** | `labelPosition=right;verticalLabelPosition=middle;align=left;verticalAlign=middle;` |
| **BOTTOM** (default) | `verticalLabelPosition=bottom;verticalAlign=top;align=center;labelPosition=center;` |
| **TOP** | `verticalLabelPosition=top;verticalAlign=bottom;align=center;labelPosition=center;` |

**Heuristics:**
- Devices on the **right edge** of the topology → neighbors are to the left → label **RIGHT**
- Devices on the **left edge** → neighbors are to the right → label **LEFT**
- Devices at the **bottom** of a column (link only goes up) → label **BOTTOM** (bottom is free)
- Devices at the **top** of a column (link only goes down) → label **TOP** (top is free)
- Devices with links in **multiple directions** → label **BOTTOM** (default)

**Examples from the style-guide reference diagram:**
- **R1** (center, links go right/left/up/down) → BOTTOM (all sides used — default)
- **SW1** (center, links up/down-left/down-right — left side free) → **LEFT**
- **SW2** (left pod, link up-right to SW1 and down to PC1 — left side free) → **LEFT**
- **SW3** (right pod, link up-left to SW1 and down to PC2 — right side free) → **RIGHT**
- **R2** (right edge of branch, links left/down) → **RIGHT**
- **SW4** (right column, links up/down — right side free) → **RIGHT**
- **PC1/PC2/PC3** (bottom of column, link only goes up) → **BOTTOM**

### 4.4 Connection Lines

#### 4.4.1 Link Type Reference Table

| Link Type | Color | Hex | strokeWidth | Dashed | dashPattern |
|-----------|-------|-----|-------------|--------|-------------|
| Routed / P2P | White | `#FFFFFF` | 2 | no | — |
| WAN | White | `#FFFFFF` | 2 | no | — (same as routed, no special color) |
| Trunk 802.1Q | Blue | `#006EAF` | 3 | no | — |
| Access port | White | `#FFFFFF` | 1 | no | — |
| EtherChannel / PortChannel | White | `#FFFFFF` | 5 | no | — |
| OOB Management | Gray | `#888888` | 1 | yes | `8 4` (long dash) |
| OSPF Virtual Link | Lavender | `#CE93D8` | 1 | yes | `4 4` (short dash) |

All links use `endArrow=none;html=1;`.

#### 4.4.2 Style Strings

**Routed / P2P / WAN (white, w=2):**
```
endArrow=none;html=1;strokeWidth=2;strokeColor=#FFFFFF;
```

**Trunk 802.1Q (blue, w=3):**
```
endArrow=none;html=1;strokeWidth=3;strokeColor=#006EAF;
```

**Access port (white, w=1):**
```
endArrow=none;html=1;strokeWidth=1;strokeColor=#FFFFFF;
```

**EtherChannel / PortChannel (thick white, w=5):**
```
endArrow=none;html=1;strokeWidth=5;strokeColor=#FFFFFF;
```

**OOB Management (gray, dashed):**
```
endArrow=none;html=1;strokeWidth=1;strokeColor=#888888;dashed=1;dashPattern=8 4;
```

**OSPF Virtual Link (lavender, short-dash):**
```
endArrow=none;html=1;strokeWidth=1;strokeColor=#CE93D8;dashed=1;dashPattern=4 4;
```

#### 4.4.3 Trunk Link — Dual Parallel Lines Convention

Trunk links between switches are shown as **two parallel lines**. Draw two separate edge cells between the same source and target with offset `exitX`/`entryX` values:

```xml
<!-- Trunk line 1 -->
<mxCell id="trunk1" value="" style="endArrow=none;html=1;strokeWidth=3;strokeColor=#006EAF;exitX=0.7;exitY=1;exitDx=0;exitDy=0;entryX=0.3;entryY=0;entryDx=0;entryDy=0;" edge="1" parent="1" source="SW1" target="SW3">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>
<!-- Trunk line 2 (offset) -->
<mxCell id="trunk2" value="" style="endArrow=none;html=1;strokeWidth=3;strokeColor=#006EAF;exitX=0.85;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;" edge="1" parent="1" source="SW1" target="SW3">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>
<!-- Label on the second line -->
<mxCell id="trunk_lbl" value="..." style="edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;points=[];labelBackgroundColor=none;" vertex="1" connectable="0" parent="trunk2">
  <mxGeometry relative="0.5" as="geometry"/>
</mxCell>
```

#### 4.4.4 EtherChannel / PortChannel Convention

An EtherChannel is shown as a **thick white line (w=5)** with **two small rotated ellipses** at each end — one near the source port, one near the target port — to indicate physical port bundling.

**Step 1 — Draw the PortChannel link:**
```xml
<mxCell id="link_po1" value="" style="endArrow=none;html=1;strokeWidth=5;strokeColor=#FFFFFF;exitX=0.25;exitY=1;exitDx=0;exitDy=0;entryX=0.75;entryY=0;entryDx=0;entryDy=0;" edge="1" parent="1" source="SW1" target="SW2">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>
```

**Step 2 — Add ellipse markers at each port (w=20 h=10, rotated to match link angle):**
```xml
<!-- Ellipse near source port -->
<mxCell id="ec_src" value="" style="ellipse;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#FFFFFF;rotation=30;" vertex="1" parent="1">
  <mxGeometry x="<near_source_x>" y="<near_source_y>" width="20" height="10" as="geometry"/>
</mxCell>
<!-- Ellipse near target port -->
<mxCell id="ec_dst" value="" style="ellipse;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#FFFFFF;rotation=30;" vertex="1" parent="1">
  <mxGeometry x="<near_target_x>" y="<near_target_y>" width="20" height="10" as="geometry"/>
</mxCell>
```

Place each ellipse within ~20px of the port's connection point. Adjust `rotation` to match the link angle.

#### 4.4.5 Straight vs. Diagonal Links

**Prefer straight lines (horizontal or vertical) where topology allows.** When a switch connects straight down to a PC, align their center-X so that `exitX=0.5;entryX=0.5` produces a perfectly vertical line.

To enforce straight vertical routing:
```
exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;
```

Alignment rule: for a 60px-wide switch at `x=S` (center=`S+30`), place the 50px-wide PC at `x=S+5` (center=`S+30`).

#### 4.4.6 Edge Labels

Edge labels are parented to their edge cell:
```xml
<mxCell id="lbl1" value="Gi0/1 - Gi0/0&#xa;10.1.1.0/30" style="edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;points=[];labelBackgroundColor=none;" vertex="1" connectable="0" parent="link_id">
  <mxGeometry relative="0.5" as="geometry">
    <mxPoint x="<offset_x>" y="<offset_y>" as="offset"/>
  </mxGeometry>
</mxCell>
```

### 4.5 IP Last Octet Labels

- **Required**: Every router interface endpoint should have a small label showing the **last octet** of its IP address (e.g., `.1`, `.2`).
- **Style**: `edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;points=[];fontSize=10;labelBackgroundColor=#1a1a2e;fontColor=#FFFFFF;`

#### 4.5.1 Placement Geometry (MANDATORY — do not default to midpoint)

Octet labels anchor **close to the device endpoint**, not at the edge midpoint. The `relative` attribute on `<mxGeometry>` is the along-edge position as a fraction of the edge length starting from the edge's **source** node (`0.0` = source end, `1.0` = target end).

| Endpoint | `relative` value | Meaning |
|---|---|---|
| Source-side device (edge `source=`) | `0.05` – `0.10` | 5–10% from source — hugs the source router/interface |
| Target-side device (edge `target=`) | `0.90` – `0.95` | 90–95% from source = 5–10% from target |
| Subnet / interface name label | `0.50` | Midpoint of the edge |

Reference XML — **source-side** `.1` octet, anchored near the source router:
```xml
<mxCell id="lbl_L1_src" value=".1" style="edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;points=[];fontSize=10;fontColor=#FFFFFF;labelBackgroundColor=none;" vertex="1" connectable="0" parent="link_L1">
  <mxGeometry relative="0.08" as="geometry"/>
</mxCell>
```

Reference XML — **target-side** `.2` octet, anchored near the target router:
```xml
<mxCell id="lbl_L1_dst" value=".2" style="edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;points=[];fontSize=10;fontColor=#FFFFFF;labelBackgroundColor=none;" vertex="1" connectable="0" parent="link_L1">
  <mxGeometry relative="0.92" as="geometry"/>
</mxCell>
```

Reference XML — **midpoint** subnet / interface label:
```xml
<mxCell id="lbl_L1_mid" value="Gi0/1&#xa;10.12.0.0/30" style="edgeLabel;html=1;align=center;verticalAlign=middle;resizable=0;points=[];fontSize=10;fontColor=#FFFFFF;labelBackgroundColor=none;" vertex="1" connectable="0" parent="link_L1">
  <mxGeometry relative="0.5" as="geometry">
    <mxPoint x="-30" y="0" as="offset"/>
  </mxGeometry>
</mxCell>
```

**Rules:**
- Use **`relative` ≤ 0.10** for source-side octets and **`relative` ≥ 0.90** for target-side octets so the label sits visibly adjacent to its interface. Anything in `[0.15, 0.85]` drifts toward the midpoint and gets hard to associate with a specific endpoint.
- Default to **no `<mxPoint as="offset"/>`** on octet labels — the `relative` value alone does the placement. Only add a small perpendicular offset (`x` or `y` ≤ 15px) if the label collides with the link line or another label. Never use offset to shift further along the edge.
- **`parent` must be the edge cell's id** (e.g., `parent="link_L1"`), not `"1"`. Octet labels are children of the edge they describe so they track the edge if it moves.
- Subnet labels stay at `relative="0.5"`. Only per-endpoint octets hug the device.

### 4.6 Legend Box

Every diagram must include a legend box:

- **Position**: Bottom-right area of the canvas.
- **Style**: `rounded=1;whiteSpace=wrap;html=1;fillColor=#000000;strokeColor=#FFFFFF;fontColor=#FFFFFF;fontSize=10;align=left;verticalAlign=top;spacingLeft=8;spacingTop=8;arcSize=3;`
- **Content** to include:
  - Physical link types (white=routed/WAN/access, blue=trunk, gray=OOB)
  - EtherChannel: note that ellipses mark bundled ports
  - Tunnel overlay colors (orange=GRE+IPsec, white=bare GRE)
  - OSPF area colors (if zone shapes present)
  - Site colors (if site containers present)
  - Label placement rule: "Label on side with no links; default bottom"

### 4.7 Reference XML Snippets

**Canvas background (on mxGraphModel):**
```xml
<mxGraphModel background="#1a1a2e" ...>
```

**Title Cell:**
```xml
<mxCell id="title" value="&lt;font style=&quot;font-size:17px;&quot; color=&quot;#FFFFFF&quot;&gt;&lt;b&gt;Lab N: Title Here&lt;/b&gt;&lt;/font&gt;" style="text;html=1;align=center;verticalAlign=middle;whiteSpace=wrap;strokeColor=none;fillColor=none;" vertex="1" parent="1">
  <mxGeometry x="200" y="12" width="800" height="35" as="geometry"/>
</mxCell>
```

**Router (label LEFT):**
```xml
<mxCell id="R1" value="&lt;b style=&quot;color:#FFFFFF;&quot;&gt;R1&lt;/b&gt;&lt;br&gt;&lt;font color=&quot;#CCCCCC&quot; style=&quot;font-size:10px;&quot;&gt;HQ Gateway&lt;br&gt;Lo0: 10.0.0.1/32&lt;/font&gt;" style="sketch=0;points=[[0.5,0,0],[1,0.5,0],[0.5,1,0],[0,0.5,0],[0.145,0.145,0],[0.8555,0.145,0],[0.855,0.8555,0],[0.145,0.855,0]];labelPosition=left;verticalLabelPosition=middle;html=1;verticalAlign=middle;aspect=fixed;align=right;pointerEvents=1;shape=mxgraph.cisco19.rect;prIcon=router;fillColor=#FAFAFA;strokeColor=#005073;" vertex="1" parent="1">
  <mxGeometry x="215" y="160" width="60" height="60" as="geometry"/>
</mxCell>
```

**Router (label BOTTOM — default when all sides used):**
```xml
<mxCell id="R1" value="..." style="sketch=0;points=[...];verticalLabelPosition=bottom;html=1;verticalAlign=top;aspect=fixed;align=center;labelPosition=center;pointerEvents=1;shape=mxgraph.cisco19.rect;prIcon=router;fillColor=#FAFAFA;strokeColor=#005073;" vertex="1" parent="1">
  <mxGeometry x="215" y="160" width="60" height="60" as="geometry"/>
</mxCell>
```

**L3 Switch (label LEFT):**
```xml
<mxCell id="SW1" value="..." style="sketch=0;points=[[0.015,0.015,0],...];labelPosition=left;verticalLabelPosition=middle;html=1;verticalAlign=middle;aspect=fixed;align=right;pointerEvents=1;shape=mxgraph.cisco19.rect;prIcon=l3_switch;fillColor=#FAFAFA;strokeColor=#005073;" vertex="1" parent="1">
  <mxGeometry x="215" y="340" width="60" height="60" as="geometry"/>
</mxCell>
```

**L2 Switch (label RIGHT):**
```xml
<mxCell id="SW3" value="..." style="sketch=0;points=[[0.015,...]...];labelPosition=right;verticalLabelPosition=middle;html=1;verticalAlign=middle;aspect=fixed;align=left;pointerEvents=1;shape=mxgraph.cisco19.rect;prIcon=workgroup_switch;fillColor=#FAFAFA;strokeColor=#005073;" vertex="1" parent="1">
  <mxGeometry x="340" y="530" width="60" height="60" as="geometry"/>
</mxCell>
```

**Workstation/VPC (label BOTTOM):**
```xml
<mxCell id="PC1" value="&lt;b style=&quot;color:#FFFFFF;&quot;&gt;PC1&lt;/b&gt;&lt;br&gt;&lt;font color=&quot;#CCCCCC&quot; style=&quot;font-size:10px;&quot;&gt;VPC — VLAN10&lt;br&gt;192.168.10.10&lt;/font&gt;" style="points=[[0.03,0.03,0],[0.5,0,0],[0.97,0.03,0],[1,0.4,0],[0.97,0.745,0],[0.5,1,0],[0.03,0.745,0],[0,0.4,0]];verticalLabelPosition=bottom;sketch=0;html=1;verticalAlign=top;aspect=fixed;align=center;pointerEvents=1;shape=mxgraph.cisco19.workstation;fillColor=#005073;strokeColor=none;" vertex="1" parent="1">
  <mxGeometry x="105" y="730" width="50" height="40" as="geometry"/>
</mxCell>
```

**Cloud / Internet icon:**
```xml
<mxCell id="cloud_internet" value="&lt;b style=&quot;color:#FFFFFF;&quot;&gt;Internet&lt;/b&gt;" style="points=[[0,0.64,0],[0.2,0.15,0],[0.4,0.01,0],[0.79,0.25,0],[1,0.65,0],[0.8,0.86,0],[0.41,1,0],[0.16,0.86,0]];verticalLabelPosition=bottom;sketch=0;html=1;verticalAlign=top;aspect=fixed;align=center;pointerEvents=1;shape=mxgraph.cisco19.cloud;fillColor=#6B6B6B;strokeColor=none;" vertex="1" parent="1">
  <mxGeometry x="680" y="100" width="207" height="124" as="geometry"/>
</mxCell>
```

**White (routed/WAN) Connection Line:**
```xml
<mxCell id="link_R1_SW1" value="" style="endArrow=none;html=1;strokeWidth=2;strokeColor=#FFFFFF;" edge="1" parent="1" source="R1" target="SW1">
  <mxGeometry relative="1" as="geometry"/>
</mxCell>
```

**Legend Box:**
```xml
<mxCell id="legend" value="&lt;b&gt;LEGEND&lt;/b&gt;..." style="rounded=1;whiteSpace=wrap;html=1;fillColor=#000000;strokeColor=#FFFFFF;fontColor=#FFFFFF;fontSize=10;align=left;verticalAlign=top;spacingLeft=8;spacingTop=8;arcSize=3;" vertex="1" parent="1">
  <mxGeometry x="1270" y="620" width="300" height="350" as="geometry"/>
</mxCell>
```

### 4.8 Layout Rules — Avoiding Link Overlap

**Critical Rule**: A connection line must NEVER visually cross through an intermediate device. This happens when three or more devices share the same X coordinate in a vertical chain and a "bypass" link connects non-adjacent devices.

**Problem Pattern** (DO NOT USE when bypass links exist):
```
  R1 (400, 200)    <- bypass link R1->R3 draws a straight
  |                   vertical line through R2
  R2 (400, 400)
  |
  R3 (400, 600)
```

**Solution**: Offset the intermediate device(s) horizontally by at least 100px.

**General Rules**:
1. Before placing devices, check if any link connects two devices that skip over intermediate devices in the vertical chain.
2. Shift the intermediate device(s) by at least 100px horizontally.
3. Shift RIGHT unless right side is occupied, then shift LEFT.
4. Reapply the Empty Side Rule (§4.3.1) after any offset.

**When bypass links are NOT present** (pure linear chain), the standard vertical column at the same X is fine.

### 4.9 Overlay / Tunnel Lines

Tunnel overlays represent **logical connections** running on top of the physical topology.

#### 4.9.1 Style Rules

| Property | Value |
|----------|-------|
| Stroke width | `1` (thinner than physical `2`) |
| Dash pattern | `dashed=1;dashPattern=1 4;` (tiny dots, wide gaps) |
| Arrow | `endArrow=none;` |
| Exit point | Top center of source: `exitX=0.5;exitY=0;exitDx=0;exitDy=0;` |
| Entry point | Top center of target: `entryX=0.5;entryY=0;entryDx=0;entryDy=0;` |
| Curve | `curved=1;` |

#### 4.9.2 Color Coding by Tunnel Type

| Tunnel Type | Color | Hex | Notes |
|-------------|-------|-----|-------|
| GRE (bare, unencrypted) | White | `#FFFFFF` | Label distinguishes from physical |
| GRE over IPsec / DMVPN | Orange | `#FF6D00` | Encrypted VPN tunnels |
| SD-WAN / vEdge | Teal | `#00BCD4` | |
| MPLS | Orange (alt) | `#FF6600` | |
| VXLAN | Cyan | `#00AAFF` | |
| L2TP | Purple | `#AA00FF` | |

**Rule**: White dashed = unencrypted tunnel; Orange dashed = encrypted/IPsec VPN.

#### 4.9.3 Arc Routing — Curving Over Intermediate Devices

Use two waypoints above both endpoints:
- `arc_y = min(source_y, target_y) - 100`
- Waypoint 1: `(source_center_x, arc_y)`
- Waypoint 2: `(target_center_x, arc_y)`

**Example XML** (GRE+IPsec tunnel R1→R2, arcing above the sites):
```xml
<mxCell id="tunnel_gre_ipsec" value="" style="endArrow=none;html=1;strokeWidth=1;strokeColor=#FF6D00;dashed=1;dashPattern=1 4;curved=1;exitX=0.5;exitY=0;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;" edge="1" parent="1" source="R1" target="R2">
  <mxGeometry relative="1" as="geometry">
    <Array as="points">
      <mxPoint x="245" y="38"/>
      <mxPoint x="1130" y="38"/>
    </Array>
  </mxGeometry>
</mxCell>
```

### 4.10 Protocol Domain Zones (Area / AS Overlays)

Domain zones are drawn as **dashed, semi-transparent colored rounded rectangles** placed visually behind all routers and links.

#### 4.10.1 Drawing Order — Zones First

Zone shapes **must be placed before** all device cells and link cells in the XML. Draw.io renders in document order.

#### 4.10.2 Zone Shape Style

```
rounded=1;arcSize=5;whiteSpace=wrap;html=1;dashed=1;strokeWidth=2;opacity=35;
fontSize=12;fontStyle=1;fontColor=#ffffff;
strokeColor=<COLOR>;fillColor=<DARK_FILL>;
verticalAlign=<top|bottom>;
```

#### 4.10.3 Color Table by Domain Type

| Domain Type            | strokeColor | fillColor | Label example              |
|------------------------|-------------|-----------|----------------------------|
| OSPF Area 0 (Backbone) | `#1565C0`   | `#1a3a5c` | `Area 0 (Backbone)`        |
| OSPF Area N (Normal)   | `#2E7D32`   | `#1b3d27` | `Area 1`                   |
| OSPF Stub / NSSA       | `#E65100`   | `#4a1e00` | `Area 2 (Stub)`            |
| OSPF Totally Stubby    | `#E65100`   | `#4a1e00` | `Area 2 (Totally Stubby)`  |
| OSPF NSSA              | `#6A1B9A`   | `#2e0d40` | `Area 3 (NSSA)`            |
| BGP AS (local)         | `#00838F`   | `#003d45` | `AS 65001 (iBGP)`          |
| BGP AS (peer 2)        | `#F57F17`   | `#4a2700` | `AS 65002`                 |
| BGP AS (peer 3+)       | `#AD1457`   | `#45072a` | `AS 65003`                 |
| VRF instance           | `#4527A0`   | `#1a0f40` | `VRF CUSTOMER-A`           |
| MPLS domain            | `#37474F`   | `#1a2226` | `MPLS Core`                |

#### 4.10.4 Zone Sizing and Positioning

- Zone shapes must **fully enclose** all member devices with ≥20px padding on every side.
- Zones sharing a device (ABR in Area 0 and Area 1) will **overlap** — this is correct.
- Use `verticalAlign=top` when devices occupy the bottom of the zone; `verticalAlign=bottom` otherwise.

#### 4.10.5 Reference XML Snippets

**OSPF Area 0 (Backbone):**
```xml
<mxCell id="zone_area0" value="Area 0&#xa;(Backbone)" style="rounded=1;arcSize=5;whiteSpace=wrap;html=1;dashed=1;strokeColor=#1565C0;strokeWidth=2;fillColor=#1a3a5c;opacity=35;fontSize=12;fontStyle=1;verticalAlign=top;fontColor=#FFFFFF;" vertex="1" parent="1">
  <mxGeometry x="10" y="80" width="555" height="260" as="geometry"/>
</mxCell>
```

**OSPF Area 1 (Normal/Stub):**
```xml
<mxCell id="zone_area1" value="Area 1&#xa;(Stub)" style="rounded=1;arcSize=5;whiteSpace=wrap;html=1;dashed=1;strokeColor=#2E7D32;strokeWidth=2;fillColor=#1b3d27;opacity=35;fontSize=12;fontStyle=1;verticalAlign=bottom;fontColor=#FFFFFF;" vertex="1" parent="1">
  <mxGeometry x="55" y="290" width="510" height="380" as="geometry"/>
</mxCell>
```

**BGP AS (local):**
```xml
<mxCell id="as65001" value="AS 65001&#xa;(iBGP)" style="rounded=1;arcSize=5;whiteSpace=wrap;html=1;dashed=1;strokeColor=#00838F;strokeWidth=2;fillColor=#003d45;opacity=35;fontSize=12;fontStyle=1;verticalAlign=top;fontColor=#FFFFFF;" vertex="1" parent="1">
  <mxGeometry x="20" y="55" width="420" height="340" as="geometry"/>
</mxCell>
```

### 4.11 Site Containers (HQ, Branch, DC, Internet)

Site containers are **solid-border rounded rectangles** grouping devices by physical location.

#### 4.11.1 Container Style

```
rounded=1;arcSize=2;whiteSpace=wrap;html=1;strokeWidth=2;opacity=20;
fontSize=13;fontStyle=1;fontColor=#FFFFFF;verticalAlign=top;spacingTop=6;
strokeColor=<SITE_COLOR>;fillColor=<DARK_FILL>;
```

- `arcSize=2` — very slight rounding (nearly square corners)
- `opacity=20` — semi-transparent so devices inside are visible

#### 4.11.2 Site Color Table

| Site Type | strokeColor | fillColor |
|-----------|-------------|-----------|
| HQ / Headquarters | `#1565C0` (blue) | `default` |
| Branch / Remote | `#2E7D32` (green) | `#0D2110` |
| Data Center | `#4527A0` (purple) | `#1a0f40` |
| ISP / Internet | `#546E7A` (gray) | `#1A2226` |
| Campus | `#00838F` (teal) | `#003d45` |

#### 4.11.3 Drawing Order

Place site containers **first in the XML** (before zones, devices, and links):
1. Site containers (deepest background)
2. Protocol zone boxes
3. Cloud / Internet icon
4. Device icons
5. Physical link edges
6. Tunnel overlay edges

#### 4.11.4 Internet Representation

- Use the **Cisco 19 cloud icon** (`shape=mxgraph.cisco19.cloud`) as a standalone node on the WAN path.
- Do NOT use a site container box for Internet.
- Route the WAN link with a waypoint at the cloud's center coordinates.

#### 4.11.5 Reference XML

```xml
<!-- HQ site container (placed first in XML) -->
<mxCell id="site_hq" value="&lt;b&gt;HQ — Headquarters&lt;/b&gt;" style="rounded=1;arcSize=2;whiteSpace=wrap;html=1;strokeColor=#1565C0;strokeWidth=2;fillColor=default;opacity=20;fontSize=13;fontStyle=1;fontColor=#FFFFFF;verticalAlign=top;spacingTop=6;" vertex="1" parent="1">
  <mxGeometry x="30" y="50" width="560" height="870" as="geometry"/>
</mxCell>

<!-- Branch site container -->
<mxCell id="site_branch" value="&lt;b&gt;Branch — Dallas&lt;/b&gt;" style="rounded=1;arcSize=2;whiteSpace=wrap;html=1;strokeColor=#2E7D32;strokeWidth=2;fillColor=#0D2110;opacity=20;fontSize=13;fontStyle=1;fontColor=#FFFFFF;verticalAlign=top;spacingTop=6;" vertex="1" parent="1">
  <mxGeometry x="950" y="50" width="420" height="590" as="geometry"/>
</mxCell>
```

--# 5. Workflow

### Creating a New Diagram

1. Set canvas background to `#1a1a2e` in `mxGraphModel`.
2. Lay out XML in order: site containers → zone boxes → cloud icon → devices → physical links → tunnel overlays → legend.
3. Apply the **Empty Side Rule** (§4.3.1) for every device label.
4. Align PC/endpoint positions so switch→PC links are perfectly vertical (center-X must match).
5. **Validation Checklist**:
    - [ ] Title at top center, bold, 17pt, white.
    - [ ] Background `#1a1a2e`.
    - [ ] Device icons use **Cisco 19** shapes (`mxgraph.cisco19.rect;prIcon=...`).
    - [ ] Cloud/Internet uses `mxgraph.cisco19.cloud` (not a box container, not `rect+prIcon`).
    - [ ] Device labels placed on the empty side (§4.3.1). Default to bottom when all sides used.
    - [ ] All physical links: `endArrow=none`.
    - [ ] Routed/WAN links = white `#FFFFFF` w=2. WAN has NO special color.
    - [ ] Trunk = blue `#006EAF` w=3, drawn as two parallel lines with offset exit/entry.
    - [ ] Access port = white `#FFFFFF` w=1.
    - [ ] EtherChannel = white `#FFFFFF` w=5 + two small rotated ellipses (w=20 h=10) at each port.
    - [ ] Switch→PC links are straight vertical (center-X aligned, `exitX=0.5;entryX=0.5`).
    - [ ] OOB Management = gray `#888888` w=1, `dashPattern=8 4`.
    - [ ] OSPF Virtual Link = lavender `#CE93D8` w=1, `dashPattern=4 4`.
    - [ ] **No link visually crosses through an intermediate device** (see §4.8).
    - [ ] Tunnel overlays: thin (`w=1`) dotted curved arcs; GRE+IPsec = orange `#FF6D00`; bare GRE = white.
    - [ ] Protocol domain zones drawn as dashed semi-transparent rounded rectangles (`rounded=1;arcSize=5`) — placed FIRST in XML (before devices).
    - [ ] Each zone uses the correct color from §4.10.3.
    - [ ] Site containers placed BEFORE zone boxes in XML (deepest layer).
    - [ ] Legend box present (black fill, white text, bottom-right, arcSize=3).

### Updating a Diagram

1. Open the existing `.drawio` file.
2. Make necessary modifications following the style guide.
3. Validate against the checklist above.
4. Save the `.drawio` file.

### Reusing a Diagram From Another Lab

Copying an existing `topology.drawio` is a valid shortcut **only if the source already
follows the current style**. Older labs may pre-date the Cisco 19 migration and use the
deprecated `mxgraph.cisco.*` library.

**Pre-copy check (mandatory):**

1. `grep -c "mxgraph.cisco19" <source>/topology.drawio` — must be > 0.
2. `grep -c "mxgraph.cisco\." <source>/topology.drawio` (note the trailing dot) — must be 0.

If either check fails, **do not copy**. Regenerate the diagram from scratch using the
style strings in §4.2.1 and the validation checklist above. After copying, re-run the
checklist on the destination file — reuse does not exempt you from validation.

-# Common Issues

--# Devices show as blue fallback boxes instead of Cisco icons

- **Cause:** Wrong shape library — using old `mxgraph.cisco.routers.router` paths, or wrong `prIcon` name.
- **Solution:** Use `shape=mxgraph.cisco19.rect;prIcon=<correct_icon>`. Confirmed working icons: `router`, `l3_switch`, `workgroup_switch`, `firewall`. Cloud uses its own dedicated shape: `shape=mxgraph.cisco19.cloud`.

--# Zone boxes cover (obscure) routers and links

- **Cause:** Zone shape cells were placed after router and link cells in the XML.
- **Solution:** Move all zone `mxCell` elements before the first device cell.

--# PC links are slanted/diagonal

- **Cause:** Switch and PC center-X coordinates do not align.
- **Solution:** For a 60px-wide switch at `x=S`, place the 50px-wide PC at `x=S+5` (both centers=`S+30`). Add `exitX=0.5;exitY=1;entryX=0.5;entryY=0` to enforce vertical routing.

--# Connection lines are black instead of white

- **Cause:** Default Draw.io line color was used.
- **Solution:** Apply `strokeColor=#FFFFFF;strokeWidth=2` for routed/WAN links. See §4.4.1 for the full type table.

--# Link visually crosses through an intermediate device

- **Cause:** Three or more devices share the same X coordinate and a bypass link connects non-adjacent ones.
- **Solution:** Offset the intermediate device(s) horizontally by at least 100px. See §4.8.

--# Device label overlaps a connection line

- **Cause:** Label placed on the same side as one or more connected links.
- **Solution:** Apply the Empty Side Rule (§4.3.1) — place the label on the side with no connections.
