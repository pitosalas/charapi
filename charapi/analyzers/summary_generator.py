from typing import List, Optional
from ..data.charity_evaluation_result import (
    CharityEvaluationResult,
    Metric,
    MetricStatus,
    MetricCategory
)
from ..data.ntee_mapper import NTEEMapper


class SummaryGenerator:
    def _is_form_990_exempt(self, result: CharityEvaluationResult) -> bool:
        filing_req_metric = next(
            (m for m in result.metrics if "Form 990 Filing Required" in m.name),
            None
        )
        if filing_req_metric and filing_req_metric.display_value == "No":
            return True
        return False

    def _get_mission_description(self, result: CharityEvaluationResult) -> Optional[str]:
        mission_metric = next(
            (m for m in result.metrics if "Mission Alignment" in m.name),
            None
        )

        if not mission_metric or not mission_metric.value:
            return None

        ntee_code = mission_metric.value
        description = NTEEMapper.get_description(ntee_code)

        return f"focused on {description}"

    def generate_summary(self, result: CharityEvaluationResult) -> str:
        organization_name = result.organization_name

        mission_description = self._get_mission_description(result)
        strengths = self._identify_strengths(result)
        concerns = self._identify_concerns(result)
        confidence = self._assess_confidence(result)

        return self._build_summary_sentence(
            organization_name,
            mission_description,
            strengths,
            concerns,
            confidence
        )

    def _identify_strengths(self, result: CharityEvaluationResult) -> List[str]:
        strengths = []
        outstanding_metrics = [m for m in result.metrics if m.status == MetricStatus.OUTSTANDING]

        financial_outstanding = [m for m in outstanding_metrics if m.category == MetricCategory.FINANCIAL]
        program_metric = next((m for m in financial_outstanding if "Program" in m.name), None)
        admin_metric = next((m for m in financial_outstanding if "Admin" in m.name), None)
        fundraising_metric = next((m for m in financial_outstanding if "Fundraising" in m.name), None)

        if program_metric and admin_metric:
            strengths.append(f"spending {program_metric.display_value} on programs with only {admin_metric.display_value} on administrative costs")
        elif program_metric:
            strengths.append(f"efficiently allocating {program_metric.display_value} of expenses to programs")

        if fundraising_metric:
            strengths.append(f"just {fundraising_metric.display_value} on fundraising")

        validation_outstanding = [m for m in outstanding_metrics if m.category == MetricCategory.VALIDATION]
        rating_metric = next((m for m in validation_outstanding if "Navigator" in m.name), None)
        if rating_metric:
            strengths.append(f"holding a {rating_metric.display_value} Charity Navigator rating")

        org_type_outstanding = [m for m in outstanding_metrics if m.category == MetricCategory.ORGANIZATION_TYPE]
        years_metric = next((m for m in org_type_outstanding if "Years" in m.name), None)
        if years_metric and isinstance(years_metric.value, int):
            strengths.append(f"operating for {years_metric.value} years")

        preference_outstanding = [m for m in outstanding_metrics if m.category == MetricCategory.PREFERENCE]
        mission_metric = next((m for m in preference_outstanding if "Mission" in m.name), None)
        geo_metric = next((m for m in preference_outstanding if "Geographic" in m.name), None)

        if geo_metric:
            state_info = geo_metric.display_value.split(" ")[0]
            strengths.append(f"based in the preferred state of {state_info}")

        if result.financial_metrics.net_assets > 0 and len(strengths) < 3:
            strengths.append(f"maintaining ${result.financial_metrics.net_assets:,.0f} in positive net assets")

        return strengths[:4]

    def _identify_concerns(self, result: CharityEvaluationResult) -> List[str]:
        concerns = []
        unacceptable_metrics = [m for m in result.metrics if m.status == MetricStatus.UNACCEPTABLE]

        if not result.compliance_check.is_compliant:
            compliance_issues = result.compliance_check.issues
            if compliance_issues:
                concerns.append(f"showing critical compliance failures including {', '.join(compliance_issues[:2])}")

        compliance_unacceptable = [m for m in unacceptable_metrics if m.category == MetricCategory.COMPLIANCE]
        if compliance_unacceptable and not concerns:
            metric = compliance_unacceptable[0]
            concerns.append(f"failing {metric.name.lower()}")

        financial_unacceptable = [m for m in unacceptable_metrics if m.category == MetricCategory.FINANCIAL]
        for metric in financial_unacceptable:
            if "Admin" in metric.name:
                concerns.append(f"high administrative expenses at {metric.display_value}")
            elif "Fundraising" in metric.name:
                concerns.append(f"high fundraising costs at {metric.display_value}")
            elif "Net Assets" in metric.name:
                concerns.append("negative net assets indicating financial instability")
            elif "Program" in metric.name:
                concerns.append(f"spending only {metric.display_value} on programs")

        unknown_metrics = [m for m in result.metrics if m.status == MetricStatus.UNKNOWN]
        financial_unknown = [m for m in unknown_metrics if m.category == MetricCategory.FINANCIAL]
        is_exempt = self._is_form_990_exempt(result)
        if len(financial_unknown) >= 3 and not financial_unacceptable and not is_exempt:
            concerns.append("detailed financial breakdowns are not available to assess program efficiency")

        preference_unacceptable = [m for m in unacceptable_metrics if m.category == MetricCategory.PREFERENCE]
        mission_metric = next((m for m in preference_unacceptable if "Mission" in m.name), None)
        size_metric = next((m for m in preference_unacceptable if "Size" in m.name), None)

        if mission_metric:
            mission_info = mission_metric.display_value.split(" (")[0]
            concerns.append(f"its {mission_info} mission is a lower priority area")

        if size_metric:
            revenue = result.financial_metrics.total_revenue
            if revenue > 100000000:
                concerns.append(f"as a large national organization with ${revenue:,.0f} in revenue, it falls outside the preferred focus on smaller, grassroots charities")
            elif revenue > 5000000:
                concerns.append(f"its large size (${revenue:,.0f} revenue) doesn't align with preferences for smaller organizations")

        return concerns[:3]

    def _assess_confidence(self, result: CharityEvaluationResult) -> Optional[str]:
        unknown_metrics = [m for m in result.metrics if m.status == MetricStatus.UNKNOWN]
        unknown_count = len(unknown_metrics)
        total_count = result.total_metrics

        financial_unknown = [m for m in unknown_metrics if m.category == MetricCategory.FINANCIAL]
        is_exempt = self._is_form_990_exempt(result)

        if unknown_count == 0:
            return None

        if len(financial_unknown) >= 3 and not is_exempt:
            return "This assessment has low confidence due to missing financial data"
        elif unknown_count >= (total_count * 0.4):
            return "This assessment has moderate confidence due to limited data availability"
        elif unknown_count >= (total_count * 0.2):
            return "This assessment has good confidence despite some missing data"
        else:
            return None

    def _build_summary_sentence(
        self,
        organization_name: str,
        mission_description: Optional[str],
        strengths: List[str],
        concerns: List[str],
        confidence: Optional[str]
    ) -> str:
        if mission_description:
            base = f"{organization_name}, {mission_description},"
        else:
            base = f"{organization_name}"

        if strengths and concerns:
            strength_text = self._join_clauses(strengths)
            concern_text = self._join_clauses(concerns)
            if mission_description:
                base = f"{base} {strength_text}, though {concern_text}"
            else:
                base = f"{base} shows {strength_text}, though {concern_text}"
        elif strengths:
            strength_text = self._join_clauses(strengths)
            if mission_description:
                base = f"{base} {strength_text}"
            else:
                base = f"{base} shows {strength_text}"
        elif concerns:
            concern_text = self._join_clauses(concerns)
            if mission_description:
                base = f"{base} though it has concerns including {concern_text}"
            else:
                base = f"{base} has concerns including {concern_text}"
        else:
            if not mission_description:
                base = f"{base} has limited data available for assessment"

        if confidence:
            return f"{base}. {confidence}."
        else:
            return f"{base}."

    def _join_clauses(self, clauses: List[str]) -> str:
        if len(clauses) == 0:
            return ""
        elif len(clauses) == 1:
            return clauses[0]
        elif len(clauses) == 2:
            return f"{clauses[0]} and {clauses[1]}"
        else:
            return ", ".join(clauses[:-1]) + f", and {clauses[-1]}"
