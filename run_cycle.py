#!/usr/bin/env python3
"""SUSHI LOOP - Main execution script"""
import sys
import os
sys.path.insert(0, '.')

from core.evolve import SushiLoop
from core.schemas import CycleResult
import structlog

structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer()
    ]
)

logger = structlog.get_logger(__name__)

if __name__ == '__main__':
    logger.info("🍣 SUSHI LOOP Starting...")
    loop = SushiLoop()
    status = loop.get_status()
    logger.info(f"Current cycle: {status['cycle']}")
    logger.info(f"Total skills: {status['total_skills']}")
    result = loop.run_cycle()
    logger.info(f"Cycle finished: {result}")

    # Set GitHub Actions step outputs for auto-tweet (and future features)
    # Only triggers when a new skill was successfully generated, tested, and committed
    if result == CycleResult.SUCCESS and getattr(loop, 'last_successful_proposal', None) is not None:
        proposal = loop.last_successful_proposal
        skill_name = getattr(loop, 'last_skill_name', '')
        if os.getenv('GITHUB_ACTIONS') == 'true':
            github_output = os.getenv('GITHUB_OUTPUT')
            if github_output:
                try:
                    with open(github_output, 'a', encoding='utf-8') as f:
                        f.write("new_skill=true\n")
                        f.write(f"skill_title={proposal.title}\n")
                        desc_clean = (proposal.description or "").replace("\n", " ").replace("\r", " ").strip()
                        f.write(f"skill_description={desc_clean}\n")
                        f.write(f"skill_name={skill_name}\n")
                    logger.info("✅ GitHub Actions outputs set for new skill (new_skill, skill_title, skill_description)")
                except Exception as exc:
                    logger.warning(f"Failed to write to GITHUB_OUTPUT: {exc}")

    sys.exit(0 if result == CycleResult.SUCCESS else 1)
