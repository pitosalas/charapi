from datetime import datetime
from typing import Dict, Any, Optional
from ..data.charity_evaluation_result import OrganizationType


class OrganizationTypeAnalyzer:
    def __init__(self, config: dict):
        self.config = config.get("scoring", {}).get("organization_type", {})

    def analyze(self, charityapi_data: Optional[Dict[str, Any]]) -> OrganizationType:
        if not charityapi_data:
            return OrganizationType(
                score=0.0,
                issues=["Organization type data not available"],
                subsection=None,
                foundation_type=None,
                filing_requirement=None,
                years_operating=None
            )

        score = 0.0
        issues = []

        subsection = charityapi_data.get("subsection")
        if subsection != 3:
            penalty = self.config.get("non_501c3_penalty", 25)
            score -= penalty
            issues.append(f"Not a 501(c)(3) organization (subsection: {subsection})")

        foundation = charityapi_data.get("foundation")
        public_charity_code = self.config.get("public_charity_code", 15)
        if foundation != public_charity_code:
            penalty = self.config.get("private_foundation_penalty", 15)
            score -= penalty
            issues.append(f"Private foundation, not public charity (code: {foundation})")

        filing_req = charityapi_data.get("filing_req_cd")
        if filing_req != 1:
            penalty = self.config.get("no_filing_requirement_penalty", 10)
            score -= penalty
            issues.append("Not required to file Form 990 (lack of transparency)")

        ruling = charityapi_data.get("ruling")
        years_operating = None
        if ruling:
            ruling_year = ruling // 100
            years_operating = datetime.now().year - ruling_year
            min_years = self.config.get("established_years_threshold", 20)

            if years_operating >= min_years:
                bonus = self.config.get("established_bonus", 5)
                score += bonus

        return OrganizationType(
            score=score,
            issues=issues,
            subsection=subsection,
            foundation_type=foundation,
            filing_requirement=filing_req,
            years_operating=years_operating
        )
