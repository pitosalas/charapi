from typing import List
from ..data.charity_evaluation_result import (
    ExternalValidation,
    Ident,
    Metric,
    MetricRange,
    MetricStatus,
    MetricCategory
)
from ..data.data_field_manager import DataFieldManager


class ValidationScorer:
    def __init__(self, config: dict):
        self.config = config
        self.data_manager = DataFieldManager(config)

    def get_validation_data(self, ein: str) -> ExternalValidation:
        rating_val = self.data_manager.get_field(Ident.CHARITY_NAVIGATOR_RATING, ein)

        if rating_val is None:
            rating = None
            score = 0.0
        else:
            rating = int(rating_val)
            score = rating * 5.0

        return ExternalValidation(
            charity_navigator_rating=rating,
            charity_navigator_score=score,
            has_transparency_seal=False,
            has_advisory_alerts=False,
            negative_news_alerts=0
        )

    def calculate_bonus(self, validation: ExternalValidation) -> float:
        return validation.charity_navigator_score

    def get_validation_metrics(self, ein: str) -> List[Metric]:
        rating_val = self.data_manager.get_field(Ident.CHARITY_NAVIGATOR_RATING, ein)

        metrics_list = []

        if rating_val is None:
            rating_status = MetricStatus.UNKNOWN
            display_value = "Not rated"
        else:
            rating = int(rating_val)
            if rating >= 4:
                rating_status = MetricStatus.OUTSTANDING
            elif rating >= 3:
                rating_status = MetricStatus.ACCEPTABLE
            else:
                rating_status = MetricStatus.UNACCEPTABLE
            display_value = f"{rating} stars"

        metrics_list.append(Metric(
            name="Charity Navigator Rating",
            value=rating_val,
            status=rating_status,
            category=MetricCategory.VALIDATION,
            ranges=MetricRange(
                outstanding="≥4 stars",
                acceptable="≥3 stars"
            ),
            display_value=display_value
        ))

        return metrics_list