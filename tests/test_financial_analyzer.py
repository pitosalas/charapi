from charapi.analyzers.financial_analyzer import FinancialAnalyzer
from charapi.data.charity_evaluation_result import FinancialMetrics


TEST_CONFIG = {
    "data_fields": {
        "program_expenses": {"source": "manual"},
        "admin_expenses": {"source": "manual"},
        "fundraising_expenses": {"source": "manual"}
    },
    "manual_data": {"directory": "manual"},
    "scoring": {
        "financial": {
            "program_expense_target": 0.75,
            "admin_expense_limit": 0.15,
            "fundraising_expense_limit": 0.15,
            "program_score_max": 40,
            "admin_score_max": 20,
            "fundraising_score_max": 20,
            "stability_score_max": 20,
            "sector_overrides": {
                "A": {
                    "program_expense_target": 0.65,
                    "admin_expense_limit": 0.20
                },
                "B": {
                    "program_expense_target": 0.80,
                    "admin_expense_limit": 0.12
                },
                "E": {
                    "program_expense_target": 0.80,
                    "admin_expense_limit": 0.12
                }
            }
        }
    }
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


def test_get_sector_benchmarks_no_ntee():
    """Test getting default benchmarks when no NTEE code provided"""
    analyzer = FinancialAnalyzer(TEST_CONFIG)
    benchmarks = analyzer.get_sector_benchmarks(None)

    assert benchmarks["program_expense_target"] == 0.75
    assert benchmarks["admin_expense_limit"] == 0.15


def test_get_sector_benchmarks_unknown_sector():
    """Test getting default benchmarks for unknown sector"""
    analyzer = FinancialAnalyzer(TEST_CONFIG)
    benchmarks = analyzer.get_sector_benchmarks("Z99")

    assert benchmarks["program_expense_target"] == 0.75
    assert benchmarks["admin_expense_limit"] == 0.15


def test_get_sector_benchmarks_arts():
    """Test getting Arts sector benchmarks (NTEE A)"""
    analyzer = FinancialAnalyzer(TEST_CONFIG)
    benchmarks = analyzer.get_sector_benchmarks("A68")

    assert benchmarks["program_expense_target"] == 0.65
    assert benchmarks["admin_expense_limit"] == 0.20


def test_get_sector_benchmarks_education():
    """Test getting Education sector benchmarks (NTEE B)"""
    analyzer = FinancialAnalyzer(TEST_CONFIG)
    benchmarks = analyzer.get_sector_benchmarks("B21")

    assert benchmarks["program_expense_target"] == 0.80
    assert benchmarks["admin_expense_limit"] == 0.12


def test_get_sector_benchmarks_health():
    """Test getting Health sector benchmarks (NTEE E)"""
    analyzer = FinancialAnalyzer(TEST_CONFIG)
    benchmarks = analyzer.get_sector_benchmarks("E20")

    assert benchmarks["program_expense_target"] == 0.80
    assert benchmarks["admin_expense_limit"] == 0.12


def test_calculate_score_with_ntee_arts():
    """Test scoring with Arts sector benchmarks (lower program target, higher admin limit)"""
    analyzer = FinancialAnalyzer(TEST_CONFIG)

    metrics = FinancialMetrics(
        program_expense_ratio=65.0,
        admin_expense_ratio=20.0,
        fundraising_expense_ratio=15.0,
        net_assets=1000000,
        total_revenue=2000000,
        total_expenses=1000000,
        program_expenses=650000,
        admin_expenses=200000,
        fundraising_expenses=150000,
        total_assets=2000000,
        total_liabilities=1000000
    )

    score = analyzer.calculate_score(metrics, "A68")

    assert score == 60.0


def test_calculate_score_with_ntee_education():
    """Test scoring with Education sector benchmarks (higher program target)"""
    analyzer = FinancialAnalyzer(TEST_CONFIG)

    metrics = FinancialMetrics(
        program_expense_ratio=80.0,
        admin_expense_ratio=12.0,
        fundraising_expense_ratio=8.0,
        net_assets=1000000,
        total_revenue=2000000,
        total_expenses=1000000,
        program_expenses=800000,
        admin_expenses=120000,
        fundraising_expenses=80000,
        total_assets=2000000,
        total_liabilities=1000000
    )

    score = analyzer.calculate_score(metrics, "B21")

    assert round(score, 2) == 69.33


def test_calculate_score_without_ntee_uses_default():
    """Test that scoring without NTEE code uses default benchmarks"""
    analyzer = FinancialAnalyzer(TEST_CONFIG)

    metrics = FinancialMetrics(
        program_expense_ratio=75.0,
        admin_expense_ratio=15.0,
        fundraising_expense_ratio=10.0,
        net_assets=1000000,
        total_revenue=2000000,
        total_expenses=1000000,
        program_expenses=750000,
        admin_expenses=150000,
        fundraising_expenses=100000,
        total_assets=2000000,
        total_liabilities=1000000
    )

    score_without_ntee = analyzer.calculate_score(metrics)
    score_with_none = analyzer.calculate_score(metrics, None)

    assert score_without_ntee == score_with_none
    assert round(score_without_ntee, 2) == 66.67


if __name__ == "__main__":
    test_metrics_extraction_complete_data()
    test_metrics_extraction_missing_data()
    test_metrics_extraction_zero_expenses()
    test_calculate_score_returns_valid_range()
    test_get_sector_benchmarks_no_ntee()
    test_get_sector_benchmarks_unknown_sector()
    test_get_sector_benchmarks_arts()
    test_get_sector_benchmarks_education()
    test_get_sector_benchmarks_health()
    test_calculate_score_with_ntee_arts()
    test_calculate_score_with_ntee_education()
    test_calculate_score_without_ntee_uses_default()
    print("All financial analyzer tests passed!")