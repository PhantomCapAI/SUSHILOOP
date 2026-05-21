"""Validation layer for proposals"""
import structlog
from core.schemas import Proposal
from core.memory_manager import MemoryManager

logger = structlog.get_logger(__name__)

class CognitiveFrictionValidator:
    def __init__(self, memory: MemoryManager = None):
        self.memory = memory

    def validate(self, proposal: Proposal) -> dict:
        issues = []
        if proposal.estimated_complexity > 8 or proposal.estimated_complexity < 1:
            issues.append("Complexity must be 1-8")
        if not proposal.success_criteria:
            issues.append("Need success criteria")
        if not proposal.tests_required:
            issues.append("Need tests")
        if len(proposal.title) < 5:
            issues.append("Title too short")
        approved = len(issues) == 0
        return {'approved': approved, 'reasoning': 'OK' if approved else 'Failed', 'issues': issues}

    def check_safety_constraints(self, proposal: Proposal) -> bool:
        dangerous = ['disable', 'bypass', 'override all']
        text = f"{proposal.title} {proposal.description}".lower()
        return not any(kw in text for kw in dangerous)
