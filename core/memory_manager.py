"""Memory and state management for SUSHI LOOP"""
import structlog
import json
from pathlib import Path
from datetime import datetime
from typing import Optional
from core.schemas import LoopState, CycleHistory

logger = structlog.get_logger(__name__)

class MemoryManager:
    def __init__(self, brain_dir: str = 'brain'):
        self.brain_dir = Path(brain_dir)
        self.brain_dir.mkdir(exist_ok=True)
        self.state_file = self.brain_dir / 'state.json'
        self.memory_file = self.brain_dir / 'memory.md'
        self.skills_registry = self.brain_dir / 'skills_registry.json'
        self.skills_metadata = self.brain_dir / 'skills_metadata.json'
        self._initialize_files()

    def _initialize_files(self):
        if not self.state_file.exists():
            self.save_state(LoopState())
        if not self.memory_file.exists():
            self.memory_file.write_text(f"# SUSHI LOOP Memory\nInitialized: {datetime.now().isoformat()}\n\n")
        if not self.skills_registry.exists():
            self.skills_registry.write_text(json.dumps({}, indent=2))
        if not self.skills_metadata.exists():
            self.skills_metadata.write_text(json.dumps({}, indent=2))

    def load_state(self) -> LoopState:
        try:
            data = json.loads(self.state_file.read_text(encoding='utf-8-sig'))
            return LoopState(**data)
        except Exception as e:
            logger.warning(f"Failed to load state: {e}")
            return LoopState()

    def save_state(self, state: LoopState):
        self.state_file.write_text(state.model_dump_json(indent=2))
        logger.info(f"State saved - Cycle: {state.cycle_count}")

    def append_memory(self, text: str, metadata: dict = None):
        ts = datetime.now().isoformat()
        with open(self.memory_file, 'a', encoding='utf-8') as f:
            f.write(f"\n## [{ts}] {text}\n")
            if metadata:
                f.write(f"```json\n{json.dumps(metadata, indent=2)}\n```\n")
            f.write("---\n")

    def record_cycle(self, history: CycleHistory):
        state = self.load_state()
        state.cycle_count += 1
        state.last_run = history.timestamp
        if history.result == "SUCCESS":
            state.success_count += 1
            if history.skill_generated:
                state.total_skills += 1
        elif history.result in ["TEST_FAILED", "ERROR"]:
            state.failure_count += 1
        state.history.append(history)
        if len(state.history) > 100:
            state.history = state.history[-100:]
        self.save_state(state)
        self.append_memory(f"Cycle {state.cycle_count}: {history.result}", {
            "proposal": history.proposal.title,
            "skill": history.skill_generated
        })

    def register_skill(self, skill_name: str, metadata: dict):
        registry = json.loads(self.skills_registry.read_text(encoding='utf-8-sig'))
        registry[skill_name] = {**metadata, "created_at": datetime.now().isoformat()}
        self.skills_registry.write_text(json.dumps(registry, indent=2))
        logger.info(f"Skill registered: {skill_name}")

    def register_skill_metadata(self, skill_name: str, code: str, proposal_title: str,
                                 score: dict, diversity: float, failure_modes: list = None):
        """Rich metadata for retrieval + evolution."""
        from core.skill_scorer import hash_skill_code
        try:
            metadata = json.loads(self.skills_metadata.read_text(encoding='utf-8-sig'))
        except Exception:
            metadata = {}
        metadata[skill_name] = {
            "name": skill_name,
            "title": proposal_title,
            "code_hash": hash_skill_code(code),
            "summary": code[:600],
            "score": score,
            "diversity": diversity,
            "failure_modes": failure_modes or [],
            "timestamp": datetime.now().isoformat(),
        }
        self.skills_metadata.write_text(json.dumps(metadata, indent=2))
        logger.info(f"Metadata logged: {skill_name} (score={score.get('total')}, diversity={diversity})")

    def load_skills_metadata(self) -> dict:
        try:
            return json.loads(self.skills_metadata.read_text(encoding='utf-8-sig'))
        except Exception as e:
            logger.warning(f"Could not load skills_metadata: {e}")
            return {}

    def get_recent_failures(self, limit: int = 5) -> list:
        state = self.load_state()
        failures = [h for h in state.history if h.result in ["TEST_FAILED", "REJECTED"]]
        return failures[-limit:]

    def get_skill_performance(self) -> dict:
        state = self.load_state()
        total = state.cycle_count
        if total == 0:
            return {"success_rate": 0.0, "total_cycles": 0}
        return {
            "success_rate": state.success_count / total,
            "total_cycles": total,
            "total_skills": state.total_skills
        }
