"""Main SUSHI LOOP evolution engine"""
import structlog
import traceback
from pathlib import Path
from core.memory_manager import MemoryManager
from core.validator import CognitiveFrictionValidator
from core.test_runner import TestRunner
from core.proposal_engine import ProposalEngine
from core.skill_generator import SkillGenerator
from core.git_manager import GitManager
from core.skill_scorer import score_skill, diversity_score
from core.schemas import CycleResult, CycleHistory

logger = structlog.get_logger(__name__)

# Reject skills that are >70% similar to existing ones
DIVERSITY_THRESHOLD = 0.30


class SushiLoop:
    def __init__(self):
        self.memory = MemoryManager()
        self.validator = CognitiveFrictionValidator(self.memory)
        self.git = GitManager()
        self.proposal_engine = ProposalEngine(self.memory)
        self.skill_generator = SkillGenerator()
        self.test_runner = TestRunner()

    def run_cycle(self) -> CycleResult:
        state = self.memory.load_state()
        cycle = state.cycle_count + 1
        logger.info(f'🍣 SUSHI LOOP Cycle {cycle} started')

        try:
            proposal = self.proposal_engine.generate_proposal()
            history = CycleHistory(cycle_number=cycle, proposal=proposal, result=CycleResult.ERROR)
            logger.info(f"Proposal: {proposal.title}")

            validation = self.validator.validate(proposal)
            if not validation['approved']:
                logger.warning(f"Rejected: {validation['reasoning']}")
                history.result = CycleResult.REJECTED
                self.memory.record_cycle(history)
                return CycleResult.REJECTED

            if not self.validator.check_safety_constraints(proposal):
                logger.error("Safety violation")
                history.result = CycleResult.REJECTED
                self.memory.record_cycle(history)
                return CycleResult.REJECTED

            branch = self.git.create_evolution_branch(cycle)
            skill_name = self.skill_generator.generate(proposal)
            history.skill_generated = skill_name

            # Load generated code for scoring + diversity
            skill_path = Path('skills') / f"{skill_name}.py"
            code = skill_path.read_text(encoding='utf-8') if skill_path.exists() else ""

            # Diversity check — reject near-clones
            existing_metadata = self.memory.load_skills_metadata()
            diversity = diversity_score(code, list(existing_metadata.values()))
            logger.info(f"Diversity score: {diversity}")
            if diversity < DIVERSITY_THRESHOLD and existing_metadata:
                logger.warning(f"Rejected as clone (diversity {diversity} < {DIVERSITY_THRESHOLD})")
                if skill_path.exists():
                    skill_path.unlink()
                history.result = CycleResult.REJECTED
                self.memory.record_cycle(history)
                return CycleResult.REJECTED

            test_results = self.test_runner.run_tests(proposal, skill_name)
            history.test_results = test_results

            if self.test_runner.all_tests_passed(test_results):
                logger.info("✅ Tests passed")

                # Score the skill across 5 dimensions
                score = score_skill(skill_name, code, test_passed=True)
                logger.info(f"Skill score: {score['total']}/50 — {score}")

                self.memory.register_skill(skill_name, {
                    "title": proposal.title,
                    "category": proposal.category,
                    "cycle": cycle
                })
                self.memory.register_skill_metadata(
                    skill_name=skill_name,
                    code=code,
                    proposal_title=proposal.title,
                    score=score,
                    diversity=diversity,
                    failure_modes=[]
                )

                self.git.commit_improvement(proposal, skill_name)
                self.git.merge_and_push(branch)
                history.result = CycleResult.SUCCESS
                self.memory.record_cycle(history)
                return CycleResult.SUCCESS
            else:
                logger.error("Tests failed")
                # Log failure mode for future avoidance
                failure_modes = [r.message[:100] for r in test_results if not r.passed]
                score = score_skill(skill_name, code, test_passed=False)
                self.memory.register_skill_metadata(
                    skill_name=skill_name,
                    code=code,
                    proposal_title=proposal.title,
                    score=score,
                    diversity=diversity,
                    failure_modes=failure_modes
                )
                self.git.rollback(branch)
                history.result = CycleResult.TEST_FAILED
                self.memory.record_cycle(history)
                return CycleResult.TEST_FAILED

        except Exception as e:
            logger.error(f"Error: {e}")
            logger.error(traceback.format_exc())
            return CycleResult.ERROR

    def get_status(self) -> dict:
        state = self.memory.load_state()
        perf = self.memory.get_skill_performance()
        return {
            "cycle": state.cycle_count,
            "total_skills": state.total_skills,
            "performance": perf
        }
