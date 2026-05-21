"""Git operations"""
import structlog
from pathlib import Path
from git import Repo, GitCommandError

logger = structlog.get_logger(__name__)

class GitManager:
    def __init__(self, repo_path: str = '.'):
        try:
            self.repo = Repo(repo_path)
            self.enabled = True
        except:
            self.repo = None
            self.enabled = False

    def create_evolution_branch(self, cycle: int):
        if not self.enabled:
            return None
        branch = f'evolution/cycle-{cycle}'
        try:
            if branch in [h.name for h in self.repo.heads]:
                self.repo.delete_head(branch, force=True)
            new_branch = self.repo.create_head(branch)
            new_branch.checkout()
            return branch
        except:
            return None

    def commit_improvement(self, proposal, skill_name: str) -> bool:
        if not self.enabled:
            return True
        try:
            self.repo.index.add(['skills/', 'tests/', 'brain/'])
            self.repo.index.commit(f"[SUSHI-LOOP] {proposal.title} - {skill_name}")
            return True
        except:
            return False

    def merge_and_push(self, branch: str) -> bool:
        if not self.enabled or not branch:
            return True
        try:
            self.repo.heads.main.checkout()
            self.repo.git.merge(branch, no_ff=True)
            self.repo.remote('origin').push('main')
            self.repo.delete_head(branch, force=True)
            return True
        except:
            return False

    def rollback(self, branch: str):
        if self.enabled:
            try:
                self.repo.heads.main.checkout()
                if branch in [h.name for h in self.repo.heads]:
                    self.repo.delete_head(branch, force=True)
            except:
                pass

    def get_status(self) -> dict:
        return {"enabled": self.enabled}
