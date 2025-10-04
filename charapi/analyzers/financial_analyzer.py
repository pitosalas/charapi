from typing import Optional, List
from ..data.charity_evaluation_result import (
    FinancialMetrics,
    Ident,
    Metric,
    MetricRange,
    MetricStatus,
    MetricCategory
)
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

    def get_financial_metrics(self, financial_metrics: FinancialMetrics, ntee_code: Optional[str] = None, filing_req_cd: Optional[int] = None) -> List[Metric]:
        benchmarks = self.get_sector_benchmarks(ntee_code)

        program_target_acceptable = benchmarks.get("program_expense_target", 0.75)
        program_target_outstanding = benchmarks.get("program_expense_target_outstanding", program_target_acceptable + 0.05)
        admin_limit_acceptable = benchmarks.get("admin_expense_limit", 0.15)
        admin_limit_outstanding = benchmarks.get("admin_expense_limit_outstanding", admin_limit_acceptable - 0.05)
        fundraising_limit_acceptable = benchmarks.get("fundraising_expense_limit", 0.15)
        fundraising_limit_outstanding = benchmarks.get("fundraising_expense_limit_outstanding", fundraising_limit_acceptable - 0.05)

        metrics_list = []

        filing_not_required = filing_req_cd is not None and filing_req_cd != 1

        program_ratio = financial_metrics.program_expense_ratio
        if program_ratio >= (program_target_outstanding * 100):
            program_status = MetricStatus.OUTSTANDING
        elif program_ratio >= (program_target_acceptable * 100):
            program_status = MetricStatus.ACCEPTABLE
        elif program_ratio == 0 and filing_not_required:
            program_status = MetricStatus.ACCEPTABLE
        else:
            program_status = MetricStatus.UNACCEPTABLE if program_ratio > 0 else MetricStatus.UNKNOWN

        metrics_list.append(Metric(
            name="Program Expenses",
            value=program_ratio,
            status=program_status,
            category=MetricCategory.FINANCIAL,
            ranges=MetricRange(
                outstanding=f"≥{program_target_outstanding*100:.0f}%",
                acceptable=f"≥{program_target_acceptable*100:.0f}%"
            ),
            display_value=f"{program_ratio:.1f}%" if program_ratio > 0 else "Unknown"
        ))

        admin_ratio = financial_metrics.admin_expense_ratio
        if admin_ratio == 0 and filing_not_required:
            admin_status = MetricStatus.ACCEPTABLE
        elif admin_ratio == 0:
            admin_status = MetricStatus.UNKNOWN
        elif admin_ratio <= (admin_limit_outstanding * 100):
            admin_status = MetricStatus.OUTSTANDING
        elif admin_ratio <= (admin_limit_acceptable * 100):
            admin_status = MetricStatus.ACCEPTABLE
        else:
            admin_status = MetricStatus.UNACCEPTABLE

        metrics_list.append(Metric(
            name="Admin Expenses",
            value=admin_ratio,
            status=admin_status,
            category=MetricCategory.FINANCIAL,
            ranges=MetricRange(
                outstanding=f"≤{admin_limit_outstanding*100:.0f}%",
                acceptable=f"≤{admin_limit_acceptable*100:.0f}%"
            ),
            display_value=f"{admin_ratio:.1f}%" if admin_ratio > 0 else "Unknown"
        ))

        fundraising_ratio = financial_metrics.fundraising_expense_ratio
        if fundraising_ratio == 0 and filing_not_required:
            fundraising_status = MetricStatus.ACCEPTABLE
        elif fundraising_ratio == 0:
            fundraising_status = MetricStatus.UNKNOWN
        elif fundraising_ratio <= (fundraising_limit_outstanding * 100):
            fundraising_status = MetricStatus.OUTSTANDING
        elif fundraising_ratio <= (fundraising_limit_acceptable * 100):
            fundraising_status = MetricStatus.ACCEPTABLE
        else:
            fundraising_status = MetricStatus.UNACCEPTABLE

        metrics_list.append(Metric(
            name="Fundraising Expenses",
            value=fundraising_ratio,
            status=fundraising_status,
            category=MetricCategory.FINANCIAL,
            ranges=MetricRange(
                outstanding=f"≤{fundraising_limit_outstanding*100:.0f}%",
                acceptable=f"≤{fundraising_limit_acceptable*100:.0f}%"
            ),
            display_value=f"{fundraising_ratio:.1f}%" if fundraising_ratio > 0 else "Unknown"
        ))

        if financial_metrics.net_assets > 0:
            net_assets_status = MetricStatus.ACCEPTABLE
            net_assets_display = f"${financial_metrics.net_assets:,.0f}"
        elif financial_metrics.net_assets < 0:
            net_assets_status = MetricStatus.UNACCEPTABLE
            net_assets_display = f"-${abs(financial_metrics.net_assets):,.0f}"
        else:
            net_assets_status = MetricStatus.UNKNOWN
            net_assets_display = "Unknown"

        metrics_list.append(Metric(
            name="Net Assets",
            value=financial_metrics.net_assets,
            status=net_assets_status,
            category=MetricCategory.FINANCIAL,
            ranges=MetricRange(
                outstanding="Positive",
                acceptable="Positive"
            ),
            display_value=net_assets_display
        ))

        return metrics_list