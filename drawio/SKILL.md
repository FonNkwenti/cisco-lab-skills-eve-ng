---
name: drawio
description: Visual style guide and workflow for creating Cisco network topology diagrams in Draw.io. Use when generating a topology diagram, creating or updating a topology.drawio file, exporting a PNG, or when any other skill needs to produce or validate a network diagram.
---

# Draw.io Diagram Skill

-# Instructions

--# 1. Locations

Store diagrams in the following directories based on their type:

- **Topology Diagrams**: `labs/[chapter]/[lab-folder]/topology.drawio`
  - Use for network topologies, physical cabling, and logical connectivity.
- **Flow Diagrams**: `labs/[chapter]/[lab-folder]/flow-[description].drawio`
  - Use for packet flows, process charts, and logic flows.

--# 2. File Formats & Deliverables

For every diagram, you must maintain and deliver two files with the **exact same basename**:

1.  **Source File (`.drawio`)**: The editable XML format.
2.  **Exported Image (`.png`)**: A high-resolution visual representation for documentation.
    - **Scale**: 200% (Scale 2.0) for high DPI.
    - **Background**: Transparent.
    - **Quality**: Lossless.
    - **Automation**: Use `drawio-desktop` CLI or automated scripts when possible.

--# 3. Naming Conventions

- Use **kebab-case** for all filenames.
- **Pattern**: `[lab-name]-[diagram-type].extension`
- **Examples**:
  - `eigrp-basic-adjacency-topology.drawio`
  - `eigrp-basic-adjacency-topology.png`
  - `packet-flow-vlan-routing.drawio`

--# 4. Visual Style Guide

This section defines the canonical visual style for all topology diagrams. Every generated `.drawio` file **must** follow these rules.

### 4.1 Canvas & Layout

- **Background**: Default Draw.io canvas (assumed dark-theme friendly).
- **Title**: Positioned at the **top center** of the canvas. Bold, 16pt.
- **Legend Box**: Required in every diagram. Positioned at the **bottom-right** corner. Black fill (`#000000`) with white text (`#FFFFFF`), rounded corners, 10pt font.

### 4.2 Device Icons

- Use official **Cisco Network Topology Icons** from the `mxgraph.cisco` shape library.
- **Style Strings**:
  - **Router**: `shape=mxgraph.cisco.routers.router;fillColor=#036897;strokeColor=#ffffff;strokeWidth=2;verticalLabelPosition=bottom;verticalAlign=top;align=center;outlineConnect=0;`
  - **L3 Switch**: `shape=mxgraph.cisco.switches.layer_3_switch;fillColor=#036897;strokeColor=#ffffff;strokeWidth=2;`
  - **L2 Switch**: `shape=mxgraph.cisco.switches.workgroup_switch;fillColor=#036897;strokeColor=#ffffff;strokeWidth=2;`
  - **Cloud/Internet**: `shape=mxgraph.cisco.misc.cloud;fillColor=#036897;strokeColor=#ffffff;strokeWidth=2;`

### 4.3 Device Labels

- **Content**: Three lines — hostname, role, loopback IP.
- **Style**: `text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=top;whiteSpace=wrap;rounded=0;fontSize=11;fontStyle=1`
- **Example**: `R1\nHub/ABR\n10.1.1.1/32`

#### 4.3.1 Smart Label Placement — Empty Side Rule

Labels **must not overlap any connection lines**. Place the label on the side that has **no connections** exiting the device icon:

| Condition | Placement |
|-----------|-----------|
| All physical neighbors are to the **LEFT** (`nx < device_x`) | Place label **RIGHT**: `label_x = device_x + 83` |
| All physical neighbors are to the **RIGHT** (`nx > device_x`) | Place label **LEFT**: `label_x = device_x - 105` |
| Neighbors on both sides (or same-column only) | Default **LEFT**: `label_x = device_x - 105` |

- Y offset (all cases): `label_y = device_y - 7`
- Label width: `100`, height: `60`

**Examples from EIGRP Lab 08:**
- **R2** is at x=500. All neighbors (R1 at x=400, R3 at x=400) are to the LEFT → label goes **RIGHT** (`label_x = 583`).
- **R6** is at x=200. Its neighbor R1 is at x=400, which is to the RIGHT → label goes **LEFT** (`label_x = 95`).

### 4.4 Connection Lines

- **Color**: **White** (`#FFFFFF`). Never black.
- **Style String**: `endArrow=none;html=1;strokeWidth=2;strokeColor=#FFFFFF;fillColor=#f5f5f5;`
- **Dashed Links** (tunnels): `endArrow=none;html=1;strokeWidth=2;strokeColor=#FFFFFF;fillColor=#f5f5f5;dashed=1;`
- **Edge Labels** (interface names + subnet): Centered on the link. 10pt. Include interface pair and subnet on separate lines.
  - Example value: `Fa1/0 - Fa0/0\n10.12.0.0/30`

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
- **Content**: Key information for reading the diagram:
  - OSPF Area designations (if applicable)
  - Link type indicators (solid = physical, dashed = tunnel)
  - Any cost or metric annotations
  - Protocol identifiers (OSPF Process ID, EIGRP AS, etc.)

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

#### 4.9.2 Color Coding by Tunnel Type

| Tunnel Type | Color | Hex |
|-------------|-------|-----|
| GRE | White | `#FFFFFF` |
| MPLS | Orange | `#FF6600` |
| IPsec VPN | Red | `#FF0000` |
| VXLAN | Cyan | `#00AAFF` |
| L2TP | Purple | `#AA00FF` |
| Other/Unknown | Yellow | `#FFFF00` |

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

### 4.7 Reference XML Snippets

**Title Cell:**
```xml
<mxCell id="title" value="Lab N: Title Here" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=16;fontStyle=1" vertex="1" parent="1">
  <mxGeometry x="200" y="40" width="400" height="40" as="geometry" />
</mxCell>
```

**Device Icon:**
```xml
<mxCell id="R1" value="" style="shape=mxgraph.cisco.routers.router;fillColor=#036897;strokeColor=#ffffff;strokeWidth=2;verticalLabelPosition=bottom;verticalAlign=top;align=center;outlineConnect=0;" vertex="1" parent="1">
  <mxGeometry x="400" y="200" width="78" height="53" as="geometry" />
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

--# 5. Workflow

### Creating a New Diagram
1.  Open Draw.io (Desktop or Web).
2.  Create the diagram following the Visual Style Guide (Section 4).
3.  **Validation Checklist**:
    - [ ] Title is at the top center, bold, 16pt.
    - [ ] All connection lines are **white** (`#FFFFFF`), strokeWidth=2.
    - [ ] Device labels are positioned on the **empty side** of the icon (no connection lines on that side). See Section 4.3.1.
    - [ ] Every device has a hostname, role, and Loopback IP.
    - [ ] Every link has interface names on BOTH ends.
    - [ ] Every interface has a **last octet** label (`.1`, `.2`) near the router.
    - [ ] Subnet ID is visible on every link (centered edge label).
    - [ ] **No link visually crosses through an intermediate device** (see Section 4.8).
    - [ ] **Tunnel overlays** use thin colored dotted lines and arc above physical devices (see Section 4.9).
    - [ ] **Tunnel endpoint octets** (`.1` / `.2`) are placed near the top of source/target devices (see Section 4.9.4).
    - [ ] Protocol boundaries (Areas, AS) are clearly marked.
    - [ ] **Legend box** is present (black fill, white text, bottom-right) and lists tunnel colors if tunnels are present.
4.  Save the editable file as `.drawio` in the appropriate subdirectory.
5.  Export the diagram as a `.png` (Transparent Background, 200% Zoom/Scale 2.0 for high DPI) to the same directory.
6.  Link the PNG in your README.md files.

### Updating a Diagram
1.  Open the existing `.drawio` file.
2.  Make necessary modifications.
3.  Validate against the checklist above.
4.  Save the `.drawio` file.
5.  Re-export to `.png`, overwriting the existing image.

-# Common Issues

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
