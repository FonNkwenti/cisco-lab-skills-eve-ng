# Resolution Report Template

Use this template to generate the final troubleshooting report.

---

## Formatting Rules (read before filling in)

Reports must be readable as standalone documents. Follow these rules strictly:

- **Use prose paragraphs** for explanations, rationale, and analysis — not code blocks
- **Use tables** for incident metadata, methodology selection, and verification results
- **Use bullet points** for lists of impacts, root cause details, and preventive checks
- **Use code blocks only for**:
  - Actual IOS `show` command output (verbatim)
  - Configuration commands being applied
  - Diagnostic log entries (timestamped observations)
- **Use ASCII diagrams** when a concept is better shown visually (e.g., tunnel mode comparison, packet flow, state machine)
- **Never wrap plain text in a code block** — if it isn't a command or verbatim output, it belongs in prose or a list

A report that puts all content inside code blocks is unreadable. Headings, tables, and bullet points exist for a reason — use them.

---

## 1. Incident Summary

| Field | Value |
|-------|-------|
| **Incident ID** | INC-YYYYMMDD-ticket-NNN |
| **Lab** | `labs/<topic>/lab-NN-<slug>/` |
| **Reported** | YYYY-MM-DD HH:MM |
| **Severity** | High / Medium / Low |
| **Status** | Resolved / Resolved (follow-up pending) |

### Reported Symptoms

**Fault A** — [Device + interface + symptom]. Expected: [what should have been seen].

**Fault B** — [Device + interface + symptom]. Expected: [what should have been seen].

### Additional Findings *(discovered during verification)*

**Fault C** — [Brief description]. [Why it matters].

**Fault D** *(out of scope — follow-up recommended)* — [Brief description].

---

## 2. Methodology Applied

| Fault | Approach | Rationale |
|-------|----------|-----------|
| A | **[Method]** | [One sentence: why this method for this fault] |
| B | **[Method]** | [One sentence: why this method for this fault] |

---

## 3. Diagnostic Log

Use one code block per timestamped step. Each block should contain: the command run, the key output, and a brief observation. Keep observations factual — save analysis for Section 4.

```
HH:MM  [Action — what was done and why]

       Command: show ...
       Output:
         [relevant lines only]

       Observation: [what the output means, factually]
```

```
HH:MM  HYPOTHESIS: [what you think is wrong and why]
       TEST: [what command or change will confirm it]
```

```
HH:MM  *** ROOT CAUSE CONFIRMED (Fault X): [one-line description] ***

       Fix applied:
         [Device](config-if)# [command]

       Immediate result: [syslog or show output confirming fix took effect]
```

---

## 4. Root Cause Analysis

### Fault A — [Short title]

[Prose paragraph explaining what was wrong and why it caused the observed symptom. Be specific about the IOS mechanism involved.]

- **Specific misconfiguration:** `[command]` instead of `[correct command]`
- **Why it failed:** [Mechanism explanation]
- **Impact:** [What broke as a result]

Use an ASCII diagram if the distinction is best shown visually:

```
┌─────────────────────────────────────────────────────────────┐
│  [Wrong config]                                             │
│  ├─ [What this mode does]                                   │
│  └─ [Why it causes the symptom]                             │
│                                                             │
│  [Correct config]                                           │
│  ├─ [What this mode does]                                   │
│  └─ [Why this fixes it]                                     │
└─────────────────────────────────────────────────────────────┘
```

**ENCOR Exam Objective:** [e.g., 2.2.b — GRE and IPsec tunneling]

---

### Fault B — [Short title]

[Prose explanation. One paragraph per fault.]

---

## 5. Resolution Actions

### Fault A — [Short title]

```
! [Device]
[Device]# configure terminal
[Device](config)# [command]
[Device](config)# end
```

**Verification:**

```
[Device]# show [command]
  [relevant output line]       ← [what this confirms]
  [relevant output line]       ← [what this confirms]
```

---

### Fault B — [Short title]

[If no config change was needed, say so in prose and explain why.]

---

### Recommended follow-up for Fault D

```
! [Device]
[Device](config)# [command]
```

---

## 6. Testing and Verification

| # | Test | Command | Result |
|---|------|---------|--------|
| 1 | [What is being confirmed] | `[command]` | [outcome] ✓ / ✗ |
| 2 | [What is being confirmed] | `[command]` | [outcome] ✓ / ✗ |
| 3 | [What is being confirmed] | `[command]` | [outcome] ✓ / ✗ |

**All reported symptoms resolved:** YES / NO

[If NO or partial: note which symptoms remain and why.]

---

## 7. Lessons Learned

### Root Cause Categories

- **Fault A:** [Category — e.g., Tunnel Mode Misconfiguration]
- **Fault C:** [Category — e.g., Missing Interface]

---

### ENCOR Exam Traps

[Prose describing the exam-relevant concept this fault illustrates. Include a decision table if the fault involves a common "which command do I use?" trap.]

| [Condition] | [Correct choice] |
|-------------|-----------------|
| [Scenario A] | [Answer A] |
| [Scenario B] | [Answer B] |

---

### Preventive Checklist

When configuring [feature]:

- [ ] [Specific thing to verify]
- [ ] [Specific thing to verify]
- [ ] [Specific thing to verify]
