#!/usr/bin/env python3

import sys
import os
import time

sys.path.insert(0, os.path.dirname(__file__))

from charapi import evaluate_charity
from charapi.clients.propublica_client import ProPublicaClient
from charapi.data.charity_evaluation_result import MetricCategory, MetricStatus


def print_health_report(result, mode):
    print(f"\nCHARITY HEALTH REPORT: {result.organization_name}")
    print(f"EIN: {result.ein}")
    print("=" * 70)

    print(f"\nSUMMARY")
    print(f"  {result.summary}")
    print()

    # Group metrics by category
    financial_metrics = [m for m in result.metrics if m.category == MetricCategory.FINANCIAL]
    compliance_metrics = [m for m in result.metrics if m.category == MetricCategory.COMPLIANCE]
    org_type_metrics = [m for m in result.metrics if m.category == MetricCategory.ORGANIZATION_TYPE]
    validation_metrics = [m for m in result.metrics if m.category == MetricCategory.VALIDATION]
    preference_metrics = [m for m in result.metrics if m.category == MetricCategory.PREFERENCE]

    # Print Financial Health
    if financial_metrics:
        print(f"\nFINANCIAL HEALTH")
        print(f"  {'Metric':30s} {'Value':15s} {'Range':20s} {'Status':15s}")
        print(f"  {'-'*30} {'-'*15} {'-'*20} {'-'*15}")
        for metric in financial_metrics:
            status_symbol = get_status_symbol(metric.status)
            range_str = f"{metric.ranges.outstanding}/{metric.ranges.acceptable}"
            print(f"  {metric.name:30s} {metric.display_value:15s} {range_str:20s} {status_symbol}")

    # Print Compliance
    if compliance_metrics:
        print(f"\nCOMPLIANCE (IRS Requirements)")
        print(f"  {'Metric':30s} {'Value':15s} {'Required':15s} {'Status':15s}")
        print(f"  {'-'*30} {'-'*15} {'-'*15} {'-'*15}")
        for metric in compliance_metrics:
            status_symbol = get_status_symbol(metric.status)
            print(f"  {metric.name:30s} {metric.display_value:15s} {metric.ranges.acceptable:15s} {status_symbol}")

    # Print Organization Type
    if org_type_metrics:
        print(f"\nORGANIZATION TYPE")
        print(f"  {'Metric':30s} {'Value':15s} {'Required':15s} {'Status':15s}")
        print(f"  {'-'*30} {'-'*15} {'-'*15} {'-'*15}")
        for metric in org_type_metrics:
            status_symbol = get_status_symbol(metric.status)
            print(f"  {metric.name:30s} {metric.display_value:15s} {metric.ranges.acceptable:15s} {status_symbol}")

    # Print External Validation
    if validation_metrics:
        print(f"\nEXTERNAL VALIDATION")
        print(f"  {'Metric':30s} {'Value':15s} {'Range':20s} {'Status':15s}")
        print(f"  {'-'*30} {'-'*15} {'-'*20} {'-'*15}")
        for metric in validation_metrics:
            status_symbol = get_status_symbol(metric.status)
            range_str = f"{metric.ranges.outstanding}/{metric.ranges.acceptable}"
            print(f"  {metric.name:30s} {metric.display_value:15s} {range_str:20s} {status_symbol}")

    # Print Preferences
    if preference_metrics:
        print(f"\nPREFERENCES (Your Priorities)")
        print(f"  {'Metric':30s} {'Value':30s} {'Range':20s} {'Status':15s}")
        print(f"  {'-'*30} {'-'*30} {'-'*20} {'-'*15}")
        for metric in preference_metrics:
            status_symbol = get_status_symbol(metric.status)
            range_str = f"{metric.ranges.outstanding}/{metric.ranges.acceptable}"
            print(f"  {metric.name:30s} {metric.display_value:30s} {range_str:20s} {status_symbol}")

    # Print Overall Assessment
    print(f"\nOVERALL ASSESSMENT")
    outstanding_pct = (result.outstanding_count / result.total_metrics * 100) if result.total_metrics > 0 else 0
    acceptable_pct = (result.acceptable_count / result.total_metrics * 100) if result.total_metrics > 0 else 0
    unacceptable_pct = (result.unacceptable_count / result.total_metrics * 100) if result.total_metrics > 0 else 0

    print(f"  ⭐ Outstanding:   {result.outstanding_count:2d} metrics ({outstanding_pct:.0f}%)")
    print(f"  ✓ Acceptable:    {result.acceptable_count:2d} metrics ({acceptable_pct:.0f}%)")
    print(f"  ⚠ Unacceptable:  {result.unacceptable_count:2d} metrics ({unacceptable_pct:.0f}%)")

    data_sources = ", ".join(result.data_sources_used)
    data_mode = "Live APIs" if mode == "real" else "Mock data for testing"
    print(f"\n📊 Data Sources: {data_sources} ({data_mode})")


def get_status_symbol(status: MetricStatus) -> str:
    if status == MetricStatus.OUTSTANDING:
        return "⭐ Outstanding"
    elif status == MetricStatus.ACCEPTABLE:
        return "✓ Acceptable"
    elif status == MetricStatus.UNACCEPTABLE:
        return "⚠ Unacceptable"
    else:
        return "? Unknown"


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
        # "530196605",  # Red Cross
        "043255365",  # Passim
        # "13-1930176", # The World Union for Progressive Judaism Ltd
        # "13-1644147", # Planned Parenthood Federation of America, Inc.
        # "13-5660870", # International Rescue Committee Inc (IRC)
        # "13-3433452", # Doctors Without Borders USA Inc (MSF)
        # "04-2105780", # The Trustees of Reservations
        # "04-3567502", # Partners In Health (PIH)
        # "53-0196605", # American National Red Cross
        "47-5005730",  # Arlington Eats
        "04-3129124",   # Zoo New England
        "02-0475057"    # Moulton borough Historical"

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
        print("-" * 70)

        try:
            start_time = time.time()
            result = evaluate_charity(ein, config_path)
            end_time = time.time()

            print_health_report(result, mode)

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
