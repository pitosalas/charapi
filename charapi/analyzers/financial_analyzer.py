from ..data.charity_evaluation_result import FinancialMetrics


class FinancialAnalyzer:
    def extract_metrics(self, filing_data: dict) -> FinancialMetrics:
        # Extract raw values
        total_expenses = filing_data.get("totfuncexpns", 0)
        total_revenue = filing_data.get("totrevenue", 0)

        # ProPublica doesn't break down admin/fundraising/program expenses
        # These require IRS Form 990 detailed parsing
        program_expenses = filing_data.get("totprogrevexp", 0)
        admin_expenses = filing_data.get("totadminexp", 0)
        fundraising_expenses = filing_data.get("totfndrsexp", 0)

        # Calculate ratios when total expenses > 0
        if total_expenses > 0:
            program_ratio = program_expenses / total_expenses if program_expenses else 0.0
            admin_ratio = admin_expenses / total_expenses if admin_expenses else 0.0
            fundraising_ratio = fundraising_expenses / total_expenses if fundraising_expenses else 0.0
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