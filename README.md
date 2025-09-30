# CharAPI - Charity Evaluation API

A comprehensive charity evaluation API that analyzes nonprofit organizations using multiple data sources and provides scoring with letter grades (A-F).

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

### IRS Tax Exempt Organization Data 🔄 Planned
**Sources**: Bulk CSV downloads from IRS

**Information Retrieved:**
- Publication 78 status (tax-deductible eligibility)
- Auto-revocation list (organizations that lost exemption)
- EO Business Master File (comprehensive organization details)
- Recent filing compliance status

### Charity Navigator API 🔄 Planned
**Base URL**: `https://developer.charitynavigator.org/`

**Information Retrieved:**
- Overall star rating (1-4 stars)
- Financial performance score
- Accountability & transparency score
- Advisory alerts and warnings
- Transparency seal status

### CharityAPI.org 🔄 Planned
**Base URL**: `https://www.charityapi.org/`

**Information Retrieved:**
- Real-time IRS tax-exempt status
- Current public charity classification
- Compliance verification

### Candid APIs 🔄 Future Enhancement
**Base URL**: `https://candid.org/use-our-data/apis`

**Information Retrieved:**
- Seal of Transparency status
- News alerts and mentions
- Advanced compliance validation

## Calculation Equations & Derived Metrics

### Financial Health Score (0-100 points)

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

### Trend Analysis Modifier (±20 points)

#### Revenue Growth Rate
```
Annual Growth Rate = (Current Year Revenue - Previous Year Revenue) / Previous Year Revenue
5-Year Average Growth = Average of annual growth rates over 5 years

Growth Modifier = ±10 points based on consistency:
- Stable positive growth (2-8% annually): +10 points
- Volatile but positive: +5 points
- Declining revenue: -10 points
```

#### Volatility Penalty
```
Revenue Volatility = Standard Deviation of annual revenue changes
Volatility Penalty = min(10, (Volatility / 0.3) * 10)

Final Trend Modifier = Growth Modifier - Volatility Penalty
Range: -20 to +10 points
```

### External Validation Bonus (0-45 points)

#### Charity Navigator Integration
```
Star Rating Bonus = Charity Navigator Stars × 5 points (max 20 points)
No Advisory Alerts = +5 points
```

#### Transparency & Compliance
```
Transparency Seal = +10 points
IRS Pub 78 Listed = +5 points
Recent Form 990 Filing = +5 points
```

#### Negative News Penalty
```
Negative News Alerts = -10 points per significant alert
```

### Compliance Penalties

#### IRS Status Violations
```
Not in IRS Pub 78 = -50 points
Auto-revoked status = -100 points (immediate F grade)
No recent filing (>3 years) = -25 points
```

### Final Grade Assignment

#### Total Score Calculation
```
Total Score = Financial Health Score + Trend Modifier + Validation Bonus + Compliance Penalties
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
- ✅ **Basic Financial Metrics**: Revenue, assets, liabilities extracted
- 🔄 **Financial Ratios**: Require detailed Form 990 parsing
- 🔄 **Trend Analysis**: Multi-year data processing needed
- 🔄 **External Validation**: API registrations required
- 🔄 **Compliance Checking**: IRS bulk data integration needed

Run `python demo.py real` to see which calculations require additional API integrations.