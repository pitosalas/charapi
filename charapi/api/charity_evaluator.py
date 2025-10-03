import yaml
from datetime import datetime
from typing import List

from ..data.charity_evaluation_result import (
    CharityEvaluationResult,
    Issue,
    Metric,
    MetricStatus
)
from ..clients.propublica_client import ProPublicaClient
from ..clients.charityapi_client import CharityAPIClient
from ..analyzers.financial_analyzer import FinancialAnalyzer
from ..analyzers.compliance_checker import ComplianceChecker
from ..analyzers.validation_scorer import ValidationScorer
from ..analyzers.organization_type_analyzer import OrganizationTypeAnalyzer


def evaluate_charity(ein: str, config_path: str) -> CharityEvaluationResult:
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    propublica = ProPublicaClient(config_path)
    charityapi = CharityAPIClient(config_path)
    financial_analyzer = FinancialAnalyzer(config)
    compliance_checker = ComplianceChecker(config)
    validation_scorer = ValidationScorer(config)
    organization_type_analyzer = OrganizationTypeAnalyzer(config)

    # Get organization data from ProPublica
    org_data = propublica.get_organization(ein)
    filings = propublica.get_all_filings(ein)

    # Get CharityAPI data for compliance checking and organization type analysis
    charityapi_data = charityapi.get_organization(ein)
    compliance_checker.data_manager.set_charityapi_data(charityapi_data)
    financial_analyzer.data_manager.set_charityapi_data(charityapi_data)

    # Get NTEE code for sector-specific benchmarking
    ntee_code = charityapi_data.get("ntee_cd") if charityapi_data else None

    # Extract financial metrics (keep for backward compatibility)
    latest_filing = filings[0] if filings else {}
    financial_metrics = financial_analyzer.extract_metrics(latest_filing, ein)
    compliance_check = compliance_checker.check_compliance(ein)
    organization_type = organization_type_analyzer.analyze(charityapi_data)
    external_validation = validation_scorer.get_validation_data(ein)

    # Collect all metrics
    all_metrics: List[Metric] = []
    all_metrics.extend(financial_analyzer.get_financial_metrics(financial_metrics, ntee_code))
    all_metrics.extend(compliance_checker.get_compliance_metrics(ein))
    all_metrics.extend(organization_type_analyzer.get_organization_type_metrics(charityapi_data))
    all_metrics.extend(validation_scorer.get_validation_metrics(ein))

    # Count metric statuses
    outstanding_count = sum(1 for m in all_metrics if m.status == MetricStatus.OUTSTANDING)
    acceptable_count = sum(1 for m in all_metrics if m.status == MetricStatus.ACCEPTABLE)
    unacceptable_count = sum(1 for m in all_metrics if m.status == MetricStatus.UNACCEPTABLE)
    total_metrics = len(all_metrics)

    # Calculate score based on percentage of metrics in good range
    # Outstanding: 10 points, Acceptable: 5 points, Unacceptable/Unknown: 0 points
    total_points = (outstanding_count * 10) + (acceptable_count * 5)
    max_points = total_metrics * 10
    score = (total_points / max_points * 100) if max_points > 0 else 0

    # Handle both mock and real API response structures
    org_name = org_data.get("name") or org_data.get("organization", {}).get(
        "name", "Unknown"
    )

    return CharityEvaluationResult(
        ein=ein,
        organization_name=org_name,
        score=score,
        metrics=all_metrics,
        financial_metrics=financial_metrics,
        compliance_check=compliance_check,
        external_validation=external_validation,
        organization_type=organization_type,
        evaluation_timestamp=datetime.now().isoformat(),
        data_sources_used=["ProPublica", "CharityAPI", "Charity Navigator"],
        outstanding_count=outstanding_count,
        acceptable_count=acceptable_count,
        unacceptable_count=unacceptable_count,
        total_metrics=total_metrics
    )


def batch_evaluate(eins: List[str], config_path: str) -> List[CharityEvaluationResult]:
    return [evaluate_charity(ein, config_path) for ein in eins]
