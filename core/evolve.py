"""Main SUSHI LOOP evolution engine"""
import structlog
import traceback
from core.memory_manager import MemoryManager
from core.validator import CognitiveFrictionValidator
from core.test_runner import TestRunner
from core.proposal_engine import ProposalEngine
from core.skill_generator import SkillGenerator
from core.git_manager import GitManager
from core.schemas import CycleResult, CycleHistory

logger = structlog.get_logger(__name__)

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
        
        history = CycleHistory(cycle_number=cycle, proposal=None, result=CycleResult.ERROR)
        
        try:
            proposal = self.proposal_engine.generate_proposal()
            history.proposal = proposal
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
            
            test_results = self.test_runner.run_tests(proposal, skill_name)
            history.test_results = test_results
            
            if self.test_runner.all_tests_passed(test_results):
                logger.info("✅ Tests passed")
                self.memory.register_skill(skill_name, {
                    "title": proposal.title,
                    "category": proposal.category,
                    "cycle": cycle
                })
                self.git.commit_improvement(proposal, skill_name)
                self.git.merge_and_push(branch)
                history.result = CycleResult.SUCCESS
                self.memory.record_cycle(history)
                return CycleResult.SUCCESS
            else:
                logger.error("Tests failed")
                self.git.rollback(branch)
                history.result = CycleResult.TEST_FAILED
                self.memory.record_cycle(history)
                return CycleResult.TEST_FAILED
                
        except Exception as e:
            logger.error(f"Error: {e}")
            if history.proposal:
                history.result = CycleResult.ERROR
                history.error_message = str(e)[:500]
                self.memory.record_cycle(history)
            return CycleResult.ERROR

    def get_status(self) -> dict:
        state = self.memory.load_state()
        perf = self.memory.get_skill_performance()
        return {
            "cycle": state.cycle_count,
            "total_skills": state.total_skills,
            "performance": perf
        }
