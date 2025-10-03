from typing import List
from ..data.charity_evaluation_result import (
    ComplianceCheck,
    Ident,
    Metric,
    MetricRange,
    MetricStatus,
    MetricCategory
)
from ..data.data_field_manager import DataFieldManager


class ComplianceChecker:
    def __init__(self, config: dict):
        self.data_manager = DataFieldManager(config)

    def check_compliance(self, ein: str) -> ComplianceCheck:
        in_pub78_val = self.data_manager.get_field(Ident.IN_PUB78, ein)
        is_revoked_val = self.data_manager.get_field(Ident.IS_REVOKED, ein)
        has_recent_filing_val = self.data_manager.get_field(Ident.HAS_RECENT_FILING, ein)

        in_pub78 = bool(in_pub78_val) if in_pub78_val is not None else False
        is_revoked = bool(is_revoked_val) if is_revoked_val is not None else False
        has_recent_filing = bool(has_recent_filing_val) if has_recent_filing_val is not None else False

        issues = []
        if not in_pub78:
            issues.append("Not in IRS Publication 78")
        if is_revoked:
            issues.append("Tax-exempt status revoked")
        if not has_recent_filing:
            issues.append("No recent Form 990 filing")

        is_compliant = len(issues) == 0

        return ComplianceCheck(
            is_compliant=is_compliant,
            issues=issues,
            in_pub78=in_pub78,
            is_revoked=is_revoked,
            has_recent_filing=has_recent_filing
        )

    def get_compliance_metrics(self, ein: str) -> List[Metric]:
        in_pub78_val = self.data_manager.get_field(Ident.IN_PUB78, ein)
        is_revoked_val = self.data_manager.get_field(Ident.IS_REVOKED, ein)
        has_recent_filing_val = self.data_manager.get_field(Ident.HAS_RECENT_FILING, ein)

        in_pub78 = bool(in_pub78_val) if in_pub78_val is not None else False
        is_revoked = bool(is_revoked_val) if is_revoked_val is not None else False
        has_recent_filing = bool(has_recent_filing_val) if has_recent_filing_val is not None else False

        metrics_list = []

        pub78_status = MetricStatus.ACCEPTABLE if in_pub78 else MetricStatus.UNACCEPTABLE
        metrics_list.append(Metric(
            name="Publication 78 Listed",
            value=in_pub78,
            status=pub78_status,
            category=MetricCategory.COMPLIANCE,
            ranges=MetricRange(
                outstanding="Yes",
                acceptable="Yes"
            ),
            display_value="Yes" if in_pub78 else "No"
        ))

        revoked_status = MetricStatus.ACCEPTABLE if not is_revoked else MetricStatus.UNACCEPTABLE
        metrics_list.append(Metric(
            name="Tax-Exempt Status",
            value=not is_revoked,
            status=revoked_status,
            category=MetricCategory.COMPLIANCE,
            ranges=MetricRange(
                outstanding="Active",
                acceptable="Active"
            ),
            display_value="Active" if not is_revoked else "Revoked"
        ))

        filing_status = MetricStatus.ACCEPTABLE if has_recent_filing else MetricStatus.UNACCEPTABLE
        metrics_list.append(Metric(
            name="Recent Form 990 Filing",
            value=has_recent_filing,
            status=filing_status,
            category=MetricCategory.COMPLIANCE,
            ranges=MetricRange(
                outstanding="≤3 years",
                acceptable="≤3 years"
            ),
            display_value="Yes" if has_recent_filing else "No"
        ))

        return metrics_list