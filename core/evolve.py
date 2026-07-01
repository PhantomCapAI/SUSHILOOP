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
from core.charter_auditor import audit_skill
from core.schemas import CycleResult, CycleHistory

logger = structlog.get_logger(__name__)

# Reject skills that are >70% similar to existing ones
DIVERSITY_THRESHOLD = 0.30

# Behavioral floor — reject skills that pass tests but don't actually DO their job.
# discrimination (0-10) measures whether the skill distinguishes input it should
# flag from input it shouldn't; 2 = keyword-matching theater, 5 = real signal.
# A guardrail that doesn't discriminate isn't protecting cognition (Charter
# principle 1), it's theater — so we gate on it the same as a charter violation.
# CONSERVATIVE start per handoff: too high stalls the loop, too low ships theater.
# Tune empirically by watching live cycles; raise only if shallow skills slip past.
MIN_DISCRIMINATION = 5      # out of 10 (scorer emits 0/2/5/7/10)
MIN_BEHAVIORAL_TOTAL = 18   # out of 30

# Best-of-N generation. A single free-tier 70B generation clears the quality
# gates only ~1-in-8 times, so a single-shot cycle rejects most of the time even
# though the gates are correct. Generating a few candidates per cycle and keeping
# the best one that passes — with the rejection reason fed back between attempts —
# raises the per-cycle ship rate to ~1-(1-p)^N WITHOUT touching the gates, so
# quality is unchanged (a shallow skill still cannot pass). Bounded to stay well
# within the free tier over a 6-hourly schedule.
GENERATION_ATTEMPTS = 4


class SushiLoop:
    def __init__(self):
        self.memory = MemoryManager()
        self.validator = CognitiveFrictionValidator(self.memory)
        self.git = GitManager()
        self.proposal_engine = ProposalEngine(self.memory)
        self.skill_generator = SkillGenerator()
        self.test_runner = TestRunner()

    def _generate_best_candidate(self, proposal, existing_metadata):
        """Generate up to GENERATION_ATTEMPTS candidates for this proposal and
        return the name of the best one, with its code left on disk.

        Stops at the first candidate that clears diversity + the behavioral floor;
        otherwise returns the highest-scoring attempt so the existing downstream
        gates still make the real ship/reject decision on a genuine candidate.
        The concrete rejection reason is fed back between attempts so the model
        fixes THAT instead of resampling the same failure. This changes only
        WHICH candidate reaches the gates — never the gates themselves — so the
        quality bar is identical; we just stop wasting cycles on the first
        unlucky draw."""
        existing = list(existing_metadata.values())
        best = None            # (rank_tuple, skill_name, code)
        feedback = None
        for attempt in range(1, GENERATION_ATTEMPTS + 1):
            skill_name = self.skill_generator.generate(proposal, feedback=feedback)
            if not skill_name or skill_name.startswith('unnamed_skill_'):
                continue
            path = Path('skills') / f"{skill_name}.py"
            code = path.read_text(encoding='utf-8') if path.exists() else ""
            if not code:
                continue
            div = diversity_score(code, existing)
            beh = score_skill(skill_name, code, test_passed=True).get('behavioral', {})
            disc = beh.get('discrimination', 0)
            btot = beh.get('behavioral_total', 0)
            div_ok = (div >= DIVERSITY_THRESHOLD) or not existing
            passes = div_ok and disc >= MIN_DISCRIMINATION and btot >= MIN_BEHAVIORAL_TOTAL
            rank = (passes, div_ok, disc, btot, div)
            logger.info(f"Candidate {attempt}/{GENERATION_ATTEMPTS}: {skill_name} "
                        f"div={div:.2f} discrim={disc} behavioral={btot} pass={passes}")
            if best is None or rank > best[0]:
                best = (rank, skill_name, code)
            if passes:
                break
            reasons = []
            if not div_ok:
                reasons.append(f"too similar to an existing skill (diversity {div:.2f} < {DIVERSITY_THRESHOLD}) — use a genuinely different detection approach and signals")
            if disc < MIN_DISCRIMINATION:
                reasons.append(f"it did not discriminate (score {disc}/10) — make `blocked` clearly True on strong positives and False on benign input, and widen the confidence range")
            if btot < MIN_BEHAVIORAL_TOTAL:
                reasons.append(f"weak behavioral score ({btot}/30) — vary confidence with signal strength and handle empty/edge input without raising")
            feedback = "; ".join(reasons) or "make the detection deeper and more discriminating"
        if best is None:
            return None
        # Later attempts overwrite the same path, so re-materialize the winner.
        best_name, best_code = best[1], best[2]
        (Path('skills') / f"{best_name}.py").write_text(best_code, encoding='utf-8')
        return best_name

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
            existing_metadata = self.memory.load_skills_metadata()
            skill_name = self._generate_best_candidate(proposal, existing_metadata)
            history.skill_generated = skill_name

            # Name guard: never ship empty or fallback-named skills (the bug that
            # produced skills/.py and tests/test_.py).
            if not skill_name or skill_name.startswith('unnamed_skill_'):
                logger.error(f"Refusing to ship invalid skill name: {skill_name!r}")
                skill_path_bad = Path('skills') / f"{skill_name}.py"
                if skill_path_bad.exists():
                    skill_path_bad.unlink()
                self.git.rollback(branch)
                history.result = CycleResult.REJECTED
                self.memory.record_cycle(history)
                return CycleResult.REJECTED

            # Load generated code for scoring + diversity
            skill_path = Path('skills') / f"{skill_name}.py"
            code = skill_path.read_text(encoding='utf-8') if skill_path.exists() else ""

            # Diversity check — reject near-clones (existing_metadata loaded above)
            diversity = diversity_score(code, list(existing_metadata.values()))
            logger.info(f"Diversity score: {diversity}")
            if diversity < DIVERSITY_THRESHOLD and existing_metadata:
                logger.warning(f"Rejected as clone (diversity {diversity} < {DIVERSITY_THRESHOLD})")
                if skill_path.exists():
                    skill_path.unlink()
                history.result = CycleResult.REJECTED
                self.memory.record_cycle(history)
                return CycleResult.REJECTED

            # Charter step 4 — self-audit the GENERATED CODE against CHARTER.md.
            # Fails closed on an explicit VIOLATES verdict; fails open on infra error.
            audit = audit_skill(proposal, skill_name, code)
            if not audit['approved']:
                logger.warning(f"Charter audit rejected: {audit['reasoning']}")
                if skill_path.exists():
                    skill_path.unlink()
                # Log as a failure mode so the proposal engine learns to avoid it.
                self.memory.register_skill_metadata(
                    skill_name=skill_name,
                    code=code,
                    proposal_title=proposal.title,
                    score=score_skill(skill_name, code, test_passed=False),
                    diversity=diversity,
                    failure_modes=[f"charter:{audit['reasoning']}"],
                )
                history.result = CycleResult.REJECTED
                self.memory.record_cycle(history)
                return CycleResult.REJECTED

            test_results = self.test_runner.run_tests(proposal, skill_name)
            history.test_results = test_results

            if self.test_runner.all_tests_passed(test_results):
                logger.info("✅ Tests passed")

                # Score the skill across 5 dimensions
                score = score_skill(skill_name, code, test_passed=True)
                logger.info(f"Skill score: {score['total']}/80 "
                            f"(static {score.get('static_total')}/50, "
                            f"behavioral {score.get('behavioral', {}).get('behavioral_total')}/30)")

                # Behavioral floor — a skill can pass every test and still be
                # theater: returns valid verdicts but barely distinguishes input
                # it should flag from input it shouldn't. That's a Charter
                # principle 1 violation in spirit (it doesn't protect cognition,
                # it performs protecting it). Gate on it like a charter violation:
                # don't ship, log the reason as a failure mode so the proposal
                # engine learns, delete the file so the workflow can't commit it.
                behavioral = score.get('behavioral', {})
                discrimination = behavioral.get('discrimination', 0)
                behavioral_total = behavioral.get('behavioral_total', 0)
                behavioral_error = behavioral.get('error')
                if discrimination < MIN_DISCRIMINATION or behavioral_total < MIN_BEHAVIORAL_TOTAL:
                    detail = f" (load/run error: {behavioral_error})" if behavioral_error else ""
                    logger.warning(
                        f"Behavioral floor: {skill_name} too shallow "
                        f"(discrim={discrimination}<{MIN_DISCRIMINATION} or "
                        f"total={behavioral_total}<{MIN_BEHAVIORAL_TOTAL}){detail} — rejecting")
                    if skill_path.exists():
                        skill_path.unlink()
                    # Log as a failure mode so the proposal engine learns to avoid it.
                    self.memory.register_skill_metadata(
                        skill_name=skill_name,
                        code=code,
                        proposal_title=proposal.title,
                        score=score,
                        diversity=diversity,
                        failure_modes=[f"shallow:discrimination={discrimination},behavioral_total={behavioral_total}"],
                    )
                    self.git.rollback(branch)
                    history.result = CycleResult.REJECTED
                    self.memory.record_cycle(history)
                    return CycleResult.REJECTED

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
