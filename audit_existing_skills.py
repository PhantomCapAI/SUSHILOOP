"""Retroactively audit all shipped skills against the Charter + behavioral bar.

The Charter auditor (core/charter_auditor.py) only gates FUTURE skills. The 12
skills already in skills/ were never checked. This script checks them.

Run locally with GROQ_API_KEY set:
    python audit_existing_skills.py            # report only
    python audit_existing_skills.py --quarantine   # move failures aside

Quarantine (not delete) is deliberate: a failing skill is moved to
skills/quarantine/ so it stops shipping but stays available for you to read the
verdict and decide. Auto-deleting or auto-regenerating would remove the human
review step on exactly the skills that most need it.

Failure = EITHER an explicit Charter VIOLATES verdict OR a behavioral score
below MIN_BEHAVIORAL (a skill that doesn't discriminate isn't protecting anyone).
"""
import sys
import shutil
from pathlib import Path

from core.skill_scorer import behavioral_score
from core.charter_auditor import audit_skill
from core.schemas import Proposal, ProposalType, SkillCategory

MIN_BEHAVIORAL = 12  # out of 30; below this the skill barely works
QUARANTINE = Path("skills/quarantine")


def _proposal_for(name: str, code: str) -> Proposal:
    # Minimal proposal so the auditor has title/description context.
    doc = ""
    for line in code.splitlines():
        s = line.strip().strip('"').strip()
        if s and not s.startswith(("import", "from", "#")):
            doc = s
            break
    return Proposal(
        proposal_type=ProposalType.NEW_SKILL,
        category=SkillCategory.INPUT_VALIDATION,
        title=name.replace("_", " ").title(),
        description=doc[:200] or name,
        rationale="Retroactive audit of an already-shipped skill.",
        success_criteria=["returns valid verdict", "discriminates inputs"],
        tests_required=["auto"], estimated_complexity=5,
        rollback_plan="Quarantine.",
    )


def main(quarantine: bool):
    skills = sorted(p for p in Path("skills").glob("*.py") if p.stem != "__init__")
    if not skills:
        print("No skills found.")
        return

    failures = []
    print(f"Auditing {len(skills)} skills (behavioral bar={MIN_BEHAVIORAL}/30)\n")
    print(f"{'skill':38s} {'behav':>6s}  {'charter':>9s}  verdict")
    print("-" * 78)

    for sp in skills:
        name = sp.stem
        code = sp.read_text(encoding="utf-8")
        behav = behavioral_score(name)
        bt = behav.get("behavioral_total", 0)
        audit = audit_skill(_proposal_for(name, code), name, code)
        verdict = audit.get("verdict", "?")
        audited = audit.get("audited", False)

        behav_fail = bt < MIN_BEHAVIORAL
        charter_fail = (verdict == "VIOLATES")
        failed = behav_fail or charter_fail

        tag = "FAIL" if failed else "ok"
        charter_disp = verdict if audited else f"{verdict}(open)"
        print(f"{name:38s} {bt:4d}/30  {charter_disp:>9s}  {tag}"
              + (f"  <- {audit.get('reasoning','')[:60]}" if charter_fail else "")
              + (f"  <- behavioral too low" if behav_fail else ""))

        if failed:
            failures.append((name, bt, verdict, audit.get("reasoning", "")))

    print("-" * 78)
    print(f"\n{len(failures)}/{len(skills)} flagged.")
    if not failures:
        print("All shipped skills pass. Nothing to quarantine.")
        return

    if quarantine:
        QUARANTINE.mkdir(parents=True, exist_ok=True)
        for name, *_ in failures:
            src = Path("skills") / f"{name}.py"
            if src.exists():
                shutil.move(str(src), str(QUARANTINE / f"{name}.py"))
                print(f"  quarantined -> {QUARANTINE / (name + '.py')}")
        print("\nReview skills/quarantine/, then fix + restore or delete.")
    else:
        print("Run with --quarantine to move these aside. (report-only for now)")
        for name, bt, verdict, reason in failures:
            print(f"  - {name}: behavioral={bt}/30, charter={verdict}. {reason[:80]}")


if __name__ == "__main__":
    main(quarantine="--quarantine" in sys.argv)
