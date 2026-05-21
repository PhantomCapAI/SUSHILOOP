"""Tests for False Urgency Framing Catcher"""
import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'skills'))

from s import s

def test_basic():
    result = s("test")
    assert isinstance(result, dict)
    assert 'blocked' in result
