from ..data.charity_evaluation_result import FinancialMetrics
from ..data.data_field_manager import DataFieldManager


class FinancialAnalyzer:
    def __init__(self, config: dict):
        self.data_manager = DataFieldManager(config)

    def extract_metrics(self, filing_data: dict, ein: str) -> FinancialMetrics:
        total_expenses = filing_data.get("totfuncexpns", 0)
        total_revenue = filing_data.get("totrevenue", 0)

        program_expenses_str = self.data_manager.get_field("program_expenses", ein)
        admin_expenses_str = self.data_manager.get_field("admin_expenses", ein)
        fundraising_expenses_str = self.data_manager.get_field("fundraising_expenses", ein)

        program_expenses = 0 if program_expenses_str == "manual data not available" else int(program_expenses_str)
        admin_expenses = 0 if admin_expenses_str == "manual data not available" else int(admin_expenses_str)
        fundraising_expenses = 0 if fundraising_expenses_str == "manual data not available" else int(fundraising_expenses_str)

        # Calculate ratios as percentages when total expenses > 0
        if total_expenses > 0:
            program_ratio = (program_expenses / total_expenses * 100) if program_expenses else 0.0
            admin_ratio = (admin_expenses / total_expenses * 100) if admin_expenses else 0.0
            fundraising_ratio = (fundraising_expenses / total_expenses * 100) if fundraising_expenses else 0.0
        else:
            program_ratio = admin_ratio = fundraising_ratio = 0.0

        return FinancialMetrics(
            program_expense_ratio=program_ratio,
            admin_expense_ratio=admin_ratio,
            fundraising_expense_ratio=fundraising_ratio,
            net_assets=filing_data.get("totassetsend", 0) - filing_data.get("totliabend", 0),
            total_revenue=total_revenue,
            total_expenses=total_expenses,
            program_expenses=program_expenses,
            admin_expenses=admin_expenses,
            fundraising_expenses=fundraising_expenses,
            total_assets=filing_data.get("totassetsend", 0),
            total_liabilities=filing_data.get("totliabend", 0)
        )

    def calculate_score(self, metrics: FinancialMetrics) -> float:
        # This is still a stub - would need detailed implementation
        return 75.0