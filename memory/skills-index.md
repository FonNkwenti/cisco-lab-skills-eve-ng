# Skills Index

Quick reference for all skills in this repository.

| Skill | When to Use | Key Output |
|-------|-------------|------------|
| `chapter-topics-creator` | Starting a new chapter from scratch | `baseline.yaml`, chapter `README.md` |
| `chapter-builder` | Generating multiple labs at once with config chaining | All lab artifacts for a chapter |
| `lab-workbook-creator` | Generating a single lab | `workbook.md`, configs, `setup_lab.py`, `topology.drawio` |
| `fault-injector` | Creating automated troubleshooting scenario scripts | `inject_scenario_0N.py`, `apply_solution.py` |
| `drawio` | Creating or fixing topology diagrams | `topology.drawio` |
| `gns3` | Reference for platform capabilities and constraints | (reference only) |
| `cisco-troubleshooting-1` | Systematically diagnosing a network fault | Structured resolution report |

## Typical Workflow for a New Chapter

```
1. chapter-topics-creator  →  baseline.yaml + README.md
2. chapter-builder         →  all labs in sequence
   └── lab-workbook-creator (called per lab)
       └── fault-injector  (called per lab, after workbook)
3. drawio                  →  verify/fix topology diagrams
```
