#!/usr/bin/env python3
"""SUSHI LOOP - Main execution script"""
import sys
import os
sys.path.insert(0, '.')

from core.evolve import SushiLoop
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
    sys.exit(0 if result == "SUCCESS" else 1)
