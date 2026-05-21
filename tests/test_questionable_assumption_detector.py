"""Tests for Questionable Assumption Detector"""
import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'skills'))

from questionable_assumption_detector import questionable_assumption_detector

def test_basic():
    result = questionable_assumption_detector("test")
    assert isinstance(result, dict)
    assert 'blocked' in result
