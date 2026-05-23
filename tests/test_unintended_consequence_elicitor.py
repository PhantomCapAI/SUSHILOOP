"""Tests for Unintended Consequence Elicitor"""
import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'skills'))

from unintended_consequence_elicitor import unintended_consequence_elicitor

def test_basic():
    result = unintended_consequence_elicitor("test")
    assert isinstance(result, dict)
    assert 'blocked' in result
