import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from charapi.analyzers.financial_analyzer import FinancialAnalyzer


def test_metrics_extraction_complete_data():
    """Test extracting metrics from complete filing data"""
    analyzer = FinancialAnalyzer()
    filing = {
        "totfuncexpns": 1000000,
        "totprogrevexp": 750000,
        "totadminexp": 150000,
        "totfndrsexp": 100000,
        "totrevenue": 1500000,
        "totassetsend": 2000000,
        "totliabend": 500000
    }
    metrics = analyzer.extract_metrics(filing)

    assert metrics.program_expense_ratio == 0.75
    assert metrics.admin_expense_ratio == 0.15
    assert metrics.fundraising_expense_ratio == 0.10
    assert metrics.net_assets == 1500000
    assert metrics.total_revenue == 1500000


def test_metrics_extraction_missing_data():
    """Test extracting metrics when some data is missing"""
    analyzer = FinancialAnalyzer()
    filing = {
        "totfuncexpns": 1000000,
        "totprogrevexp": 750000
    }
    metrics = analyzer.extract_metrics(filing)

    assert metrics.program_expense_ratio == 0.75
    assert metrics.total_expenses == 1000000
    assert metrics.net_assets == 0


def test_metrics_extraction_zero_expenses():
    """Test handling when total expenses are zero"""
    analyzer = FinancialAnalyzer()
    filing = {"totfuncexpns": 0}
    metrics = analyzer.extract_metrics(filing)

    assert metrics.program_expense_ratio == 0.0
    assert metrics.admin_expense_ratio == 0.0
    assert metrics.fundraising_expense_ratio == 0.0


def test_calculate_score_returns_valid_range():
    """Test that scoring returns a valid value"""
    analyzer = FinancialAnalyzer()
    filing = {
        "totfuncexpns": 1000000,
        "totprogrevexp": 750000,
        "totassetsend": 2000000,
        "totliabend": 500000
    }
    metrics = analyzer.extract_metrics(filing)
    score = analyzer.calculate_score(metrics)

    assert 0 <= score <= 100


if __name__ == "__main__":
    test_metrics_extraction_complete_data()
    test_metrics_extraction_missing_data()
    test_metrics_extraction_zero_expenses()
    test_calculate_score_returns_valid_range()
    print("All financial analyzer tests passed!")