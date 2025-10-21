"""
Analyze Flexibility Tender Success Rates
Compares tender zones with actual dispatch zones to calculate procurement success
"""

import requests
import pandas as pd
import json
import os
from datetime import datetime
import time
import matplotlib.pyplot as plt
import seaborn as sns

API_KEY = os.getenv('UKPN_API_KEY', '')  # Set via environment variable: export UKPN_API_KEY=your_key_here
BASE_URL = "https://ukpowernetworks.opendatasoft.com/api/v2/catalog/datasets"

def fetch_tender_zones(limit=100):
    """Fetch unique zones from tender data"""
    print("Fetching flexibility tender data...")

    url = f"{BASE_URL}/ukpn-flexibility-tender-data/records"
    params = {
        "limit": limit,
        "apikey": API_KEY,
        "select": "flexibility_zone,competition_pot,tender_round",
        "group_by": "flexibility_zone,competition_pot,tender_round"
    }

    all_tenders = []
    offset = 0

    # Fetch aggregated data
    while offset < 10000:  # API limit
        params['offset'] = offset
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            records = data.get('records', [])
            if not records:
                break

            for record in records:
                all_tenders.append(record['record']['fields'])

            offset += limit
            print(f"Fetched {len(all_tenders)} tender zone combinations...", end='\r')
            time.sleep(0.1)

        except Exception as e:
            print(f"\nError: {e}")
            break

    print(f"\nTotal tender records fetched: {len(all_tenders)}")
    return pd.DataFrame(all_tenders)

def analyze_tender_success():
    """Analyze tender success by comparing with actual dispatches"""

    print("\n" + "="*80)
    print("FLEXIBILITY TENDER SUCCESS ANALYSIS")
    print("="*80 + "\n")

    # Load dispatch data
    print("Loading dispatch data...")
    dispatches_df = pd.read_csv('ukpn_flexibility_dispatches.csv')

    # Calculate total cost if not present
    if 'total_cost' not in dispatches_df.columns:
        dispatches_df['availability_cost'] = dispatches_df['availability_mwh_req'] * dispatches_df['availability_price']
        dispatches_df['utilisation_cost'] = dispatches_df['utilisation_mwh_req'] * dispatches_df['utilisation_price']
        dispatches_df['total_cost'] = dispatches_df['availability_cost'] + dispatches_df['utilisation_cost']

    # Fetch tender data (aggregated by zone)
    # For full analysis, we'll aggregate by zone from dispatches
    tender_zones_full = fetch_tender_zones(limit=100)

    if tender_zones_full is not None and len(tender_zones_full) > 0:
        tender_zones = set(tender_zones_full['flexibility_zone'].unique())
    else:
        print("Using simplified analysis with dispatches only")
        tender_zones = None

    # Get zones with actual dispatches
    dispatch_zones = set(dispatches_df['zone'].unique())

    print("\n" + "-"*80)
    print("ZONE COVERAGE ANALYSIS")
    print("-"*80)

    print(f"\nTotal unique zones with dispatches: {len(dispatch_zones)}")

    if tender_zones is not None:
        print(f"Total unique zones in tender data (sample): {len(tender_zones)}")

        # Zones with both tenders and dispatches
        successful_zones = dispatch_zones.intersection(tender_zones)
        print(f"Zones with both tenders AND dispatches: {len(successful_zones)}")

        # Tender-only zones (no dispatches yet)
        tender_only = tender_zones - dispatch_zones
        print(f"Zones with tenders but NO dispatches: {len(tender_only)}")

        if len(tender_zones) > 0:
            success_rate = (len(successful_zones) / len(tender_zones)) * 100
            print(f"\nProcurement Success Rate: {success_rate:.1f}%")

    # Analyze dispatch activity by zone
    print("\n" + "-"*80)
    print("DISPATCH ACTIVITY BY ZONE")
    print("-"*80)

    zone_activity = dispatches_df.groupby('zone').agg({
        'fu_id': 'count',
        'company_name': 'nunique',
        'utilisation_mwh_req': 'sum',
        'total_cost': 'sum'
    }).rename(columns={
        'fu_id': 'total_dispatches',
        'company_name': 'num_providers'
    }).sort_values('total_dispatches', ascending=False)

    print(f"\nZones with active flexibility services: {len(zone_activity)}")
    print(f"Average dispatches per zone: {zone_activity['total_dispatches'].mean():.1f}")
    print(f"Median dispatches per zone: {zone_activity['total_dispatches'].median():.1f}")

    # Categorize zones by activity level
    high_activity = zone_activity[zone_activity['total_dispatches'] >= 100]
    medium_activity = zone_activity[(zone_activity['total_dispatches'] >= 20) &
                                     (zone_activity['total_dispatches'] < 100)]
    low_activity = zone_activity[zone_activity['total_dispatches'] < 20]

    print(f"\nHigh activity zones (≥100 dispatches): {len(high_activity)} ({len(high_activity)/len(zone_activity)*100:.1f}%)")
    print(f"Medium activity zones (20-99 dispatches): {len(medium_activity)} ({len(medium_activity)/len(zone_activity)*100:.1f}%)")
    print(f"Low activity zones (<20 dispatches): {len(low_activity)} ({len(low_activity)/len(zone_activity)*100:.1f}%)")

    print("\n" + "-"*80)
    print("TOP 20 MOST ACTIVE ZONES")
    print("-"*80)
    print(zone_activity.head(20))

    # Provider competition analysis
    print("\n" + "-"*80)
    print("PROVIDER COMPETITION IN ZONES")
    print("-"*80)

    provider_competition = zone_activity.groupby('num_providers').size()
    print("\nNumber of zones by provider count:")
    for providers, count in provider_competition.sort_index(ascending=False).items():
        print(f"  {providers} providers: {count} zones")

    # Product analysis
    print("\n" + "-"*80)
    print("DISPATCH SUCCESS BY PRODUCT")
    print("-"*80)

    product_stats = dispatches_df.groupby('product').agg({
        'fu_id': 'count',
        'zone': 'nunique',
        'company_name': 'nunique',
        'utilisation_mwh_req': 'sum'
    }).rename(columns={
        'fu_id': 'total_dispatches',
        'zone': 'num_zones',
        'company_name': 'num_providers'
    }).sort_values('total_dispatches', ascending=False)

    print(product_stats)

    # Technology success
    print("\n" + "-"*80)
    print("DISPATCH SUCCESS BY TECHNOLOGY")
    print("-"*80)

    tech_stats = dispatches_df.groupby('technology').agg({
        'fu_id': 'count',
        'zone': 'nunique',
        'company_name': 'nunique'
    }).rename(columns={
        'fu_id': 'total_dispatches',
        'zone': 'num_zones',
        'company_name': 'num_providers'
    }).sort_values('total_dispatches', ascending=False)

    print(tech_stats.head(10))

    # Temporal success - how dispatches evolved
    print("\n" + "-"*80)
    print("MARKET GROWTH & PROCUREMENT SUCCESS")
    print("-"*80)

    dispatches_df['start_time_local'] = pd.to_datetime(dispatches_df['start_time_local'])
    dispatches_df['year_month'] = dispatches_df['start_time_local'].dt.to_period('M')

    monthly_growth = dispatches_df.groupby('year_month').agg({
        'fu_id': 'count',
        'zone': 'nunique',
        'company_name': 'nunique'
    }).rename(columns={
        'fu_id': 'dispatches',
        'zone': 'active_zones',
        'company_name': 'active_providers'
    })

    print("\nMonthly growth in market participation:")
    print(monthly_growth.tail(12))

    # Create visualization
    create_success_visualizations(zone_activity, product_stats, tech_stats, monthly_growth)

    return {
        'zone_activity': zone_activity,
        'product_stats': product_stats,
        'tech_stats': tech_stats,
        'monthly_growth': monthly_growth
    }

def create_success_visualizations(zone_activity, product_stats, tech_stats, monthly_growth):
    """Create visualizations for tender success analysis"""

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # 1. Zone activity distribution
    ax1 = axes[0, 0]
    activity_bins = [0, 10, 20, 50, 100, 500]
    zone_activity['activity_bin'] = pd.cut(zone_activity['total_dispatches'],
                                           bins=activity_bins,
                                           labels=['<10', '10-20', '20-50', '50-100', '100+'])
    activity_dist = zone_activity['activity_bin'].value_counts().sort_index()
    ax1.bar(range(len(activity_dist)), activity_dist.values, color='steelblue')
    ax1.set_xticks(range(len(activity_dist)))
    ax1.set_xticklabels(activity_dist.index)
    ax1.set_ylabel('Number of Zones', fontweight='bold')
    ax1.set_xlabel('Dispatch Count Range', fontweight='bold')
    ax1.set_title('Zone Activity Distribution', fontweight='bold', fontsize=12)
    ax1.grid(True, alpha=0.3, axis='y')

    # 2. Provider competition
    ax2 = axes[0, 1]
    provider_dist = zone_activity['num_providers'].value_counts().sort_index()
    ax2.bar(provider_dist.index, provider_dist.values, color='green')
    ax2.set_ylabel('Number of Zones', fontweight='bold')
    ax2.set_xlabel('Number of Providers', fontweight='bold')
    ax2.set_title('Provider Competition by Zone', fontweight='bold', fontsize=12)
    ax2.grid(True, alpha=0.3, axis='y')

    # 3. Product success
    ax3 = axes[1, 0]
    product_stats_sorted = product_stats.sort_values('total_dispatches', ascending=True)
    ax3.barh(range(len(product_stats_sorted)), product_stats_sorted['total_dispatches'], color='coral')
    ax3.set_yticks(range(len(product_stats_sorted)))
    ax3.set_yticklabels(product_stats_sorted.index)
    ax3.set_xlabel('Total Dispatches', fontweight='bold')
    ax3.set_title('Dispatch Success by Product', fontweight='bold', fontsize=12)
    ax3.grid(True, alpha=0.3, axis='x')

    # 4. Monthly growth
    ax4 = axes[1, 1]
    monthly_growth.index = monthly_growth.index.to_timestamp()
    ax4.plot(monthly_growth.index, monthly_growth['active_zones'],
             marker='o', linewidth=2, label='Active Zones', color='blue')
    ax4.plot(monthly_growth.index, monthly_growth['active_providers'],
             marker='s', linewidth=2, label='Active Providers', color='green')
    ax4.set_ylabel('Count', fontweight='bold')
    ax4.set_xlabel('Month', fontweight='bold')
    ax4.set_title('Market Participation Growth', fontweight='bold', fontsize=12)
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45, ha='right')

    plt.tight_layout()
    plt.savefig('tender_success_analysis.png', dpi=300, bbox_inches='tight')
    print("\n✓ Saved tender success visualization to tender_success_analysis.png")
    plt.close()

if __name__ == "__main__":
    results = analyze_tender_success()

    print("\n" + "="*80)
    print("TENDER SUCCESS ANALYSIS COMPLETE")
    print("="*80)
