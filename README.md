# 🍣 SUSHILOOP

**Self-improving AI Guardrail Engine — autonomously generating safety skills to protect human cognition in the AI era.**

Every 6 hours, SUSHILOOP wakes up, designs a new AI safety guardrail, writes the code, tests it, and ships it to this repo. No humans in the loop. 100% free to run.

Built by [@phantomcap_ai](https://x.com/phantomcap_ai) under [Phantom Capital](https://github.com/PhantomCapAI).

---

## Why this exists

By 2040, the average human brain is projected to use significantly less of its deep-thinking circuitry — outsourcing 40–60% of what we once did internally to AI.

- **Critical thinking**: 20–40% projected decline by 2040. Gerlich (2025) found r = −0.68 between frequent AI use and critical thinking, fully mediated by cognitive offloading.
- **Cognitive surrender**: UPenn (2026) — people abandon internal logic for AI outputs.
- **Motivation to think deeply**: 40–60% projected drop.
- **The Flynn effect has reversed** in some countries due to cognitive offloading.
- **Elites pull further ahead** — top 10–20% use AI as a sparring partner. Everyone else offloads and loses.

SUSHILOOP is armor against that. Every guardrail it produces helps people use AI without surrendering their thinking to it.

The next generation deserves tools that protect their brains, not erode them.

---

## How it works

```
GitHub Actions (every 6 hours)
  ↓
Propose (Groq/Llama) → Generate skill → Test → Register → Commit to main
```

**Stack:**
- Proposal + code generation: Groq + Llama 3.3 70B (free tier)
- Validation: Cognitive Friction Validator
- Tests: pytest smoke tests
- Memory: JSON state + markdown ledger + skills registry
- Orchestration: GitHub Actions (free tier)
- **Total cost: $0/month**

---

## Skill categories

| Category | Purpose |
|---|---|
| `INPUT_VALIDATION` | Catch jailbreaks, prompt injection, unsafe instructions |
| `OUTPUT_FILTERING` | Filter PII, harmful content, hallucinations on the way out |
| `RATE_LIMITING` | Prevent abuse and runaway costs |
| `CONTENT_SAFETY` | Block harmful generations |
| `PII_DETECTION` | GDPR-compliant data protection |
| `COGNITIVE_PROTECTION` | Keep the user thinking — scaffold reasoning instead of replacing it |
| `VERIFICATION_PROMPT` | Inject verify-before-acting checkpoints on actionable output |
| `BIAS_DETECTION` | Catch loaded framing and one-sided prompts that entrench priors |

All generated skills live in [`skills/`](./skills) — drop them into your own pipelines.

---

## Setup (run your own fork)

1. Fork this repo
2. Get a free Groq API key: https://console.groq.com/keys
3. Add it to your fork's GitHub Secrets as `GROQ_API_KEY`
4. Enable GitHub Actions
5. Done. Runs automatically every 6 hours.

To trigger manually: **Actions → SUSHI LOOP Evolution → Run workflow**.

---

## Project structure

```
SUSHILOOP/
├── .github/workflows/evolve.yml
├── core/                  # evolve, proposal_engine, skill_generator, validator, test_runner, memory_manager, git_manager, schemas
├── skills/                # 🍣 Auto-generated guardrails live here
├── tests/                 # Auto-generated tests
├── brain/                 # Memory + state
├── docs/
├── run_cycle.py
└── requirements.txt
```

---

## Philosophy

- **Ships over polish** — autonomous evolution beats human perfectionism
- **Free over premium** — zero cost, infinite runway
- **Anti-AI-slop** — every skill tested before it ships
- **Open by default** — every guardrail is public infrastructure
- **The cognitive arms race is real** — SUSHILOOP is on the side of keeping humans sharp

---

## Status

- ✅ First autonomous skill shipped: May 21, 2026 — `prompt_injection_detector.py`
- 🍣 Running 24/7 on GitHub Actions

---

## Sources

- Gerlich, M. (2025). MDPI.
- University of Pennsylvania (2026). *Cognitive Surrender.*
- Microsoft (2025). Knowledge worker AI survey.
- Council on Strategic Risks — 2040 projections.
- Anthropic — 80k-user study.
- Policy Options — Flynn effect reversal.

---

## License

MIT. See [LICENSE](./LICENSE).

---

Built by **[@phantomcap_ai](https://x.com/phantomcap_ai)** · [Phantom Capital](https://github.com/PhantomCapAI) · 🍣 May 2026
