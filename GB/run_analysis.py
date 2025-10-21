"""
Run Complete UK Power Networks Flexibility Market Analysis
Author: Data Analysis Script
Date: 2025-10-21

This script runs the complete analysis pipeline:
1. Fetch data from UKPN API
2. Perform statistical analysis
3. Generate visualizations
"""

import subprocess
import sys
import os
from datetime import datetime

def run_script(script_name, description):
    """Run a Python script and handle errors"""
    print("\n" + "="*80)
    print(f"{description}")
    print("="*80)

    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        if result.stderr:
            print("Warnings/Errors:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name}:")
        print(e.stdout)
        print(e.stderr)
        return False
    except FileNotFoundError:
        print(f"Error: {script_name} not found")
        return False

def main():
    """Run the complete analysis pipeline"""
    print("="*80)
    print("UK POWER NETWORKS FLEXIBILITY MARKET ANALYSIS")
    print("="*80)
    print(f"Analysis started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Check if data file already exists
    data_file = "ukpn_flexibility_dispatches.csv"
    if os.path.exists(data_file):
        response = input(f"\n{data_file} already exists. Re-download data? (y/n): ")
        if response.lower() == 'y':
            fetch_data = True
        else:
            fetch_data = False
            print("Using existing data file...")
    else:
        fetch_data = True

    # Step 1: Fetch data
    if fetch_data:
        success = run_script(
            "fetch_flexibility_data.py",
            "STEP 1: FETCHING DATA FROM UKPN API"
        )
        if not success:
            print("\n❌ Data fetching failed. Aborting analysis.")
            return

    # Step 2: Run analysis
    success = run_script(
        "analyze_flexibility_market.py",
        "STEP 2: PERFORMING STATISTICAL ANALYSIS"
    )
    if not success:
        print("\n⚠️  Analysis failed, but continuing to visualizations...")

    # Step 3: Generate visualizations
    success = run_script(
        "visualize_flexibility_market.py",
        "STEP 3: GENERATING VISUALIZATIONS"
    )
    if not success:
        print("\n⚠️  Visualization generation failed")

    # Summary
    print("\n" + "="*80)
    print("ANALYSIS PIPELINE COMPLETE")
    print("="*80)
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("Generated files:")
    print("  Data:")
    print("    - ukpn_flexibility_dispatches.csv")
    print()
    print("  Visualizations:")
    print("    - temporal_trends.png")
    print("    - daily_weekly_patterns.png")
    print("    - zone_analysis.png")
    print("    - technology_analysis.png")
    print("    - product_analysis.png")
    print("    - provider_analysis.png")
    print("    - price_distribution.png")
    print("    - cumulative_growth.png")
    print()
    print("="*80)

if __name__ == "__main__":
    main()
