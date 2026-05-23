"""Tests for Input Redundancy Analyzer"""
import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'skills'))

from input_redundancy_analyzer import input_redundancy_analyzer

def test_basic():
    result = input_redundancy_analyzer("test")
    assert isinstance(result, dict)
    assert 'blocked' in result
