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

    # Write the outcome so the workflow can decide what to commit.
    # Only SUCCESS should ship skill/test files; brain/ state persists regardless
    # so the loop still learns from rejections.
    try:
        with open('.cycle_result', 'w', encoding='utf-8') as f:
            f.write(result.value if hasattr(result, 'value') else str(result))
    except Exception as e:
        logger.warning(f"Could not write .cycle_result: {e}")

    # Exit code reflects RUN health, not whether a skill shipped.
    # SUCCESS      -> a skill passed every gate and shipped.
    # REJECTED     -> a gate correctly blocked a bad skill (the system working).
    # TEST_FAILED  -> the test gate correctly caught a broken skill (working).
    # ERROR        -> an actual unhandled fault. THIS is the only real failure.
    # Only ERROR exits non-zero, so a red Action means something is genuinely wrong.
    if result == CycleResult.ERROR:
        logger.error("Cycle errored — exiting non-zero for visibility")
        sys.exit(1)
    sys.exit(0)
