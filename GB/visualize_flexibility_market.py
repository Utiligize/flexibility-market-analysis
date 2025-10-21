"""
Visualize UK Power Networks Flexibility Market Data
Author: Data Analysis Script
Date: 2025-10-21

This script creates comprehensive visualizations of flexibility market activations
at the DNO level, including trends, geographic distributions, and market dynamics.
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

class FlexibilityMarketVisualizer:
    """Create visualizations for UKPN flexibility market data"""

    def __init__(self, csv_file: str = "ukpn_flexibility_dispatches.csv"):
        """Initialize visualizer with data from CSV file"""
        print(f"Loading data from {csv_file}...")
        self.df = pd.read_csv(csv_file)

        # Convert datetime columns
        self.df['start_time_local'] = pd.to_datetime(self.df['start_time_local'])
        self.df['end_time_local'] = pd.to_datetime(self.df['end_time_local'])

        # Extract time features
        self.df['year'] = self.df['start_time_local'].dt.year
        self.df['month'] = self.df['start_time_local'].dt.month
        self.df['year_month'] = self.df['start_time_local'].dt.to_period('M')
        self.df['week'] = self.df['start_time_local'].dt.isocalendar().week
        self.df['day_of_week'] = self.df['start_time_local'].dt.dayofweek
        self.df['hour'] = self.df['start_time_local'].dt.hour
        self.df['date'] = self.df['start_time_local'].dt.date

        # Calculate costs
        self.df['availability_cost'] = self.df['availability_mwh_req'] * self.df['availability_price']
        self.df['utilisation_cost'] = self.df['utilisation_mwh_req'] * self.df['utilisation_price']
        self.df['total_cost'] = self.df['availability_cost'] + self.df['utilisation_cost']

        print(f"Loaded {len(self.df):,} records")

    def plot_temporal_trends(self, save_path: str = "temporal_trends.png"):
        """Plot temporal trends in flexibility dispatches"""
        fig, axes = plt.subplots(3, 1, figsize=(16, 12))

        # Monthly trends
        monthly = self.df.groupby('year_month').agg({
            'fu_id': 'count',
            'utilisation_mwh_req': 'sum',
            'total_cost': 'sum'
        })
        monthly.index = monthly.index.to_timestamp()

        ax1, ax2, ax3 = axes

        # Plot 1: Monthly dispatch count
        ax1.plot(monthly.index, monthly['fu_id'], marker='o', linewidth=2, markersize=6)
        ax1.fill_between(monthly.index, monthly['fu_id'], alpha=0.3)
        ax1.set_ylabel('Number of Dispatches', fontsize=12, fontweight='bold')
        ax1.set_title('Monthly Flexibility Dispatch Trends', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)

        # Plot 2: Monthly energy
        ax2.plot(monthly.index, monthly['utilisation_mwh_req'], marker='o',
                linewidth=2, markersize=6, color='green')
        ax2.fill_between(monthly.index, monthly['utilisation_mwh_req'], alpha=0.3, color='green')
        ax2.set_ylabel('Energy Dispatched (MWh)', fontsize=12, fontweight='bold')
        ax2.set_title('Monthly Energy Dispatch Volume', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)

        # Plot 3: Monthly cost
        ax3.plot(monthly.index, monthly['total_cost'], marker='o',
                linewidth=2, markersize=6, color='red')
        ax3.fill_between(monthly.index, monthly['total_cost'], alpha=0.3, color='red')
        ax3.set_ylabel('Total Cost (£)', fontsize=12, fontweight='bold')
        ax3.set_xlabel('Month', fontsize=12, fontweight='bold')
        ax3.set_title('Monthly Flexibility Service Costs', fontsize=14, fontweight='bold')
        ax3.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(save_path, bbox_inches='tight')
        print(f"Saved temporal trends plot to {save_path}")
        plt.close()

    def plot_daily_weekly_patterns(self, save_path: str = "daily_weekly_patterns.png"):
        """Plot daily and weekly dispatch patterns"""
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))

        # Day of week analysis
        dow_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        dow_data = self.df.groupby('day_of_week').agg({
            'fu_id': 'count',
            'utilisation_mwh_req': 'sum'
        })

        axes[0].bar(range(7), dow_data['fu_id'], color=sns.color_palette("husl", 7))
        axes[0].set_xticks(range(7))
        axes[0].set_xticklabels(dow_names)
        axes[0].set_ylabel('Number of Dispatches', fontsize=12, fontweight='bold')
        axes[0].set_xlabel('Day of Week', fontsize=12, fontweight='bold')
        axes[0].set_title('Dispatches by Day of Week', fontsize=14, fontweight='bold')
        axes[0].grid(True, alpha=0.3, axis='y')

        # Hourly patterns
        hourly_data = self.df.groupby('hour').agg({
            'fu_id': 'count',
            'utilisation_mwh_req': 'sum'
        })

        axes[1].bar(hourly_data.index, hourly_data['fu_id'], color='steelblue')
        axes[1].set_ylabel('Number of Dispatches', fontsize=12, fontweight='bold')
        axes[1].set_xlabel('Hour of Day', fontsize=12, fontweight='bold')
        axes[1].set_title('Dispatches by Hour of Day', fontsize=14, fontweight='bold')
        axes[1].set_xticks(range(0, 24, 2))
        axes[1].grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        plt.savefig(save_path, bbox_inches='tight')
        print(f"Saved daily/weekly patterns plot to {save_path}")
        plt.close()

    def plot_zone_analysis(self, save_path: str = "zone_analysis.png", top_n: int = 20):
        """Plot analysis by flexibility zone"""
        fig, axes = plt.subplots(2, 2, figsize=(18, 12))

        zone_data = self.df.groupby('zone').agg({
            'fu_id': 'count',
            'utilisation_mwh_req': 'sum',
            'total_cost': 'sum',
            'utilisation_price': 'mean'
        }).rename(columns={'fu_id': 'count'})

        # Top zones by dispatch count
        top_zones_count = zone_data.nlargest(top_n, 'count')
        axes[0, 0].barh(range(top_n), top_zones_count['count'], color='skyblue')
        axes[0, 0].set_yticks(range(top_n))
        axes[0, 0].set_yticklabels(top_zones_count.index, fontsize=9)
        axes[0, 0].set_xlabel('Number of Dispatches', fontsize=11, fontweight='bold')
        axes[0, 0].set_title(f'Top {top_n} Zones by Dispatch Count', fontsize=12, fontweight='bold')
        axes[0, 0].invert_yaxis()
        axes[0, 0].grid(True, alpha=0.3, axis='x')

        # Top zones by energy
        top_zones_energy = zone_data.nlargest(top_n, 'utilisation_mwh_req')
        axes[0, 1].barh(range(top_n), top_zones_energy['utilisation_mwh_req'], color='green')
        axes[0, 1].set_yticks(range(top_n))
        axes[0, 1].set_yticklabels(top_zones_energy.index, fontsize=9)
        axes[0, 1].set_xlabel('Energy Dispatched (MWh)', fontsize=11, fontweight='bold')
        axes[0, 1].set_title(f'Top {top_n} Zones by Energy Dispatched', fontsize=12, fontweight='bold')
        axes[0, 1].invert_yaxis()
        axes[0, 1].grid(True, alpha=0.3, axis='x')

        # Top zones by cost
        top_zones_cost = zone_data.nlargest(top_n, 'total_cost')
        axes[1, 0].barh(range(top_n), top_zones_cost['total_cost'], color='coral')
        axes[1, 0].set_yticks(range(top_n))
        axes[1, 0].set_yticklabels(top_zones_cost.index, fontsize=9)
        axes[1, 0].set_xlabel('Total Cost (£)', fontsize=11, fontweight='bold')
        axes[1, 0].set_title(f'Top {top_n} Zones by Total Cost', fontsize=12, fontweight='bold')
        axes[1, 0].invert_yaxis()
        axes[1, 0].grid(True, alpha=0.3, axis='x')

        # Average price by zone
        top_zones_price = zone_data.nlargest(top_n, 'utilisation_price')
        axes[1, 1].barh(range(top_n), top_zones_price['utilisation_price'], color='purple')
        axes[1, 1].set_yticks(range(top_n))
        axes[1, 1].set_yticklabels(top_zones_price.index, fontsize=9)
        axes[1, 1].set_xlabel('Average Price (£/MWh)', fontsize=11, fontweight='bold')
        axes[1, 1].set_title(f'Top {top_n} Zones by Average Price', fontsize=12, fontweight='bold')
        axes[1, 1].invert_yaxis()
        axes[1, 1].grid(True, alpha=0.3, axis='x')

        plt.tight_layout()
        plt.savefig(save_path, bbox_inches='tight')
        print(f"Saved zone analysis plot to {save_path}")
        plt.close()

    def plot_technology_analysis(self, save_path: str = "technology_analysis.png"):
        """Plot analysis by technology type"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))

        tech_data = self.df.groupby('technology').agg({
            'fu_id': 'count',
            'utilisation_mwh_req': 'sum',
            'total_cost': 'sum',
            'utilisation_price': 'mean'
        }).rename(columns={'fu_id': 'count'})
        tech_data = tech_data.sort_values('count', ascending=False)

        # Technology distribution (pie chart)
        colors = sns.color_palette("husl", len(tech_data))
        axes[0, 0].pie(tech_data['count'], labels=tech_data.index, autopct='%1.1f%%',
                       colors=colors, startangle=90)
        axes[0, 0].set_title('Distribution of Dispatches by Technology', fontsize=12, fontweight='bold')

        # Energy by technology
        tech_data.plot(kind='bar', y='utilisation_mwh_req', ax=axes[0, 1],
                      color='green', legend=False)
        axes[0, 1].set_ylabel('Energy Dispatched (MWh)', fontsize=11, fontweight='bold')
        axes[0, 1].set_xlabel('Technology', fontsize=11, fontweight='bold')
        axes[0, 1].set_title('Energy Dispatched by Technology', fontsize=12, fontweight='bold')
        axes[0, 1].tick_params(axis='x', rotation=45)
        axes[0, 1].grid(True, alpha=0.3, axis='y')

        # Cost by technology
        tech_data.plot(kind='bar', y='total_cost', ax=axes[1, 0],
                      color='coral', legend=False)
        axes[1, 0].set_ylabel('Total Cost (£)', fontsize=11, fontweight='bold')
        axes[1, 0].set_xlabel('Technology', fontsize=11, fontweight='bold')
        axes[1, 0].set_title('Total Cost by Technology', fontsize=12, fontweight='bold')
        axes[1, 0].tick_params(axis='x', rotation=45)
        axes[1, 0].grid(True, alpha=0.3, axis='y')

        # Average price by technology
        tech_data.plot(kind='bar', y='utilisation_price', ax=axes[1, 1],
                      color='purple', legend=False)
        axes[1, 1].set_ylabel('Average Price (£/MWh)', fontsize=11, fontweight='bold')
        axes[1, 1].set_xlabel('Technology', fontsize=11, fontweight='bold')
        axes[1, 1].set_title('Average Price by Technology', fontsize=12, fontweight='bold')
        axes[1, 1].tick_params(axis='x', rotation=45)
        axes[1, 1].grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        plt.savefig(save_path, bbox_inches='tight')
        print(f"Saved technology analysis plot to {save_path}")
        plt.close()

    def plot_product_analysis(self, save_path: str = "product_analysis.png"):
        """Plot analysis by product type"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        product_data = self.df.groupby('product').agg({
            'fu_id': 'count',
            'utilisation_mwh_req': 'sum',
            'total_cost': 'sum',
            'utilisation_price': 'mean'
        }).rename(columns={'fu_id': 'count'})

        # Product distribution
        colors = sns.color_palette("Set2", len(product_data))
        axes[0, 0].pie(product_data['count'], labels=product_data.index, autopct='%1.1f%%',
                       colors=colors, startangle=90)
        axes[0, 0].set_title('Dispatch Distribution by Product', fontsize=12, fontweight='bold')

        # Count by product
        product_data.plot(kind='bar', y='count', ax=axes[0, 1], color='steelblue', legend=False)
        axes[0, 1].set_ylabel('Number of Dispatches', fontsize=11, fontweight='bold')
        axes[0, 1].set_xlabel('Product', fontsize=11, fontweight='bold')
        axes[0, 1].set_title('Dispatches by Product Type', fontsize=12, fontweight='bold')
        axes[0, 1].tick_params(axis='x', rotation=45)
        axes[0, 1].grid(True, alpha=0.3, axis='y')

        # Energy by product
        product_data.plot(kind='bar', y='utilisation_mwh_req', ax=axes[1, 0],
                         color='green', legend=False)
        axes[1, 0].set_ylabel('Energy Dispatched (MWh)', fontsize=11, fontweight='bold')
        axes[1, 0].set_xlabel('Product', fontsize=11, fontweight='bold')
        axes[1, 0].set_title('Energy Dispatched by Product', fontsize=12, fontweight='bold')
        axes[1, 0].tick_params(axis='x', rotation=45)
        axes[1, 0].grid(True, alpha=0.3, axis='y')

        # Price by product
        product_data.plot(kind='bar', y='utilisation_price', ax=axes[1, 1],
                         color='purple', legend=False)
        axes[1, 1].set_ylabel('Average Price (£/MWh)', fontsize=11, fontweight='bold')
        axes[1, 1].set_xlabel('Product', fontsize=11, fontweight='bold')
        axes[1, 1].set_title('Average Price by Product', fontsize=12, fontweight='bold')
        axes[1, 1].tick_params(axis='x', rotation=45)
        axes[1, 1].grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        plt.savefig(save_path, bbox_inches='tight')
        print(f"Saved product analysis plot to {save_path}")
        plt.close()

    def plot_provider_analysis(self, save_path: str = "provider_analysis.png", top_n: int = 15):
        """Plot top flexibility service providers"""
        fig, axes = plt.subplots(2, 2, figsize=(18, 12))

        provider_data = self.df.groupby('company_name').agg({
            'fu_id': 'count',
            'utilisation_mwh_req': 'sum',
            'total_cost': 'sum',
            'zone': 'nunique'
        }).rename(columns={'fu_id': 'count', 'zone': 'num_zones'})

        # Top providers by dispatch count
        top_providers = provider_data.nlargest(top_n, 'count')
        axes[0, 0].barh(range(top_n), top_providers['count'], color='skyblue')
        axes[0, 0].set_yticks(range(top_n))
        axes[0, 0].set_yticklabels(top_providers.index, fontsize=9)
        axes[0, 0].set_xlabel('Number of Dispatches', fontsize=11, fontweight='bold')
        axes[0, 0].set_title(f'Top {top_n} Providers by Dispatch Count', fontsize=12, fontweight='bold')
        axes[0, 0].invert_yaxis()
        axes[0, 0].grid(True, alpha=0.3, axis='x')

        # Top providers by energy
        top_energy = provider_data.nlargest(top_n, 'utilisation_mwh_req')
        axes[0, 1].barh(range(top_n), top_energy['utilisation_mwh_req'], color='green')
        axes[0, 1].set_yticks(range(top_n))
        axes[0, 1].set_yticklabels(top_energy.index, fontsize=9)
        axes[0, 1].set_xlabel('Energy Dispatched (MWh)', fontsize=11, fontweight='bold')
        axes[0, 1].set_title(f'Top {top_n} Providers by Energy Delivered', fontsize=12, fontweight='bold')
        axes[0, 1].invert_yaxis()
        axes[0, 1].grid(True, alpha=0.3, axis='x')

        # Top providers by cost
        top_cost = provider_data.nlargest(top_n, 'total_cost')
        axes[1, 0].barh(range(top_n), top_cost['total_cost'], color='coral')
        axes[1, 0].set_yticks(range(top_n))
        axes[1, 0].set_yticklabels(top_cost.index, fontsize=9)
        axes[1, 0].set_xlabel('Total Revenue (£)', fontsize=11, fontweight='bold')
        axes[1, 0].set_title(f'Top {top_n} Providers by Revenue', fontsize=12, fontweight='bold')
        axes[1, 0].invert_yaxis()
        axes[1, 0].grid(True, alpha=0.3, axis='x')

        # Provider geographic reach
        top_zones = provider_data.nlargest(top_n, 'num_zones')
        axes[1, 1].barh(range(top_n), top_zones['num_zones'], color='mediumpurple')
        axes[1, 1].set_yticks(range(top_n))
        axes[1, 1].set_yticklabels(top_zones.index, fontsize=9)
        axes[1, 1].set_xlabel('Number of Zones Served', fontsize=11, fontweight='bold')
        axes[1, 1].set_title(f'Top {top_n} Providers by Geographic Reach', fontsize=12, fontweight='bold')
        axes[1, 1].invert_yaxis()
        axes[1, 1].grid(True, alpha=0.3, axis='x')

        plt.tight_layout()
        plt.savefig(save_path, bbox_inches='tight')
        print(f"Saved provider analysis plot to {save_path}")
        plt.close()

    def plot_price_distribution(self, save_path: str = "price_distribution.png"):
        """Plot price distribution and analysis"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))

        price_data = self.df[self.df['utilisation_price'] > 0]['utilisation_price']

        # Price distribution histogram
        axes[0, 0].hist(price_data, bins=50, color='steelblue', edgecolor='black', alpha=0.7)
        axes[0, 0].axvline(price_data.mean(), color='red', linestyle='--',
                          linewidth=2, label=f'Mean: £{price_data.mean():.2f}')
        axes[0, 0].axvline(price_data.median(), color='green', linestyle='--',
                          linewidth=2, label=f'Median: £{price_data.median():.2f}')
        axes[0, 0].set_xlabel('Price (£/MWh)', fontsize=11, fontweight='bold')
        axes[0, 0].set_ylabel('Frequency', fontsize=11, fontweight='bold')
        axes[0, 0].set_title('Utilisation Price Distribution', fontsize=12, fontweight='bold')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3, axis='y')

        # Box plot by technology
        tech_price = self.df[self.df['utilisation_price'] > 0].copy()
        tech_price.boxplot(column='utilisation_price', by='technology', ax=axes[0, 1])
        axes[0, 1].set_xlabel('Technology', fontsize=11, fontweight='bold')
        axes[0, 1].set_ylabel('Price (£/MWh)', fontsize=11, fontweight='bold')
        axes[0, 1].set_title('Price Distribution by Technology', fontsize=12, fontweight='bold')
        axes[0, 1].tick_params(axis='x', rotation=45)
        plt.sca(axes[0, 1])
        plt.xticks(rotation=45, ha='right')

        # Box plot by product
        product_price = self.df[self.df['utilisation_price'] > 0].copy()
        product_price.boxplot(column='utilisation_price', by='product', ax=axes[1, 0])
        axes[1, 0].set_xlabel('Product', fontsize=11, fontweight='bold')
        axes[1, 0].set_ylabel('Price (£/MWh)', fontsize=11, fontweight='bold')
        axes[1, 0].set_title('Price Distribution by Product', fontsize=12, fontweight='bold')
        axes[1, 0].tick_params(axis='x', rotation=45)

        # Price over time
        monthly_price = self.df[self.df['utilisation_price'] > 0].groupby('year_month')['utilisation_price'].mean()
        monthly_price.index = monthly_price.index.to_timestamp()
        axes[1, 1].plot(monthly_price.index, monthly_price, marker='o', linewidth=2, color='darkblue')
        axes[1, 1].fill_between(monthly_price.index, monthly_price, alpha=0.3, color='darkblue')
        axes[1, 1].set_xlabel('Month', fontsize=11, fontweight='bold')
        axes[1, 1].set_ylabel('Average Price (£/MWh)', fontsize=11, fontweight='bold')
        axes[1, 1].set_title('Average Utilisation Price Over Time', fontsize=12, fontweight='bold')
        axes[1, 1].grid(True, alpha=0.3)

        # Remove default titles added by boxplot
        for ax in [axes[0, 1], axes[1, 0]]:
            ax.get_figure().suptitle('')

        plt.tight_layout()
        plt.savefig(save_path, bbox_inches='tight')
        print(f"Saved price distribution plot to {save_path}")
        plt.close()

    def plot_cumulative_growth(self, save_path: str = "cumulative_growth.png"):
        """Plot cumulative growth metrics"""
        fig, axes = plt.subplots(2, 1, figsize=(16, 10))

        # Prepare daily data
        daily = self.df.groupby('date').agg({
            'fu_id': 'count',
            'utilisation_mwh_req': 'sum',
            'total_cost': 'sum'
        })
        daily['cumulative_dispatches'] = daily['fu_id'].cumsum()
        daily['cumulative_energy'] = daily['utilisation_mwh_req'].cumsum()
        daily['cumulative_cost'] = daily['total_cost'].cumsum()

        # Cumulative dispatches and energy
        ax1 = axes[0]
        ax1_twin = ax1.twinx()

        ax1.plot(daily.index, daily['cumulative_dispatches'],
                color='blue', linewidth=2, label='Cumulative Dispatches')
        ax1.set_ylabel('Cumulative Dispatches', fontsize=12, fontweight='bold', color='blue')
        ax1.tick_params(axis='y', labelcolor='blue')

        ax1_twin.plot(daily.index, daily['cumulative_energy'],
                     color='green', linewidth=2, label='Cumulative Energy (MWh)')
        ax1_twin.set_ylabel('Cumulative Energy (MWh)', fontsize=12, fontweight='bold', color='green')
        ax1_twin.tick_params(axis='y', labelcolor='green')

        ax1.set_title('Cumulative Flexibility Market Growth', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)

        # Daily dispatches with rolling average
        ax2 = axes[1]
        ax2.bar(daily.index, daily['fu_id'], alpha=0.5, color='skyblue', label='Daily Dispatches')

        rolling_avg = daily['fu_id'].rolling(window=7).mean()
        ax2.plot(daily.index, rolling_avg, color='red', linewidth=2,
                label='7-day Moving Average')

        ax2.set_ylabel('Number of Dispatches', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Date', fontsize=12, fontweight='bold')
        ax2.set_title('Daily Dispatch Activity', fontsize=14, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        plt.savefig(save_path, bbox_inches='tight')
        print(f"Saved cumulative growth plot to {save_path}")
        plt.close()

    def generate_all_plots(self):
        """Generate all visualization plots"""
        print("\n" + "="*80)
        print("GENERATING FLEXIBILITY MARKET VISUALIZATIONS")
        print("="*80 + "\n")

        self.plot_temporal_trends()
        self.plot_daily_weekly_patterns()
        self.plot_zone_analysis()
        self.plot_technology_analysis()
        self.plot_product_analysis()
        self.plot_provider_analysis()
        self.plot_price_distribution()
        self.plot_cumulative_growth()

        print("\n" + "="*80)
        print("ALL VISUALIZATIONS GENERATED SUCCESSFULLY")
        print("="*80)


if __name__ == "__main__":
    # Create visualizer instance
    viz = FlexibilityMarketVisualizer("ukpn_flexibility_dispatches.csv")

    # Generate all plots
    viz.generate_all_plots()

    print("\n\nAll visualization files saved in the current directory:")
    print("- temporal_trends.png")
    print("- daily_weekly_patterns.png")
    print("- zone_analysis.png")
    print("- technology_analysis.png")
    print("- product_analysis.png")
    print("- provider_analysis.png")
    print("- price_distribution.png")
    print("- cumulative_growth.png")
