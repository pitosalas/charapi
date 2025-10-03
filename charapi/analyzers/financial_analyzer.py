from typing import Optional
from ..data.charity_evaluation_result import FinancialMetrics, Ident
from ..data.data_field_manager import DataFieldManager


class FinancialAnalyzer:
    def __init__(self, config: dict):
        self.config = config
        self.data_manager = DataFieldManager(config)
        self.scoring_config = config.get("scoring", {}).get("financial", {})

    def extract_metrics(self, filing_data: dict, ein: str) -> FinancialMetrics:
        total_expenses = filing_data.get("totfuncexpns", 0)

        program_expenses_val = self.data_manager.get_field(Ident.PROGRAM_EXPENSES, ein)
        admin_expenses_val = self.data_manager.get_field(Ident.ADMIN_EXPENSES, ein)
        fundraising_expenses_val = self.data_manager.get_field(Ident.FUNDRAISING_EXPENSES, ein)

        program_expenses = int(program_expenses_val) if program_expenses_val is not None else 0
        admin_expenses = int(admin_expenses_val) if admin_expenses_val is not None else 0
        fundraising_expenses = int(fundraising_expenses_val) if fundraising_expenses_val is not None else 0

        if total_expenses > 0:
            program_ratio = (program_expenses / total_expenses * 100) if program_expenses else 0.0
            admin_ratio = (admin_expenses / total_expenses * 100) if admin_expenses else 0.0
            fundraising_ratio = (fundraising_expenses / total_expenses * 100) if fundraising_expenses else 0.0
        else:
            program_ratio = 0.0
            admin_ratio = 0.0
            fundraising_ratio = 0.0

        return FinancialMetrics(
            program_expense_ratio=program_ratio,
            admin_expense_ratio=admin_ratio,
            fundraising_expense_ratio=fundraising_ratio,
            net_assets=filing_data.get("totassetsend", 0) - filing_data.get("totliabend", 0),
            total_revenue=filing_data.get("totrevenue", 0),
            total_expenses=total_expenses,
            program_expenses=program_expenses,
            admin_expenses=admin_expenses,
            fundraising_expenses=fundraising_expenses,
            total_assets=filing_data.get("totassetsend", 0),
            total_liabilities=filing_data.get("totliabend", 0)
        )

    def get_sector_benchmarks(self, ntee_code: Optional[str]) -> dict:
        if not ntee_code:
            return self.scoring_config

        sector = ntee_code[0] if ntee_code else None

        sector_overrides = self.scoring_config.get("sector_overrides", {})

        if sector and sector in sector_overrides:
            benchmarks = self.scoring_config.copy()
            benchmarks.update(sector_overrides[sector])
            return benchmarks

        return self.scoring_config

    def calculate_score(self, metrics: FinancialMetrics, ntee_code: Optional[str] = None) -> float:
        benchmarks = self.get_sector_benchmarks(ntee_code)

        program_target = benchmarks.get("program_expense_target", 0.75)
        admin_limit = benchmarks.get("admin_expense_limit", 0.15)
        fundraising_limit = benchmarks.get("fundraising_expense_limit", 0.15)
        program_max = benchmarks.get("program_score_max", 40)
        admin_max = benchmarks.get("admin_score_max", 20)
        fundraising_max = benchmarks.get("fundraising_score_max", 20)
        stability_max = benchmarks.get("stability_score_max", 20)

        program_ratio = metrics.program_expense_ratio / 100.0
        admin_ratio = metrics.admin_expense_ratio / 100.0
        fundraising_ratio = metrics.fundraising_expense_ratio / 100.0

        program_score = min(program_max * (program_ratio / program_target), program_max)
        admin_score = max(0, admin_max * (admin_limit - admin_ratio) / admin_limit)
        fundraising_score = max(0, fundraising_max * (fundraising_limit - fundraising_ratio) / fundraising_limit)
        stability_score = stability_max if metrics.net_assets > 0 else 0

        return program_score + admin_score + fundraising_score + stability_score