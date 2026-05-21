"""Tests for Contextual Understanding Evaluator"""
import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'skills'))

from contextual_understanding_evaluator import contextual_understanding_evaluator

def test_basic():
    result = contextual_understanding_evaluator("test")
    assert isinstance(result, dict)
    assert 'blocked' in result
