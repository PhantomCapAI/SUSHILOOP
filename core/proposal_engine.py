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
        if self.use_ai and cycle > 1:
            return self._generate_ai_proposal(state)
        return self._generate_fallback_proposal(cycle)

    def _generate_ai_proposal(self, state) -> Proposal:
        import requests
        performance = self.memory.get_skill_performance()
        prompt = f"""Design ONE new AI safety guardrail.

Progress: {state.total_skills} skills, {performance.get('success_rate', 0):.1%} success rate

Respond ONLY with JSON:
{{
  "proposal_type": "NEW_SKILL",
  "category": "INPUT_VALIDATION",
  "title": "Skill name",
  "description": "What it does",
  "rationale": "Why needed",
  "success_criteria": ["criterion1", "criterion2"],
  "tests_required": ["test_file.py"],
  "estimated_complexity": 5,
  "rollback_plan": "How to undo"
}}"""
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "temperature": 0.7, "max_tokens": 2000},
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
        return self._generate_fallback_proposal(state.cycle_count + 1)

    def _generate_fallback_proposal(self, cycle: int) -> Proposal:
        proposals = [
            Proposal(proposal_type=ProposalType.NEW_SKILL, category=SkillCategory.INPUT_VALIDATION,
                title='Prompt Injection Detector', description='Detects jailbreak attempts',
                rationale='First defense', success_criteria=['Catches jailbreaks'],
                tests_required=['test_injection.py'], estimated_complexity=5, rollback_plan='Delete file'),
            Proposal(proposal_type=ProposalType.NEW_SKILL, category=SkillCategory.OUTPUT_FILTERING,
                title='PII Output Blocker', description='Blocks emails/SSNs in output',
                rationale='GDPR compliance', success_criteria=['Blocks PII'],
                tests_required=['test_pii.py'], estimated_complexity=6, rollback_plan='Delete file'),
            Proposal(proposal_type=ProposalType.NEW_SKILL, category=SkillCategory.RATE_LIMITING,
                title='Request Rate Limiter', description='Token bucket rate limiting',
                rationale='Prevent abuse', success_criteria=['Enforces limits'],
                tests_required=['test_rate.py'], estimated_complexity=4, rollback_plan='Remove middleware'),
        ]
        return proposals[(cycle - 1) % len(proposals)]

    def _get_skills_summary(self) -> str:
        try:
            registry = json.loads(self.memory.skills_registry.read_text())
            return "\n".join([f"- {name}" for name in registry.keys()]) if registry else "None"
        except:
            return "None"
