from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class Ident(Enum):
    PROGRAM_EXPENSES = "program_expenses"
    ADMIN_EXPENSES = "admin_expenses"
    FUNDRAISING_EXPENSES = "fundraising_expenses"
    CHARITY_NAVIGATOR_RATING = "charity_navigator_rating"
    IN_PUB78 = "in_pub78"
    IS_REVOKED = "is_revoked"
    HAS_RECENT_FILING = "has_recent_filing"
    TOTAL_REVENUE = "total_revenue"
    TOTAL_EXPENSES = "total_expenses"
    NTEE_CODE = "ntee_code"
    SUBSECTION = "subsection"
    FOUNDATION_TYPE = "foundation_type"
    FILING_REQUIREMENT = "filing_requirement"
    RULING_YEAR = "ruling_year"


class Issue(Enum):
    MISSING_CHARITY_NAVIGATOR = "MISSING_CHARITY_NAVIGATOR"
    MISSING_EXPENSE_DATA = "MISSING_EXPENSE_DATA"
    COMPLIANCE_FAILURE = "COMPLIANCE_FAILURE"


@dataclass
class FinancialMetrics:
    program_expense_ratio: float
    admin_expense_ratio: float
    fundraising_expense_ratio: float
    net_assets: float
    total_revenue: int
    total_expenses: int
    program_expenses: int
    admin_expenses: int
    fundraising_expenses: int
    total_assets: int
    total_liabilities: int


@dataclass
class ComplianceCheck:
    is_compliant: bool
    issues: List[str]
    in_pub78: bool
    is_revoked: bool
    has_recent_filing: bool


@dataclass
class OrganizationType:
    score: float
    issues: List[str]
    subsection: Optional[int]
    foundation_type: Optional[int]
    filing_requirement: Optional[int]
    years_operating: Optional[int]


@dataclass
class ExternalValidation:
    charity_navigator_rating: Optional[int]
    charity_navigator_score: float
    has_transparency_seal: bool
    has_advisory_alerts: bool
    negative_news_alerts: int


@dataclass
class CharityEvaluationResult:
    ein: str
    organization_name: str
    total_score: float
    grade: str
    financial_score: float
    validation_bonus: float
    compliance_penalty: float
    organization_type_score: float
    financial_metrics: FinancialMetrics
    compliance_check: ComplianceCheck
    external_validation: ExternalValidation
    organization_type: OrganizationType
    evaluation_timestamp: str
    data_sources_used: List[str]
    issues: List[str]
    issue_codes: List[Issue]