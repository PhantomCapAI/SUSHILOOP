"""Tests for Cognitive Load Analyzer"""
import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'skills'))

from cognitive_load_analyzer import cognitive_load_analyzer

def test_basic():
    result = cognitive_load_analyzer("test")
    assert isinstance(result, dict)
    assert 'blocked' in result
