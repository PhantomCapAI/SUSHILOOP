"""AI-powered proposal generation using Groq"""
import os
import json
import structlog
from core.schemas import Proposal, ProposalType, SkillCategory
from core.memory_manager import MemoryManager

logger = structlog.get_logger(__name__)

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
        if self.use_ai:
            return self._generate_ai_proposal(state, cycle)
        return self._generate_fallback_proposal(cycle)

    def _generate_ai_proposal(self, state, cycle: int) -> Proposal:
        import requests
        existing_skills = self._get_skills_summary()
        recent_failures = self._get_recent_failures_summary()

        prompt = f"""You are designing AI safety guardrails for SUSHILOOP, an open-source project protecting human cognition from AI overreliance.

MISSION: Every guardrail must help humans use AI as a sparring partner, not a brain replacement. Skills must detect manipulation, surface uncertainty, protect vulnerable users, or counter cognitive offloading patterns.

EXISTING SKILLS (do NOT duplicate):
{existing_skills}

RECENT FAILED PROPOSALS (avoid these patterns):
{recent_failures}

DESIGN ONE NEW guardrail that is:
- Novel (not in existing skills list)
- Practical (deployable as a pure Python function in ~50-150 lines)
- Mission-aligned (protects cognition, not just safety)
- Specific (NOT "general jailbreak detector" — be precise, e.g. "Authority impersonation detector" or "False urgency framing catcher")

Prioritize categories: COGNITIVE_PROTECTION, VERIFICATION_PROMPT, BIAS_DETECTION, INPUT_VALIDATION, OUTPUT_FILTERING.

Respond ONLY with JSON:
{{
  "proposal_type": "NEW_SKILL",
  "category": "INPUT_VALIDATION",
  "title": "Specific Skill Name",
  "description": "What it does in 1-2 sentences",
  "rationale": "Why this specific guardrail matters for protecting human cognition",
  "success_criteria": ["measurable criterion 1", "criterion 2", "criterion 3"],
  "tests_required": ["test_skill_name.py"],
  "estimated_complexity": 5,
  "rollback_plan": "Delete file from skills/"
}}

Be creative. Cycle {cycle}. Make this skill genuinely useful, not a copy of what's been done."""

        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "temperature": 0.85, "max_tokens": 2000},
                timeout=30
            )
            if response.status_code == 200:
                content = response.json()['choices'][0]['message']['content']
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    proposal_data = json.loads(content[json_start:json_end])
                    return Proposal(**proposal_data)
            logger.warning(f"API failed: {response.status_code}")
        except Exception as e:
            logger.error(f"AI proposal failed: {e}")
        return self._generate_fallback_proposal(cycle)

    def _generate_fallback_proposal(self, cycle: int) -> Proposal:
        proposals = [
            Proposal(proposal_type=ProposalType.NEW_SKILL, category=SkillCategory.INPUT_VALIDATION,
                title='Authority Impersonation Detector', description='Detects when prompts impersonate authority figures (CEO, doctor, lawyer) to bypass user judgment',
                rationale='Authority framing is a primary cognitive offloading trigger - users defer to perceived expertise',
                success_criteria=['Catches role impersonation', 'Returns confidence score', 'Logs reason'],
                tests_required=['test_authority.py'], estimated_complexity=5, rollback_plan='Delete file'),
            Proposal(proposal_type=ProposalType.NEW_SKILL, category=SkillCategory.OUTPUT_FILTERING,
                title='Hallucination Confidence Marker', description='Flags AI outputs that present uncertain claims as definitive facts',
                rationale='Users accept AI outputs without verifying when confidence appears high',
                success_criteria=['Detects hedge-free assertions', 'Flags numeric claims without sources', 'Returns confidence'],
                tests_required=['test_hallucination.py'], estimated_complexity=6, rollback_plan='Delete file'),
            Proposal(proposal_type=ProposalType.NEW_SKILL, category=SkillCategory.INPUT_VALIDATION,
                title='False Urgency Framing Catcher', description='Detects manufactured time pressure in prompts that pushes users to skip verification',
                rationale='Urgency framing bypasses critical thinking - core cognitive offloading vector',
                success_criteria=['Catches time-pressure language', 'Identifies artificial scarcity', 'Confidence scored'],
                tests_required=['test_urgency.py'], estimated_complexity=4, rollback_plan='Delete file'),
            Proposal(proposal_type=ProposalType.NEW_SKILL, category=SkillCategory.PII_DETECTION,
                title='Granular PII Classifier', description='Distinguishes between PII categories (financial, medical, identity) with category-specific blocking',
                rationale='One-size-fits-all PII blocking is too coarse - different categories need different responses',
                success_criteria=['Detects 6+ PII categories', 'Returns category and confidence', 'Configurable thresholds'],
                tests_required=['test_pii_granular.py'], estimated_complexity=7, rollback_plan='Delete file'),
            Proposal(proposal_type=ProposalType.NEW_SKILL, category=SkillCategory.CONTENT_SAFETY,
                title='Verification Prompt Injector', description='Adds verify-before-accept prompts when AI output contains actionable advice',
                rationale='Counters cognitive surrender by forcing a verification beat',
                success_criteria=['Detects actionable advice', 'Injects verification prompt', 'Configurable triggers'],
                tests_required=['test_verify.py'], estimated_complexity=5, rollback_plan='Delete file'),
            Proposal(proposal_type=ProposalType.NEW_SKILL, category=SkillCategory.RATE_LIMITING,
                title='Compulsive Use Throttle', description='Detects and throttles patterns of compulsive/anxious AI use vs deliberate use',
                rationale='Protects users from forming dependency loops - cognitive health',
                success_criteria=['Distinguishes query patterns', 'Soft throttling with explanation', 'User-overridable'],
                tests_required=['test_throttle.py'], estimated_complexity=6, rollback_plan='Delete file'),
        ]
        return proposals[(cycle - 1) % len(proposals)]

    def _get_skills_summary(self) -> str:
        try:
            registry = json.loads(self.memory.skills_registry.read_text(encoding='utf-8-sig'))
            if not registry:
                return "None yet - this is an early skill"
            return "\n".join([f"- {name}: {meta.get('title', 'Unknown')}" for name, meta in registry.items()])
        except Exception as e:
            logger.warning(f"Could not load registry: {e}")
            return "None"

    def _get_recent_failures_summary(self) -> str:
        try:
            failures = self.memory.get_recent_failures(limit=3)
            if not failures:
                return "None"
            return "\n".join([f"- {f.proposal.title} ({f.result})" for f in failures])
        except Exception:
            return "None"
