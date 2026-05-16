---
description: Branching strategy and workflow conventions for the cisco-lab-skills repository, covering main/feature branches, submodule consumption by exam repos, and merge practices.
---

# Branching Strategy — `cisco-lab-skills`

This repository is a **shared skill library** mounted as a git submodule at
`.agent/skills/` inside multiple exam-specific lab repos (CCNP SPRI, ENARSI,
ENCOR, SPCOR, etc.). Anything pushed to `main` is inherited by every consumer
the moment they run `git submodule update --remote`.

**Treat `main` as a published API. The bar for landing on `main` is higher
than it would be in a single-project repo.**

---

## The Rule

**Default to a branch when the change is speculative or untested. Land on
`main` only after the change is proven in at least one downstream exam repo.**

This is the inverse of the trunk-default rule used in the exam repos. The
asymmetry is deliberate: a buggy commit on a single exam repo's trunk affects
one project; a buggy commit on this repo's trunk affects every consumer.

### On `main` directly

- Documentation cleanups, typo fixes, comment improvements with no behavioral impact.
- Mature, well-tested skill updates that have already been validated in a
  downstream exam repo via a submodule branch.
- New skills that have shipped at least one passing lab build downstream.
- `LESSONS_LEARNED.md` and `ios-compatibility.yaml` entries (these are
  append-only documentation; downstream consumers benefit from them
  immediately).

### On a branch

Anything else. Specifically:

- New builder behavior, new skill steps, new gates, new validators.
- Changes to `lab-assembler`, `spec-creator`, `exam-planner`, `lab-builder`,
  or `mega-capstone-creator` that alter generated artifacts.
- Schema changes to `baseline.yaml`, `meta.yaml`, `model-policy.yaml`, or any
  template under `lab-assembler/assets/`.
- Cross-cutting features (the XR retrofit was a textbook case — it touched
  `spec-creator` and `lab-assembler` and would have polluted every downstream
  exam repo if landed directly on `main`).

---

## Branch Naming

Mirror the parent exam repo's branch name when the work is coordinated across
both repos. Two prefixes:

| Prefix         | Meaning                                                      |
| -------------- | ------------------------------------------------------------ |
| `experiment/`  | Speculative skill change. May be abandoned. Kill-date req'd. |
| `feat/`        | Definitely shipping. Big enough to want a single revert handle. |

**Kill-date convention** for `experiment/` branches — first commit message must
include:

```
Kill-date: YYYY-MM-DD — abandon if not merged by then.
```

This forces a go/no-go decision instead of letting the branch drift. Without
a kill-date, an experiment branch in a shared skills repo becomes invisible
debt: nobody else can see it from their exam repos, but it consumes mental
overhead every time you context-switch back.

---

## Coordination With Downstream Exam Repos

When a feature spans both this repo and an exam repo (e.g., a new builder
behavior plus the labs that exercise it), use **matching branch names** in
both repos:

```
exam repo:    git checkout -b experiment/xr-retrofit
this repo:    git checkout -b experiment/xr-retrofit
```

The exam repo's submodule pointer references this repo's branch SHA during
development. When the work is ready:

1. **In the submodule:** merge `experiment/xr-retrofit` into `main`, push.
2. **In the exam repo:** bump the submodule pointer to the new `main` SHA on
   the experiment branch, validate the parent's experiment branch still
   passes, then merge the parent branch into its own `master`.

When the work is abandoned:

1. **In the submodule:** `git push origin --delete experiment/xr-retrofit`,
   `git branch -D experiment/xr-retrofit`.
2. **In the exam repo:** `git branch -D experiment/xr-retrofit`. The pointer
   never made it to the exam repo's trunk, so nothing else needs cleanup.

The matched-name discipline matters because it gives a single audit point: if
you see `experiment/xr-retrofit` open in either repo and not in the other,
something is in an inconsistent state.

---

## What This Means in Practice

- **Bumping the submodule pointer in an exam repo from a session?** Only do
  it if the new SHA is on `main`. Pointing the parent's `master` at a
  submodule branch is a footgun — it makes the parent's trunk dependent on
  unstable skill code.
- **Landing a skill fix that came from an exam repo testing session?**
  Trivial fixes (typo, missing comma in a template) can go straight to
  `main`. Anything that changes behavior — even a "small" tweak — goes on a
  branch, gets validated against a downstream lab build, then merges.
- **The `LESSONS_LEARNED.md` exception.** This file is append-only and
  documents bugs after they've been fixed elsewhere. Direct commits to `main`
  are fine because nothing else reads it programmatically.
- **The `ios-compatibility.yaml` exception.** Per the parent repo's "Command
  Compatibility Rule," this file gets updated immediately when a command
  failure is discovered. Direct commits to `main` are expected and required —
  the whole point is that downstream projects inherit the compatibility data
  fast.

---

## Anti-Patterns

- **Pushing untested skill changes to `main` because "it's just a small
  refactor."** Other projects auto-pull. There's no such thing as a small
  refactor in a published API.
- **Long-lived `experiment/` branches with no kill-date.** Especially bad
  here because experiment branches in a shared repo are invisible to other
  projects — the rot accumulates without external pressure to resolve it.
- **Branching here without a matching parent-repo branch.** Speculative skill
  work needs a downstream exam repo to validate against. Without one, the
  branch is producing untested artifacts.
- **Letting an exam repo's `master` point at a submodule branch.** Even
  briefly. The exam repo's trunk should only ever reference `main` SHAs in
  this repo.

---

## Quick Reference

```
$ # Doc fix or LESSONS_LEARNED entry — straight to main.
$ git checkout main
$ # ...edit...
$ git commit -m "docs(lessons): IOSv rejects 'mpls mtu' on Ethernet sub-ifs"
$ git push

$ # New builder behavior — branch, validate downstream, then merge.
$ git checkout -b feat/xr-mode-flag
$ # ...work, push branch...
$ # In the exam repo: git submodule update --remote on the matching branch,
$ # run /build-lab, validate. When green:
$ git checkout main && git merge --no-ff feat/xr-mode-flag && git push

$ # Speculative experiment.
$ git checkout -b experiment/dual-stack-everywhere
$ # First commit message includes:  Kill-date: 2026-06-15
$ # If shipped: merge as feat/. If abandoned: git branch -D and walk away.
```
