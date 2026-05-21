"""Tests for Overreliance Detector"""
import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'skills'))

from overreliance_detector import overreliance_detector

def test_basic():
    result = overreliance_detector("test")
    assert isinstance(result, dict)
    assert 'blocked' in result
