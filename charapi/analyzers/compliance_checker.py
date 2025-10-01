from ..data.charity_evaluation_result import ComplianceCheck
from ..data.data_field_manager import DataFieldManager


class ComplianceChecker:
    def __init__(self, config: dict):
        self.data_manager = DataFieldManager(config)

    def check_compliance(self, ein: str) -> ComplianceCheck:
        in_pub78_str = self.data_manager.get_field("in_pub78", ein)
        is_revoked_str = self.data_manager.get_field("is_revoked", ein)
        has_recent_filing_str = self.data_manager.get_field("has_recent_filing", ein)

        in_pub78 = in_pub78_str != "manual data not available" and in_pub78_str.lower() in ["1", "true", "yes"]
        is_revoked = is_revoked_str != "manual data not available" and is_revoked_str.lower() in ["1", "true", "yes"]
        has_recent_filing = has_recent_filing_str != "manual data not available" and has_recent_filing_str.lower() in ["1", "true", "yes"]

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