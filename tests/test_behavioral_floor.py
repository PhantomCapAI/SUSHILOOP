"""
Offline unit tests for the behavioral floor gate (core/evolve.py).

The floor rejects skills that pass tests but don't actually discriminate —
"safe but shallow" theater that violates Charter principle 1 in spirit.

These tests exercise the gate's decision predicate directly with synthetic
score dicts (no GROQ key, no live calls) AND against the real behavioral
scores of skills currently in the repo, so the thresholds stay calibrated
to actual scorer output (which emits discrimination in {0,2,5,7,10}).
"""
from core.evolve import MIN_DISCRIMINATION, MIN_BEHAVIORAL_TOTAL


def _rejected(score: dict) -> bool:
    """Mirror of the gate predicate in evolve.run_cycle.

    Kept in lockstep with the production condition:
        if discrimination < MIN_DISCRIMINATION or behavioral_total < MIN_BEHAVIORAL_TOTAL
    """
    behavioral = score.get('behavioral', {})
    discrimination = behavioral.get('discrimination', 0)
    behavioral_total = behavioral.get('behavioral_total', 0)
    return discrimination < MIN_DISCRIMINATION or behavioral_total < MIN_BEHAVIORAL_TOTAL


def _score(discrimination, behavioral_total, **extra):
    b = {"discrimination": discrimination, "behavioral_total": behavioral_total}
    b.update(extra)
    return {"total": behavioral_total, "behavioral": b}


# ── Threshold sanity ────────────────────────────────────────────────────────

def test_thresholds_are_sane():
    assert 0 < MIN_DISCRIMINATION <= 10
    assert 0 < MIN_BEHAVIORAL_TOTAL <= 30


# ── Shallow skills get rejected ───────────────────────────────────────────────

def test_theater_discrimination_2_rejected():
    # The exact profile of anthropomorphism_detector / overreliance_detector.
    assert _rejected(_score(discrimination=2, behavioral_total=22)) is True


def test_discrimination_0_rejected():
    assert _rejected(_score(discrimination=0, behavioral_total=20)) is True


def test_low_total_rejected_even_if_discrimination_ok():
    # Discrimination clears, but overall behavior collapsed (e.g. broke robustness).
    assert _rejected(_score(discrimination=5, behavioral_total=10)) is True


# ── Genuine skills pass ───────────────────────────────────────────────────────

def test_strong_skill_passes():
    # Profile of prompt_injection_detector.
    assert _rejected(_score(discrimination=10, behavioral_total=30)) is False


def test_borderline_real_skill_passes():
    # Profile of input_premise_validator: discrimination exactly at floor.
    assert _rejected(_score(discrimination=5, behavioral_total=25)) is False


# ── Boundary conditions (the scorer emits only 0/2/5/7/10 for discrimination) ──

def test_discrimination_exactly_at_floor_passes():
    assert _rejected(_score(discrimination=MIN_DISCRIMINATION,
                            behavioral_total=MIN_BEHAVIORAL_TOTAL)) is False


def test_discrimination_just_below_floor_rejected():
    # 2 is the next value below 5 the scorer can emit.
    assert _rejected(_score(discrimination=2, behavioral_total=MIN_BEHAVIORAL_TOTAL)) is True


def test_total_exactly_at_floor_passes():
    assert _rejected(_score(discrimination=10, behavioral_total=MIN_BEHAVIORAL_TOTAL)) is False


def test_total_just_below_floor_rejected():
    assert _rejected(_score(discrimination=10, behavioral_total=MIN_BEHAVIORAL_TOTAL - 1)) is True


# ── Defensive: missing/error behavioral block ─────────────────────────────────

def test_missing_behavioral_block_rejected():
    # If behavioral scoring produced nothing, defaults are 0 → reject (fail safe:
    # a skill we couldn't behaviorally verify must not ship as SUCCESS).
    assert _rejected({"total": 0}) is True


def test_load_error_behavioral_rejected():
    # behavioral_score returns total/discrimination 0 plus an error string when
    # the skill file won't import; that must reject.
    assert _rejected(_score(discrimination=0, behavioral_total=0,
                            error="no callable foo")) is True


# ── Calibration against REAL scorer output (keeps thresholds honest) ──────────

def test_real_known_shallow_skills_would_be_rejected():
    from core.skill_scorer import behavioral_score
    for name in ("anthropomorphism_detector", "overreliance_detector"):
        b = behavioral_score(name)
        score = {"total": b["behavioral_total"], "behavioral": b}
        assert _rejected(score) is True, f"{name} should fail the floor: {b}"


def test_real_strong_skill_would_pass():
    from core.skill_scorer import behavioral_score
    b = behavioral_score("prompt_injection_detector")
    score = {"total": b["behavioral_total"], "behavioral": b}
    assert _rejected(score) is False, f"prompt_injection_detector should pass: {b}"
