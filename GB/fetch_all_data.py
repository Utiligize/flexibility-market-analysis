"""
Fetch ALL UKPN Flexibility Dispatches (bypass 10k limit)
Uses date filtering to work around API offset+limit ≤ 10,000 restriction
"""

import requests
import pandas as pd
import time
import os
from datetime import datetime

API_KEY = os.getenv('UKPN_API_KEY', '')
BASE_URL = 'https://ukpowernetworks.opendatasoft.com/api/v2/catalog/datasets'
DATASET_ID = 'ukpn-flexibility-dispatches'

if not API_KEY:
    print("ERROR: UKPN_API_KEY environment variable not set")
    print("Set it with: export UKPN_API_KEY=your_key_here")
    exit(1)

print('='*80)
print('FETCHING ALL UKPN FLEXIBILITY DISPATCHES')
print('='*80)
print()

# Strategy: Fetch in date chunks to bypass 10k limit
# Each chunk fetches up to 10k records for a date range

date_ranges = [
    ('2023-01-01', '2023-12-31'),
    ('2024-01-01', '2024-06-30'),
    ('2024-07-01', '2024-12-31'),
    ('2025-01-01', '2025-06-30'),
    ('2025-07-01', '2025-12-31'),
]

all_records = []
url = f'{BASE_URL}/{DATASET_ID}/records'

for start_date, end_date in date_ranges:
    print(f'Fetching {start_date} to {end_date}...')

    offset = 0
    chunk_records = []

    while offset < 10000:
        params = {
            'limit': 100,
            'offset': offset,
            'where': f'start_time_local >= "{start_date}" AND start_time_local < "{end_date}"',
            'apikey': API_KEY
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            records = data.get('records', [])
            if not records:
                break

            for record in records:
                chunk_records.append(record['record']['fields'])

            total_in_range = data.get('total_count', 0)
            offset += 100

            print(f'  Fetched {len(chunk_records)}/{total_in_range}...', end='\r')

            # Stop if we got all records in this date range
            if len(chunk_records) >= total_in_range:
                break

            # Rate limiting
            time.sleep(0.2)

        except requests.exceptions.RequestException as e:
            print(f'\n  Error: {e}')
            break

    print(f'  ✓ Got {len(chunk_records)} records for this period')
    all_records.extend(chunk_records)
    print()

print('='*80)
print(f'TOTAL RECORDS FETCHED: {len(all_records):,}')
print('='*80)
print()

# Save to CSV
if all_records:
    df = pd.DataFrame(all_records)
    df['start_time_local'] = pd.to_datetime(df['start_time_local'], errors='coerce')
    df = df.sort_values('start_time_local', ascending=False)

    # Remove duplicates (in case of overlap)
    df = df.drop_duplicates(subset=['fu_id', 'zone', 'start_time_local', 'end_time_local'])

    filename = 'ukpn_flexibility_dispatches_FULL.csv'
    df.to_csv(filename, index=False)

    print(f'✓ Saved to {filename}')
    print()
    print('Summary:')
    print(f'  Total records: {len(df):,}')
    print(f'  After deduplication: {len(df):,}')
    print(f'  Date range: {df[\"start_time_local\"].min()} to {df[\"start_time_local\"].max()}')
    print(f'  Zones: {df[\"zone\"].nunique()}')
    print(f'  Providers: {df[\"company_name\"].nunique()}')
    print()
    print('Compare with original:')
    original = pd.read_csv('ukpn_flexibility_dispatches.csv')
    print(f'  Original: {len(original):,} records')
    print(f'  New: {len(df):,} records')
    print(f'  Additional: {len(df) - len(original):,} records')
else:
    print('No records fetched')

print()
print('Note: API key must be set via: export UKPN_API_KEY=your_key_here')
