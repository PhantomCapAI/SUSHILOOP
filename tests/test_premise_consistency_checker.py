"""Tests for Premise Consistency Checker"""
import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'skills'))

from premise_consistency_checker import premise_consistency_checker

def test_basic():
    result = premise_consistency_checker("test")
    assert isinstance(result, dict)
    assert 'blocked' in result
