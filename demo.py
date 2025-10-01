#!/usr/bin/env python3

import sys
import os
import time
sys.path.insert(0, os.path.dirname(__file__))

from charapi import evaluate_charity
from charapi.clients.propublica_client import ProPublicaClient

def format_value_or_api_message(value, api_name, condition=None):
    if condition is None:
        condition = value == 0

    if condition:
        return f"{api_name} API required to compute this value"
    elif isinstance(value, (int, float)) and value >= 1000:
        return f"${value:,}" if value > 0 else f"${value:,}"
    else:
        return f"{value:.1f}%" if isinstance(value, float) and value < 1 else f"{value}"

def print_results(result, mode):
    print(f"Organization: {result.organization_name}")
    print(f"EIN: {result.ein}")
    print(f"Grade: {result.grade}")
    print(f"Total Score: {result.total_score:.1f}")

    # Show scores with data availability status
    print(f"Financial Score: {result.financial_score:.1f}")
    print(f"Trend Modifier: {result.trend_modifier:.1f} (stub - needs implementation)")

    if result.external_validation.charity_navigator_rating is None:
        print(f"Validation Bonus: {result.validation_bonus:.1f} (manual data not available - edit manual/charity_navigator_rating.csv)")
    else:
        print(f"Validation Bonus: {result.validation_bonus:.1f} (Charity Navigator rating: {result.external_validation.charity_navigator_rating} stars)")

    # Show compliance with manual data status
    if not result.compliance_check.is_compliant:
        print(f"Compliance Penalty: {result.compliance_penalty:.1f} (issues: {', '.join(result.compliance_check.issues)})")
        print(f"  → Check manual data files: in_pub78.csv, is_revoked.csv, has_recent_filing.csv")
    else:
        print(f"Compliance Penalty: {result.compliance_penalty:.1f}")

    print(f"Revenue: ${result.financial_metrics.total_revenue:,}")
    print(f"Net Assets: ${result.financial_metrics.net_assets:,}")

    # Show expense ratios with manual data status
    if result.financial_metrics.program_expenses == 0:
        print(f"Program Expense Ratio: Manual data not available (edit manual/program_expenses.csv)")
        print(f"Admin Expense Ratio: Manual data not available (edit manual/admin_expenses.csv)")
        print(f"Fundraising Expense Ratio: Manual data not available (edit manual/fundraising_expenses.csv)")
    else:
        print(f"Program Expense Ratio: {result.financial_metrics.program_expense_ratio:.1f}%")
        print(f"Admin Expense Ratio: {result.financial_metrics.admin_expense_ratio:.1f}%")
        print(f"Fundraising Expense Ratio: {result.financial_metrics.fundraising_expense_ratio:.1f}%")

    data_source = "Live ProPublica API" if mode == "real" else "Mock data for testing"
    print(f"\n📊 Data Source: {data_source}")

def show_cache_stats(config_path):
    client = ProPublicaClient(config_path)
    stats = client.get_cache_stats()

    if stats.get("cache_enabled", True):
        print(f"\n🗃️  Cache Stats:")
        print(f"  Valid entries: {stats.get('valid_entries', 0)}")
        print(f"  Expired entries: {stats.get('expired_entries', 0)}")
        print(f"  API sources: {stats.get('api_sources', 0)}")
    else:
        print(f"\n🗃️  Cache: Disabled")

def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ["mock", "real"]:
        print("Usage: python demo.py [mock|real]")
        print("  mock - Use mock data for testing")
        print("  real - Use live ProPublica API")
        sys.exit(1)

    mode = sys.argv[1]
    eins = [
        "530196605",  # Red Cross
        "043255365",  # Additional charity
    ]

    config_path = "charapi/config/test_config.yaml" if mode == "mock" else "charapi/config/config.yaml"
    mode_label = "🧪 MOCK MODE - Using test data" if mode == "mock" else "🌐 REAL MODE - Using live ProPublica API"

    print(mode_label)

    for ein in eins:
        print(f"\nEvaluating charity with EIN: {ein}")
        print("-" * 50)

        try:
            start_time = time.time()
            result = evaluate_charity(ein, config_path)
            end_time = time.time()

            print_results(result, mode)

            print(f"⏱️  Evaluation time: {end_time - start_time:.2f} seconds")

        except Exception as e:
            print(f"❌ Error: {e}")
            if mode == "real":
                print("This might be due to API rate limiting or network issues")

    if mode == "real":
        show_cache_stats(config_path)

if __name__ == "__main__":
    main()