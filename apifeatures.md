## General Requirement

* Use APIs and manual data sources to research charities
* Goal: Given an EIN, prepare a comprehensive datastructure to determine if it's a charity worth supporting
* Configuration via YAML files
* Separate Python module/package for reuse in charapi and other applications

## Data Sources

### **1. ProPublica Nonprofit Explorer API** ✅ IMPLEMENTED
- **URL**: `https://projects.propublica.org/nonprofits/api/v2/`
- **Status**: Fully implemented with caching
- **Endpoints**:
  - Search: `/search.json?q={query}`
  - Organization: `/organizations/{ein}.json`
- **Key Fields**: `totrevenue`, `totfuncexpns`, `totassetsend`, `totliabend`, `tax_prd_yr`
- **Features**: Mock mode, SQLite caching, real-time API calls

### **2. Manual Data Entry System** ✅ IMPLEMENTED
- **Location**: `manual/` directory with YAML files
- **Files**:
  - `brief_manual.yaml` - Simplified format (recommended)
  - `manual_data.yaml` - Comprehensive format
  - `irs990/` - Downloaded Form 990 PDFs for reference
  - `eins.yaml` - EIN registry
- **Key Fields**:
  - Expense breakdowns (program/admin/fundraising) by fiscal year
  - IRS compliance (in_pub78, is_revoked, has_recent_filing)
  - Charity Navigator ratings (1-4 stars)
- **Features**:
  - Multi-year fallback (FY2024 → FY2023 → FY2022)
  - Config-driven field routing via DataFieldManager
  - Non-modifying (read-only, never auto-updates)
  - Skips zero values when falling back to previous years

### **3. Charity Navigator API** ⚠️ MANUAL ONLY
- **URL**: `https://developer.charitynavigator.org/`
- **Status**: Manual entry via YAML (API integration not implemented)
- **Current Implementation**: Star ratings (1-4) entered manually
- **Scoring**: 5 points per star

### **4. Future Data Sources** ❌ NOT IMPLEMENTED
- **CharityAPI.org** (LOW COST) - Real-time IRS status
- **Candid APIs** (COMMERCIAL $6K+) - Seal of Transparency, news alerts

## Charity Evaluation Algorithm

### Core Financial Health Score (0-100 points)

**Components:**
- **Program Expense Ratio** (40 points max)
  - Target: 75%+ of total expenses
  - Formula: `min(40 * (program_ratio / 0.75), 40)`

- **Administrative Expenses** (20 points max)
  - Target: <15% of total expenses
  - Formula: `max(0, 20 * (0.15 - admin_ratio) / 0.15)`

- **Fundraising Expenses** (20 points max)
  - Target: <15% of total expenses
  - Formula: `max(0, 20 * (0.15 - fundraising_ratio) / 0.15)`

- **Financial Stability** (20 points)
  - 20 points if net assets (assets - liabilities) > 0
  - 0 points otherwise

**Status:** ✅ Implemented

### Compliance Check (Pass/Fail with -50 penalty)

**Checks:**
- **IRS Pub. 78 Status**: Tax-deductible eligibility (manual data)
- **Revocation Check**: Auto-revocation list (manual data)
- **Recent Filing**: Form 990 within 3 years (manual data)

**Penalty:** -50 points for any compliance issue

**Status:** ✅ Implemented via manual data entry

### External Validation Bonus (0-45 points)

**Current Implementation:**
- **Charity Navigator Rating**: 5 points per star (1-4 stars) = 5-20 points ✅

**Future Additions:**
- No advisory alerts bonus: +5 points ❌
- Candid Seal of Transparency: +10 points ❌
- Negative news penalty: -10 points ❌

**Status:** ⚠️ Partial (star ratings only)

### Final Scoring Algorithm

**Formula:**
```
total_score = financial_score + validation_bonus + compliance_penalty
```

**Maximum Possible Score:** 120 points
- Financial: 100 points
- Validation bonus: 20 points (Charity Navigator only)
- Compliance: 0 points (or -50 penalty)

**Grade Assignment:**
- A: 90-120 points
- B: 75-89 points
- C: 60-74 points
- D: 45-59 points
- F: <45 points

**Status:** ✅ Implemented

## Implementation Status

### ✅ Completed
1. ProPublica API client with caching ✅
2. Manual data entry system (YAML-based) ✅
3. Compliance checking (manual data) ✅
4. Financial scoring formulas (0-100 points) ✅
5. Grade assignment system ✅
6. Multi-year data fallback ✅
7. Charity Navigator ratings (manual entry) ✅

### ❌ Not Started
1. Charity Navigator API integration
2. CharityAPI.org integration
3. Candid APIs integration
4. Advisory alerts checking
5. News sentiment analysis
6. Sector-specific benchmarking

## Key Features

### Caching System
- SQLite-based persistent caching
- Configurable TTL per API (default 24 hours for ProPublica)
- 17x performance improvement (0.17s → 0.00s for cached requests)

### Mock Mode Support
- Two-level mock system (global + service-specific)
- Realistic test data for development
- No API keys required for testing

### Data Quality
- Multi-year fallback with zero-value skipping
- Config-driven field routing (API vs manual data)
- Non-defensive error handling (let exceptions bubble up)
- Form type support (990, 990-EZ, 990-PF)

### Manual Data Management
- Read-only system (never auto-modifies YAML files)
- User-maintained via brief_manual.yaml or manual_data.yaml
- Form 990 PDF storage in irs990/ for reference
- Multi-year fiscal data (FY2024, FY2023, FY2022)