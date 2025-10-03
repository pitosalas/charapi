# Charity Evaluation API - Current State

*Last Updated: October 3, 2025 - CharityAPI Integration Complete*

## Project Overview

A comprehensive charity evaluation API that analyzes nonprofit organizations using multiple data sources (ProPublica, CharityAPI.org for IRS data, Charity Navigator) and provides scoring with letter grades (A-F). Features automated compliance checking, sector-specific financial benchmarking (NTEE codes), and organization type analysis. Built as a separate Python module for reuse in charapi and other applications.

## Architecture

### Directory Structure
```
charapi/
├── charapi/                # Main package directory
│   ├── api/                # Main API interfaces
│   │   └── charity_evaluator.py
│   ├── clients/            # External API clients
│   │   ├── base_client.py
│   │   ├── propublica_client.py
│   │   ├── charityapi_client.py (NEW - Oct 3)
│   │   └── manual_data_client.py (Oct 1)
│   ├── analyzers/          # Analysis logic
│   │   ├── financial_analyzer.py (NTEE benchmarking - Oct 3)
│   │   ├── compliance_checker.py (uses CharityAPI - Oct 3)
│   │   ├── organization_type_analyzer.py (NEW - Oct 3)
│   │   └── validation_scorer.py (uses manual data)
│   ├── data/               # Data models and manual data management
│   │   ├── charity_evaluation_result.py (updated - Oct 3)
│   │   ├── mock_data.py
│   │   └── data_field_manager.py (CharityAPI support - Oct 3)
│   ├── cache/              # SQLite caching system
│   │   └── api_cache.py
│   └── config/             # Configuration files
│       ├── config.yaml (with data_fields config)
│       └── test_config.yaml
├── manual/                 # Manual data entry YAML files (Oct 1-2)
│   ├── brief_manual.yaml        # Simplified manual data (recommended)
│   ├── manual_data.yaml         # Comprehensive manual data
│   ├── eins.yaml               # EIN registry
│   └── irs990/                 # Downloaded Form 990 PDFs
├── tests/                  # Test files
│   ├── test_charapi.py
│   ├── test_api_cache.py
│   ├── test_propublica_client.py
│   ├── test_charityapi_client.py (NEW - Oct 3)
│   ├── test_compliance_checker.py (NEW - Oct 3)
│   ├── test_organization_type_analyzer.py (NEW - Oct 3)
│   ├── test_financial_analyzer.py (NTEE tests - Oct 3)
│   └── test_grading.py
├── cache/                  # SQLite database storage
│   └── charapi_cache.db
├── demo.py                 # CLI demo with manual data status messages
├── pyproject.toml          # Package configuration
└── README.md               # Comprehensive documentation
```

### Technology Stack
- **Python 3.12+** with modern uv package management
- **SQLite caching** for persistent API response storage
- **YAML configuration** for API keys and parameters
- **Mock mode support** for development and testing
- **Manual data entry system** with YAML files for missing API data
- **Modular architecture** following CLAUDE.md principles

## Current Implementation Status

### ✅ Completed (40/40 tasks - 100%)

#### Infrastructure & Setup
1. **Project Structure**: uv-based Python package with pyproject.toml
2. **Configuration System**: YAML-based with global and service-level mock modes
3. **Directory Organization**: Clean separation of concerns (api/, clients/, analyzers/, data/, config/, tests/)
4. **Version Control**: Comprehensive .gitignore for Python/uv projects

#### ProPublica API Integration
5. **Client Implementation**: Full ProPublica API client with search and organization endpoints
6. **Mock Data System**: Realistic sample data for Red Cross and Salvation Army (5 years of financials)
7. **Error Handling**: API timeouts and rate limiting support
8. **Data Parsing**: JSON response structure handling with real/mock compatibility
9. **Real API Testing**: Successfully tested live ProPublica API calls
10. **Response Structure Fix**: Handle real API nested organization data structure

#### Core Framework
11. **Data Models**: Complete dataclass structure for evaluation results
12. **Test Infrastructure**: Working end-to-end test with mock mode
13. **Analyzer Stubs**: Framework classes for financial, trend, compliance, and validation analysis
14. **API Interface**: Main evaluate_charity() function with orchestration
15. **Grade Assignment**: Data-driven A-F scoring system
16. **Package Interface**: Clean __init__.py exports
17. **Mock Mode**: Two-level mock system (global + service-specific)

#### Caching System
18. **SQLite Cache Module**: Persistent API response caching with TTL
19. **Cache Integration**: ProPublica client with automatic caching
20. **Cache Configuration**: YAML-based cache settings with per-API TTL
21. **Performance Improvement**: 0.17s → 0.00s for cached requests

#### User Interface & Documentation
22. **CLI Demo**: Command-line interface with mock/real modes
23. **API Requirement Messages**: Clear indicators when additional APIs needed
24. **Comprehensive README**: Data sources, equations, and implementation guide
25. **Updated Documentation**: Current state tracking and technical specifications

#### Code Architecture & Testing (NEW - September 30 Evening)
26. **BaseAPIClient Class**: Parent class for all API clients with shared config/cache logic
27. **Client Refactoring**: ProPublicaClient refactored to use BaseAPIClient (43% code reduction)
28. **Comprehensive Test Suite**: Added 19 new tests across 3 test files
    - test_propublica_client.py: 8 tests for API client behavior
    - test_financial_analyzer.py: 4 tests for metrics extraction
    - test_grading.py: 2 tests for grade boundary precision
29. **Code Quality Review**: Full codebase review against CLAUDE.md standards

#### Manual Data Entry System (NEW - October 1-2)
30. **ManualDataClient**: YAML-based manual data entry system for missing API data
31. **DataFieldManager**: Config-driven routing between manual and API data sources with multi-year fallback
32. **Manual YAML Files**: brief_manual.yaml (simplified) and manual_data.yaml (comprehensive)
33. **Integration with Analyzers**: FinancialAnalyzer, ComplianceChecker, and ValidationScorer use manual data
34. **Demo Improvements**: Clear messages showing which manual data files need editing
35. **IRS Rollback**: Removed all IRS-related code and 2.3GB of data files (user decision)
36. **Expense Ratio Fix**: Corrected calculations to display as percentages (was showing decimals)
37. **Charity Navigator Integration**: Manual rating entry (1-4 stars) with 5 points per star scoring
38. **Non-modifying Tests**: Removed auto-add functionality to prevent test pollution of manual data files
39. **Multi-year Fallback Fix**: DataFieldManager now skips zero values and falls back to previous fiscal years (Oct 2)
40. **Financial Scoring Formulas**: Implemented real scoring calculations (program/admin/fundraising ratios + stability) (Oct 2)

### 🔄 Current Implementation Gaps

None - all planned features with available data are implemented.

#### Data Availability
- **Manual data population**: brief_manual.yaml needs expense data from Form 990 PDFs
  - Expense breakdowns (program/admin/fundraising) - not in ProPublica API
  - IRS compliance fields (in_pub78, is_revoked, has_recent_filing) - included in YAML
  - Charity Navigator ratings - included in YAML
  - Form 990 PDFs stored in manual/irs990/ for reference

## Technical Context for Future Development

### Mock Mode Design
```yaml
# Global mock mode overrides all services
mock_mode: true

# Service-specific mock mode
propublica:
  mock_mode: false  # Ignored if global is true
```

### Financial Scoring Framework (NTEE-based)
- **Program Expense Ratio**: Sector-specific targets (40 points max)
  - Default: 75%+
  - Arts (A): 65%+
  - Education (B): 80%+
  - Health (E): 80%+
  - Medical Research (H): 70%+
  - Human Services (P): 75%+
  - International (Q): 70%+
- **Administrative Expenses**: Sector-specific limits (20 points max)
  - Default: <15%
  - Arts (A): <20%
  - Education/Health (B/E): <12%
  - Research/International (H/Q): <18%
- **Fundraising Expenses**: Target <15% (20 points max)
- **Financial Stability**: Positive net assets (20 points max)
- **Total Base Score**: 100 points possible

### Organization Type Scoring (NEW - Oct 3)
- **501(c)(3) Status**: -25 points if not 501(c)(3)
- **Foundation Type**: -15 points for private foundation (vs public charity)
- **Filing Requirement**: -10 points if not required to file Form 990
- **Organizational Maturity**: +5 points if 20+ years operating
- **Score Range**: -50 to +5 points

### External Validation Bonuses
- **Charity Navigator**: 5 points per star (1-4 stars)
- **No Advisory Alerts**: +5 points (not yet implemented)
- **Transparency Seal**: +10 points (not yet implemented)
- **Negative News**: -10 points (not yet implemented)
- **Maximum Bonus**: 20 points (current), 45 points (full implementation)

### Compliance System (Automated via CharityAPI - Oct 3)
- **IRS Pub. 78 Status**: Tax-deductible eligibility (CharityAPI deductibility field)
- **Revocation Check**: Tax-exempt status monitoring (CharityAPI status field)
- **Recent Filing**: Form 990 within 3 years (CharityAPI tax_period field)
- **Penalty**: -50 points for any non-compliance

### Total Scoring Formula (Updated Oct 3)
```
Total Score =
  Financial Health (0-100, NTEE-adjusted)
  + Validation Bonus (0-20)
  + Organization Type Score (-50 to +5)
  + Compliance Penalties (-150 to 0)

Possible Range: -150 to 125 points
```

### Manual Data Entry System
- **YAML Format**: Hierarchical structure for organization data by EIN and fiscal year
- **Location**: `manual/` directory in project root
- **Non-modifying**: System never auto-adds or modifies manual data files
- **Config-driven**: `data_fields` section in config.yaml specifies manual vs API sources
- **Multi-year Fallback**: Automatically falls back from fiscal_year_2024 → 2023 → 2022 when values are zero
- **Files**:
  1. `brief_manual.yaml` - Simplified format (recommended for most users)
  2. `manual_data.yaml` - Comprehensive format with full organizational details
  3. `irs990/` - Downloaded Form 990 PDFs for reference
- **Data Structure** (per EIN):
  - Organization metadata (name, in_pub78, is_revoked, has_recent_filing, charity_navigator_rating)
  - Fiscal year data (program/admin/fundraising expenses for FY2024, 2023, 2022)

## Current Todo List (4 pending tasks - reduced from 18)

### Priority 1: Code Quality - CLAUDE.md Compliance (2 tasks)
1. Remove all default parameters from functions (remaining violations in base_client.py, api_cache.py)
2. Refactor evaluate_charity() to be under 50 lines (currently 81)

### Priority 2: Validation & Testing (2 tasks)
1. Add EIN format validation (9-digit tax ID)
2. Validate scoring against manual calculations with populated manual data

## Proposed Technical Changes

### 1. Configuration Enhancement
```yaml
# Add to config.yaml
data_sources:
  irs:
    pub78_url: "https://www.irs.gov/pub/irs-soi/eo_xx.csv"
    cache_refresh_days: 30
  
caching:
  enabled: true
  api_cache_hours: 24
  local_storage_path: "cache/"
```

### 2. Error Handling Strategy
- **Fail Fast**: Follow CLAUDE.md principle of not coding defensively
- **Specific Exceptions**: Replace generic error handling with business logic errors
- **Graceful Degradation**: Continue evaluation with partial data when possible

### 3. Performance Optimizations
- **Async API Calls**: Implement concurrent requests to multiple data sources
- **Intelligent Caching**: Cache based on data freshness requirements
- **Batch Processing**: Support multiple EIN evaluations in single request

### 4. Code Quality Improvements
- **Method Length**: Ensure all methods stay under 50 lines (CLAUDE.md)
- **File Size**: Keep all files under 300 lines (CLAUDE.md)
- **No Default Parameters**: Force explicit parameter passing
- **Intention-Revealing Names**: Make method purposes clear from names

## Integration Context

### Current charapi Integration Points
- **Package Import**: `from charapi import evaluate_charity`
- **Configuration**: YAML-based configuration for API keys and parameters
- **Data Output**: Structured CharityEvaluationResult objects
- **Mock Mode**: Allows development and testing without API dependencies

### Future Enhancement Opportunities
1. **Interactive HTML Reports**: JavaScript-based sortable tables
2. **Export Formats**: Excel/CSV exports of analysis results
3. **Sector Benchmarking**: Industry-specific scoring adjustments
4. **News Sentiment Analysis**: Automated news impact scoring
5. **Comparative Ranking**: Multi-charity comparison features

## Development Environment

- **Python**: 3.12+ (managed by uv)
- **Package Manager**: uv (modern Python dependency management)
- **Testing**: Built-in test runner, no external framework dependencies
- **Configuration**: YAML-based, environment variable support planned
- **Mock Data**: Realistic 5-year financial datasets for major charities

## Current Context for Continued Development

### Recent Major Changes

#### September 30, 2025 - Initial Development
1. **Package Restructuring**: Moved from flat structure to proper `charapi/` package directory
2. **Caching System**: Implemented SQLite-based persistent caching with 17x performance improvement
3. **Real API Integration**: Fixed ProPublica API response structure handling
4. **BaseAPIClient**: Created parent class for API clients with shared config/cache logic
5. **Test Suite**: Built comprehensive test suite with 31 tests

#### October 1, 2025 - Manual Data System
6. **IRS Rollback**: Removed all IRS integration code and 2.3GB of data files (user decision to use manual entry instead)
7. **Manual Data Architecture**: Built YAML-based manual data entry system (brief_manual.yaml and manual_data.yaml)
8. **ManualDataClient**: Non-modifying client that reads manual YAML files
9. **DataFieldManager**: Config-driven routing between manual and API data sources
10. **Analyzer Integration**: Updated FinancialAnalyzer, ComplianceChecker, ValidationScorer to use manual data
11. **Expense Ratio Fix**: Corrected calculations to display as percentages (was 0.009, now 0.9%)
12. **Charity Navigator Manual Entry**: Integrated star ratings (1-4) with 5 points per star scoring
13. **Demo Improvements**: Added clear messages showing which manual data fields need editing

#### October 2, 2025 - Multi-year Fallback & Financial Scoring
14. **Multi-year Fallback Bug Fix**: Fixed DataFieldManager to skip zero values when falling back to previous fiscal years
15. **Trustees of Reservations Data**: Extracted and populated FY2023 expense data from Form 990 PDF
16. **PDF Storage**: Added manual/irs990/ directory for storing downloaded Form 990 PDFs
17. **Financial Scoring Implementation**: Implemented real scoring formulas (program 40pts, admin 20pts, fundraising 20pts, stability 20pts)
18. **Trend Analysis Complete Removal**: Removed all trend analysis code, dataclasses, and references (insufficient multi-year data)

#### October 3, 2025 - CharityAPI Integration (Phases 2-3)
19. **CharityAPIClient**: New API client for CharityAPI.org IRS master file data with mock support
20. **Automated Compliance Checking**: Removed manual compliance fields (in_pub78, is_revoked, has_recent_filing) - now automated via CharityAPI
21. **OrganizationTypeAnalyzer**: New analyzer for 501(c)(3) status, foundation type, filing requirements, and organizational maturity
22. **NTEE-based Benchmarking**: Financial scoring now uses sector-specific ratios (Arts 65%/20%, Education 80%/12%, Health 80%/12%, etc.)
23. **Organization Type Scoring**: Added -50 to +5 point scoring based on nonprofit type and age
24. **Updated Data Model**: CharityEvaluationResult now includes organization_type and organization_type_score fields
25. **Comprehensive Testing**: Added 44 new tests (27 CharityAPI client, 8 compliance checker, 9 organization type analyzer)
26. **Demo Updates**: Updated demo.py to display organization type details and new score breakdown
27. **Manual Data Cleanup**: Removed compliance fields from brief_manual.yaml (now automated)

### Working Demo Commands
```bash
# Mock mode (instant, uses test data)
uv run python demo.py mock

# Real mode (live API, with caching)
uv run python demo.py real
```

### Demo Output Example (Real Mode, No Manual Data)
```
Organization: American National Red Cross
EIN: 530196605
Grade: F
Total Score: 31.0
Financial Score: 75.0
Trend Modifier: 6.0 (stub - needs implementation)
Validation Bonus: 0.0 (manual data not available - edit manual/charity_navigator_rating.csv)
Compliance Penalty: -50.0 (issues: Not in IRS Publication 78, No recent Form 990 filing)
  → Check manual data files: in_pub78.csv, is_revoked.csv, has_recent_filing.csv
Revenue: $3,217,077,611
Net Assets: $3,019,994,931
Program Expense Ratio: Manual data not available (edit manual/program_expenses.csv)
Admin Expense Ratio: Manual data not available (edit manual/admin_expenses.csv)
Fundraising Expense Ratio: Manual data not available (edit manual/fundraising_expenses.csv)
```

### Cache Performance
- **First run**: 0.17 seconds (API calls)
- **Subsequent runs**: 0.00 seconds (cached data)
- **Cache location**: `cache/charapi_cache.db`
- **TTL**: 24 hours for ProPublica data

## Known Issues & Technical Debt

### Code Quality Issues (CLAUDE.md Compliance)
1. **Default Parameters**: 2 remaining instances (api_cache.py, base_client.py)
2. **Function Length**: evaluate_charity() is 81 lines (31 over limit)

### Minor Issues
3. **Manual Data Population**: Most organizations in brief_manual.yaml still need expense data from Form 990 PDFs

### System Status
- ✅ All core functionality working as expected
- ✅ API integration stable
- ✅ Caching system reliable
- ✅ Mock/real mode switching functional
- ✅ Manual data system working correctly with multi-year fallback
- ✅ All 31 tests passing

## Next Development Session Context

### Immediate Tasks (Priority Order)
1. **Fix CLAUDE.md violations** - Remove remaining default parameters, refactor long functions
2. **EIN validation** - Simple 9-digit format checking

### Code Quality Status
- **Package structure**: ✅ Properly organized with manual/ directory
- **Configuration**: ✅ YAML-based data_fields configuration
- **Error handling**: ✅ Non-defensive, lets errors bubble up
- **Testing**: ✅ Comprehensive coverage (31 tests, all passing)
- **Documentation**: ✅ Comprehensive and up-to-date
- **Manual Data System**: ✅ Working, non-modifying, config-driven with multi-year fallback
- **CLAUDE.md Compliance**: ⚠️ 2 minor violations remaining

### Key Files Modified Recently (October 3, 2025)
- `charapi/clients/charityapi_client.py` - NEW: CharityAPI.org client with mock support
- `charapi/analyzers/organization_type_analyzer.py` - NEW: Organization type scoring analyzer
- `charapi/analyzers/financial_analyzer.py` - UPDATED: NTEE-based sector-specific benchmarking
- `charapi/analyzers/compliance_checker.py` - UPDATED: Uses CharityAPI instead of manual data
- `charapi/data/charity_evaluation_result.py` - UPDATED: Added OrganizationType dataclass and organization_type_score field
- `charapi/data/data_field_manager.py` - UPDATED: Support for charityapi data source
- `charapi/api/charity_evaluator.py` - UPDATED: Integrated CharityAPI, organization type analyzer, and NTEE benchmarking
- `charapi/config/config.yaml` - UPDATED: Added CharityAPI configuration and updated data_fields mappings
- `charapi/config/test_config.yaml` - UPDATED: Added CharityAPI configuration for tests
- `manual/brief_manual.yaml` - UPDATED: Removed compliance fields (in_pub78, is_revoked, has_recent_filing)
- `demo.py` - UPDATED: Display organization type details and new score breakdown
- `tests/test_charityapi_client.py` - NEW: 27 comprehensive tests for CharityAPI client
- `tests/test_compliance_checker.py` - NEW: 8 tests for automated compliance checking
- `tests/test_organization_type_analyzer.py` - NEW: 9 tests for organization type analysis
- `tests/test_financial_analyzer.py` - UPDATED: Added 8 NTEE benchmarking tests

### Key Files Modified (October 2, 2025)
- `charapi/data/charity_evaluation_result.py` - UPDATED: Removed trend_modifier, trend_analysis fields and STUB_TREND_ANALYSIS enum
- `charapi/api/charity_evaluator.py` - UPDATED: Removed all trend analysis code
- `demo.py` - UPDATED: Removed trend modifier from output
- `tests/test_charapi.py` - UPDATED: Removed trend analysis assertions
- `charapi/analyzers/financial_analyzer.py` - UPDATED: Implemented real financial scoring formulas (0-100 points)
- `charapi/data/data_field_manager.py` - FIXED: Multi-year fallback now skips zero values
- `manual/brief_manual.yaml` - UPDATED: Added Trustees of Reservations FY2023 expense data
- `manual/irs990/` - NEW: Directory for storing downloaded Form 990 PDFs

### Key Files Modified (October 1, 2025)
- `charapi/clients/manual_data_client.py` - NEW: YAML-based manual data client
- `charapi/data/data_field_manager.py` - NEW: Routes between manual and API data sources with multi-year fallback
- `charapi/analyzers/financial_analyzer.py` - UPDATED: Uses manual data for expense breakdowns, fixed percentage calculations
- `charapi/analyzers/compliance_checker.py` - UPDATED: Uses manual data for IRS compliance fields
- `charapi/analyzers/validation_scorer.py` - UPDATED: Uses manual data for Charity Navigator rating
- `charapi/config/config.yaml` - UPDATED: Added data_fields configuration
- `manual/brief_manual.yaml` - NEW: Simplified YAML format for manual data entry
- `manual/manual_data.yaml` - NEW: Comprehensive YAML format for manual data entry
- `demo.py` - UPDATED: Shows clear messages about manual data availability
- `tests/test_charapi.py` - UPDATED: Reflects manual data system behavior
- `tests/test_financial_analyzer.py` - UPDATED: Tests with manual data

---

## Test Coverage Summary

### Total Tests: 83 across 8 test files (Updated Oct 3)
- **test_api_cache.py**: 14 tests (cache operations, TTL, stats)
- **test_propublica_client.py**: 8 tests (API client, mock/real modes, caching)
- **test_charityapi_client.py**: 27 tests (NEW - CharityAPI client and DataFieldManager integration)
- **test_compliance_checker.py**: 8 tests (NEW - automated compliance checking with CharityAPI)
- **test_organization_type_analyzer.py**: 9 tests (NEW - organization type scoring)
- **test_financial_analyzer.py**: 12 tests (4 original + 8 NTEE benchmarking tests)
- **test_charapi.py**: 3 tests (end-to-end integration)
- **test_grading.py**: 2 tests (grade boundaries)

### Coverage Areas
- ✅ Cache system (comprehensive)
- ✅ API client initialization and modes
- ✅ CharityAPI integration (NEW - Oct 3)
- ✅ Automated compliance checking (NEW - Oct 3)
- ✅ Organization type analysis (NEW - Oct 3)
- ✅ NTEE-based sector benchmarking (NEW - Oct 3)
- ✅ Mock data handling
- ✅ Financial metrics extraction with manual data
- ✅ Financial scoring formulas (real implementation with NTEE)
- ✅ Manual data system (non-modifying behavior)
- ✅ Grade assignment boundaries
- ✅ End-to-end evaluation flow
- ⚠️ ProPublica real API calls (limited to avoid rate limits)

---

**Status**: CharityAPI.org integration complete! Features automated compliance checking, sector-specific NTEE benchmarking, and organization type analysis. Manual data now only required for expense breakdowns and Charity Navigator ratings. 83 tests passing. Core system 100% complete with intelligent, data-driven charity evaluation.