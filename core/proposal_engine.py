"""AI-powered proposal generation using Groq with retrieval-augmented prompting.

Upgraded with anti-rut steering:
  1. Category-gap targeting — each cycle is FORCED toward the least-covered
     charter category, so the loop systematically fills empty buckets
     (PII_DETECTION, OUTPUT_FILTERING, CONTENT_SAFETY, ...) instead of
     camping on COGNITIVE_PROTECTION / INPUT_VALIDATION.
  2. Full-history rut memory — concepts already shipped OR proposed repeatedly
     across ALL history are hard-banned in the prompt (not just the last 3).
  3. Collision guard — if the model ignores the steer and returns a known rut,
     we fall back to a fresh proposal in the target category so the cycle still
     makes forward progress.
"""
import os
import re
import json
import structlog
from collections import Counter
from core.schemas import Proposal, ProposalType, SkillCategory
from core.memory_manager import MemoryManager
from core.skill_scorer import select_top_examples

logger = structlog.get_logger(__name__)

# All charter-sanctioned categories, in gap-fill priority order (empty/reserved first).
CHARTER_CATEGORIES = [
    "PII_DETECTION",
    "OUTPUT_FILTERING",
    "CONTENT_SAFETY",
    "BIAS_DETECTION",
    "VERIFICATION_PROMPT",
    "RATE_LIMITING",
    "INPUT_VALIDATION",
    "COGNITIVE_PROTECTION",
]

# Title suffix words that describe the *form* of a skill, not its *concept*.
# Stripping these collapses "Implicit Assumption Validator/Extractor/Clarifier"
# into one concept stem so we can see the rut.
_SUFFIX_WORDS = {
    "detector", "validator", "analyzer", "evaluator", "checker", "system",
    "catcher", "mapper", "clarifier", "extractor", "identifier", "preventer",
    "enhancer", "marker", "throttle", "classifier", "injector", "elicitor",
    "provider", "alert", "tool", "module", "guard", "guardrail",
}


def _normalize_stem(title: str) -> str:
    """Reduce a title to its core concept (lowercased, form-words removed)."""
    words = re.findall(r"[a-z0-9]+", (title or "").lower())
    core = [w for w in words if w not in _SUFFIX_WORDS]
    return " ".join(core).strip() or " ".join(words).strip()


class ProposalEngine:
    def __init__(self, memory: MemoryManager):
        self.memory = memory
        self.api_key = os.getenv('GROQ_API_KEY')
        self.use_ai = bool(self.api_key)
        if not self.use_ai:
            logger.warning("GROQ_API_KEY not set - using fallback")

    def generate_proposal(self) -> Proposal:
        state = self.memory.load_state()
        cycle = state.cycle_count + 1

        target, coverage = self._pick_target_category(cycle)
        banned = self._banned_concepts()
        logger.info(f"Target category: {target} | banned concepts: {len(banned)}")

        if self.use_ai:
            proposal = self._generate_ai_proposal(state, cycle, target, coverage, banned)
        else:
            proposal = self._fallback_for_category(target, cycle)

        # Collision guard: if the model walked back into a rut, force a fresh
        # proposal in the target category instead of shipping the cycle empty.
        if _normalize_stem(proposal.title) in banned:
            logger.warning(f"Proposal '{proposal.title}' is a known rut — using fallback for {target}")
            proposal = self._fallback_for_category(target, cycle)
        return proposal

    # ---- steering helpers -------------------------------------------------

    def _category_coverage(self) -> dict:
        """How many SHIPPED skills exist per charter category."""
        counts = {c: 0 for c in CHARTER_CATEGORIES}
        try:
            registry = json.loads(self.memory.skills_registry.read_text(encoding='utf-8-sig'))
        except Exception:
            registry = {}
        for meta in registry.values():
            cat = str(meta.get('category', '')).replace('SkillCategory.', '')
            if cat in counts:
                counts[cat] += 1
        return counts

    def _pick_target_category(self, cycle: int):
        """Force this cycle toward the least-covered category; rotate on ties."""
        counts = self._category_coverage()
        fewest = min(counts.values())
        candidates = [c for c in CHARTER_CATEGORIES if counts[c] == fewest]
        target = candidates[cycle % len(candidates)]
        return target, counts

    def _banned_concepts(self) -> set:
        """Concept stems already shipped OR proposed >=2x across ALL history."""
        banned = set()
        # Already shipped
        try:
            registry = json.loads(self.memory.skills_registry.read_text(encoding='utf-8-sig'))
            for meta in registry.values():
                banned.add(_normalize_stem(meta.get('title', '')))
        except Exception:
            pass
        # Repeatedly proposed (the actual rut signal)
        state = self.memory.load_state()
        stems = Counter(_normalize_stem(h.proposal.title) for h in state.history)
        for stem, n in stems.items():
            if n >= 2 and stem:
                banned.add(stem)
        banned.discard("")
        return banned

    def _rut_report(self, banned: set, top: int = 12) -> str:
        state = self.memory.load_state()
        stems = Counter(_normalize_stem(h.proposal.title) for h in state.history)
        ranked = sorted(((s, n) for s, n in stems.items() if s), key=lambda x: -x[1])
        lines = []
        for stem, n in ranked[:top]:
            tag = f" (proposed {n}x — STOP)" if n >= 2 else ""
            lines.append(f"- {stem}{tag}")
        return "\n".join(lines) if lines else "None yet"

    # ---- AI path ----------------------------------------------------------

    def _generate_ai_proposal(self, state, cycle, target, coverage, banned) -> Proposal:
        import requests

        existing_skills = self._get_skills_summary()
        top_examples = self._format_top_examples()
        rut_report = self._rut_report(banned)
        coverage_line = ", ".join(f"{c}:{n}" for c, n in coverage.items())

        prompt = f"""You are designing AI safety guardrails for SUSHILOOP, an open-source project protecting human cognition from AI overreliance.

MISSION: Every guardrail must help humans use AI as a sparring partner, not a brain replacement.

CURRENT CATEGORY COVERAGE (skills shipped per category):
{coverage_line}

>>> THIS CYCLE YOU MUST PROPOSE IN CATEGORY: {target} <
This category is under-covered. Do NOT propose in a different category. The
project is lopsided toward INPUT_VALIDATION and COGNITIVE_PROTECTION — we need
breadth, not another variation on the same theme.

EXISTING / OVERUSED CONCEPTS — these are BANNED. Do NOT propose anything that
resembles, rephrases, or is a synonym of these. Anything proposed 2+ times has
been rejected as a near-clone every time:
{rut_report}

TOP-SCORING PREVIOUS SKILLS (match or exceed their quality):
{top_examples}

DESIGN ONE NEW guardrail that is:
- In the {target} category (REQUIRED)
- A concept NOT in the banned list above (REQUIRED — be genuinely new)
- Specific and concrete (name the exact pattern it catches)
- Mission-aligned (protects cognition, not just generic safety)
- Practical (deployable as a ~50-200 line pure-Python function)

For tests_required: use ["auto"].

Respond ONLY with JSON:
{{
  "proposal_type": "NEW_SKILL",
  "category": "{target}",
  "title": "Specific Skill Name",
  "description": "What it does in 1-2 sentences",
  "rationale": "Why this matters for protecting human cognition",
  "success_criteria": ["criterion 1", "criterion 2", "criterion 3"],
  "tests_required": ["auto"],
  "estimated_complexity": 5,
  "rollback_plan": "Delete file from skills/"
}}

Cycle {cycle}. Make this skill genuinely useful and genuinely new."""

        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "temperature": 0.9, "max_tokens": 2000},
                timeout=30
            )
            if response.status_code == 200:
                content = response.json()['choices'][0]['message']['content']
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    proposal_data = json.loads(content[json_start:json_end])
                    # Hard-pin the category to the target; the model sometimes drifts.
                    proposal_data['category'] = target
                    return Proposal(**proposal_data)
            logger.warning(f"API failed: {response.status_code}")
        except Exception as e:
            logger.error(f"AI proposal failed: {e}")
        return self._fallback_for_category(target, cycle)

    # ---- fallback path ----------------------------------------------------

    def _fallback_for_category(self, target: str, cycle: int) -> Proposal:
        """Deterministic, category-targeted fallbacks. Multiple per category so
        repeated fallbacks in the same category still differ."""
        C = SkillCategory
        bank = {
            "PII_DETECTION": [
                ("Indirect Identifier Combiner", "Flags inputs where several non-PII fields (ZIP, birth year, job) combine into a re-identifiable fingerprint", "Quasi-identifiers leak identity even when no single field is PII"),
                ("Pasted Credential Catcher", "Detects API keys, tokens, and passwords accidentally pasted into prompts before they reach the model", "Users routinely paste secrets they meant to redact"),
            ],
            "OUTPUT_FILTERING": [
                ("Fabricated Citation Flagger", "Flags AI output that cites sources, DOIs, or case names in a format that is plausible but unverifiable", "Invented citations are the highest-trust hallucination"),
                ("Unhedged Medical/Legal Claim Filter", "Flags AI output giving medical or legal directives without a verify-with-a-professional caveat", "Directive high-stakes advice invites cognitive surrender"),
            ],
            "CONTENT_SAFETY": [
                ("Escalation Advice Detector", "Flags output that counsels confrontation, retaliation, or risky physical action and surfaces a cool-down beat", "High-arousal advice short-circuits deliberation"),
                ("Self-Harm Routing Guard", "Detects distress signals and ensures the path to human/professional support is surfaced, never replaced by the model", "A model must scaffold, not substitute, real support"),
            ],
            "BIAS_DETECTION": [
                ("Loaded-Framing Detector", "Flags when a prompt's wording presupposes a conclusion, nudging the model to confirm rather than examine it", "Confirmation framing turns AI into an echo, not a sparring partner"),
                ("One-Sided Question Detector", "Detects questions that ask only for support for a position and prompts a steelman of the opposing view", "Single-sided queries entrench priors"),
            ],
            "VERIFICATION_PROMPT": [
                ("Actionable-Step Verifier", "When output contains concrete steps the user will act on, injects a short 'verify these before acting' checkpoint", "A verification beat is the antidote to ask-accept-move-on"),
                ("Number-Claim Spotlighter", "Highlights specific figures in output and asks the user to confirm the source before relying on them", "Numbers feel authoritative and get accepted unchecked"),
            ],
            "RATE_LIMITING": [
                ("Deliberation-Pace Nudger", "Distinguishes rapid-fire dependent querying from deliberate use and adds a soft, overridable pause", "Compulsive querying forms dependency loops"),
                ("Re-ask Loop Breaker", "Detects the user re-asking the same thing in slightly different words and suggests stepping back to think", "Re-ask loops signal offloading, not progress"),
            ],
            "INPUT_VALIDATION": [
                ("Authority Impersonation Detector", "Detects prompts impersonating authority figures (CEO, doctor, lawyer) to bypass user judgment", "Authority framing is a primary cognitive offloading trigger"),
            ],
            "COGNITIVE_PROTECTION": [
                ("Effortless-Answer Warner", "Detects requests to fully outsource a task the user could reason through, and offers a scaffold instead of a finished answer", "Doing all the thinking replaces the user one decision at a time"),
            ],
        }
        options = bank.get(target) or bank["VERIFICATION_PROMPT"]
        title, desc, why = options[cycle % len(options)]
        return Proposal(
            proposal_type=ProposalType.NEW_SKILL,
            category=C(target),
            title=title,
            description=desc,
            rationale=why,
            success_criteria=["Catches the target pattern", "Returns reason + confidence", "Low false-positive rate"],
            tests_required=["auto"],
            estimated_complexity=5,
            rollback_plan="Delete file from skills/",
        )

    # ---- prompt context helpers ------------------------------------------

    def _get_skills_summary(self) -> str:
        try:
            registry = json.loads(self.memory.skills_registry.read_text(encoding='utf-8-sig'))
            if not registry:
                return "None yet"
            return "\n".join([f"- {name}: {meta.get('title', 'Unknown')}" for name, meta in registry.items()])
        except Exception as e:
            logger.warning(f"Could not load registry: {e}")
            return "None"

    def _format_top_examples(self) -> str:
        try:
            metadata = self.memory.load_skills_metadata()
            top = select_top_examples(metadata, k=3)
            if not top:
                return "None yet — this is among the earliest skills."
            lines = []
            for s in top:
                score = s.get('score', {}).get('total', 0)
                lines.append(f"- {s['title']} (score: {score}/50) — {s.get('summary', '')[:200].strip()}")
            return "\n".join(lines)
        except Exception as e:
            logger.warning(f"Could not load top examples: {e}")
            return "None"
