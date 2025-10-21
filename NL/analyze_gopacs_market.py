"""
Analyze GOPACS (Netherlands) Flexibility Market
Author: Data Analysis Script
Date: 2025-10-21

This script performs detailed analysis of Dutch flexibility market cleared buckets.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class GopacsMarketAnalyzer:
    """Analyzer for GOPACS cleared buckets data"""

    def __init__(self, csv_file: str = "gopacs_cleared_buckets.csv"):
        """
        Initialize analyzer with data from CSV file.

        Args:
            csv_file: Path to CSV file containing cleared bucket data
        """
        print(f"Loading data from {csv_file}...")
        self.df = pd.read_csv(csv_file)

        # Convert datetime columns
        datetime_cols = ['eventStartTime', 'eventEndTime', 'ptuStartTime', 'ptuEndTime']
        for col in datetime_cols:
            self.df[col] = pd.to_datetime(self.df[col])

        # Extract time features
        self.df['year'] = self.df['ptuStartTime'].dt.year
        self.df['month'] = self.df['ptuStartTime'].dt.month
        self.df['week'] = self.df['ptuStartTime'].dt.isocalendar().week
        self.df['day_of_week'] = self.df['ptuStartTime'].dt.dayofweek
        self.df['hour'] = self.df['ptuStartTime'].dt.hour
        self.df['date'] = self.df['ptuStartTime'].dt.date

        print(f"Loaded {len(self.df):,} PTU records from {self.df['clearingEventId'].nunique()} clearing events")
        print(f"Date range: {self.df['ptuStartTime'].min()} to {self.df['ptuStartTime'].max()}")

    def analyze_temporal_patterns(self):
        """Analyze temporal patterns in cleared buckets"""
        print("\n" + "="*80)
        print("TEMPORAL ANALYSIS")
        print("="*80)

        # Monthly trends
        monthly = self.df.groupby(['year', 'month']).agg({
            'clearingEventId': 'nunique',
            'buyVolumeInMW': 'sum',
            'sellVolumeInMW': 'sum'
        }).rename(columns={'clearingEventId': 'num_events'})

        print("\nMONTHLY TRENDS:")
        print(monthly.tail(24))  # Last 2 years

        # Day of week analysis
        dow_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dow_analysis = self.df.groupby('day_of_week').agg({
            'clearingEventId': 'nunique',
            'buyVolumeInMW': 'sum',
            'sellVolumeInMW': 'sum'
        }).rename(columns={'clearingEventId': 'num_events'})
        dow_analysis.index = [dow_names[i] for i in dow_analysis.index]

        print("\nCLEARED BUCKETS BY DAY OF WEEK:")
        print(dow_analysis)

        # Hourly patterns
        hourly = self.df.groupby('hour').agg({
            'clearingEventId': 'nunique',
            'buyVolumeInMW': 'sum',
            'sellVolumeInMW': 'sum'
        }).rename(columns={'clearingEventId': 'num_events'})

        print("\nHOURLY PATTERNS (Top 10 hours):")
        print(hourly.nlargest(10, 'buyVolumeInMW'))

        return monthly, dow_analysis, hourly

    def analyze_by_operator(self):
        """Analyze cleared buckets by grid operator"""
        print("\n" + "="*80)
        print("GRID OPERATOR ANALYSIS")
        print("="*80)

        operator_analysis = self.df.groupby('organisationName').agg({
            'clearingEventId': 'nunique',
            'buyVolumeInMW': ['sum', 'mean', 'median', 'max'],
            'sellVolumeInMW': ['sum', 'mean', 'median', 'max'],
            'eventDurationHours': 'mean'
        }).round(2)

        operator_analysis.columns = [
            'num_events',
            'total_buy_mw', 'avg_buy_mw', 'median_buy_mw', 'max_buy_mw',
            'total_sell_mw', 'avg_sell_mw', 'median_sell_mw', 'max_sell_mw',
            'avg_duration_hours'
        ]

        operator_analysis = operator_analysis.sort_values('num_events', ascending=False)

        print("\nGRID OPERATORS SUMMARY:")
        print(operator_analysis)

        # Operator type classification
        print("\n" + "-"*80)
        print("OPERATOR TYPE BREAKDOWN:")
        print("-"*80)

        tso = self.df[self.df['organisationName'] == 'TenneT']
        dso = self.df[self.df['organisationName'] != 'TenneT']

        print(f"TSO (TenneT) events: {tso['clearingEventId'].nunique()}")
        print(f"DSO (Liander, Enexis, Stedin) events: {dso['clearingEventId'].nunique()}")
        print(f"\nTSO average volume: {tso['buyVolumeInMW'].mean():.2f} MW")
        print(f"DSO average volume: {dso['buyVolumeInMW'].mean():.2f} MW")
        print(f"\nTSO total volume: {tso['buyVolumeInMW'].sum():.2f} MW")
        print(f"DSO total volume: {dso['buyVolumeInMW'].sum():.2f} MW")

        return operator_analysis

    def analyze_volume_patterns(self):
        """Analyze volume patterns and distributions"""
        print("\n" + "="*80)
        print("VOLUME ANALYSIS")
        print("="*80)

        print("\nBUY VOLUME STATISTICS (MW):")
        print(f"Mean: {self.df['buyVolumeInMW'].mean():.2f} MW")
        print(f"Median: {self.df['buyVolumeInMW'].median():.2f} MW")
        print(f"Min: {self.df['buyVolumeInMW'].min():.2f} MW")
        print(f"Max: {self.df['buyVolumeInMW'].max():.2f} MW")
        print(f"Std Dev: {self.df['buyVolumeInMW'].std():.2f} MW")

        # Volume distribution by operator
        print("\n" + "-"*80)
        print("VOLUME DISTRIBUTION BY OPERATOR:")
        print("-"*80)
        vol_dist = self.df.groupby('organisationName')['buyVolumeInMW'].describe()
        print(vol_dist)

        return vol_dist

    def analyze_event_characteristics(self):
        """Analyze clearing event characteristics"""
        print("\n" + "="*80)
        print("CLEARING EVENT CHARACTERISTICS")
        print("="*80)

        # Aggregate by event
        events = self.df.groupby('clearingEventId').agg({
            'organisationName': 'first',
            'buyVolumeInMWh': 'first',
            'sellVolumeInMWh': 'first',
            'eventDurationHours': 'first',
            'eventStartTime': 'first'
        })

        print(f"\nTotal clearing events: {len(events)}")
        print(f"Average event duration: {events['eventDurationHours'].mean():.2f} hours")
        print(f"Median event duration: {events['eventDurationHours'].median():.2f} hours")

        print("\nEVENT DURATION DISTRIBUTION:")
        duration_bins = [0, 1, 2, 4, 8, 24, float('inf')]
        duration_labels = ['< 1h', '1-2h', '2-4h', '4-8h', '8-24h', '> 24h']
        events['duration_category'] = pd.cut(events['eventDurationHours'],
                                             bins=duration_bins,
                                             labels=duration_labels)
        print(events['duration_category'].value_counts().sort_index())

        return events

    def growth_analysis(self):
        """Analyze market growth over time"""
        print("\n" + "="*80)
        print("MARKET GROWTH ANALYSIS")
        print("="*80)

        # Yearly aggregation
        yearly = self.df.groupby('year').agg({
            'clearingEventId': 'nunique',
            'buyVolumeInMW': 'sum',
            'organisationName': 'nunique'
        }).rename(columns={
            'clearingEventId': 'num_events',
            'organisationName': 'num_operators'
        })

        print("\nYEARLY GROWTH:")
        print(yearly)

        # Calculate year-over-year growth
        yearly['event_growth_%'] = yearly['num_events'].pct_change() * 100
        yearly['volume_growth_%'] = yearly['buyVolumeInMW'].pct_change() * 100

        print("\nYEAR-OVER-YEAR GROWTH:")
        print(yearly[['event_growth_%', 'volume_growth_%']].dropna().round(1))

        return yearly

    def generate_summary_report(self):
        """Generate a comprehensive summary report"""
        print("\n" + "="*80)
        print("COMPREHENSIVE SUMMARY REPORT")
        print("GOPACS (Netherlands) Flexibility Market Analysis")
        print("="*80)

        print(f"\nReport Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Data Period: {self.df['ptuStartTime'].min()} to {self.df['ptuStartTime'].max()}")

        print("\n" + "-"*80)
        print("OVERALL STATISTICS")
        print("-"*80)
        print(f"Total Clearing Events: {self.df['clearingEventId'].nunique():,}")
        print(f"Total PTU Records: {len(self.df):,}")
        print(f"Total Buy Volume: {self.df['buyVolumeInMW'].sum():,.2f} MW")
        print(f"Total Sell Volume: {self.df['sellVolumeInMW'].sum():,.2f} MW")
        print(f"Average Volume per PTU: {self.df['buyVolumeInMW'].mean():.2f} MW")

        print(f"\nNumber of Grid Operators: {self.df['organisationName'].nunique()}")
        print(f"Operators: {', '.join(sorted(self.df['organisationName'].unique()))}")

        print("\n" + "-"*80)
        print("MARKET CHARACTERISTICS")
        print("-"*80)
        print(f"Average PTU Duration: {self.df['ptuDurationMinutes'].mean():.1f} minutes")
        print(f"Average Event Duration: {self.df['eventDurationHours'].mean():.2f} hours")
        print(f"Median Event Duration: {self.df['eventDurationHours'].median():.2f} hours")

        # Run all analyses
        monthly, dow, hourly = self.analyze_temporal_patterns()
        operator_analysis = self.analyze_by_operator()
        vol_dist = self.analyze_volume_patterns()
        events = self.analyze_event_characteristics()
        yearly = self.growth_analysis()

        print("\n" + "="*80)
        print("ANALYSIS COMPLETE")
        print("="*80)

        return {
            'monthly': monthly,
            'dow': dow,
            'hourly': hourly,
            'operator': operator_analysis,
            'volume_dist': vol_dist,
            'events': events,
            'yearly': yearly
        }


if __name__ == "__main__":
    # Create analyzer instance
    analyzer = GopacsMarketAnalyzer("gopacs_cleared_buckets.csv")

    # Run comprehensive analysis
    results = analyzer.generate_summary_report()

    print("\n\nAnalysis results saved in 'results' dictionary")
    print("Run visualize_gopacs_market.py to generate charts and graphs")
