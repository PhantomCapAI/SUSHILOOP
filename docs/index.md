---
title: SUSHILOOP
description: Self-improving AI guardrail engine protecting human cognition in the AI era.
---

# 🍣 SUSHILOOP

**Self-improving AI guardrail engine.**
**Protecting human cognition in the AI era.**

Every 6 hours, an autonomous engine designs a new AI safety guardrail, writes the code, tests it, and ships it to a public repository. No humans in the loop. 100% free to run. Forever.

[**View the code on GitHub →**](https://github.com/PhantomCapAI/SUSHILOOP)
[**Read the manifesto →**](https://github.com/PhantomCapAI/SUSHILOOP/blob/main/MANIFESTO.md)
[**Browse the skills →**](https://github.com/PhantomCapAI/SUSHILOOP/tree/main/skills)

---

## The problem

By 2040, the average human brain is projected to use **40–60% less of its deep-thinking circuitry** — outsourcing it to AI.

- Critical thinking: **20–40% projected decline** by 2040
- Gerlich (2025): correlation of **r = −0.68** between frequent AI use and critical thinking
- UPenn (2026): "cognitive surrender" — people abandoning internal logic for AI outputs
- The **Flynn effect has reversed** in several countries
- Elites pull further ahead. Everyone else cognitively offloads and loses.

The gap widens. The boiling frog effect makes unaided thinking feel harder over time.

---

## The response

SUSHILOOP is one piece of armor.

It ships **AI safety guardrails as open infrastructure**, autonomously, around the clock, on free infrastructure that cannot be bought, captured, or shut down.

Every skill it produces is:

- **Free** — MIT licensed
- **Open** — auditable Python, no black boxes
- **Forkable** — anyone can run their own copy
- **Tested** — every skill passes a smoke test before shipping
- **Aligned** — every skill is checked against the [Charter](https://github.com/PhantomCapAI/SUSHILOOP/blob/main/CHARTER.md)

---

## How it works

GitHub Actions wakes up every 6 hours → Proposes a new guardrail (Groq + Llama 3.3 70B) → Generates the code → Runs smoke tests → Registers in memory → Commits and pushes to main.

Total cost to operate: **$0/month.**

---

## Skill categories

| Category | Purpose |
|---|---|
| Input Validation | Catch jailbreaks, prompt injection, manipulation |
| Output Filtering | Catch PII, hallucinations, harmful content |
| Rate Limiting | Prevent abuse and compulsive use |
| Content Safety | Block harmful generations |
| PII Detection | Protect personal data |
| Cognitive Protection | Counter offloading patterns |
| Verification Prompts | Prompt users to verify before accepting |
| Bias Detection | Flag biased reasoning or framing |

---

## The ask

**Companies:** Implement guardrails by default. Not as premium. As the floor.

**Educators:** Teach AI literacy alongside reading and math.

**Policymakers:** Recognize cognitive offloading as a public health concern.

**Parents:** Don't ban AI. Teach it. Model thinking first, asking second.

**Everyone:** Use AI as a sparring partner, not a brain replacement.

[**Read the full manifesto →**](https://github.com/PhantomCapAI/SUSHILOOP/blob/main/MANIFESTO.md)

---

## Use the skills

Drop them into your own AI pipeline. Example:

`from skills.prompt_injection_detector import prompt_injection_detector`

`result = prompt_injection_detector(user_input)`

If `result["blocked"]` is True, the input was flagged.

[**Browse all generated skills →**](https://github.com/PhantomCapAI/SUSHILOOP/tree/main/skills)

---

## Run your own

1. Fork [the repo](https://github.com/PhantomCapAI/SUSHILOOP)
2. Get a free [Groq API key](https://console.groq.com/keys)
3. Add it to your fork's GitHub Secrets as `GROQ_API_KEY`
4. Enable GitHub Actions
5. Done. New skills every 6 hours, forever.

---

## The bet

One person. One autonomous engine. One free GitHub account.

Shipping more guardrails than corporate safety teams ship in a quarter — because we ship every 6 hours, forever.

---

**The mind must evolve with AI, not fall back on it.**

🍣

Built by [@phantomcap_ai](https://x.com/phantomcap_ai) · [Phantom Capital](https://github.com/PhantomCapAI) · May 2026
