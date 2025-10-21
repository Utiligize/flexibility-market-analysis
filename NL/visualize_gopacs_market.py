"""
Visualize GOPACS (Netherlands) Flexibility Market Data
Author: Data Analysis Script
Date: 2025-10-21

This script creates comprehensive visualizations of Dutch flexibility market data.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set plotting style
sns.set_style("whitegrid")
sns.set_palette("husl")
plt.rcParams['figure.dpi'] = 100
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10

class GopacsMarketVisualizer:
    """Create visualizations for GOPACS flexibility market data"""

    def __init__(self, csv_file: str = "gopacs_cleared_buckets.csv"):
        """Initialize visualizer with data from CSV file"""
        print(f"Loading data from {csv_file}...")
        self.df = pd.read_csv(csv_file)

        # Convert datetime columns
        datetime_cols = ['eventStartTime', 'eventEndTime', 'ptuStartTime', 'ptuEndTime']
        for col in datetime_cols:
            self.df[col] = pd.to_datetime(self.df[col])

        # Extract time features
        self.df['year'] = self.df['ptuStartTime'].dt.year
        self.df['month'] = self.df['ptuStartTime'].dt.month
        self.df['year_month'] = self.df['ptuStartTime'].dt.to_period('M')
        self.df['day_of_week'] = self.df['ptuStartTime'].dt.dayofweek
        self.df['hour'] = self.df['ptuStartTime'].dt.hour
        self.df['date'] = self.df['ptuStartTime'].dt.date

        # Calculate energy (MW * hours)
        self.df['energyMWh'] = self.df['buyVolumeInMW'] * 0.25  # 15-min PTU = 0.25 hours

        print(f"Loaded {len(self.df):,} records")

    def plot_yearly_trends(self, save_path: str = "yearly_trends.png"):
        """Plot yearly trends in cleared buckets"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))

        yearly_all = self.df.groupby('year').agg({
            'clearingEventId': 'nunique',
            'buyVolumeInMW': 'sum',
            'energyMWh': 'sum',
            'organisationName': 'nunique'
        }).rename(columns={'clearingEventId': 'events', 'organisationName': 'operators'})

        # Plot 1: Number of events
        ax1 = axes[0, 0]
        ax1.bar(yearly_all.index, yearly_all['events'], color='steelblue', edgecolor='black')
        ax1.set_ylabel('Number of Events', fontsize=12, fontweight='bold')
        ax1.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax1.set_title('Annual Clearing Events', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='y')

        # Plot 2: Total volume (MW-PTUs)
        ax2 = axes[0, 1]
        ax2.bar(yearly_all.index, yearly_all['buyVolumeInMW'], color='green', edgecolor='black')
        ax2.set_ylabel('Total Volume (MW)', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax2.set_title('Annual Volume (MW-PTUs)', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')

        # Plot 3: Energy
        ax3 = axes[1, 0]
        ax3.bar(yearly_all.index, yearly_all['energyMWh'], color='orange', edgecolor='black')
        ax3.set_ylabel('Energy (MWh)', fontsize=12, fontweight='bold')
        ax3.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax3.set_title('Annual Energy Cleared', fontsize=14, fontweight='bold')
        ax3.grid(True, alpha=0.3, axis='y')

        # Plot 4: TSO vs DSO split by year
        ax4 = axes[1, 1]
        tso_yearly = self.df[self.df['organisationName'] == 'TenneT'].groupby('year')['clearingEventId'].nunique()
        dso_yearly = self.df[self.df['organisationName'] != 'TenneT'].groupby('year')['clearingEventId'].nunique()

        x = yearly_all.index
        width = 0.35
        ax4.bar(x - width/2, tso_yearly.reindex(x, fill_value=0), width, label='TSO (TenneT)', color='darkblue')
        ax4.bar(x + width/2, dso_yearly.reindex(x, fill_value=0), width, label='DSO (Others)', color='lightblue')
        ax4.set_ylabel('Number of Events', fontsize=12, fontweight='bold')
        ax4.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax4.set_title('TSO vs DSO Events by Year', fontsize=14, fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        plt.savefig(save_path, bbox_inches='tight')
        print(f"✓ Saved yearly trends to {save_path}")
        plt.close()

    def plot_operator_comparison(self, save_path: str = "operator_comparison.png"):
        """Plot comparison between grid operators"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))

        operator_data = self.df.groupby('organisationName').agg({
            'clearingEventId': 'nunique',
            'buyVolumeInMW': 'sum',
            'energyMWh': 'sum'
        }).rename(columns={'clearingEventId': 'events'})
        operator_data = operator_data.sort_values('events', ascending=False)

        colors = ['#003f5c', '#58508d', '#bc5090', '#ff6361']

        # Plot 1: Events by operator
        ax1 = axes[0, 0]
        ax1.barh(range(len(operator_data)), operator_data['events'], color=colors)
        ax1.set_yticks(range(len(operator_data)))
        ax1.set_yticklabels(operator_data.index)
        ax1.set_xlabel('Number of Events', fontsize=11, fontweight='bold')
        ax1.set_title('Clearing Events by Grid Operator', fontsize=12, fontweight='bold')
        ax1.invert_yaxis()
        ax1.grid(True, alpha=0.3, axis='x')

        # Plot 2: Volume by operator (log scale for visibility)
        ax2 = axes[0, 1]
        ax2.barh(range(len(operator_data)), operator_data['buyVolumeInMW'], color=colors)
        ax2.set_yticks(range(len(operator_data)))
        ax2.set_yticklabels(operator_data.index)
        ax2.set_xlabel('Total Volume (MW) - Log Scale', fontsize=11, fontweight='bold')
        ax2.set_title('Total Volume by Grid Operator', fontsize=12, fontweight='bold')
        ax2.set_xscale('log')
        ax2.invert_yaxis()
        ax2.grid(True, alpha=0.3, axis='x')

        # Plot 3: Pie chart - events share
        ax3 = axes[1, 0]
        ax3.pie(operator_data['events'], labels=operator_data.index, autopct='%1.1f%%',
                colors=colors, startangle=90)
        ax3.set_title('Event Share by Operator', fontsize=12, fontweight='bold')

        # Plot 4: Pie chart - volume share
        ax4 = axes[1, 1]
        # For pie chart, separate TSO vs combined DSOs for better visibility
        tso_vol = operator_data.loc['TenneT', 'buyVolumeInMW']
        dso_vol = operator_data.drop('TenneT')['buyVolumeInMW'].sum()

        ax4.pie([tso_vol, dso_vol], labels=['TSO (TenneT)', 'DSO (All)'],
                autopct='%1.1f%%', colors=['#003f5c', '#ff6361'], startangle=90)
        ax4.set_title('Volume Share: TSO vs DSO', fontsize=12, fontweight='bold')

        plt.tight_layout()
        plt.savefig(save_path, bbox_inches='tight')
        print(f"✓ Saved operator comparison to {save_path}")
        plt.close()

    def plot_temporal_patterns(self, save_path: str = "temporal_patterns.png"):
        """Plot daily and hourly patterns"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))

        # Day of week
        dow_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        dow_data = self.df.groupby('day_of_week').agg({
            'clearingEventId': 'nunique',
            'buyVolumeInMW': 'sum'
        })

        ax1 = axes[0, 0]
        ax1.bar(range(7), dow_data['clearingEventId'], color=sns.color_palette("husl", 7))
        ax1.set_xticks(range(7))
        ax1.set_xticklabels(dow_names)
        ax1.set_ylabel('Number of Events', fontsize=11, fontweight='bold')
        ax1.set_xlabel('Day of Week', fontsize=11, fontweight='bold')
        ax1.set_title('Events by Day of Week', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='y')

        # Hourly pattern
        hourly_data = self.df.groupby('hour').agg({
            'clearingEventId': 'nunique',
            'buyVolumeInMW': 'sum'
        })

        ax2 = axes[0, 1]
        ax2.bar(hourly_data.index, hourly_data['buyVolumeInMW'], color='steelblue')
        ax2.set_ylabel('Total Volume (MW)', fontsize=11, fontweight='bold')
        ax2.set_xlabel('Hour of Day', fontsize=11, fontweight='bold')
        ax2.set_title('Volume by Hour of Day', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')

        # Monthly trend over time
        monthly = self.df.groupby('year_month').agg({
            'clearingEventId': 'nunique',
            'buyVolumeInMW': 'sum'
        })
        monthly.index = monthly.index.to_timestamp()

        ax3 = axes[1, 0]
        ax3.plot(monthly.index, monthly['clearingEventId'], marker='o', linewidth=2, markersize=4)
        ax3.fill_between(monthly.index, monthly['clearingEventId'], alpha=0.3)
        ax3.set_ylabel('Number of Events', fontsize=11, fontweight='bold')
        ax3.set_xlabel('Month', fontsize=11, fontweight='bold')
        ax3.set_title('Monthly Event Trend', fontsize=12, fontweight='bold')
        ax3.grid(True, alpha=0.3)
        plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45, ha='right')

        # Event duration distribution
        events = self.df.groupby('clearingEventId')['eventDurationHours'].first()

        ax4 = axes[1, 1]
        ax4.hist(events, bins=30, color='green', edgecolor='black', alpha=0.7)
        ax4.axvline(events.mean(), color='red', linestyle='--', linewidth=2,
                   label=f'Mean: {events.mean():.1f}h')
        ax4.axvline(events.median(), color='orange', linestyle='--', linewidth=2,
                   label=f'Median: {events.median():.1f}h')
        ax4.set_ylabel('Frequency', fontsize=11, fontweight='bold')
        ax4.set_xlabel('Event Duration (hours)', fontsize=11, fontweight='bold')
        ax4.set_title('Event Duration Distribution', fontsize=12, fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        plt.savefig(save_path, bbox_inches='tight')
        print(f"✓ Saved temporal patterns to {save_path}")
        plt.close()

    def plot_dso_detail(self, save_path: str = "dso_detail.png"):
        """Plot detailed DSO analysis"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))

        dso_data = self.df[self.df['organisationName'] != 'TenneT']

        # DSO comparison
        dso_stats = dso_data.groupby('organisationName').agg({
            'clearingEventId': 'nunique',
            'buyVolumeInMW': ['sum', 'mean'],
            'energyMWh': 'sum'
        })
        dso_stats.columns = ['events', 'total_mw', 'avg_mw', 'energy_mwh']
        dso_stats = dso_stats.sort_values('events', ascending=False)

        # Plot 1: Events by DSO
        ax1 = axes[0, 0]
        colors_dso = ['#bc5090', '#ff6361', '#ffa600']
        ax1.bar(range(len(dso_stats)), dso_stats['events'], color=colors_dso, edgecolor='black')
        ax1.set_xticks(range(len(dso_stats)))
        ax1.set_xticklabels(dso_stats.index, rotation=0)
        ax1.set_ylabel('Number of Events', fontsize=11, fontweight='bold')
        ax1.set_title('DSO Events Comparison', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='y')

        # Plot 2: Energy by DSO
        ax2 = axes[0, 1]
        ax2.bar(range(len(dso_stats)), dso_stats['energy_mwh'], color=colors_dso, edgecolor='black')
        ax2.set_xticks(range(len(dso_stats)))
        ax2.set_xticklabels(dso_stats.index, rotation=0)
        ax2.set_ylabel('Energy (MWh)', fontsize=11, fontweight='bold')
        ax2.set_title('DSO Energy Cleared', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')

        # Plot 3: DSO yearly trend
        ax3 = axes[1, 0]
        for i, dso in enumerate(dso_stats.index):
            dso_yearly = dso_data[dso_data['organisationName'] == dso].groupby('year')['clearingEventId'].nunique()
            ax3.plot(dso_yearly.index, dso_yearly.values, marker='o', linewidth=2,
                    label=dso, color=colors_dso[i])
        ax3.set_ylabel('Number of Events', fontsize=11, fontweight='bold')
        ax3.set_xlabel('Year', fontsize=11, fontweight='bold')
        ax3.set_title('DSO Events Over Time', fontsize=12, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        # Plot 4: Average PTU volume by DSO
        ax4 = axes[1, 1]
        ax4.bar(range(len(dso_stats)), dso_stats['avg_mw'], color=colors_dso, edgecolor='black')
        ax4.set_xticks(range(len(dso_stats)))
        ax4.set_xticklabels(dso_stats.index, rotation=0)
        ax4.set_ylabel('Average MW per PTU', fontsize=11, fontweight='bold')
        ax4.set_title('DSO Average PTU Volume', fontsize=12, fontweight='bold')
        ax4.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        plt.savefig(save_path, bbox_inches='tight')
        print(f"✓ Saved DSO detail to {save_path}")
        plt.close()

    def plot_volume_analysis(self, save_path: str = "volume_analysis.png"):
        """Plot volume distribution and analysis"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))

        # Plot 1: Volume distribution histogram (log scale)
        ax1 = axes[0, 0]
        volume_data = self.df[self.df['buyVolumeInMW'] > 0]['buyVolumeInMW']
        ax1.hist(volume_data, bins=50, color='steelblue', edgecolor='black', alpha=0.7)
        ax1.set_ylabel('Frequency', fontsize=11, fontweight='bold')
        ax1.set_xlabel('Volume (MW) - Log Scale', fontsize=11, fontweight='bold')
        ax1.set_title('PTU Volume Distribution', fontsize=12, fontweight='bold')
        ax1.set_xscale('log')
        ax1.grid(True, alpha=0.3, axis='y')

        # Plot 2: Box plot by operator
        ax2 = axes[0, 1]
        operators = self.df['organisationName'].unique()
        box_data = [self.df[self.df['organisationName'] == op]['buyVolumeInMW'].values for op in operators]
        bp = ax2.boxplot(box_data, labels=operators, patch_artist=True)
        for patch, color in zip(bp['boxes'], ['#003f5c', '#58508d', '#bc5090', '#ff6361']):
            patch.set_facecolor(color)
        ax2.set_ylabel('Volume (MW) - Log Scale', fontsize=11, fontweight='bold')
        ax2.set_title('Volume Distribution by Operator', fontsize=12, fontweight='bold')
        ax2.set_yscale('log')
        ax2.tick_params(axis='x', rotation=45)
        ax2.grid(True, alpha=0.3, axis='y')

        # Plot 3: TSO vs DSO volume over time
        ax3 = axes[1, 0]
        tso_monthly = self.df[self.df['organisationName'] == 'TenneT'].groupby('year_month')['buyVolumeInMW'].sum()
        dso_monthly = self.df[self.df['organisationName'] != 'TenneT'].groupby('year_month')['buyVolumeInMW'].sum()

        tso_monthly.index = tso_monthly.index.to_timestamp()
        dso_monthly.index = dso_monthly.index.to_timestamp()

        ax3.plot(tso_monthly.index, tso_monthly.values, marker='o', linewidth=2, label='TSO (TenneT)', color='darkblue')
        ax3.plot(dso_monthly.index, dso_monthly.values, marker='s', linewidth=2, label='DSO (All)', color='lightblue')
        ax3.set_ylabel('Volume (MW)', fontsize=11, fontweight='bold')
        ax3.set_xlabel('Month', fontsize=11, fontweight='bold')
        ax3.set_title('Monthly Volume: TSO vs DSO', fontsize=12, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45, ha='right')

        # Plot 4: Cumulative energy
        ax4 = axes[1, 1]
        daily = self.df.groupby('date')['energyMWh'].sum().sort_index()
        cumulative = daily.cumsum()

        ax4.plot(cumulative.index, cumulative.values, linewidth=2, color='green')
        ax4.fill_between(cumulative.index, cumulative.values, alpha=0.3, color='green')
        ax4.set_ylabel('Cumulative Energy (MWh)', fontsize=11, fontweight='bold')
        ax4.set_xlabel('Date', fontsize=11, fontweight='bold')
        ax4.set_title('Cumulative Energy Cleared', fontsize=12, fontweight='bold')
        ax4.grid(True, alpha=0.3)
        plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45, ha='right')

        plt.tight_layout()
        plt.savefig(save_path, bbox_inches='tight')
        print(f"✓ Saved volume analysis to {save_path}")
        plt.close()

    def generate_all_plots(self):
        """Generate all visualization plots"""
        print("\n" + "="*80)
        print("GENERATING GOPACS MARKET VISUALIZATIONS")
        print("="*80 + "\n")

        self.plot_yearly_trends()
        self.plot_operator_comparison()
        self.plot_temporal_patterns()
        self.plot_dso_detail()
        self.plot_volume_analysis()

        print("\n" + "="*80)
        print("ALL VISUALIZATIONS GENERATED SUCCESSFULLY")
        print("="*80)


if __name__ == "__main__":
    # Create visualizer instance
    viz = GopacsMarketVisualizer("gopacs_cleared_buckets.csv")

    # Generate all plots
    viz.generate_all_plots()

    print("\n\nAll visualization files saved:")
    print("- yearly_trends.png")
    print("- operator_comparison.png")
    print("- temporal_patterns.png")
    print("- dso_detail.png")
    print("- volume_analysis.png")
