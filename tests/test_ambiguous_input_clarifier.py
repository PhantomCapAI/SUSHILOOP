"""Tests for Ambiguous Input Clarifier"""
import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'skills'))

from ambiguous_input_clarifier import ambiguous_input_clarifier

def test_basic():
    result = ambiguous_input_clarifier("test")
    assert isinstance(result, dict)
    assert 'blocked' in result
