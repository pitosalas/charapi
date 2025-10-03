from typing import Optional, Dict, Any, List
from ..data.charity_evaluation_result import (
    Metric,
    MetricRange,
    MetricStatus,
    MetricCategory
)


class PreferenceAnalyzer:
    def __init__(self, config: dict):
        self.config = config
        self.preferences_config = config.get("preferences", {})

    def get_preference_metrics(
        self,
        charityapi_data: Optional[Dict[str, Any]],
        total_revenue: int
    ) -> List[Metric]:
        metrics = []

        mission_metric = self._get_mission_alignment_metric(charityapi_data)
        if mission_metric:
            metrics.append(mission_metric)

        geographic_metric = self._get_geographic_alignment_metric(charityapi_data)
        if geographic_metric:
            metrics.append(geographic_metric)

        size_metric = self._get_organization_size_metric(total_revenue)
        if size_metric:
            metrics.append(size_metric)

        return metrics

    def _get_mission_alignment_metric(
        self,
        charityapi_data: Optional[Dict[str, Any]]
    ) -> Optional[Metric]:
        mission_config = self.preferences_config.get("mission_alignment", {})
        if not mission_config.get("enabled", False):
            return None

        priorities = mission_config.get("priorities", {})

        if not charityapi_data:
            return Metric(
                name="Mission Alignment",
                value=None,
                status=MetricStatus.UNKNOWN,
                category=MetricCategory.PREFERENCE,
                ranges=MetricRange(
                    outstanding="High",
                    acceptable="Med"
                ),
                display_value="Unknown"
            )

        ntee_code = charityapi_data.get("ntee_cd")
        if not ntee_code:
            return Metric(
                name="Mission Alignment",
                value=None,
                status=MetricStatus.UNKNOWN,
                category=MetricCategory.PREFERENCE,
                ranges=MetricRange(
                    outstanding="High",
                    acceptable="Med"
                ),
                display_value="No NTEE code"
            )

        sector = ntee_code[0] if ntee_code else None
        priority = priorities.get(sector, "low")

        ntee_names = {
            "A": "Arts & Culture",
            "B": "Education",
            "C": "Environment",
            "D": "Animal-Related",
            "E": "Health",
            "F": "Mental Health",
            "G": "Disease/Disorders",
            "H": "Medical Research",
            "I": "Crime & Legal",
            "J": "Employment",
            "K": "Food & Agriculture",
            "L": "Housing & Shelter",
            "M": "Public Safety",
            "N": "Recreation & Sports",
            "O": "Youth Development",
            "P": "Human Services",
            "Q": "International",
            "R": "Civil Rights",
            "S": "Community Improvement",
            "T": "Philanthropy",
            "U": "Science & Technology",
            "V": "Social Science",
            "W": "Public Benefit",
            "X": "Religion",
            "Y": "Mutual Benefit",
            "Z": "Unknown"
        }

        sector_name = ntee_names.get(sector, "Unknown")

        if priority == "high":
            status = MetricStatus.OUTSTANDING
            priority_label = "High"
        elif priority == "medium":
            status = MetricStatus.ACCEPTABLE
            priority_label = "Med"
        else:
            status = MetricStatus.UNACCEPTABLE
            priority_label = "Low"

        return Metric(
            name="Mission Alignment",
            value=ntee_code,
            status=status,
            category=MetricCategory.PREFERENCE,
            ranges=MetricRange(
                outstanding="High",
                acceptable="Med"
            ),
            display_value=f"{sector_name} ({priority_label})"
        )

    def _get_geographic_alignment_metric(
        self,
        charityapi_data: Optional[Dict[str, Any]]
    ) -> Optional[Metric]:
        geo_config = self.preferences_config.get("geographic_alignment", {})
        if not geo_config.get("enabled", False):
            return None

        if not charityapi_data:
            return Metric(
                name="Geographic Alignment",
                value=None,
                status=MetricStatus.UNKNOWN,
                category=MetricCategory.PREFERENCE,
                ranges=MetricRange(
                    outstanding="Pref",
                    acceptable="Accept"
                ),
                display_value="Unknown"
            )

        state = charityapi_data.get("state")
        if not state:
            return Metric(
                name="Geographic Alignment",
                value=None,
                status=MetricStatus.UNKNOWN,
                category=MetricCategory.PREFERENCE,
                ranges=MetricRange(
                    outstanding="Pref",
                    acceptable="Accept"
                ),
                display_value="No state data"
            )

        preferred_states = geo_config.get("preferred_states", [])
        acceptable_states = geo_config.get("acceptable_states", [])

        if state in preferred_states:
            status = MetricStatus.OUTSTANDING
            label = "Pref"
        elif state in acceptable_states:
            status = MetricStatus.ACCEPTABLE
            label = "Accept"
        else:
            status = MetricStatus.UNACCEPTABLE
            label = "Low"

        return Metric(
            name="Geographic Alignment",
            value=state,
            status=status,
            category=MetricCategory.PREFERENCE,
            ranges=MetricRange(
                outstanding="Pref",
                acceptable="Accept"
            ),
            display_value=f"{state} ({label})"
        )

    def _get_organization_size_metric(
        self,
        total_revenue: int
    ) -> Optional[Metric]:
        size_config = self.preferences_config.get("organization_size", {})
        if not size_config.get("enabled", False):
            return None

        if total_revenue == 0:
            return Metric(
                name="Organization Size",
                value=0,
                status=MetricStatus.UNKNOWN,
                category=MetricCategory.PREFERENCE,
                ranges=MetricRange(
                    outstanding="Small",
                    acceptable="Med"
                ),
                display_value="Unknown"
            )

        small_max = size_config.get("small_max", 500000)
        medium_max = size_config.get("medium_max", 5000000)

        if total_revenue < small_max:
            status = MetricStatus.OUTSTANDING
            size_label = "Small"
        elif total_revenue < medium_max:
            status = MetricStatus.ACCEPTABLE
            size_label = "Med"
        else:
            status = MetricStatus.UNACCEPTABLE
            size_label = "Large"

        return Metric(
            name="Organization Size",
            value=total_revenue,
            status=status,
            category=MetricCategory.PREFERENCE,
            ranges=MetricRange(
                outstanding="Small",
                acceptable="Med"
            ),
            display_value=f"${total_revenue:,.0f} ({size_label})"
        )
