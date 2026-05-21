# SUSHILOOP Charter

**The values every generated skill must align with.**

This is the document the validator checks against. Every skill SUSHILOOP produces must pass these tests before it ships. Every skill already in `skills/` is presumed to comply. Any skill found to violate this charter will be removed.

---

## Core principles

**1. Skills must protect human cognition, not replace it.**
A skill that helps a user think more clearly, verify more carefully, or catch their own errors is aligned. A skill that does the thinking for the user is not.

**2. Skills must be transparent.**
No black boxes. Every skill returns its reasoning (`reason` field) and a confidence score. Users must always be able to see why a guardrail fired.

**3. Skills must fail open, not closed — unless safety requires otherwise.**
A guardrail that breaks should not silently block legitimate use. It should log, surface the failure, and let the user decide. Exception: skills protecting against verified high-harm categories (CSAM, weapons of mass destruction, etc.) fail closed by default.

**4. Skills must be auditable.**
Pure Python, standard library only (or well-known dependencies). No obfuscation. No remote calls without explicit user consent. Every skill must be readable end-to-end in under 5 minutes by a competent developer.

**5. Skills must be free, open, and forkable.**
MIT licensed. No telemetry. No phone-home. No vendor lock-in. If someone wants to fork the entire engine and run their own version with different values, they should be able to.

---

## What skills must NOT do

A generated skill is **rejected** if it:

- Disables, bypasses, weakens, or overrides any existing safety mechanism
- Collects user data without explicit consent
- Calls external services without disclosure
- Targets, surveils, or profiles individuals
- Encourages users to defer to AI rather than think for themselves
- Implements functionality that primarily serves a commercial interest rather than the user
- Contains hidden behavior not described in its docstring
- Could be repurposed as an attack tool against other AI systems (red-team tools must be explicitly scoped and labeled)

---

## What skills SHOULD do

A generated skill is **encouraged** if it:

- Prompts the user to verify AI outputs before acting on them
- Surfaces uncertainty rather than hiding it
- Detects manipulation, deception, or social engineering attempts
- Protects vulnerable populations (children, elderly, cognitively impaired) from AI overreach
- Teaches the user something about how AI works while protecting them
- Adds friction in the right places — the places where unaided thinking matters most
- Is composable with other skills (chainable, modular)

---

## Acceptable skill categories

| Category | Purpose |
|---|---|
| `INPUT_VALIDATION` | Detect jailbreaks, injection, manipulation attempts before they reach the model |
| `OUTPUT_FILTERING` | Catch PII, hallucinations, harmful content on the way out |
| `RATE_LIMITING` | Prevent abuse, runaway costs, compulsive use |
| `CONTENT_SAFETY` | Block content known to harm users or third parties |
| `PII_DETECTION` | Protect personal data from leakage |
| `COGNITIVE_PROTECTION` | (Reserved) Skills that specifically counter cognitive offloading patterns |
| `VERIFICATION_PROMPT` | (Reserved) Skills that prompt users to verify before accepting AI output |
| `BIAS_DETECTION` | (Reserved) Skills that flag biased reasoning or framing |

Categories marked "Reserved" are mission-critical and will be prioritized in future evolution cycles.

---

## Validation process

Every cycle, before a skill is committed:

1. **Schema validation** — proposal must include all required fields
2. **Safety constraint check** — proposal must not contain mission-incompatible concepts (this charter's "must NOT" list)
3. **Code generation** — Groq/Llama writes the skill
4. **Self-audit** *(planned)* — a second Groq call reviews the generated skill against this charter
5. **Smoke test** — the skill must execute without error and return a valid response shape
6. **Registration** — skill is logged in `brain/skills_registry.json`
7. **Public commit** — skill is pushed to `main` for the world to use

Skills that fail any stage are rejected and logged in `brain/memory.md`.

---

## Amendments

This charter is a living document. It will be updated as:

- New cognitive offloading research is published
- New AI capabilities create new threat surfaces
- The community proposes improvements via pull request
- The mission requires it

All amendments will be made in public commits with reasoning in the commit message.

---

## The non-negotiables

These will never change without forking the project entirely:

1. **The engine is and remains free to run.**
2. **The skills are and remain MIT licensed.**
3. **The mission is and remains: protect human cognition.**
4. **No paid tiers. No premium skills. No corporate capture.**

---

🍣

Built by [@phantomcap_ai](https://x.com/phantomcap_ai) · [Phantom Capital](https://github.com/PhantomCapAI) · May 2026
