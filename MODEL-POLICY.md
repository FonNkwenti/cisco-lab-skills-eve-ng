# Model Policy

The skills submodule ships a `model-policy.yaml` that defines which
Anthropic model IDs are allowed to build labs at each difficulty tier.

## Why this exists

1. **Cost discipline** — Foundation labs don't need Opus-level reasoning.
   Advanced labs shouldn't be built by Haiku.
2. **Quality floor** — the OSPF lab-01 three-model comparison showed that
   Haiku ships with structural defects (misplaced drawio, thin ticket
   narratives) that are unacceptable on exam-critical content.
3. **Single source of truth** — when Anthropic rotates model IDs, this
   one file updates and every exam repo picks it up on `git submodule update`.

## Tier summary

| Tier | Allowed models | Recommended |
|---|---|---|
| Foundation | Haiku 4.5, Sonnet 4.6, Opus 4.7 | Sonnet 4.6 |
| Intermediate | Sonnet 4.6, Opus 4.7 | Sonnet 4.6 |
| Advanced | Opus 4.7 only | Opus 4.7 |

See `model-policy.yaml` for the exact model ID strings and effort guidance.

## Editing the policy

1. Bump `version` at the top of `model-policy.yaml`.
2. Update `tiers[*].allowed_models` and `recommended` as needed.
3. Append an entry to this doc under "Change log".
4. Commit to the skills submodule; exam repos pick it up on next submodule pull.

## Model ID rotation

When Anthropic releases a new model generation:

1. Add the new model ID to `allowed_models` for each tier where it qualifies.
2. Keep the old ID for one release cycle so in-flight builds don't break.
3. After the cycle, remove the old ID and bump `version`.
4. Append a "Change log" entry below.

## Enforcement

Enforcement lives in the slash commands (`build-lab.md`, `build-topic.md`)
in each exam repo's `.claude/commands/`. Before invoking any skill, the
command:

1. Reads `.agent/skills/model-policy.yaml`.
2. Reads the target lab's `difficulty` from `baseline.yaml`.
3. Self-identifies its own model ID from the system prompt.
4. Aborts with a `[GATE FAILED]` message if the model isn't in the allowed list.

The skills submodule cannot enforce at runtime — it has no hook into Claude
Code's model selection. Enforcement is prompt-level: the agent reads the
command prompt and refuses to proceed on mismatch. This catches ~95% of
"distracted operator" mistakes.

## Override mechanism

Pass `--force-model` to `/build-lab` or `/build-topic` to skip the gate.
Overrides are logged to the lab's `decisions.md` with the running model,
the tier, and the allowed list — so reviewers see provenance.

Use `--force-model` only for intentional experiments (draft builds on a
cheaper model, model-comparison studies). Never use it to ship student-
facing content below the tier threshold.

## Future work — true runtime enforcement

The prompt-level gate can be bypassed by invoking `lab-assembler` directly
instead of through `/build-lab`. For true enforcement, a Claude Code
`PreToolUse` hook in `.claude/settings.json` can inspect each Write/Edit
and return `"decision": "block"` when the model is wrong for the target
lab. Deferred until the prompt-level gate proves insufficient.

## Change log

- **2026-04-24** — Initial policy (v1). Haiku for Foundation; Sonnet for
  Foundation/Intermediate; Opus required for Advanced. Derived from the
  OSPF lab-01 three-model comparison report (`labs/ospf/report.md` in the
  CCNP SPRI repo).
