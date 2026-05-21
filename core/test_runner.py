"""Automated testing for generated skills"""
import structlog
import subprocess
import time
from pathlib import Path
from core.schemas import Proposal, TestResult

logger = structlog.get_logger(__name__)

class TestRunner:
    def __init__(self):
        self.tests_dir = Path('tests')
        self.tests_dir.mkdir(exist_ok=True)

    def run_tests(self, proposal: Proposal, skill_name: str) -> list:
        results = []
        test_file = self._ensure_test_file(proposal, skill_name)
        results.append(self._run_smoke_test(skill_name))
        return results

    def _ensure_test_file(self, proposal: Proposal, skill_name: str) -> Path:
        test_path = self.tests_dir / f"test_{skill_name}.py"
        if not test_path.exists():
            test_code = f'''"""Tests for {proposal.title}"""
import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'skills'))

from {skill_name} import {skill_name}

def test_basic():
    result = {skill_name}("test")
    assert isinstance(result, dict)
    assert 'blocked' in result
'''
            test_path.write_text(test_code, encoding='utf-8')
        return test_path

    def _run_smoke_test(self, skill_name: str) -> TestResult:
        start = time.time()
        test_code = f'''
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'skills'))
import {skill_name}
result = {skill_name}.{skill_name}("test")
assert isinstance(result, dict)
print("PASS")
'''
        try:
            result = subprocess.run(['python', '-c', test_code], capture_output=True, text=True, timeout=10, cwd=Path.cwd())
            passed = 'PASS' in result.stdout
            return TestResult(passed=passed, test_name=f"smoke:{skill_name}", message=result.stdout[:200], duration_seconds=time.time()-start)
        except Exception as e:
            return TestResult(passed=False, test_name=f"smoke:{skill_name}", message=str(e)[:200], duration_seconds=time.time()-start)

    def all_tests_passed(self, results: list) -> bool:
        return all(r.passed for r in results)
