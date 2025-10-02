import yaml
from datetime import datetime
from typing import List

from ..data.charity_evaluation_result import CharityEvaluationResult, Issue
from ..clients.propublica_client import ProPublicaClient
from ..analyzers.financial_analyzer import FinancialAnalyzer
from ..analyzers.trend_analyzer import TrendAnalyzer
from ..analyzers.compliance_checker import ComplianceChecker
from ..analyzers.validation_scorer import ValidationScorer


def evaluate_charity(ein: str, config_path: str) -> CharityEvaluationResult:
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    
    propublica = ProPublicaClient(config_path)
    financial_analyzer = FinancialAnalyzer(config)
    trend_analyzer = TrendAnalyzer()
    compliance_checker = ComplianceChecker(config)
    validation_scorer = ValidationScorer(config)

    # Get organization data from ProPublica
    org_data = propublica.get_organization(ein)
    filings = propublica.get_all_filings(ein)

    # Calculate financial health score
    latest_filing = filings[0] if filings else {}
    financial_metrics = financial_analyzer.extract_metrics(latest_filing, ein)
    financial_score = financial_analyzer.calculate_score(financial_metrics)
    
    # Calculate trend analysis
    trend_analysis = trend_analyzer.analyze_trends(filings)
    trend_modifier = trend_analyzer.calculate_modifier(trend_analysis)
    
    # Check compliance
    compliance_check = compliance_checker.check_compliance(ein)
    compliance_penalty = -50 if not compliance_check.is_compliant else 0
    
    # Get external validation
    external_validation = validation_scorer.get_validation_data(ein)
    validation_bonus = validation_scorer.calculate_bonus(external_validation)
    
    # Calculate final score and grade
    total_score = financial_score + trend_modifier + validation_bonus + compliance_penalty
    grade = _assign_grade(total_score)

    # Handle both mock and real API response structures
    org_name = org_data.get("name") or org_data.get("organization", {}).get("name", "Unknown")

    # Collect issues
    issues = []
    issue_codes = []

    if external_validation.charity_navigator_rating is None:
        issue_codes.append(Issue.MISSING_CHARITY_NAVIGATOR)
        issues.append("Charity Navigator rating not available - edit manual/brief_manual.yaml")

    if financial_metrics.program_expenses == 0:
        issue_codes.append(Issue.MISSING_EXPENSE_DATA)
        issues.append("Expense breakdown data missing - edit manual/brief_manual.yaml")

    if not compliance_check.is_compliant:
        issue_codes.append(Issue.COMPLIANCE_FAILURE)
        issues.append(f"IRS compliance issues: {', '.join(compliance_check.issues)} - edit manual/brief_manual.yaml")

    issue_codes.append(Issue.STUB_TREND_ANALYSIS)
    issues.append("Trend analysis using stub implementation - needs real formulas")

    issue_codes.append(Issue.STUB_FINANCIAL_SCORING)
    issues.append("Financial scoring using stub implementation - needs real formulas")

    return CharityEvaluationResult(
        ein=ein,
        organization_name=org_name,
        total_score=total_score,
        grade=grade,
        financial_score=financial_score,
        trend_modifier=trend_modifier,
        validation_bonus=validation_bonus,
        compliance_penalty=compliance_penalty,
        financial_metrics=financial_metrics,
        trend_analysis=trend_analysis,
        compliance_check=compliance_check,
        external_validation=external_validation,
        evaluation_timestamp=datetime.now().isoformat(),
        data_sources_used=["ProPublica", "IRS", "Charity Navigator"],
        issues=issues,
        issue_codes=issue_codes
    )


def batch_evaluate(eins: List[str], config_path: str) -> List[CharityEvaluationResult]:
    return [evaluate_charity(ein, config_path) for ein in eins]


class GradeAssigner:
    GRADE_THRESHOLDS = [
        (90, "A"),
        (75, "B"), 
        (60, "C"),
        (45, "D")
    ]
    
    def assign_grade(self, total_score: float) -> str:
        for threshold, grade in self.GRADE_THRESHOLDS:
            if total_score >= threshold:
                return grade
        return "F"


def _assign_grade(total_score: float) -> str:
    return GradeAssigner().assign_grade(total_score)