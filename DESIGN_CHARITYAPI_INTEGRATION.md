# CharityAPI.org Integration Design

## Overview
Integrate CharityAPI.org to replace manual IRS compliance data entry and add sophisticated organization type analysis with sector-specific benchmarking.

## Goals
1. Remove redundant manual data entry (in_pub78, is_revoked, has_recent_filing)
2. Prefer API data over manual data
3. Add organization type evaluation (501c3 status, foundation type, filing requirements)
4. Enable sector-specific financial benchmarking using NTEE codes
5. Add organizational maturity scoring
6. Make all scoring constants configurable in config.yaml

## Data Migration

### Fields Moving from Manual → CharityAPI.org

| Manual Field | CharityAPI Field | Mapping Logic |
|--------------|------------------|---------------|
| in_pub78 | deductibility | `deductibility == 1` = eligible |
| is_revoked | status | `status == 1` = active, else revoked |
| has_recent_filing | tax_period | Parse YYYYMM, check if < 3 years old |

### Fields Remaining Manual

| Field | Reason |
|-------|--------|
| program_expenses | Not available in any API, requires Form 990 PDF |
| admin_expenses | Not available in any API, requires Form 990 PDF |
| fundraising_expenses | Not available in any API, requires Form 990 PDF |
| charity_navigator_rating | Requires Charity Navigator API (future) |

### New Fields from CharityAPI.org

| Field | Use Case |
|-------|----------|
| foundation | Distinguish public charity (15) from private foundation |
| subsection | Verify 501(c)(3) status (value = 3) |
| filing_req_cd | Transparency check (1 = required, 2 = not required) |
| ntee_cd | Sector-specific benchmarking (A=arts, E=health, etc.) |
| ruling | Organization age/maturity scoring |
| ntee_cd | Category classification for reporting |

## Architecture Changes

### 1. New Client: CharityAPIClient

**File**: `charapi/clients/charityapi_client.py`

```python
class CharityAPIClient(BaseAPIClient):
    def __init__(self, config_path: str):
        super().__init__("charityapi", config_path)

    def get_organization(self, ein: str):
        """Get organization data by EIN"""
        url = f"{self.base_url}/organizations/{ein}"
        response = self._make_request("GET", url)
        return response.get("data")

    def get_deductibility_status(self, ein: str):
        """Check if organization is eligible for tax-deductible donations"""
        org = self.get_organization(ein)
        return org.get("deductibility") == 1 if org else False

    def get_revocation_status(self, ein: str):
        """Check if organization's tax-exempt status is revoked"""
        org = self.get_organization(ein)
        return org.get("status") != 1 if org else True

    def get_recent_filing_status(self, ein: str):
        """Check if organization has filed Form 990 in last 3 years"""
        org = self.get_organization(ein)
        if not org or not org.get("tax_period"):
            return False

        from datetime import datetime
        tax_period = str(org["tax_period"])
        tax_year = int(tax_period[:4])
        current_year = datetime.now().year
        return (current_year - tax_year) <= 3
```

### 2. New Analyzer: OrganizationTypeAnalyzer

**File**: `charapi/analyzers/organization_type_analyzer.py`

```python
class OrganizationTypeAnalyzer:
    def __init__(self, config: dict):
        self.config = config

    def analyze(self, charityapi_data: dict):
        """Analyze organization type for penalties/bonuses"""
        score = 0
        issues = []

        # 501(c)(3) check
        subsection = charityapi_data.get("subsection")
        if subsection != 3:
            penalty = self.config["scoring"]["organization_type"]["non_501c3_penalty"]
            score -= penalty
            issues.append(f"Not a 501(c)(3) organization (subsection: {subsection})")

        # Foundation type check
        foundation = charityapi_data.get("foundation")
        public_charity_code = self.config["scoring"]["organization_type"]["public_charity_code"]
        if foundation != public_charity_code:
            penalty = self.config["scoring"]["organization_type"]["private_foundation_penalty"]
            score -= penalty
            issues.append(f"Private foundation, not public charity (code: {foundation})")

        # Filing requirement check
        filing_req = charityapi_data.get("filing_req_cd")
        if filing_req != 1:
            penalty = self.config["scoring"]["organization_type"]["no_filing_requirement_penalty"]
            score -= penalty
            issues.append("Not required to file Form 990 (lack of transparency)")

        # Organizational maturity bonus
        ruling = charityapi_data.get("ruling")
        if ruling:
            from datetime import datetime
            ruling_year = ruling // 100
            years_operating = datetime.now().year - ruling_year
            min_years = self.config["scoring"]["organization_type"]["established_years_threshold"]

            if years_operating >= min_years:
                bonus = self.config["scoring"]["organization_type"]["established_bonus"]
                score += bonus

        return {
            "score": score,
            "issues": issues,
            "subsection": subsection,
            "foundation_type": foundation,
            "filing_requirement": filing_req,
            "years_operating": years_operating if ruling else None
        }
```

### 3. Updated FinancialAnalyzer with NTEE Benchmarking

**File**: `charapi/analyzers/financial_analyzer.py` (updated)

```python
def get_sector_benchmarks(self, ntee_code: str):
    """Get sector-specific financial benchmarks based on NTEE code"""
    if not ntee_code:
        return self.config["scoring"]["financial"]

    # NTEE major category is first character
    sector = ntee_code[0] if ntee_code else None

    sector_overrides = self.config["scoring"]["financial"].get("sector_overrides", {})

    if sector and sector in sector_overrides:
        benchmarks = self.config["scoring"]["financial"].copy()
        benchmarks.update(sector_overrides[sector])
        return benchmarks

    return self.config["scoring"]["financial"]
```

### 4. Updated DataFieldManager

**File**: `charapi/data/data_field_manager.py` (updated)

Add support for `charityapi` as a data source alongside `manual` and `api`.

```python
def get_field_value(self, field_name: str, ein: str, propublica_data: dict, charityapi_data: dict):
    """Get field value from configured source"""
    source = self.field_config.get(field_name, {}).get("source")

    if source == "charityapi":
        return self._get_from_charityapi(field_name, charityapi_data)
    elif source == "api":
        return self._get_from_propublica(field_name, propublica_data)
    elif source == "manual":
        return self._get_from_manual(field_name, ein)

    return None

def _get_from_charityapi(self, field_name: str, charityapi_data: dict):
    """Extract field from CharityAPI.org data with mapping"""
    mapping = {
        "in_pub78": lambda d: d.get("deductibility") == 1,
        "is_revoked": lambda d: d.get("status") != 1,
        "has_recent_filing": self._check_recent_filing,
        "ntee_code": lambda d: d.get("ntee_cd"),
        "subsection": lambda d: d.get("subsection"),
        "foundation_type": lambda d: d.get("foundation"),
        "filing_requirement": lambda d: d.get("filing_req_cd"),
        "ruling_year": lambda d: d.get("ruling") // 100 if d.get("ruling") else None,
    }

    if field_name in mapping:
        return mapping[field_name](charityapi_data)

    return charityapi_data.get(field_name)
```

## Configuration Changes

### config.yaml Updates

```yaml
# CharityAPI.org configuration
charityapi:
  base_url: "https://api.charityapi.org/api"
  api_key: "${CHARITYAPI_KEY}"
  timeout: 30
  mock_mode: false

# Updated data_fields configuration
data_fields:
  # Compliance fields now from CharityAPI
  in_pub78:
    source: charityapi
    field: "deductibility"
  is_revoked:
    source: charityapi
    field: "status"
  has_recent_filing:
    source: charityapi
    field: "tax_period"

  # Organization type fields from CharityAPI
  ntee_code:
    source: charityapi
    field: "ntee_cd"
  subsection:
    source: charityapi
    field: "subsection"
  foundation_type:
    source: charityapi
    field: "foundation"
  filing_requirement:
    source: charityapi
    field: "filing_req_cd"
  ruling_year:
    source: charityapi
    field: "ruling"

  # Expense fields remain manual
  program_expenses:
    source: manual
    path: "fiscal_year_2024.expenses.program"
  admin_expenses:
    source: manual
    path: "fiscal_year_2024.expenses.admin"
  fundraising_expenses:
    source: manual
    path: "fiscal_year_2024.expenses.fundraising"

  # Charity Navigator remains manual
  charity_navigator_rating:
    source: manual
    path: "organization.charity_navigator_rating.stars"

# Updated scoring configuration
scoring:
  financial:
    program_expense_target: 0.75
    admin_expense_limit: 0.15
    fundraising_expense_limit: 0.15
    program_score_max: 40
    admin_score_max: 20
    fundraising_score_max: 20
    stability_score_max: 20

    # Sector-specific overrides by NTEE major category
    sector_overrides:
      A:  # Arts, Culture, Humanities
        program_expense_target: 0.65
        admin_expense_limit: 0.20
      B:  # Education
        program_expense_target: 0.80
        admin_expense_limit: 0.12
      E:  # Health
        program_expense_target: 0.80
        admin_expense_limit: 0.12
      H:  # Medical Research
        program_expense_target: 0.70
        admin_expense_limit: 0.18
      P:  # Human Services
        program_expense_target: 0.75
        admin_expense_limit: 0.15
      Q:  # International
        program_expense_target: 0.70
        admin_expense_limit: 0.18

  organization_type:
    # 501(c)(3) verification
    non_501c3_penalty: 25

    # Foundation type
    public_charity_code: 15
    private_foundation_penalty: 15

    # Filing requirements
    no_filing_requirement_penalty: 10

    # Organizational maturity
    established_years_threshold: 20
    established_bonus: 5

  compliance:
    not_in_pub78_penalty: 50
    revoked_penalty: 50
    no_recent_filing_penalty: 50

# Caching configuration
caching:
  enabled: true
  database_path: "cache/charapi_cache.db"
  default_ttl_hours: 24
  propublica_ttl_hours: 24
  charityapi_ttl_hours: 168  # 7 days (IRS master file data changes slowly)
  charity_navigator_ttl_hours: 168
  cleanup_on_startup: true
```

## Updated Manual Data Structure

### brief_manual.yaml (simplified)

```yaml
# Only expense data remains - compliance data now from CharityAPI.org
131644147:  # Planned Parenthood Federation
  name: "PLANNED PARENTHOOD FEDERATION OF"

  # Charity Navigator rating (until API integration)
  charity_navigator_rating:
    stars: 3

  # Expense breakdowns from Form 990 Part IX
  fiscal_year_2023:
    expenses:
      program: 300000000
      admin: 50000000
      fundraising: 28000000
```

## Implementation Order

### Phase 1: Core Integration (Tasks 2-4)
1. Create `CharityAPIClient` extending `BaseAPIClient`
2. Update `config.yaml` with charityapi configuration
3. Update `DataFieldManager` to support charityapi source
4. Test basic CharityAPI integration

### Phase 2: Compliance Migration (Task 5)
1. Update `ComplianceChecker` to use CharityAPI data
2. Remove manual compliance fields from YAML files
3. Update tests for compliance checking

### Phase 3: New Analysis (Tasks 6-7)
1. Create `OrganizationTypeAnalyzer`
2. Update `FinancialAnalyzer` for NTEE benchmarking
3. Add sector-specific scoring tests

### Phase 4: Integration (Task 8)
1. Update `CharityEvaluator` to use new client and analyzers
2. Update scoring calculation to include organization type score
3. Update demo.py output format

### Phase 5: Cleanup (Tasks 9-10)
1. Clean up manual YAML files
2. Update all tests
3. Update CURRENT.md and README.md

## New Scoring Formula

```
Total Score =
  Financial Health Score (0-100, NTEE-adjusted)
  + Validation Bonus (0-20)
  + Organization Type Score (-50 to +5)
  + Compliance Penalties (-150 to 0)

Organization Type Score breakdown:
  - Non-501(c)(3): -25 points
  - Private foundation: -15 points
  - No filing requirement: -10 points
  - Established (20+ years): +5 points
```

## Benefits

1. **Reduced Manual Entry**: 3 compliance fields automated (43% reduction)
2. **More Accurate**: Real-time IRS master file data vs manual entry
3. **Smarter Evaluation**: Sector-specific benchmarks instead of one-size-fits-all
4. **Better Scoring**: Organization type matters (501c3, public charity, transparency)
5. **Highly Configurable**: All constants in config.yaml for easy tuning
6. **Better UX**: Less data entry, more accurate results

## Testing Strategy

1. Unit tests for `CharityAPIClient`
2. Unit tests for `OrganizationTypeAnalyzer`
3. Unit tests for NTEE-based benchmarking in `FinancialAnalyzer`
4. Integration tests for end-to-end evaluation with CharityAPI
5. Mock mode support for all CharityAPI operations
6. Test edge cases: missing NTEE codes, invalid subsections, etc.

## Risk Mitigation

1. **API Availability**: Use caching with 7-day TTL (IRS data changes slowly)
2. **Missing Data**: Graceful fallback when CharityAPI fields are null
3. **Rate Limits**: Cache aggressively, batch evaluations if needed
4. **Cost**: Free tier allows 200 req/hour, paid tier is affordable
5. **Backward Compatibility**: Keep manual data support as fallback

## Success Metrics

- ✅ 3 manual fields eliminated
- ✅ Sector-specific benchmarking working for major NTEE categories
- ✅ Organization type scoring integrated
- ✅ All tests passing
- ✅ Documentation updated
- ✅ Demo showing CharityAPI data in use
