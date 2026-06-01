---
name: explainer
description: Generates a self-contained HTML explainer for a networking topic or lab. Produces an interactive single-page document with animated SVG packet-flow diagrams (a label-stack packet that moves node-to-node across the topology, showing how the frame is switched/routed and re-encapsulated at each hop), comparison tables, route-type references, CLI command examples, analogies, and a "labs roadmap" mapping theory to practical exercises. Output is a standalone `.html` file with no external dependencies.
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
          type: "animated_flow",   # SVG label-stack packet animated node-to-node
          heading: str,
          id: str,                 # unique flow id; host div is <div class="flow" id="flow-{id}">
          # Topology the packet travels over. Coordinates are hand-laid within the
          # SVG viewBox (see Authoring the Flow Data in the Animated Flow Script section).
          # Usually ONE shared nodes/links pair is reused by every flow in the explainer.
          nodes: {                 # keyed by node id
            "{node_id}": {
              x: int, y: int, w: int, h: int,   # box geometry inside the viewBox
              color: str,          # var(--teal|amber|purple|blue|green|coral)
              label: str,          # e.g. "PE1"
              sub: str,            # e.g. "1.1.1.1 (XE)"
              dash: bool           # optional: dashed border (non-member / control-only node)
            }
          },
          links: [                 # straight lines drawn between node centres
            { a: "{node_id}", b: "{node_id}", ctl: bool }   # ctl=true → dashed control link
          ],
          steps: [
            {
              desc: str,           # step narration (may contain <b>, <i>, <code>)
              path: [str],         # ordered node ids the packet traverses this step;
                                   # [] (empty) = static step: no movement, annotations only.
                                   # A return trip is just the reversed node sequence.
              stack: [             # the label/encapsulation stack drawn ON the packet,
                                   # top row = outermost. Re-author per step to show push/pop.
                { text: str, kind: "transport"|"evpn"|"frame"|"ctrl" }
              ],
              annotes: [           # callout boxes shown at the END of the step's movement
                { at: "{node_id}", dx: int, dy: int, text: str, color: str }  # \n splits lines
              ]
            }
          ]
          # NOTE: the legacy ASCII `art` per-step field is retired. Packet flows MUST use
          # the SVG engine below. Static diagrams (topology, decision trees) still use
          # ascii_topology.
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

- **Always build a sentence mnemonic — a phrase that reads as English and whose words'
  first letters map 1:1 to the items being memorised.** The sentence itself doesn't need
  to be technically accurate; it only needs to be easy to recall under exam pressure.
  Example: BGP path attributes = "**W**ill **L**ocal **L**eaders **A**ccept **O**verpriced
  **M**achinery **E**very **I**nstant? **R**eally" (Weight → Local Pref → Locally Originated
  → AS-Path → Origin → MED → EBGP→IGP metric → Router-ID). A bare first-letter acrostic
  like "SCSVM" fails because it is not language the brain can rehearse.
- **Derive the first letters from the item's key word** — the word that already anchors
  the concept for the learner (e.g. Auto-Discovery → A, MAC → M, IMET → I, Ethernet Segment
  → E, IP Prefix → P → "**A**ll **M**ACs **I**nvite **E**very **P**ath"). Don't force
  every word to exactly describe its item; the sentence just needs to be memorable.
- **One emoji per item, chosen to evoke the item's job.** The emoji connects the mnemonic
  word back to the real technology so the learner bridges both. For EVPN route types:
  🔍 All (Auto-Discovery = discovering all segments), 📇 MACs (address book), 📩 Invite
  (IMET invites PEs to the flood list), 🗳️ Every (DF election = every PE votes), 🗺️ Path
  (IP Prefix = route paths). The same emoji appears in the headline `phrase` and on that
  item's row, so the row links back to the phrase.
- **A real emoji per item is mandatory — emojis are core to the mnemonic.** Put the emoji
  in the `phrase` AND in each item's `.gly` sticker box. **Never substitute geometric
  glyphs (⬡ ⬢ ▲ ◆) for emojis** — a previous build regressed to glyphs because a cloned
  template encoded them; render and confirm real emojis appear. The `.gly` box shows the
  emoji in its own colour (do not set `color` on it).
- **Exploit acronyms that already exist** (e.g. BUM = Broadcast / Unknown-unicast /
  Multicast) — bold the letters in the phrase and give each its own row.
- **End with a `foot`** stating the first-letter string (e.g. "AMIEP"), the sentence
  decoded, and the unifying insight or which-service-uses-which mapping.
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

Generate a single self-contained HTML file. The reference style is **Neo-Brutalism 2.0
"STOCK"** (design skill: `~/.claude/skills/neo-brutalism`, `directions/carbon.css`): a
dual-ground component kit — **Carbon** (dark) and **Chalk** (light) — with hard
near-black borders, offset matte shadows, mono-display headings, paper grain, and one
variabilised electric accent (default **lime `#c6f24a`**, the "neo green"). **Chalk (light)
is the default** for explainers: set `data-theme="light"` on `<html>` AND default the
switcher to light (no dark flash). Do NOT default to amber — amber is not a STOCK accent.

**Coherent theme rule (apply everywhere):** *editorial* surfaces flip with the theme
(prose, cards, table bodies, mnemonic boxes, analogies, page ground); *technical* surfaces
stay dark in BOTH themes (the SVG flow canvas, CLI `.out`/`.cmd`, `.ascii-block`) so the
fixed diagram role-palette is always legible. The HTML must have:

### Required Features

1. **Tab navigation** — CSS/JS tabs that switch panels. Active tab state persists.
2. **Per-panel prev/next nav** — every panel ends with a Back/Next bar so the reader can
   advance to the adjacent tab without scrolling back up. Labels show the adjacent tab
   **names** (Back ◀ <prev name> | Next ▶ <next name>). Generate the bars in JS from the
   tab list (single source of truth — do NOT hardcode per panel). First panel has no Back,
   last has no Next (render a hidden ghost button to keep alignment). Clicking activates the
   tab AND smooth-scrolls to the top of the page.
3. **Animated SVG packet flows** — Every packet flow is an inline SVG where a
   **label-stack packet box travels node-to-node** along the topology (CE → PE → P →
   PE → CE and back), the traversed devices/links highlight, the on-packet stack shows
   push/pop re-encapsulation at each PE, and callout annotations pop at the destination.
   Step-through with Prev/Next/Play (auto-advance every 3.6s). Pure JS + SVG, no external
   libraries. Use the engine in **Animated Flow Script** verbatim — do NOT hand-roll a
   per-explainer animation, and do NOT fall back to stepped ASCII art for packet flows.
3. **Color-coded ASCII art** — Span classes for green, teal, purple, amber, blue, red,
   grey. Applied inline in the ASCII content.
4. **Tables** — Route type tables (colored badges), comparison tables (grouped rows),
   grid cards (2-column responsive grid).
5. **Packet diagrams** — Horizontal field-by-field breakdown with colored backgrounds.
6. **Infoboxes** — Left-border accent boxes (teal, amber, purple, green).
7. **Analogy blocks** — Tagged with pink accent label.
8. **Mnemonic blocks** — Accent-bordered box with an uppercase tag, a centered headline
   `phrase` (bold first-letters), a numbered list, and an optional footer. **A real emoji
   per item is REQUIRED — it is core to the mnemonic, not decoration.** The same emoji
   appears in the headline `phrase` AND in that item's `.gly` box (a bordered sticker that
   shows the emoji in its own colour — do NOT force `color` on it). **Never substitute
   geometric glyphs (⬡ ⬢ ▲) for emojis** — that is a regression; use 🔍 📇 📩 🗳️ 🗺️ etc.
   Emojis appear ONLY in mnemonic blocks; the rest of the document stays emoji-free.
9. **Dual theme + switcher** — Carbon (dark) + Chalk (light) via `data-theme` on `<html>`,
   **Chalk default**. Include the topbar Carbon/Chalk toggle + accent dots (lime/cyan/coral/
   blue) from **Theme & Accent Switcher** verbatim. Editorial surfaces flip; technical
   surfaces (SVG/CLI/ASCII) stay dark in both themes.
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

Use this token system verbatim. The `:root` block is **Carbon (dark)**; the
`[data-theme="light"]` block is **Chalk** and flips only the editorial tokens. The
diagram constants (`--dia-…`, `--dev-…`, `--lbl-…`) live ONLY in `:root` and are
deliberately NOT overridden in Chalk — the diagram canvas stays dark in both themes, and
the SVG engine references these (never the editorial `--bg`/`--card`/`--text`, which flip).
Fonts are the system mono fallback (no CDN). Note: do not write the glob notation
`--dia-*` inside a `/* … */` comment — the `*/` ends the comment early and silently drops
the whole rule; spell prefixes out in words.

```css
:root{
  --mono-display:'Space Mono', ui-monospace, 'Cascadia Code', 'Consolas', monospace;
  --mono-ui:'JetBrains Mono', ui-monospace, 'Cascadia Code', 'Consolas', monospace;
  /* CARBON (dark) editorial defaults */
  --bg:#14161a; --surface:#1c1f25; --card:#21252c; --card-2:#262b33;
  --line:#3a414c; --line-2:#525a67;
  --text:#ece6d6; --text-60:#9aa0ab; --text-40:#6b7280;
  /* ACCENT (switchable; default lime "neo green") */
  --accent:#c6f24a; --accent-rgb:198,242,74; --accent-ink:#11140a;
  --accent-text:var(--accent); --warn:#ffd27a; --err:#ff7a5c;
  --glow-a:0.4;
  --shadow:6px 6px 0 #000; --shadow-sm:3px 3px 0 #000; --shadow-lg:11px 11px 0 #000;
  --glow:0 0 24px rgba(var(--accent-rgb),var(--glow-a));
  --shadow-accent:4px 4px 0 rgba(var(--accent-rgb),0.3);
  --shadow-accent-hover:7px 7px 0 rgba(var(--accent-rgb),0.4), var(--glow);
  --chrome:#0e0f12; --grid-line:rgba(255,255,255,0.018);
  /* DIAGRAM CONSTANTS — theme-independent (always dark canvas). Prefixes: dia / dev / lbl */
  --dia-bg:#0e0f12; --dia-surface:#1c1f25; --dia-pkt-bg:#14161a; --dia-edge:#ece6d6;
  --dia-line:#525a67; --dia-sub:#9aa0ab; --dia-hl:#c6f24a; --dia-ok:#4ae04a; --dia-bad:#ff7a5c;
  --dev-ce:#5a8bff; --dev-pe:#5fe0d8; --dev-xr:#b388ff; --dev-core:#ffd27a;
  --lbl-transport:#ffd27a; --lbl-evpn:#b388ff; --lbl-frame:#5a8bff; --lbl-ctrl:#5fe0d8;
}
/* CHALK (light) — editorial inverse; hard black edges + offset shadows hold; glow dies.
   No diagram constants here: the diagram stays on its dark canvas in both themes. */
[data-theme="light"]{
  --bg:#e9e6dd; --surface:#f3f0e8; --card:#fbf9f2; --card-2:#efece2;
  --line:#16130d; --line-2:#4a463e;
  --text:#16161a; --text-60:#56524a; --text-40:#87837a;
  --glow-a:0; --grid-line:rgba(0,0,0,0.05);
  --accent-text:color-mix(in oklab, var(--accent) 70%, #0c0e06);
  --warn:color-mix(in oklab, #ffd27a 52%, #000);
  --err:color-mix(in oklab, #ff7a5c 72%, #000);
  --shadow-accent:4px 4px 0 #000; --shadow-accent-hover:7px 7px 0 #000;
}
```

Reskin the explainer's component classes (`.brutal-head`/`.sec-head`/`.sec-num`/`.tabs`/
`.tab-btn`/`.panel`/`.btn`/`.alert`/`.analogy`/`.mnem`/`.lcard`/`.panelnav`, tables) with
these tokens: `var(--line)` borders, `var(--shadow)` offset shadows, `var(--accent)` fills
with `var(--accent-ink)` text, `var(--mono-display)` headings. Keep the class NAMES and the
component set (reskin, do not rename). The grain overlay is a self-contained data-URI noise
(no external asset).

Include all CSS classes from the reference for `.ascii`, `.rt-table`, `.cmp`, `.flow-container`,
`.pkt`, `.infobox`, `.analogy`, `.grid2`, `.card`, `.tabs`, `.tab`, `.panel`, `.btn`,
plus `.mnem` / `.mtag` / `.mphrase` / `.mlist` / `.mitem` / `.gly` / `.mfoot` (accent
mnemonic block — `.gly` is the emoji sticker), the topbar/switcher classes `.topbar` /
`.topbar-in` / `.brand` / `.switches` / `.seg` / `.seg-btn` / `.acc-dot` and the masthead
`.brutal-head` / `.stamp` / `.eyebrow`, and
`.panelnav` / `.pnav` (per-panel prev/next bar; `.pnav.ghost{visibility:hidden}` for the
missing-edge case on the first/last panel), and the SVG-flow classes `.flow` / `.fhead` /
`.fdesc` / `.fbody` / `.fctl` / `.dots`, `.svg-wrap`, `.dev-rect` (+ `.dev-rect.hl`),
`.dev-label`, `.dev-sub`, `.link-line` (+ `.link-line.ctl` / `.link-line.hl`) — all
provided verbatim in the **Animated Flow Script** section.

### ASCII Color Classes

Apply these inline classes in your ASCII art via `<span>` wrappers:

- `.g` (green) — correct configs, successful outputs, data plane
- `.t` (teal) — technology names, control plane, EVPN
- `.a` (amber) — route reflectors, intermediate systems
- `.p` (purple) — VXLAN, overlay concepts
- `.b` (blue) — CE, endpoints, hosts
- `.r` (red) — faults, errors, misconfigurations
- `.d` (text2/grey) — decorative borders, labels, framing

### Theme & Accent Switcher (verbatim)

A sticky dark topbar carries the Carbon/Chalk toggle and the accent dots. Markup:

```html
<nav class="topbar"><div class="topbar-in">
  <div class="brand"><span class="mk"></span> {TOPIC} · {EXAM}</div>
  <div class="switches">
    <div class="theme-switch"><span class="lbl">Theme</span><div class="seg">
      <button class="seg-btn" data-theme-btn="light" aria-pressed="true">Chalk</button>
      <button class="seg-btn" data-theme-btn="dark"  aria-pressed="false">Carbon</button>
    </div></div>
    <div class="accent-switch"><span class="lbl">Accent</span>
      <button class="acc-dot" data-acc="lime"  style="background:#c6f24a" aria-pressed="true"  title="Lime"></button>
      <button class="acc-dot" data-acc="cyan"  style="background:#5fe0d8" aria-pressed="false" title="Cyan"></button>
      <button class="acc-dot" data-acc="coral" style="background:#ff7a5c" aria-pressed="false" title="Coral"></button>
      <button class="acc-dot" data-acc="blue"  style="background:#5a8bff" aria-pressed="false" title="Electric blue"></button>
    </div>
  </div>
</div></nav>
```

JS (also set `data-theme="light"` on `<html>` in the markup so there is no dark flash):

```javascript
var root = document.documentElement;
var ACCENTS = {
  lime:{c:'#c6f24a',rgb:'198,242,74',ink:'#11140a'}, cyan:{c:'#5fe0d8',rgb:'95,224,216',ink:'#06201e'},
  coral:{c:'#ff7a5c',rgb:'255,122,92',ink:'#1a0d08'}, blue:{c:'#5a8bff',rgb:'90,139,255',ink:'#ffffff'}
};
function applyAccent(n){ var a=ACCENTS[n]; if(!a) return;
  root.style.setProperty('--accent',a.c); root.style.setProperty('--accent-rgb',a.rgb); root.style.setProperty('--accent-ink',a.ink);
  document.querySelectorAll('.acc-dot').forEach(function(d){ d.setAttribute('aria-pressed', String(d.dataset.acc===n)); });
  try{ localStorage.setItem('expl-accent',n); }catch(e){} }
function applyTheme(n){ if(n!=='dark') n='light'; root.setAttribute('data-theme',n);
  document.querySelectorAll('[data-theme-btn]').forEach(function(b){ b.setAttribute('aria-pressed', String(b.dataset.themeBtn===n)); });
  try{ localStorage.setItem('expl-theme',n); }catch(e){} }
document.querySelectorAll('.acc-dot').forEach(function(d){ d.addEventListener('click', function(){ applyAccent(d.dataset.acc); }); });
document.querySelectorAll('[data-theme-btn]').forEach(function(b){ b.addEventListener('click', function(){ applyTheme(b.dataset.themeBtn); }); });
var sA,sT; try{ sA=localStorage.getItem('expl-accent'); sT=localStorage.getItem('expl-theme'); }catch(e){}
applyAccent(sA && ACCENTS[sA] ? sA : 'lime');
applyTheme(sT || 'light');   // Chalk is the default
```

Required topbar/switcher CSS (dark chrome in both themes): `.topbar`/`.topbar-in`/`.brand`,
`.switches`/`.lbl`, `.seg`/`.seg-btn` (`[aria-pressed=true]` = accent fill), `.acc-dot`
(`[aria-pressed=true]` = ring). Pin their ink to the dark palette (`#ece6d6`/`#9aa0ab`) so
they stay legible when the page flips to Chalk — see `directions/carbon.css` `.topbar`.

### Animated Flow Script (SVG packet-flow engine — use verbatim)

Packet flows are inline SVG. A **label-stack packet box** is translated along a path of
node centres (`requestAnimationFrame`, ease-in-out), the devices/links it crosses
highlight, the on-packet stack is re-authored each step to show push/pop encapsulation,
and callout boxes appear at the destination when the move finishes. This is the canonical
look the project standardised on — **every packet flow must use this engine.** Copy the
engine functions exactly; author only the per-topic data (`nodes`, `links`, `flows`).

**Self-containment:** the engine uses ONLY the theme-independent diagram constants from
the CSS Template `:root` (`--dia-…`, `--dev-…`, `--lbl-…`, `--mono-ui`) — never the
editorial tokens (`--bg`/`--card`/`--text`/`--line`), which flip with the theme and would
render the SVG light-on-light in Chalk. Every diagram colour must resolve to a constant.
**Verify by grep:** after generating, no `var(--bg|surface|card|card-2|line|line-2|text|
text-60|text-40|accent)` may appear inside `buildTopo`/`buildPacket`/`showAnn` or the
`.svg-wrap` CSS — only `--dia-…`/`--dev-…`/`--lbl-…`. Reminder: an unresolved `var()` in an
SVG `fill`/`stroke` attribute does NOT fall back — it computes to **black**, turning every
node into an invisible box. The only proof it works is rendering both themes (Step 4).

**Required CSS (the flow shell + the SVG layer; the canvas is dark in BOTH themes):**

```css
.flow { border:3px solid var(--line); background:var(--surface); box-shadow:var(--shadow-lg); margin:18px 0; overflow:hidden; }
.flow .fhead { display:flex; align-items:center; justify-content:space-between; gap:12px; padding:14px 20px; border-bottom:3px solid var(--line); background:var(--chrome); flex-wrap:wrap; }
.flow .fhead .ft { font-family:var(--mono-display); font-weight:700; font-size:14px; color:#ece6d6; }
.flow .fhead .fc { font-size:10px; letter-spacing:0.12em; text-transform:uppercase; color:var(--accent); }
.flow .fdesc { padding:16px 20px 8px; font-size:13.5px; line-height:1.6; color:var(--text); min-height:58px; }
.flow .fdesc b { color:var(--accent-text); }
.flow .fdesc code { font-family:var(--mono-ui); font-size:12px; background:var(--card-2); border:2px solid var(--line); padding:1px 5px; color:var(--accent-text); }
.flow .fbody { padding:6px 20px 16px; }
.flow .fctl { display:flex; align-items:center; gap:10px; padding:14px 20px; border-top:3px solid var(--line); background:var(--chrome); flex-wrap:wrap; }
.flow .dots { display:flex; gap:6px; margin-left:auto; }
.flow .dots i { width:10px; height:10px; border:2px solid #525a67; display:inline-block; transition:all 0.1s; }
.flow .dots i.on { background:var(--accent); border-color:var(--accent); }
/* SVG layer — fully theme-independent (dark canvas in both themes) */
.svg-wrap { border:3px solid var(--line); background:var(--dia-bg); box-shadow:var(--shadow); padding:10px; overflow-x:auto; margin:0; }
.svg-wrap svg { width:100%; display:block; min-width:580px; }
.dev-rect { transition:stroke 0.2s; }
.dev-rect.hl { stroke:var(--dia-hl) !important; stroke-width:3 !important; }
.dev-label { font-family:var(--mono-ui); font-size:12px; font-weight:700; }
.dev-sub { font-family:var(--mono-ui); font-size:10px; }
.link-line { stroke:var(--dia-line); stroke-width:2; fill:none; transition:stroke 0.2s; }
.link-line.ctl { stroke-dasharray:5,4; stroke-width:1.5; }
.link-line.hl { stroke:var(--dia-hl) !important; stroke-width:3; }
```

**Host markup:** each flow is just an empty div the engine fills:
`<div class="flow" id="flow-{id}"></div>` — the `{id}` matches a key in the `flows` object.

**Authoring the flow data (this is the part you write per explainer):**

- Define **one shared topology** (`TOPO` nodes + `LINKS`) and reuse it across every flow so
  all animations render on the same picture. Node coordinates are **hand-laid inside the
  `viewBox`** (default `0 0 814 432`) — laying out a readable topology is the real authoring
  work; the engine itself never changes. Keep CE nodes low/outer, P/RR nodes high/centre.
- Each `step.path` is the ordered list of node ids the packet visits. `path:[]` = a **static
  step** (no movement) used to narrate state or show a drop, with `annotes` only. A **return
  trip** is just the reversed id sequence — the engine matches both `lnk-A-B` and `lnk-B-A`,
  so no special-casing.
- **Lead with a single-node origin beat and advance ONE hop per step.** Step 1 should be
  `path:["{source}"]` (e.g. `["ce1"]`) so the packet visibly rests *at the source*; then each
  step moves one hop (`["ce1","pe1"]`, `["pe1","p1"]`, …). This matters because **flows render
  on page load even while their tab is hidden, and the packet rests at the LAST node of the
  step.** If step 1 is a multi-hop or non-source path, the reader opens the tab to find the
  packet already parked mid-fabric (e.g. at PE1) — it looks like the animation "starts in the
  wrong place." A source-origin step 1 fixes this and reads as "the frame begins here." Control-
  plane propagation that genuinely originates at a PE (a BGP update PE→RR→PE) still begins after
  the frame has first walked CE→PE in the opening hops.
- Re-author `step.stack` each step to tell the encapsulation story: `frame` alone at the CE,
  push `transport`+`evpn` rows at the ingress PE, pop them at the egress PE. `kind` maps to a
  colour via `STACK_COL` (extend it for non-MPLS encaps). Top row = outermost label.
- `annotes` are callouts anchored at a node centre plus `dx/dy`; use them for "learn MAC",
  "push 2 labels", "not in flood list → no BUM", etc. `\n` splits lines.

**The engine (paste verbatim into the single `<script>` block; change only `TOPO`/`LINKS`/`flows`):**

```javascript
/* ---- per-topic data: define ONE shared topology, reuse for all flows ---- */
var TOPO = {
  ce1:{x:8,y:362,w:104,h:46,color:"var(--dev-ce)",  label:"CE1",    sub:"192.168.x.10"},
  pe1:{x:120,y:212,w:104,h:46,color:"var(--dev-pe)",label:"PE1",    sub:"1.1.1.1 (XE)"},
  p1 :{x:352,y:40, w:128,h:48,color:"var(--dev-core)",label:"P1 (RR)",sub:"2.2.2.2"},
  pe2:{x:588,y:212,w:104,h:46,color:"var(--dev-pe)",label:"PE2",    sub:"4.4.4.4 (XE)"},
  ce2:{x:700,y:362,w:104,h:46,color:"var(--dev-ce)",label:"CE2",    sub:"192.168.x.20"}
  // PE-XR / non-member PEs: add {…,color:"var(--dev-xr)",dash:true}
};
var LINKS = [ {a:"ce1",b:"pe1"},{a:"pe1",b:"p1"},{a:"p1",b:"pe2"},{a:"pe2",b:"ce2"} ];
// kind -> role colour. Extend for non-MPLS encaps (vxlan, srv6, …).
var STACK_COL = {transport:"var(--lbl-transport)", evpn:"var(--lbl-evpn)", frame:"var(--lbl-frame)", ctrl:"var(--lbl-ctrl)"};

var flows = {
  // example shape — one entry per packet flow, keyed to its host div id (flow-<key>):
  rt2:{ title:"Type-2 MAC/IP Advertisement", caption:"control-plane MAC learning",
    nodes:TOPO, links:LINKS, steps:[
      // step 1 = ORIGIN beat: single-node path so the packet rests AT the source on load
      { desc:"<b>CE1</b> has a frame for CE2; its MAC is unknown in the fabric.",
        path:["ce1"], stack:[{text:"ETH frame",kind:"frame"}],
        annotes:[{at:"ce1",dx:0,dy:-40,text:"src MAC\naabb.cc00.0010",color:"var(--dev-ce)"}] },
      { desc:"The frame reaches <b>PE1</b>, which learns CE1's MAC on the local AC.",
        path:["ce1","pe1"], stack:[{text:"ETH frame",kind:"frame"}],
        annotes:[{at:"pe1",dx:66,dy:-34,text:"learn MAC\naabb.cc00.0010",color:"var(--dia-ok)"}] },
      { desc:"<b>Known-unicast:</b> CE2 → CE1. PE2 <b>pushes two labels</b>; core swaps transport; PE1 pops both.",
        path:["ce2","pe2","p1","pe1","ce1"],
        stack:[{text:"Lbl 16001 transport",kind:"transport"},{text:"Lbl 24020 EVPN",kind:"evpn"},{text:"ETH frame",kind:"frame"}],
        annotes:[{at:"pe2",dx:0,dy:-44,text:"push 2 labels",color:"var(--lbl-transport)"},
                 {at:"pe1",dx:0,dy:-40,text:"pop → deliver",color:"var(--dia-ok)"}] }
      // annotation colours: use --dia-ok (success), --dia-bad (failure/drop), --lbl-* / --dev-* — never editorial tokens
    ]}
};

/* ---- engine: do not modify ---- */
function ipath(wps, t){
  var segL=[], total=0;
  for(var j=1;j<wps.length;j++){var dx=wps[j].x-wps[j-1].x,dy=wps[j].y-wps[j-1].y,len=Math.sqrt(dx*dx+dy*dy);segL.push(len);total+=len;}
  if(total===0) return {x:wps[0].x,y:wps[0].y};
  var d=t*total,acc=0;
  for(j=0;j<segL.length;j++){ if(d<=acc+segL[j]){ var st=segL[j]===0?0:(d-acc)/segL[j]; return {x:wps[j].x+(wps[j+1].x-wps[j].x)*st,y:wps[j].y+(wps[j+1].y-wps[j].y)*st}; } acc+=segL[j]; }
  var L=wps.length-1; return {x:wps[L].x,y:wps[L].y};
}
function showAnn(svg, anns, devs){
  var g=svg.getElementById('annotes'), h='';
  if(!anns){ g.innerHTML=''; return; }
  for(var a=0;a<anns.length;a++){
    var an=anns[a], dc=devs[an.at], cx=dc[0]+(an.dx||0), cy=dc[1]+(an.dy||0);
    var ls=an.text.split('\n'), lh=15, pad=12, maxW=0;
    for(var l=0;l<ls.length;l++) maxW=Math.max(maxW, ls[l].length*6.8);
    var bw=maxW+pad, bh=ls.length*lh+pad;
    h+='<rect x="'+(cx-bw/2)+'" y="'+(cy-bh/2)+'" width="'+bw+'" height="'+bh+'" style="fill:var(--dia-surface);stroke:'+an.color+';stroke-width:2;opacity:0.97"/>';
    for(l=0;l<ls.length;l++) h+='<text x="'+cx+'" y="'+(cy-(ls.length-1)*lh/2+l*lh+5)+'" text-anchor="middle" style="fill:'+an.color+';font-family:var(--mono-ui);font-size:11px">'+ls[l]+'</text>';
  }
  g.innerHTML=h;
}
function centersFrom(nodes){ var c={}; for(var k in nodes){ var n=nodes[k]; c[k]=[n.x+n.w/2,n.y+n.h/2]; } return c; }
function buildTopo(nodes, links){
  var s='<svg viewBox="0 0 814 432" xmlns="http://www.w3.org/2000/svg"><g id="links">';
  for(var i=0;i<links.length;i++){
    var a=nodes[links[i].a], b=nodes[links[i].b];
    s+='<line id="lnk-'+links[i].a+'-'+links[i].b+'" class="link-line'+(links[i].ctl?' ctl':'')
      +'" x1="'+(a.x+a.w/2)+'" y1="'+(a.y+a.h/2)+'" x2="'+(b.x+b.w/2)+'" y2="'+(b.y+b.h/2)+'"/>';
  }
  s+='</g><g id="devs">';
  for(var k in nodes){ var d=nodes[k], cx=d.x+d.w/2, cy=d.y+d.h/2;
    s+='<g id="dev-'+k+'"><rect class="dev-rect" x="'+d.x+'" y="'+d.y+'" width="'+d.w+'" height="'+d.h
      +'" fill="var(--dia-surface)" stroke="'+d.color+'" stroke-width="2"'+(d.dash?' stroke-dasharray="5,4"':'')+'/>'
      +'<text class="dev-label" x="'+cx+'" y="'+(cy-1)+'" text-anchor="middle" fill="'+d.color+'">'+d.label+'</text>'
      +'<text class="dev-sub" x="'+cx+'" y="'+(cy+13)+'" text-anchor="middle" fill="var(--dia-sub)">'+d.sub+'</text></g>';
  }
  s+='</g><g id="pkt-grp" opacity="0"></g><g id="annotes"></g></svg>';
  return s;
}
function buildPacket(stack){
  if(!stack||!stack.length) return '';
  var w=148, rh=17, h=stack.length*rh, x=-w/2, y=-h/2, s='';
  s+='<rect x="'+x+'" y="'+y+'" width="'+w+'" height="'+h+'" fill="var(--dia-pkt-bg)" stroke="var(--dia-edge)" stroke-width="1.5" opacity="0.98"/>';
  for(var k=0;k<stack.length;k++){
    var row=stack[k], ry=y+k*rh, col=STACK_COL[row.kind]||"var(--dia-edge)";
    if(k>0) s+='<line x1="'+x+'" y1="'+ry+'" x2="'+(x+w)+'" y2="'+ry+'" stroke="var(--dia-line)" stroke-width="0.8"/>';
    s+='<rect x="'+x+'" y="'+ry+'" width="4" height="'+rh+'" fill="'+col+'"/>';
    s+='<text x="'+(x+11)+'" y="'+(ry+rh-5)+'" fill="'+col+'" font-family="var(--mono-ui)" font-size="10">'+row.text+'</text>';
  }
  return s;
}
function renderSvg(host, f, i){
  var svg=host.querySelector('svg'), desc=host.querySelector('.fdesc');
  var pktG=svg.getElementById('pkt-grp'), step=f.steps[i];
  if(host._aid){ cancelAnimationFrame(host._aid); host._aid=null; }
  desc.innerHTML='<b>'+(i+1)+'.</b> '+step.desc;
  pktG.setAttribute('opacity','0');
  showAnn(svg, null);
  svg.querySelectorAll('.hl').forEach(function(el){ el.classList.remove('hl'); });
  if(step.path && step.path.length>0){
    for(var d=0;d<step.path.length;d++){ var de=svg.getElementById('dev-'+step.path[d]); if(de) de.querySelector('.dev-rect').classList.add('hl'); }
    for(d=0;d<step.path.length-1;d++){
      var ln=svg.getElementById('lnk-'+step.path[d]+'-'+step.path[d+1]) || svg.getElementById('lnk-'+step.path[d+1]+'-'+step.path[d]);
      if(ln) ln.classList.add('hl');
    }
    pktG.innerHTML=buildPacket(step.stack);
    var wps=[]; for(d=0;d<step.path.length;d++){ var c=f.devs[step.path[d]]; wps.push({x:c[0],y:c[1]}); }
    pktG.setAttribute('transform','translate('+wps[0].x+','+wps[0].y+')');
    pktG.setAttribute('opacity','1');
    var stt=null, dur=1200;
    function anim(now){
      if(!stt) stt=now;
      var el=now-stt, t=Math.min(1, el/dur);
      var et=t<.5?2*t*t:-1+(4-2*t)*t;
      var pos=ipath(wps, et);
      pktG.setAttribute('transform','translate('+pos.x+','+pos.y+')');
      if(t<1){ host._aid=requestAnimationFrame(anim); }
      else { showAnn(svg, step.annotes, f.devs); }
    }
    host._aid=requestAnimationFrame(anim);
  } else { showAnn(svg, step.annotes, f.devs); }
}
Object.keys(flows).forEach(function(fid){
  var host=document.getElementById('flow-'+fid); if(!host) return;
  var f=flows[fid];
  host.innerHTML =
    '<div class="fhead"><span class="ft">'+f.title+'</span><span class="fc">'+f.caption+'</span></div>'+
    '<div class="fdesc"></div>'+
    '<div class="fbody"><div class="svg-wrap"></div></div>'+
    '<div class="fctl">'+
      '<button class="btn" data-a="prev">◀ Prev</button>'+
      '<button class="btn btn--primary" data-a="play">▶ Play</button>'+
      '<button class="btn" data-a="next">Next ▶</button>'+
      '<span class="dots"></span>'+
    '</div>';
  host.querySelector('.svg-wrap').innerHTML = buildTopo(f.nodes, f.links);
  f.devs = centersFrom(f.nodes);
  var i=0, timer=null;
  var dotsEl=host.querySelector('.dots');
  var playBtn=host.querySelector('[data-a="play"]');
  f.steps.forEach(function(){ var d=document.createElement('i'); dotsEl.appendChild(d); });
  function render(){ renderSvg(host, f, i); dotsEl.querySelectorAll('i').forEach(function(d,k){ d.classList.toggle('on', k===i); }); }
  function go(n){ i=(n+f.steps.length)%f.steps.length; render(); }
  function stop(){ if(timer){ clearInterval(timer); timer=null; playBtn.innerHTML='▶ Play'; } }
  host.querySelector('[data-a="prev"]').addEventListener('click', function(){ stop(); go(i-1); });
  host.querySelector('[data-a="next"]').addEventListener('click', function(){ stop(); go(i+1); });
  playBtn.addEventListener('click', function(){
    if(timer){ stop(); return; }
    playBtn.innerHTML='❚❚ Pause';
    timer=setInterval(function(){ go(i+1); if(i===f.steps.length-1){ stop(); } }, 3600);
  });
  render();
});
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
