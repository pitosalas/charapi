from ..data.charity_evaluation_result import ExternalValidation
from ..data.data_field_manager import DataFieldManager


class ValidationScorer:
    def __init__(self, config: dict):
        self.config = config
        self.data_manager = DataFieldManager(config)

    def get_validation_data(self, ein: str) -> ExternalValidation:
        rating_val = self.data_manager.get_field("charity_navigator_rating", ein)

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