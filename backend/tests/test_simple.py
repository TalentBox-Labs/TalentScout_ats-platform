"""Simple test to check pytest functionality."""
import pytest

def test_simple():
    assert 1 + 1 == 2

class TestSimple:
    def test_simple_in_class(self):
        assert 2 + 2 == 4