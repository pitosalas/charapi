#!/usr/bin/env python3

import sys
import os
import time

sys.path.insert(0, os.path.dirname(__file__))

from charapi import evaluate_charity
from charapi.clients.propublica_client import ProPublicaClient


def format_value_or_api_message(value, api_name, condition):
    if condition:
        return f"{api_name} API required to compute this value"
    elif isinstance(value, (int, float)) and value >= 1000:
        return f"${value:,}"
    else:
        return f"{value:.1f}%" if isinstance(value, float) and value < 1 else f"{value}"


def print_results(result, mode):
    print(f"Organization: {result.organization_name}")
    print(f"EIN: {result.ein}")
    print(f"Grade: {result.grade}")
    print(f"Total Score: {result.total_score:.1f}")
    print(f"Financial Score: {result.financial_score:.1f}")
    print(f"Validation Bonus: {result.validation_bonus:.1f}")
    print(f"Compliance Penalty: {result.compliance_penalty:.1f}")
    print(f"Revenue: ${result.financial_metrics.total_revenue:,}")
    print(f"Net Assets: ${result.financial_metrics.net_assets:,}")

    if result.financial_metrics.program_expenses > 0:
        print(
            f"Program Expense Ratio: {result.financial_metrics.program_expense_ratio:.1f}%"
        )
        print(
            f"Admin Expense Ratio: {result.financial_metrics.admin_expense_ratio:.1f}%"
        )
        print(
            f"Fundraising Expense Ratio: {result.financial_metrics.fundraising_expense_ratio:.1f}%"
        )

    if result.issues:
        print(f"\n⚠️  Issues:")
        for issue in result.issues:
            print(f"  • {issue}")

    data_source = "Live ProPublica API" if mode == "real" else "Mock data for testing"
    print(f"\n📊 Data Source: {data_source}")


def show_cache_stats(config_path):
    stats = ProPublicaClient(config_path).get_cache_stats()

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
        "13-1930176",  # The World Union for Progressive Judaism Ltd
        "04-3129124",  # Commonwealth Zoological Corporation (Zoo New England)
        "31-1640316",  # Donor Advised Charitable Giving, Inc. (Schwab Charitable
    ]

    config_path = (
        "charapi/config/test_config.yaml"
        if mode == "mock"
        else "charapi/config/config.yaml"
    )

    print(
        "🧪 MOCK MODE - Using test data"
        if mode == "mock"
        else "🌐 REAL MODE - Using live ProPublica API"
    )

    for ein in eins:
        print(f"\nEvaluating charity with EIN: {ein}")
        print("-" * 50)

        try:
            start_time = time.time()
            result = evaluate_charity(ein, config_path)
            end_time = time.time()

            print_results(result, mode)

            print(f"⏱️  Evaluation time: {end_time - start_time:.2f} seconds")

        except (KeyError, ValueError, FileNotFoundError, OSError) as e:
            additional_msg = (
                "\nThis might be due to API rate limiting or network issues"
                if mode == "real"
                else ""
            )
            print(f"❌ Error: {e}{additional_msg}")

    if mode == "real":
        show_cache_stats(config_path)


if __name__ == "__main__":
    main()
