"""
Fetch GOPACS (Netherlands) Flexibility Market Data
Author: Data Analysis Script
Date: 2025-10-21

This script fetches all cleared bucket records from the GOPACS public API
and saves them to a CSV file for analysis.
"""

import requests
import pandas as pd
import json
from datetime import datetime
from typing import Dict, List
import time

# API Configuration
BASE_URL = "https://public-reporting.gopacs-services.eu/clearedbuckets"

def fetch_all_records(page_size: int = 100) -> List[Dict]:
    """
    Fetch all cleared bucket records from the GOPACS API.

    Args:
        page_size: Number of records to fetch per request (max 100)

    Returns:
        List of all cleared bucket records
    """
    all_records = []
    page = 0
    total_pages = None

    print(f"Fetching GOPACS cleared buckets data...")

    while True:
        url = BASE_URL
        params = {
            "page": page,
            "size": page_size
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if total_pages is None:
                total_pages = data.get('totalPages', 0)
                total_elements = data.get('totalElements', 0)
                print(f"Total records to fetch: {total_elements}")
                print(f"Total pages: {total_pages}")

            records = data.get('content', [])
            if not records:
                break

            all_records.extend(records)
            page += 1

            print(f"Fetched page {page}/{total_pages} ({len(all_records)} records)...", end='\r')

            # Check if we've fetched all pages
            if page >= total_pages:
                break

            # Be nice to the API
            time.sleep(0.1)

        except requests.exceptions.RequestException as e:
            print(f"\nError fetching data: {e}")
            break

    print(f"\nSuccessfully fetched {len(all_records)} records")
    return all_records


def flatten_ptu_data(records: List[Dict]) -> List[Dict]:
    """
    Flatten PTU (Program Time Unit) data into individual rows.

    Each clearing event has multiple 15-minute PTUs. This function
    creates a separate row for each PTU.
    """
    flattened = []

    for record in records:
        base_data = {
            'clearingEventId': record.get('clearingEventId'),
            'organisationName': record.get('organisationName'),
            'buyVolumeInMWh': record.get('buyVolumeInMWh'),
            'sellVolumeInMWh': record.get('sellVolumeInMWh'),
            'eventStartTime': record.get('startTime'),
            'eventEndTime': record.get('endTime'),
        }

        # Add each PTU as a separate row
        for ptu in record.get('clearedVolumesForPtus', []):
            ptu_row = {
                **base_data,
                'ptuStartTime': ptu.get('startTime'),
                'ptuEndTime': ptu.get('endTime'),
                'buyVolumeInMW': ptu.get('buyVolumeInMW'),
                'sellVolumeInMW': ptu.get('sellVolumeInMW')
            }
            flattened.append(ptu_row)

    return flattened


def save_to_csv(records: List[Dict], filename: str = "gopacs_cleared_buckets.csv"):
    """
    Save records to CSV file.

    Args:
        records: List of cleared bucket records
        filename: Output filename
    """
    if not records:
        print("No records to save")
        return

    # Flatten PTU data
    print("\nFlattening PTU (Program Time Unit) data...")
    flattened_records = flatten_ptu_data(records)

    df = pd.DataFrame(flattened_records)

    # Convert datetime strings to datetime objects
    datetime_cols = ['eventStartTime', 'eventEndTime', 'ptuStartTime', 'ptuEndTime']
    for col in datetime_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    # Calculate duration
    df['eventDurationHours'] = (df['eventEndTime'] - df['eventStartTime']).dt.total_seconds() / 3600
    df['ptuDurationMinutes'] = (df['ptuEndTime'] - df['ptuStartTime']).dt.total_seconds() / 60

    # Sort by start time
    df = df.sort_values('ptuStartTime', ascending=False)

    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

    # Print summary statistics
    print("\n" + "="*80)
    print("DATA SUMMARY")
    print("="*80)
    print(f"Total clearing events: {len(records):,}")
    print(f"Total PTU records: {len(df):,}")
    print(f"Date range: {df['ptuStartTime'].min()} to {df['ptuStartTime'].max()}")

    print(f"\nTotal buy volume: {df['buyVolumeInMW'].sum():.2f} MW")
    print(f"Total sell volume: {df['sellVolumeInMW'].sum():.2f} MW")
    print(f"\nNumber of grid operators: {df['organisationName'].nunique()}")

    print("\n" + "-"*80)
    print("CLEARED BUCKETS BY GRID OPERATOR")
    print("-"*80)
    org_stats = df.groupby('organisationName').agg({
        'clearingEventId': 'nunique',
        'buyVolumeInMW': 'sum',
        'sellVolumeInMW': 'sum'
    }).rename(columns={'clearingEventId': 'num_events'})
    print(org_stats)

    print("\n" + "-"*80)
    print("AVERAGE PTU VOLUMES BY OPERATOR")
    print("-"*80)
    avg_volumes = df.groupby('organisationName').agg({
        'buyVolumeInMW': 'mean',
        'sellVolumeInMW': 'mean'
    }).round(2)
    print(avg_volumes)

    return df


if __name__ == "__main__":
    print("GOPACS Cleared Buckets Data Fetcher")
    print("="*80)
    print()

    # Fetch all records
    records = fetch_all_records(page_size=100)

    # Save to CSV and display summary
    df = save_to_csv(records)

    print("\n" + "="*80)
    print(f"Data fetching complete!")
    print("="*80)
