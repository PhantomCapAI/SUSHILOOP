"""Tests for Prompt Injection Detector"""
import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'skills'))

from prompt_injection_detector import prompt_injection_detector

def test_basic():
    result = prompt_injection_detector("test")
    assert isinstance(result, dict)
    assert 'blocked' in result
