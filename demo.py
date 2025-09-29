#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from charapi import evaluate_charity

def main():
    ein = "530196605"  # Red Cross
    config_path = "charapi/config/test_config.yaml"
    
    print(f"Evaluating charity with EIN: {ein}")
    print("-" * 50)
    
    result = evaluate_charity(ein, config_path)
    
    print(f"Organization: {result.organization_name}")
    print(f"EIN: {result.ein}")
    print(f"Grade: {result.grade}")
    print(f"Total Score: {result.total_score:.1f}")
    print(f"Financial Score: {result.financial_score:.1f}")
    print(f"Trend Modifier: {result.trend_modifier:.1f}")
    print(f"Validation Bonus: {result.validation_bonus:.1f}")
    print(f"Compliance Penalty: {result.compliance_penalty:.1f}")
    print(f"Revenue: ${result.financial_metrics.total_revenue:,}")
    print(f"Net Assets: ${result.financial_metrics.net_assets:,}")

if __name__ == "__main__":
    main()