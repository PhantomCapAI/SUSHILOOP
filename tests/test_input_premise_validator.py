"""Tests for Input Premise Validator"""
import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'skills'))

from input_premise_validator import input_premise_validator

def test_basic():
    result = input_premise_validator("test")
    assert isinstance(result, dict)
    assert 'blocked' in result
