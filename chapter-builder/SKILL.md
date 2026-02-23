---
name: chapter-builder
description: Orchestrates batch generation of multiple labs for a chapter, ensuring config chaining and topology continuity. NOT the default workflow — labs should normally be built one at a time using the create-lab skill to allow review between each lab. Only use chapter-builder when the user explicitly asks to "generate all labs at once", "batch generate the chapter", or "regenerate all labs" and understands that individual review will happen after the batch completes.
---

# Chapter Builder Skill

This skill orchestrates the generation of an entire chapter with proper lab continuity. It ensures all labs share consistent topology from baseline.yaml, each lab builds on the previous lab's solution configs, and device additions are handled seamlessly.

-# Instructions

--# Step 1: Load Baseline
Read `baseline.yaml` for the specified chapter from `labs/[chapter]/baseline.yaml`.

--# Step 2: Generate Foundation (Lab 01)
Generate Lab 01 using the `lab-workbook-creator` skill.
- `initial-configs/`: Use base IP addressing from baseline `core_topology` (IP only, no protocol config).
- `solutions/`: Generate the completed configuration.
- **New Devices:** Add baseline devices (e.g., R1, R2, R3) as declared in `labs[1].devices`.

--# Step 3: Generate Subsequent Labs (N = 2, 3, ...)
For each subsequent lab number:
1. Identify active devices from `labs[N].devices`.
2. Set `initial-configs/` by copying exactly from Lab (N-1) `solutions/`.
3. Add new devices ONLY if `labs[N].devices` introduces them beyond the previous lab.
4. Use the `lab-workbook-creator` skill to generate: `workbook.md`, `initial-configs/`, `solutions/`, and `topology.drawio`.

--# Step 4: Generate Topology Diagrams
All generated `topology.drawio` files MUST follow the drawio Visual Style Guide. Invoke the `drawio` skill to ensure:
- White connection lines (`strokeColor=#FFFFFF`), never black.
- Device labels to the left of icons.
- IP last octet labels (`.1`, `.2`) near each router interface.
- Title at top center, legend box (black fill, white text) at bottom-right.

--# Step 5: Validation Checklist
After generating all labs, verify:
- [ ] All devices use IPs from `baseline.yaml`
- [ ] Lab N `initial-configs/` match Lab (N-1) `solutions/` exactly
- [ ] New devices are only added when declared in `labs[N].devices`
- [ ] No configs are removed between labs (chaining rule: only add, never remove)
- [ ] `topology.drawio` shows the correct devices per lab
- [ ] `topology.drawio` follows the drawio Visual Style Guide

-# Common Issues

--# Missing baseline.yaml
- **Cause:** `labs/[chapter]/baseline.yaml` does not exist.
- **Solution:** Stop execution. Inform the user and suggest running the `chapter-topics` skill first to generate the baseline for this chapter.

--# Config Chaining Failure
- **Cause:** Lab N `initial-configs/` is missing configurations present in Lab (N-1) `solutions/`.
- **Solution:** Re-copy the exact contents of Lab (N-1) `solutions/` into Lab N `initial-configs/` before applying any new changes for Lab N.

--# New Device Added Without Declaration
- **Cause:** A device appears in a lab's configs that was not listed in `labs[N].devices` in `baseline.yaml`.
- **Solution:** Cross-check the device list in `baseline.yaml`. Only add devices explicitly declared for that lab number.

--# Topology Diagram Style Violation
- **Cause:** `topology.drawio` was generated without invoking the `drawio` skill.
- **Solution:** Invoke the `drawio` skill on the generated file to apply the correct Visual Style Guide (white links, left labels, IP octets, legend box).

-# Reference: Chaining Table

| Lab | `initial-configs/` Source | New Devices |
|-----|--------------------------|-------------|
| 01 | `baseline.yaml` core_topology (IP only) | All baseline devices |
| 02 | Lab 01 `solutions/` | As declared |
| 03 | Lab 02 `solutions/` | As declared |
| N  | Lab (N-1) `solutions/` | As declared in `labs[N].devices` |

-# Examples

User says: "Use the chapter-builder skill to generate all EIGRP labs (1-9) in labs/eigrp/."

Actions:
1. Read `labs/eigrp/baseline.yaml`.
2. Generate Lab 01 using `lab-workbook-creator` with base IP configs.
3. For Labs 02–09: copy previous lab's `solutions/` as `initial-configs/`, then invoke `lab-workbook-creator`.
4. After each lab, invoke `drawio` skill to apply topology style.
5. Run validation checklist against all 9 labs.
