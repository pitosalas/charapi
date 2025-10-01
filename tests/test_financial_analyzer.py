from charapi.analyzers.financial_analyzer import FinancialAnalyzer


TEST_CONFIG = {
    "data_fields": {
        "program_expenses": {"source": "manual"},
        "admin_expenses": {"source": "manual"},
        "fundraising_expenses": {"source": "manual"}
    },
    "manual_data": {"directory": "manual"}
}


def test_metrics_extraction_complete_data():
    """Test extracting metrics from filing data when manual data is not available"""
    analyzer = FinancialAnalyzer(TEST_CONFIG)
    filing = {
        "totfuncexpns": 3000000000,
        "totrevenue": 3500000000,
        "totassetsend": 5400000000,
        "totliabend": 2000000000
    }
    metrics = analyzer.extract_metrics(filing, "530196605")

    assert metrics.program_expenses == 0
    assert metrics.admin_expenses == 0
    assert metrics.fundraising_expenses == 0
    assert metrics.net_assets == 3400000000
    assert metrics.total_revenue == 3500000000


def test_metrics_extraction_missing_data():
    """Test extracting metrics when some data is missing"""
    analyzer = FinancialAnalyzer(TEST_CONFIG)
    filing = {
        "totfuncexpns": 1000000
    }
    metrics = analyzer.extract_metrics(filing, "530196605")

    assert metrics.total_expenses == 1000000
    assert metrics.net_assets == 0


def test_metrics_extraction_zero_expenses():
    """Test handling when total expenses are zero"""
    analyzer = FinancialAnalyzer(TEST_CONFIG)
    filing = {"totfuncexpns": 0}
    metrics = analyzer.extract_metrics(filing, "530196605")

    assert metrics.program_expense_ratio == 0.0
    assert metrics.admin_expense_ratio == 0.0
    assert metrics.fundraising_expense_ratio == 0.0


def test_calculate_score_returns_valid_range():
    """Test that scoring returns a valid value"""
    analyzer = FinancialAnalyzer(TEST_CONFIG)
    filing = {
        "totfuncexpns": 1000000,
        "totassetsend": 2000000,
        "totliabend": 500000
    }
    metrics = analyzer.extract_metrics(filing, "530196605")
    score = analyzer.calculate_score(metrics)

    assert 0 <= score <= 100


if __name__ == "__main__":
    test_metrics_extraction_complete_data()
    test_metrics_extraction_missing_data()
    test_metrics_extraction_zero_expenses()
    test_calculate_score_returns_valid_range()
    print("All financial analyzer tests passed!")