import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from charapi.api.charity_evaluator import _assign_grade


def test_grade_boundaries():
    """Test grade assignment at exact boundary values"""
    assert _assign_grade(90) == "A"
    assert _assign_grade(89.99) == "B"
    assert _assign_grade(75) == "B"
    assert _assign_grade(74.99) == "C"
    assert _assign_grade(60) == "C"
    assert _assign_grade(59.99) == "D"
    assert _assign_grade(45) == "D"
    assert _assign_grade(44.99) == "F"
    assert _assign_grade(0) == "F"


def test_grade_extreme_values():
    """Test grade assignment with extreme scores"""
    assert _assign_grade(150) == "A"  # Over 100
    assert _assign_grade(-50) == "F"  # Negative


if __name__ == "__main__":
    test_grade_boundaries()
    test_grade_extreme_values()
    print("All grading tests passed!")