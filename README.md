# CharAPI - Charity Evaluation API

A comprehensive charity evaluation API that analyzes nonprofit organizations using multiple data sources and provides transparent metric-by-metric health assessment without overall scores.

## Quick Start

```bash
# Install dependencies
uv sync

# Run demo with mock data
uv run python demo.py mock

# Run demo with live ProPublica API
uv run python demo.py real

# Use in your code
from charapi import evaluate_charity
result = evaluate_charity("530196605", "charapi/config/config.yaml")
```

## Data Sources & Information Retrieved

### ProPublica Nonprofit Explorer API ✅ Implemented
**Base URL**: `https://projects.propublica.org/nonprofits/api/v2/`

**Information Retrieved:**
- Organization basic info: name, EIN, address, city, state, zip
- Tax-exempt status codes and classification
- Financial data from Form 990 filings:
  - `totrevenue` - Total revenue
  - `totfuncexpns` - Total functional expenses
  - `totassetsend` - Total assets (end of year)
  - `totliabend` - Total liabilities (end of year)
  - `totprogrevexp` - Program service expenses
  - `totadminexp` - Administrative expenses
  - `totfndrsexp` - Fundraising expenses
- Multiple years of filings (when available)
- PDF links to original Form 990 documents

### Manual Data Entry System ✅ Implemented
**Location**: `manual/` directory

**Information Managed:**
- Expense breakdowns (program/admin/fundraising) from Form 990 PDFs
- Charity Navigator ratings (1-4 stars)
- Multi-year fiscal data (FY2024, 2023, 2022) with automatic fallback

**Note**: IRS compliance fields (in_pub78, is_revoked, has_recent_filing) are now automated via CharityAPI

**Files:**
- `brief_manual.yaml` - Simplified format (recommended)
- `manual_data.yaml` - Comprehensive format
- `irs990/` - Downloaded Form 990 PDFs for reference

**Data Structure (per EIN):**
```yaml
530196605:  # American Red Cross
  name: "American National Red Cross"
  in_pub78: true
  is_revoked: false
  has_recent_filing: true
  charity_navigator_rating: 3
  fiscal_year_2024:
    program_expenses: 0
    admin_expenses: 0
    fundraising_expenses: 0
  fiscal_year_2023:
    program_expenses: 2500000000
    admin_expenses: 150000000
    fundraising_expenses: 200000000
```

### Charity Navigator Ratings ✅ Manual Entry
**Implementation**: Manual data entry in YAML files

**Information Retrieved:**
- Star rating (1-4 stars) - 5 points per star
- Stored in manual data files per EIN

### CharityAPI.org ✅ Implemented
**Base URL**: `https://api.charityapi.org/api`

**Information Retrieved:**
- Organization name and NTEE category code
- 501(c)(3) status (subsection field)
- Public charity vs private foundation classification
- Form 990 filing requirements
- IRS Publication 78 listing status
- Tax-exempt status and revocation status
- Recent filing information
- Organization ruling year

### Candid APIs 🔄 Future Enhancement
**Base URL**: `https://candid.org/use-our-data/apis`

**Information Retrieved:**
- Seal of Transparency status
- News alerts and mentions
- Advanced compliance validation

## Calculation Equations & Derived Metrics

### Financial Health Score (0-100 points) ✅ Implemented

#### Program Expense Ratio
```
Program Expense Ratio = Program Expenses / Total Expenses
Target: ≥75% (40 points maximum)

Score = min(40, (Program Expense Ratio / 0.75) * 40)
```

#### Administrative Expense Ratio
```
Admin Expense Ratio = Administrative Expenses / Total Expenses
Target: ≤15% (20 points maximum)

Score = max(0, 20 - ((Admin Expense Ratio - 0.15) * 133.33))
```

#### Fundraising Expense Ratio
```
Fundraising Expense Ratio = Fundraising Expenses / Total Expenses
Target: ≤15% (20 points maximum)

Score = max(0, 20 - ((Fundraising Expense Ratio - 0.15) * 133.33))
```

#### Financial Stability
```
Net Assets = Total Assets - Total Liabilities
Stability Score = 20 points if Net Assets > 0, else 0 points
```

### External Validation Bonus (0-20 points) ✅ Implemented

#### Charity Navigator Integration
```
Star Rating Bonus = Charity Navigator Stars × 5 points (max 20 points)
```

**Note**: Ratings are entered manually in `brief_manual.yaml` or `manual_data.yaml`

### Compliance Penalties ✅ Implemented

#### IRS Status Violations
```
Not in IRS Pub 78 = -50 points
Auto-revoked status = -50 points
No recent filing (>3 years) = -50 points
```

**Note**: All compliance data entered manually in YAML files

### Final Grade Assignment

#### Total Score Calculation
```
Total Score = Financial Health Score + Validation Bonus + Compliance Penalties
```

#### Grade Thresholds
```
A: ≥90 points - Excellent charity
B: 75-89 points - Good charity
C: 60-74 points - Acceptable charity
D: 45-59 points - Poor charity
F: <45 points - Failing charity
```

## Current Implementation Status

- ✅ **ProPublica API**: Fully integrated with real and mock modes
- ✅ **Manual Data System**: YAML-based entry for expense breakdowns and compliance
- ✅ **SQLite Caching**: 24-hour cache for ProPublica API responses
- ✅ **Financial Scoring**: Real formulas implemented (program/admin/fundraising ratios + stability)
- ✅ **Charity Navigator**: Manual star rating entry (1-4 stars)
- ✅ **Multi-year Fallback**: Automatically falls back FY2024→2023→2022 when values are zero
- ❌ **Trend Analysis**: Removed (insufficient multi-year data)
- ❌ **IRS Integration**: Removed (using manual YAML entry instead)

Run `python demo.py real` to see which manual data fields need population.

## Setup Instructions

### 1. Install Dependencies
```bash
uv sync
```

### 2. Configure ProPublica API (Optional for Mock Mode)
Add API key to `charapi/config/config.yaml` if using real mode.

### 3. Populate Manual Data
Edit `manual/brief_manual.yaml` to add:
- Expense breakdowns from Form 990 PDFs (store PDFs in `manual/irs990/`)
- IRS compliance status (in_pub78, is_revoked, has_recent_filing)
- Charity Navigator star ratings (1-4)

**Example:**
```yaml
530196605:  # Your charity's EIN
  name: "Charity Name"
  in_pub78: true
  is_revoked: false
  has_recent_filing: true
  charity_navigator_rating: 3
  fiscal_year_2023:
    program_expenses: 2500000000
    admin_expenses: 150000000
    fundraising_expenses: 200000000
```

### 4. Run Demo
```bash
# Mock mode (no API or manual data needed)
uv run python demo.py mock

# Real mode (requires ProPublica API, manual data optional)
uv run python demo.py real
```