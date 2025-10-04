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
from ..analyzers.preference_analyzer import PreferenceAnalyzer
from ..analyzers.summary_generator import SummaryGenerator


def evaluate_charity(ein: str, config_path: str) -> CharityEvaluationResult:
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    config["_config_file_path"] = config_path

    propublica = ProPublicaClient(config_path)
    charityapi = CharityAPIClient(config_path)
    financial_analyzer = FinancialAnalyzer(config)
    compliance_checker = ComplianceChecker(config)
    validation_scorer = ValidationScorer(config)
    organization_type_analyzer = OrganizationTypeAnalyzer(config)
    preference_analyzer = PreferenceAnalyzer(config)

    # Get organization data from ProPublica
    org_data = propublica.get_organization(ein)
    filings = propublica.get_all_filings(ein)

    # Get CharityAPI data for compliance checking and organization type analysis
    charityapi_data = charityapi.get_organization(ein)
    compliance_checker.data_manager.set_charityapi_data(charityapi_data)
    financial_analyzer.data_manager.set_charityapi_data(charityapi_data)

    # Get NTEE code for sector-specific benchmarking
    ntee_code = charityapi_data.get("ntee_cd") if charityapi_data else None
    filing_req_cd = charityapi_data.get("filing_req_cd") if charityapi_data else None

    # Extract financial metrics (keep for backward compatibility)
    latest_filing = filings[0] if filings else {}
    financial_metrics = financial_analyzer.extract_metrics(latest_filing, ein)
    compliance_check = compliance_checker.check_compliance(ein)
    organization_type = organization_type_analyzer.analyze(charityapi_data)
    external_validation = validation_scorer.get_validation_data(ein)

    # Collect all metrics
    all_metrics: List[Metric] = []
    all_metrics.extend(financial_analyzer.get_financial_metrics(financial_metrics, ntee_code, filing_req_cd))
    all_metrics.extend(compliance_checker.get_compliance_metrics(ein))
    all_metrics.extend(organization_type_analyzer.get_organization_type_metrics(charityapi_data))
    all_metrics.extend(validation_scorer.get_validation_metrics(ein))
    all_metrics.extend(preference_analyzer.get_preference_metrics(charityapi_data, financial_metrics.total_revenue))

    # Count metric statuses
    outstanding_count = sum(1 for m in all_metrics if m.status == MetricStatus.OUTSTANDING)
    acceptable_count = sum(1 for m in all_metrics if m.status == MetricStatus.ACCEPTABLE)
    unacceptable_count = sum(1 for m in all_metrics if m.status == MetricStatus.UNACCEPTABLE)
    total_metrics = len(all_metrics)

    # Handle both mock and real API response structures
    if org_data:
        org_name = org_data.get("name") or org_data.get("organization", {}).get("name", "Unknown")
    elif charityapi_data:
        org_name = charityapi_data.get("name", "Unknown")
    else:
        org_name = "Unknown"

    result = CharityEvaluationResult(
        ein=ein,
        organization_name=org_name,
        score=0.0,
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
        total_metrics=total_metrics,
        summary=""
    )

    summary_generator = SummaryGenerator()
    result.summary = summary_generator.generate_summary(result)

    return result


def batch_evaluate(eins: List[str], config_path: str) -> List[CharityEvaluationResult]:
    return [evaluate_charity(ein, config_path) for ein in eins]
