---
name: explainer
description: Generates a self-contained HTML explainer for a networking topic or lab. Produces an interactive single-page document with animated packet flows, topology diagrams (ASCII/SVG), comparison tables, route-type references, CLI command examples, analogies, and a "labs roadmap" mapping theory to practical exercises. Output is a standalone `.html` file with no external dependencies.
---

# Explainer Skill

Generates an interactive HTML explainer for a Cisco networking topic or lab. The output
is a single self-contained `.html` file viewable in any browser (no CDN, no images).

Two modes:

- **Topic mode** (`topic: <topic-slug>`): Broad theoretical explainer covering the
  technology. Pulls from `labs/<topic>/spec.md` (objectives, blueprint coverage) and
  `labs/<topic>/baseline.yaml` (topology). Good as a warm-up before labs.

- **Lab mode** (`lab: <topic>/<lab-slug>`): Specific explainer for a single lab.
  Pulls from the same files PLUS `workbook.md`, `solutions/`, `initial-configs/`, and
  `topology/topology.drawio` for exact topology + config + fault scenarios.

This skill is invoked by the `/explain` command (`.claude/commands/explain.md`).

-# Instructions

--# Step 1: Read Inputs

Read all available inputs based on mode. Fail silently on missing optional files
(e.g., no workbook yet in topic mode).

### Topic mode inputs

Read these in parallel:

1. `labs/<topic>/spec.md` — lab objectives, exam bullet coverage, lab progression.
   This is the **primary source** for explaining "what does this technology cover?"
2. `labs/<topic>/baseline.yaml` — core topology, device roles, IP scheme, active labs list.
   If absent, use generic Cisco reference topology.
3. `specs/topic-plan.yaml` — exam context, domain mapping, weight distribution.
   Extract: exam code, exam name, blueprint version.
4. `labs/<topic>/lab-*` directories — list them to enumerate what labs exist.
   Read each `workbook.md` (if exists) for the learning objectives per lab.
5. `.agent/skills/reference-data/` — scan for any platform references that are relevant
   (e.g., `ios-compatibility.yaml` for platform quirks).

### Lab mode inputs

Read all topic-mode inputs PLUS:

6. `labs/<topic>/<lab-slug>/workbook.md` — full lab workbook (learners' tasks).
7. `labs/<topic>/<lab-slug>/solutions/` — solution configs per device (read all `.cfg`).
8. `labs/<topic>/<lab-slug>/initial-configs/` — starting configs per device (if exists).
9. `labs/<topic>/<lab-slug>/topology/topology.drawio` — extract device names and links
   (process via drawio XML parsing if available, otherwise fall back to baseline).
10. `labs/<topic>/<lab-slug>/fault-injection/` — read fault scenario scripts/tickets.

--# Step 2: Build Content Model

Build an in-memory content structure. This is what gets rendered into HTML sections.

### For Both Modes

```
explainer_content = {
  title: str,                  # e.g., "EVPN — Ethernet VPN"
  subtitle: str,               # e.g., "RFC 7432 · MP-BGP control plane for L2/L3 VPN services"
  exam_context: {               # from topic-plan.yaml
    exam_code: str,
    exam_name: str,
    blueprint_version: str,
    topic_weight: str
  },
  tabs: [                      # each tab becomes a panel in the HTML
    {
      id: str,                 # "overview", "sp", "dc", etc.
      label: str,              # "Overview", "SP / MPLS Core", "Data Center"
      sections: [
        {
          type: "prose",       # paragraph text, optionally with infoboxes
          heading: str,
          body: str,
          style: "normal"|"info"|"warning"|"tip"
        },
        {
          type: "ascii_topology",  # ASCII art diagram
          heading: str,
          art: str,             # multi-line ASCII string
          legend: str           # optional legend
        },
        {
          type: "table",
          heading: str,
          columns: [str],
          rows: [[str]],       # each row is a list of cell values
          highlight_col: int,  # optional column index for numeric tint
        },
        {
          type: "packet_diagram",
          heading: str,
          fields: [            # e.g., [ {label, value, color}, ... ]
            {label: str, value: str, color: str}
          ]
        },
        {
          type: "cli_example",
          heading: str,
          command: str,        # "show bgp l2vpn evpn route-type 2"
          output: str,         # truncated CLI output
          annotation: str      # explanation of what to look for
        },
        {
          type: "animated_flow",
          heading: str,
          id: str,             # unique flow ID for JS
          steps: [
            {
              desc: str,       # step description
              art: str         # ASCII art for this step
            }
          ]
        },
        {
          type: "analogy",
          tag: str,            # e.g., "EVPN vs traditional VPLS"
          body: str            # analogy paragraph
        },
        {
          type: "mnemonic",    # memory aid — emoji-paired, see Mnemonic Guidance below
          tag: str,            # e.g., "the 5 route types are EVPN's life story, in order"
          phrase: str,         # the headline mnemonic line, bold first letters + one emoji per item
          items: [             # one row per memorised item
            {emoji: str, keyword: str, body: str}
          ],
          foot: str            # optional: the unifying insight / which-applies-when line
        },
        {
          type: "grid_cards",
          heading: str,
          cards: [
            {title: str, items: [str], color: "teal"|"purple"|"green"|"amber"}
          ]
        },
        {
          type: "labs_roadmap",  # maps theory to labs
          heading: str,
          labs: [
            # Describe what each lab TEACHES (title, objectives, blueprint refs).
            # NEVER emit a build-status field (built/planned/speced) — see Roadmap Rule below.
            {slug: str, title: str, objectives: [str], blueprint_refs: [str]}
          ]
        },
        {
          type: "comparison_table",
          heading: str,
          columns: ["Dimension", "Column A", "Column B"],
          groups: [
            {label: str, rows: [[str, str, str]]}
          ]
        }
      ]
    }
  ]
}
```

### Topic Mode — Heuristics

When generating content in topic mode:

1. **Identify the core technology** from `<topic-slug>` (e.g., `evpn`, `mpls-lsr`, `bgp`,
   `ospf`, `eigrp`, `mpls-l3vpn`, `multicast`, `segment-routing`).
2. **Map RFCs and standards** associated with the technology. Include standard numbers
   (RFC 4271, RFC 7432, etc.) in prose sections.
3. **Create 4-6 tabs** that cover:
   - **Overview**: What it is, what problem it solves, key concepts, RFC references.
   - **Core Concepts** (or architecture): Deep dive into the technology's operation.
   - **Configuration** (or practical): CLI commands, verification, common gotchas.
   - **Troubleshooting**: Common faults, diagnostic commands, debugs.
   - **Labs Roadmap** (if labs exist): Map theory bullets to actual lab exercises.
   - **Reference** (or comparisons): Tables of route types, message types, etc.
4. **Include at least one animated_flow** showing a packet flow or protocol exchange
   across the topology.
5. **Include at least one analogy** per major concept.
6. **Include CLI examples** with realistic (but simplified) output.
7. **If baseline.yaml exists with a topology**, generate an ascii_topology section
   showing the lab topology.
8. **Add `mnemonic` sections wherever a list of facts must be memorised** (route types,
   message types, state machines, acronyms, ordered procedures). See Mnemonic Guidance.

### Mnemonic Guidance (both modes)

Mnemonics are memory aids for list-shaped facts. Pair each with an emoji to add a visual
anchor — this is the **only** place emojis are allowed in the output (keep all other prose
emoji-free).

- **Prefer a narrative mnemonic when the items have a natural order** (e.g. the EVPN route
  types fire in roughly operational order: discover → learn MAC → flood BUM → elect DF →
  route L3). Encode that order into the phrase so the memory aid and the conceptual model
  reinforce each other. Fall back to a first-letter acrostic only when there is no order.
- **One emoji per item, chosen to evoke the item's job** (🧭 discover, 📇 catalog/address-book,
  📢 shout/flood, 🗳️ vote/elect, 🗺️ map/route). The same emoji appears in the headline
  `phrase` and on that item's row, so the row links back to the phrase.
- **Exploit acronyms that already exist** (e.g. BUM = Broadcast / Unknown-unicast / Multicast)
  — bold the letters in the phrase and give each its own row.
- **End with a `foot`** stating the unifying insight or which-service-uses-which mapping.
- Good candidates: route/message-type lists, the BUM acronym, state machines, ordered
  bring-up procedures. Skip mnemonics for single concepts an analogy already covers.

### Roadmap Rule

The `labs_roadmap` section describes what each lab **teaches** — title, objectives, blueprint
refs. It MUST NOT show build status (built / planned / speced) or any other state that goes
stale as labs are built. The explainer is a static file; encoding mutable state it cannot keep
in sync would make it lie the moment a lab is built. State only durable facts.

### Lab Mode — Heuristics

1. **Topology comes first**: Show the lab's exact topology (from baseline or drawio).
2. **Lab objectives** from workbook.md map to sections.
3. **Config walkthrough**: For each device, show key config blocks with annotations.
4. **Packet flows**: Animate the exact flows the lab exercises (e.g., "PE-1 sends BGP
   update → RR → PE-3").
5. **Verification**: Show the `show` commands from the workbook with expected output.
6. **Fault scenarios**: For each Section 9 ticket, embed an interactive "fault mode"
   where the explainer shows broken output and asks the learner to diagnose.

--# Step 3: Generate HTML

Generate a single self-contained HTML file. Use the Claude `evpn_explainer.html` as the
reference style (dark theme, GitHub-dark-inspired). The HTML must have:

### Required Features

1. **Tab navigation** — CSS/JS tabs that switch panels. Active tab state persists.
2. **Per-panel prev/next nav** — every panel ends with a Back/Next bar so the reader can
   advance to the adjacent tab without scrolling back up. Labels show the adjacent tab
   **names** (Back ◀ <prev name> | Next ▶ <next name>). Generate the bars in JS from the
   tab list (single source of truth — do NOT hardcode per panel). First panel has no Back,
   last has no Next (render a hidden ghost button to keep alignment). Clicking activates the
   tab AND smooth-scrolls to the top of the page.
3. **Animated flows** — Step-through with Prev/Next/Play (auto-advance every 2.8s).
   Pure JS, no external libraries.
3. **Color-coded ASCII art** — Span classes for green, teal, purple, amber, blue, red,
   grey. Applied inline in the ASCII content.
4. **Tables** — Route type tables (colored badges), comparison tables (grouped rows),
   grid cards (2-column responsive grid).
5. **Packet diagrams** — Horizontal field-by-field breakdown with colored backgrounds.
6. **Infoboxes** — Left-border accent boxes (teal, amber, purple, green).
7. **Analogy blocks** — Tagged with pink accent label.
8. **Mnemonic blocks** — Pink-bordered box with an uppercase tag, a centered headline
   `phrase` (bold first-letters + emoji), a numbered emoji list (concept emoji + pink
   keyword + plain-language meaning), and an optional footer. Emojis appear ONLY here.
9. **Dark theme** — CSS variables for bg, bg2, bg3, border, text, text2, accent colors.
10. **Responsive** — Grid collapses to single column below 600px.
11. **No external dependencies** — Everything inline. No CDN fonts, no external images,
    no external JS.
12. **No emojis outside mnemonic blocks** — the rest of the document stays emoji-free.

### HTML Structure

```
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} — Cisco Lab Explainer</title>
  <style>
    /* All CSS inline - dark theme, responsive, animations */
  </style>
</head>
<body>
  <div class="page">
    <h1>{title}</h1>
    <p class="subtitle">{subtitle}</p>
    {exam_context_bar}

    <div class="tabs">
      {tab_buttons}
    </div>

    {tab_panels}

  </div>
  <script>
    // Tab switching
    // Flow animation (step, play, pause)
    // renderStep() for each animated_flow
  </script>
</body>
</html>
```

### CSS Template (use as the base, extend per content)

Include these CSS variables and classes. They match the `evpn_explainer.html` reference
style and should be used as-is for consistency:

```css
:root {
  --bg: #0d1117;
  --bg2: #161b22;
  --bg3: #21262d;
  --border: #30363d;
  --text: #e6edf3;
  --text2: #8b949e;
  --green: #3fb950;
  --green2: #238636;
  --teal: #39d0d8;
  --purple: #a371f7;
  --amber: #e3b341;
  --blue: #58a6ff;
  --red: #f85149;
  --pink: #f778ba;
  --mono: 'Courier New', monospace;
  --sans: 'Segoe UI', system-ui, sans-serif;
}
```

Include all CSS classes from the reference for `.ascii`, `.rt-table`, `.cmp`, `.flow-container`,
`.pkt`, `.infobox`, `.analogy`, `.grid2`, `.card`, `.tabs`, `.tab`, `.panel`, `.btn`,
plus `.mnemonic` / `.mphrase` / `.mlist` / `.mfoot` (pink mnemonic block) and
`.panelnav` / `.pnav` (per-panel prev/next bar; `.pnav.ghost{visibility:hidden}` for the
missing-edge case on the first/last panel).

### ASCII Color Classes

Apply these inline classes in your ASCII art via `<span>` wrappers:

- `.g` (green) — correct configs, successful outputs, data plane
- `.t` (teal) — technology names, control plane, EVPN
- `.a` (amber) — route reflectors, intermediate systems
- `.p` (purple) — VXLAN, overlay concepts
- `.b` (blue) — CE, endpoints, hosts
- `.r` (red) — faults, errors, misconfigurations
- `.d` (text2/grey) — decorative borders, labels, framing

### Animated Flow Script

Each animated_flow section gets its own button group + ASCII pre + controls. The
JavaScript for all flows lives in the single `<script>` block:

```javascript
const flows = {
  "{flow_id}": {
    title: "{flow_title}",
    steps: [
      { desc: "...", ascii: "..." },
      ...
    ]
  }
};
// Plus tab switching, play/pause, step forward/backward
```

Also build a single `activate(id, scroll)` helper that toggles the active tab + panel and,
when `scroll` is true, `window.scrollTo({top:0, behavior:'smooth'})`. Derive an `order`
array from the `.tab` elements (id + text), wire it to both the top tabs and the
auto-generated `.panelnav` bars (Required Feature 2), so tab order has one source of truth.

--# Step 4: Write Output File

### Topic mode

Write to `labs/<topic>/explainer.html`.

### Lab mode

Write to `labs/<topic>/<lab-slug>/explainer.html`.

### File metadata

Write a comment block at the top of the HTML (inside an HTML comment) with:

```html
<!--
  Generated by: explainer skill
  Date: {ISO date}
  Mode: topic|lab
  Exam: {exam-code}
  Topic: {topic-slug}
  Lab: {lab-slug} (if lab mode)
  Sources: spec.md, baseline.yaml, [workbook.md, ...]
-->
```

--# Step 5: Report

Print the output path, file size (KB), and a summary of what was generated:

> **Explainer generated: `labs/evpn/explainer.html` (48 KB)**
>
> Tabs: Overview · Core Concepts · Configuration · Troubleshooting · Labs Roadmap
> Animated flows: 2 (EVPN RT-2 Advertisement, BUM Flooding)
> Tables: 4 (Route Types, Encapsulation Comparison, SP vs DC)
> CLI examples: 3
> Analogies: 2

Also suggest the user can share the file directly — it's completely self-contained with
no external dependencies.
