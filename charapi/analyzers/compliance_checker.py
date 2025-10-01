from ..data.charity_evaluation_result import ComplianceCheck
from ..data.data_field_manager import DataFieldManager


class ComplianceChecker:
    def __init__(self, config: dict):
        self.data_manager = DataFieldManager(config)

    def check_compliance(self, ein: str) -> ComplianceCheck:
        in_pub78_val = self.data_manager.get_field("in_pub78", ein)
        is_revoked_val = self.data_manager.get_field("is_revoked", ein)
        has_recent_filing_val = self.data_manager.get_field("has_recent_filing", ein)

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