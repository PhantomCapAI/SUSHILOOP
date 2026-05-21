"""Git operations - simplified. Workflow handles actual commits/pushes."""
import structlog

logger = structlog.get_logger(__name__)


class GitManager:
    """No-op stub. Workflow's 'Commit and push changes' step handles git."""

    def __init__(self, repo_path: str = '.'):
        self.enabled = False

    def create_evolution_branch(self, cycle: int):
        logger.info(f"Cycle {cycle} - working on main (workflow handles git)")
        return None

    def commit_improvement(self, proposal, skill_name: str) -> bool:
        logger.info(f"Skill ready for commit: {skill_name}")
        return True

    def merge_and_push(self, branch: str) -> bool:
        return True

    def rollback(self, branch: str):
        pass

    def get_status(self) -> dict:
        return {"enabled": False, "note": "git handled by workflow"}
