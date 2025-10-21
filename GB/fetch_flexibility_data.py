"""
Fetch UK Power Networks Flexibility Dispatches Data
Author: Data Analysis Script
Date: 2025-10-21

This script fetches all flexibility dispatch records from UKPN's Open Data API
and saves them to a CSV file for analysis.
"""

import requests
import pandas as pd
import json
import os
from datetime import datetime
from typing import Dict, List
import time

# API Configuration
API_KEY = os.getenv('UKPN_API_KEY', '')  # Set via environment variable: export UKPN_API_KEY=your_key_here
BASE_URL = "https://ukpowernetworks.opendatasoft.com/api/v2/catalog/datasets"
DATASET_ID = "ukpn-flexibility-dispatches"

def fetch_all_records(limit: int = 100) -> List[Dict]:
    """
    Fetch all flexibility dispatch records from the API.

    Args:
        limit: Number of records to fetch per request (max 100)

    Returns:
        List of all dispatch records
    """
    all_records = []
    offset = 0
    total_count = None

    print(f"Fetching flexibility dispatch data from UKPN API...")

    while True:
        url = f"{BASE_URL}/{DATASET_ID}/records"
        params = {
            "limit": limit,
            "offset": offset,
            "apikey": API_KEY
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if total_count is None:
                total_count = data.get('total_count', 0)
                print(f"Total records to fetch: {total_count}")

            records = data.get('records', [])
            if not records:
                break

            # Extract the fields from each record
            for record in records:
                all_records.append(record['record']['fields'])

            offset += limit
            print(f"Fetched {len(all_records)}/{total_count} records...", end='\r')

            # Check if we've fetched all records
            if offset >= total_count:
                break

            # Be nice to the API
            time.sleep(0.1)

        except requests.exceptions.RequestException as e:
            print(f"\nError fetching data: {e}")
            break

    print(f"\nSuccessfully fetched {len(all_records)} records")
    return all_records


def save_to_csv(records: List[Dict], filename: str = "ukpn_flexibility_dispatches.csv"):
    """
    Save records to CSV file.

    Args:
        records: List of dispatch records
        filename: Output filename
    """
    if not records:
        print("No records to save")
        return

    df = pd.DataFrame(records)

    # Convert datetime strings to datetime objects
    datetime_cols = ['start_time_local', 'end_time_local']
    for col in datetime_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    # Sort by start time
    df = df.sort_values('start_time_local', ascending=False)

    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

    # Print summary statistics
    print("\n" + "="*80)
    print("DATA SUMMARY")
    print("="*80)
    print(f"Total dispatches: {len(df):,}")
    print(f"Date range: {df['start_time_local'].min()} to {df['start_time_local'].max()}")
    print(f"\nTotal energy dispatched: {df['utilisation_mwh_req'].sum():.2f} MWh")
    print(f"Total capacity dispatched: {df['utilisation_mw_req'].sum():.2f} MW")
    print(f"\nNumber of unique zones: {df['zone'].nunique()}")
    print(f"Number of unique companies: {df['company_name'].nunique()}")
    print(f"Number of unique flexible units: {df['fu_id'].nunique()}")

    print("\n" + "-"*80)
    print("DISPATCHES BY PRODUCT")
    print("-"*80)
    print(df['product'].value_counts())

    print("\n" + "-"*80)
    print("DISPATCHES BY TECHNOLOGY")
    print("-"*80)
    print(df['technology'].value_counts())

    print("\n" + "-"*80)
    print("DISPATCHES BY TYPE")
    print("-"*80)
    print(df['dispatch_type'].value_counts())

    print("\n" + "-"*80)
    print("TOP 10 ZONES BY DISPATCH COUNT")
    print("-"*80)
    print(df['zone'].value_counts().head(10))

    print("\n" + "-"*80)
    print("TOP 10 COMPANIES BY DISPATCH COUNT")
    print("-"*80)
    print(df['company_name'].value_counts().head(10))

    return df


if __name__ == "__main__":
    print("UKPN Flexibility Dispatches Data Fetcher")
    print("="*80)
    print()

    # Fetch all records
    records = fetch_all_records(limit=100)

    # Save to CSV and display summary
    df = save_to_csv(records)

    print("\n" + "="*80)
    print(f"Data fetching complete!")
    print("="*80)
