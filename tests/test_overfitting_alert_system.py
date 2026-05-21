"""Tests for Overfitting Alert System"""
import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'skills'))

from overfitting_alert_system import overfitting_alert_system

def test_basic():
    result = overfitting_alert_system("test")
    assert isinstance(result, dict)
    assert 'blocked' in result
