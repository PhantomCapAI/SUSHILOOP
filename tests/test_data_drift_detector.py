"""Tests for Data Drift Detector"""
import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'skills'))

from data_drift_detector import data_drift_detector

def test_basic():
    result = data_drift_detector("test")
    assert isinstance(result, dict)
    assert 'blocked' in result
