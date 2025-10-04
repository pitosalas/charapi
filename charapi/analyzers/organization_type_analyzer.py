from datetime import datetime
from typing import Dict, Any, Optional, List
from ..data.charity_evaluation_result import (
    OrganizationType,
    Metric,
    MetricRange,
    MetricStatus,
    MetricCategory
)


class OrganizationTypeAnalyzer:
    def __init__(self, config: dict):
        self.config = config.get("scoring", {}).get("organization_type", {})
        self.org_type_config = config.get("scoring", {}).get("organization_type", {})

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

    def get_organization_type_metrics(self, charityapi_data: Optional[Dict[str, Any]]) -> List[Metric]:
        metrics_list = []

        if not charityapi_data:
            metrics_list.append(Metric(
                name="Organization Data",
                value=None,
                status=MetricStatus.UNKNOWN,
                category=MetricCategory.ORGANIZATION_TYPE,
                ranges=MetricRange(
                    outstanding="Available",
                    acceptable="Available"
                ),
                display_value="Unknown"
            ))
            return metrics_list

        subsection = charityapi_data.get("subsection")
        subsection_required = self.org_type_config.get("subsection_required", 3)
        subsection_status = MetricStatus.ACCEPTABLE if subsection == subsection_required else MetricStatus.UNACCEPTABLE
        metrics_list.append(Metric(
            name="501(c)(3) Status",
            value=subsection,
            status=subsection_status,
            category=MetricCategory.ORGANIZATION_TYPE,
            ranges=MetricRange(
                outstanding="Yes",
                acceptable="Yes"
            ),
            display_value="Yes" if subsection == subsection_required else "No"
        ))

        foundation = charityapi_data.get("foundation")
        public_charity_code = self.org_type_config.get("public_charity_code", 15)
        foundation_status = MetricStatus.ACCEPTABLE if foundation == public_charity_code else MetricStatus.UNACCEPTABLE
        metrics_list.append(Metric(
            name="Public Charity",
            value=foundation,
            status=foundation_status,
            category=MetricCategory.ORGANIZATION_TYPE,
            ranges=MetricRange(
                outstanding="Yes",
                acceptable="Yes"
            ),
            display_value="Yes" if foundation == public_charity_code else "No"
        ))

        filing_req = charityapi_data.get("filing_req_cd")
        acceptable_values = self.org_type_config.get("filing_requirement_acceptable_values", [0, 1])
        filing_status = MetricStatus.ACCEPTABLE if filing_req in acceptable_values else MetricStatus.UNACCEPTABLE
        metrics_list.append(Metric(
            name="Form 990 Filing Required",
            value=filing_req,
            status=filing_status,
            category=MetricCategory.ORGANIZATION_TYPE,
            ranges=MetricRange(
                outstanding="Yes",
                acceptable="Yes/No"
            ),
            display_value="Yes" if filing_req == 1 else "No"
        ))

        ruling = charityapi_data.get("ruling")
        if ruling:
            ruling_year = ruling // 100
            years_operating = datetime.now().year - ruling_year
            min_years = self.config.get("established_years_threshold", 20)

            if years_operating >= min_years:
                years_status = MetricStatus.OUTSTANDING
            else:
                years_status = MetricStatus.ACCEPTABLE

            metrics_list.append(Metric(
                name="Years Operating",
                value=years_operating,
                status=years_status,
                category=MetricCategory.ORGANIZATION_TYPE,
                ranges=MetricRange(
                    outstanding=f"≥{min_years}",
                    acceptable="≥1"
                ),
                display_value=str(years_operating)
            ))

        return metrics_list
