"""Skill scoring + diversity checks. Drives retrieval and clone prevention."""
import hashlib
import re
from pathlib import Path
from typing import List, Dict, Any


def hash_skill_code(code: str) -> str:
    """Stable hash of skill code, ignoring whitespace + comments."""
    stripped = re.sub(r'#.*', '', code)
    stripped = re.sub(r'\s+', '', stripped)
    return hashlib.sha256(stripped.encode()).hexdigest()[:16]


def score_skill(skill_name: str, code: str, test_passed: bool) -> Dict[str, Any]:
    """
    Score a freshly generated skill across 5 dimensions, 0-10 each.
    Total 0-50. Higher = better.
    """
    scores = {
        "tests_pass": 10 if test_passed else 0,
        "complexity": _score_complexity(code),
        "structure": _score_structure(code),
        "documentation": _score_documentation(code),
        "strategies": _score_strategy_count(code),
    }
    scores["total"] = sum(scores.values())
    return scores


def _score_complexity(code: str) -> int:
    """Reward 50-300 lines. Penalize trivial or bloated."""
    lines = len([l for l in code.splitlines() if l.strip() and not l.strip().startswith('#')])
    if lines < 30:
        return 2
    if lines < 50:
        return 5
    if lines <= 300:
        return 10
    if lines <= 500:
        return 7
    return 4


def _score_structure(code: str) -> int:
    """Reward proper return shape and type hints."""
    score = 0
    if 'def ' in code and '-> dict' in code.lower() or '-> Dict' in code:
        score += 3
    if '"blocked"' in code and '"confidence"' in code:
        score += 3
    if '"reason"' in code:
        score += 2
    if 'if __name__' in code:
        score += 2
    return min(score, 10)


def _score_documentation(code: str) -> int:
    """Reward docstrings."""
    score = 0
    if code.count('"""') >= 2:
        score += 4
    if 'Args:' in code or 'Returns:' in code or 'Mission' in code:
        score += 3
    if 'SUSHILOOP' in code or 'mission' in code.lower():
        score += 3
    return min(score, 10)


def _score_strategy_count(code: str) -> int:
    """Reward multi-strategy detection over single-pattern."""
    indicators = [
        code.lower().count('strategy'),
        code.count('pattern'),
        code.count('re.search') + code.count('re.match'),
        1 if 'weighted' in code.lower() else 0,
        1 if 'confidence' in code.lower() else 0,
    ]
    total = sum(indicators)
    if total >= 8:
        return 10
    if total >= 5:
        return 7
    if total >= 3:
        return 4
    return 1


def diversity_score(new_code: str, existing_skills: List[Dict[str, Any]]) -> float:
    """
    Returns 0.0-1.0. Higher = more diverse from existing skills.
    Compares against title keywords + code hash similarity.
    Used to reject near-clones.
    """
    if not existing_skills:
        return 1.0

    new_hash = hash_skill_code(new_code)
    new_lower = new_code.lower()

    similarities = []
    for skill in existing_skills:
        if skill.get('code_hash') == new_hash:
            return 0.0
        existing_summary = (skill.get('summary') or '').lower()
        if not existing_summary:
            continue
        existing_words = set(re.findall(r'\w+', existing_summary))
        new_words = set(re.findall(r'\w+', new_lower[:500]))
        if not existing_words or not new_words:
            continue
        overlap = len(existing_words & new_words) / max(len(existing_words | new_words), 1)
        similarities.append(overlap)

    if not similarities:
        return 1.0
    max_sim = max(similarities)
    return round(1.0 - max_sim, 3)


def select_top_examples(metadata: Dict[str, Dict], k: int = 3) -> List[Dict]:
    """
    Pick top k skills by total score for retrieval injection.
    Falls back to most recent if fewer than k exist.
    """
    if not metadata:
        return []
    items = list(metadata.values())
    items.sort(key=lambda s: s.get('score', {}).get('total', 0), reverse=True)
    return items[:k]
