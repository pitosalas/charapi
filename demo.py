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

    # Show API requirements for different calculations
    if mode == "real":
        print(f"Financial Score: {format_value_or_api_message(result.financial_score, 'IRS Form 990 detailed', result.financial_score == 75.0)}")
        print(f"Trend Modifier: {format_value_or_api_message(result.trend_modifier, 'Multi-year ProPublica', result.trend_modifier == 6.0)}")
        print(f"Validation Bonus: {format_value_or_api_message(result.validation_bonus, 'Charity Navigator', result.validation_bonus == 20.0)}")
        print(f"Compliance Penalty: {format_value_or_api_message(result.compliance_penalty, 'IRS Pub 78', result.compliance_penalty == 0.0)}")
    else:
        print(f"Financial Score: {result.financial_score:.1f}")
        print(f"Trend Modifier: {result.trend_modifier:.1f}")
        print(f"Validation Bonus: {result.validation_bonus:.1f}")
        print(f"Compliance Penalty: {result.compliance_penalty:.1f}")

    print(f"Revenue: ${result.financial_metrics.total_revenue:,}")
    print(f"Net Assets: ${result.financial_metrics.net_assets:,}")

    # Show expense ratios with API requirements
    if mode == "real" and result.financial_metrics.program_expenses == 0:
        print(f"Program Expense Ratio: IRS Form 990 detailed API required to compute this value")
        print(f"Admin Expense Ratio: IRS Form 990 detailed API required to compute this value")
        print(f"Fundraising Expense Ratio: IRS Form 990 detailed API required to compute this value")
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
    ein = "530196605"  # Red Cross

    config_path = "charapi/config/test_config.yaml" if mode == "mock" else "charapi/config/config.yaml"
    mode_label = "🧪 MOCK MODE - Using test data" if mode == "mock" else "🌐 REAL MODE - Using live ProPublica API"

    print(mode_label)
    print(f"Evaluating charity with EIN: {ein}")
    print("-" * 50)

    try:
        start_time = time.time()
        result = evaluate_charity(ein, config_path)
        end_time = time.time()

        print_results(result, mode)

        print(f"⏱️  Evaluation time: {end_time - start_time:.2f} seconds")

        if mode == "real":
            show_cache_stats(config_path)

    except Exception as e:
        print(f"❌ Error: {e}")
        if mode == "real":
            print("This might be due to API rate limiting or network issues")
        sys.exit(1)

if __name__ == "__main__":
    main()