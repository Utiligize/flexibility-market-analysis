"""
Analyze UK Power Networks Flexibility Market Activations
Author: Data Analysis Script
Date: 2025-10-21

This script performs detailed analysis of flexibility market activations
at the DNO level, including temporal patterns, market dynamics, and cost analysis.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Set plotting style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10

class FlexibilityMarketAnalyzer:
    """Analyzer for UKPN flexibility market data"""

    def __init__(self, csv_file: str = "ukpn_flexibility_dispatches.csv"):
        """
        Initialize analyzer with data from CSV file.

        Args:
            csv_file: Path to CSV file containing dispatch data
        """
        print(f"Loading data from {csv_file}...")
        self.df = pd.read_csv(csv_file)

        # Convert datetime columns
        self.df['start_time_local'] = pd.to_datetime(self.df['start_time_local'])
        self.df['end_time_local'] = pd.to_datetime(self.df['end_time_local'])

        # Extract time features
        self.df['year'] = self.df['start_time_local'].dt.year
        self.df['month'] = self.df['start_time_local'].dt.month
        self.df['week'] = self.df['start_time_local'].dt.isocalendar().week
        self.df['day_of_week'] = self.df['start_time_local'].dt.dayofweek
        self.df['hour'] = self.df['start_time_local'].dt.hour
        self.df['date'] = self.df['start_time_local'].dt.date

        # Calculate costs
        self.df['availability_cost'] = self.df['availability_mwh_req'] * self.df['availability_price']
        self.df['utilisation_cost'] = self.df['utilisation_mwh_req'] * self.df['utilisation_price']
        self.df['total_cost'] = self.df['availability_cost'] + self.df['utilisation_cost']

        print(f"Loaded {len(self.df):,} dispatch records")
        print(f"Date range: {self.df['start_time_local'].min()} to {self.df['start_time_local'].max()}")

    def analyze_temporal_patterns(self):
        """Analyze temporal patterns in flexibility dispatches"""
        print("\n" + "="*80)
        print("TEMPORAL ANALYSIS")
        print("="*80)

        # Monthly trends
        monthly = self.df.groupby(['year', 'month']).agg({
            'fu_id': 'count',
            'utilisation_mwh_req': 'sum',
            'total_cost': 'sum'
        }).rename(columns={'fu_id': 'dispatch_count'})

        print("\nMONTHLY TRENDS:")
        print(monthly)

        # Day of week analysis
        dow_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dow_analysis = self.df.groupby('day_of_week').agg({
            'fu_id': 'count',
            'utilisation_mwh_req': 'sum',
            'total_cost': 'sum'
        }).rename(columns={'fu_id': 'dispatch_count'})
        dow_analysis.index = [dow_names[i] for i in dow_analysis.index]

        print("\nDISPATCHES BY DAY OF WEEK:")
        print(dow_analysis)

        # Hourly patterns
        hourly = self.df.groupby('hour').agg({
            'fu_id': 'count',
            'utilisation_mwh_req': 'sum',
            'total_cost': 'sum'
        }).rename(columns={'fu_id': 'dispatch_count'})

        print("\nHOURLY DISPATCH PATTERNS (Top 10 hours):")
        print(hourly.nlargest(10, 'dispatch_count'))

        return monthly, dow_analysis, hourly

    def analyze_by_zone(self):
        """Analyze dispatches by flexibility zone"""
        print("\n" + "="*80)
        print("ZONE-LEVEL ANALYSIS")
        print("="*80)

        zone_analysis = self.df.groupby('zone').agg({
            'fu_id': 'count',
            'utilisation_mwh_req': 'sum',
            'utilisation_mw_req': 'mean',
            'total_cost': 'sum',
            'utilisation_price': 'mean',
            'hours_requested': 'sum',
            'company_name': 'nunique'
        }).rename(columns={
            'fu_id': 'dispatch_count',
            'utilisation_mw_req': 'avg_capacity_mw',
            'utilisation_price': 'avg_price_per_mwh',
            'company_name': 'num_providers'
        }).round(2)

        zone_analysis = zone_analysis.sort_values('dispatch_count', ascending=False)

        print("\nTOP 20 ZONES BY DISPATCH COUNT:")
        print(zone_analysis.head(20))

        print("\nTOP 20 ZONES BY TOTAL ENERGY DISPATCHED (MWh):")
        print(zone_analysis.nlargest(20, 'utilisation_mwh_req')[['dispatch_count', 'utilisation_mwh_req', 'total_cost']])

        print("\nTOP 20 ZONES BY TOTAL COST:")
        print(zone_analysis.nlargest(20, 'total_cost')[['dispatch_count', 'utilisation_mwh_req', 'total_cost']])

        return zone_analysis

    def analyze_by_technology(self):
        """Analyze dispatches by technology type"""
        print("\n" + "="*80)
        print("TECHNOLOGY ANALYSIS")
        print("="*80)

        tech_analysis = self.df.groupby('technology').agg({
            'fu_id': 'count',
            'utilisation_mwh_req': 'sum',
            'utilisation_mw_req': 'mean',
            'total_cost': 'sum',
            'utilisation_price': 'mean',
            'hours_requested': 'mean',
            'company_name': 'nunique'
        }).rename(columns={
            'fu_id': 'dispatch_count',
            'utilisation_mw_req': 'avg_capacity_mw',
            'utilisation_price': 'avg_price_per_mwh',
            'hours_requested': 'avg_duration_hours',
            'company_name': 'num_providers'
        }).round(2)

        tech_analysis = tech_analysis.sort_values('dispatch_count', ascending=False)

        print("\nDISPATCHES BY TECHNOLOGY:")
        print(tech_analysis)

        return tech_analysis

    def analyze_by_product(self):
        """Analyze dispatches by flexibility product"""
        print("\n" + "="*80)
        print("PRODUCT ANALYSIS")
        print("="*80)

        product_analysis = self.df.groupby('product').agg({
            'fu_id': 'count',
            'utilisation_mwh_req': 'sum',
            'utilisation_mw_req': 'mean',
            'total_cost': 'sum',
            'utilisation_price': 'mean',
            'hours_requested': 'mean',
            'zone': 'nunique'
        }).rename(columns={
            'fu_id': 'dispatch_count',
            'utilisation_mw_req': 'avg_capacity_mw',
            'utilisation_price': 'avg_price_per_mwh',
            'hours_requested': 'avg_duration_hours',
            'zone': 'num_zones'
        }).round(2)

        product_analysis = product_analysis.sort_values('dispatch_count', ascending=False)

        print("\nDISPATCHES BY PRODUCT TYPE:")
        print(product_analysis)

        return product_analysis

    def analyze_market_providers(self):
        """Analyze flexibility service providers"""
        print("\n" + "="*80)
        print("MARKET PROVIDERS ANALYSIS")
        print("="*80)

        provider_analysis = self.df.groupby('company_name').agg({
            'fu_id': 'count',
            'utilisation_mwh_req': 'sum',
            'utilisation_mw_req': 'mean',
            'total_cost': 'sum',
            'utilisation_price': 'mean',
            'zone': 'nunique',
            'technology': lambda x: ', '.join(x.unique()[:3])
        }).rename(columns={
            'fu_id': 'dispatch_count',
            'utilisation_mw_req': 'avg_capacity_mw',
            'utilisation_price': 'avg_price_per_mwh',
            'zone': 'num_zones',
            'technology': 'technologies'
        }).round(2)

        provider_analysis = provider_analysis.sort_values('dispatch_count', ascending=False)

        print("\nTOP 20 PROVIDERS BY DISPATCH COUNT:")
        print(provider_analysis.head(20))

        print("\nTOP 20 PROVIDERS BY ENERGY DELIVERED:")
        print(provider_analysis.nlargest(20, 'utilisation_mwh_req')[['dispatch_count', 'utilisation_mwh_req', 'total_cost']])

        return provider_analysis

    def price_analysis(self):
        """Analyze pricing patterns"""
        print("\n" + "="*80)
        print("PRICE ANALYSIS")
        print("="*80)

        # Overall statistics
        price_data = self.df[self.df['utilisation_price'] > 0]['utilisation_price']

        print("\nUTILISATION PRICE STATISTICS (£/MWh):")
        print(f"Mean: £{price_data.mean():.2f}")
        print(f"Median: £{price_data.median():.2f}")
        print(f"Min: £{price_data.min():.2f}")
        print(f"Max: £{price_data.max():.2f}")
        print(f"Std Dev: £{price_data.std():.2f}")

        # Price by technology
        print("\nAVERAGE UTILISATION PRICE BY TECHNOLOGY:")
        tech_prices = self.df[self.df['utilisation_price'] > 0].groupby('technology')['utilisation_price'].agg(['mean', 'median', 'count']).round(2)
        tech_prices = tech_prices.sort_values('mean', ascending=False)
        print(tech_prices)

        # Price by product
        print("\nAVERAGE UTILISATION PRICE BY PRODUCT:")
        product_prices = self.df[self.df['utilisation_price'] > 0].groupby('product')['utilisation_price'].agg(['mean', 'median', 'count']).round(2)
        print(product_prices)

        # Price by dispatch type
        print("\nAVERAGE UTILISATION PRICE BY DISPATCH TYPE:")
        dispatch_prices = self.df[self.df['utilisation_price'] > 0].groupby('dispatch_type')['utilisation_price'].agg(['mean', 'median', 'count']).round(2)
        print(dispatch_prices)

        return price_data, tech_prices, product_prices

    def growth_analysis(self):
        """Analyze market growth over time"""
        print("\n" + "="*80)
        print("MARKET GROWTH ANALYSIS")
        print("="*80)

        # Daily aggregation
        daily = self.df.groupby('date').agg({
            'fu_id': 'count',
            'utilisation_mwh_req': 'sum',
            'total_cost': 'sum'
        }).rename(columns={'fu_id': 'dispatch_count'})

        # Calculate cumulative metrics
        daily['cumulative_dispatches'] = daily['dispatch_count'].cumsum()
        daily['cumulative_energy_mwh'] = daily['utilisation_mwh_req'].cumsum()
        daily['cumulative_cost'] = daily['total_cost'].cumsum()

        # Calculate rolling averages
        daily['dispatches_7day_avg'] = daily['dispatch_count'].rolling(window=7).mean()
        daily['energy_7day_avg'] = daily['utilisation_mwh_req'].rolling(window=7).mean()

        print("\nMARKET GROWTH SUMMARY:")
        print(f"Total dispatches: {daily['cumulative_dispatches'].iloc[-1]:,.0f}")
        print(f"Total energy dispatched: {daily['cumulative_energy_mwh'].iloc[-1]:,.2f} MWh")
        print(f"Total cost: £{daily['cumulative_cost'].iloc[-1]:,.2f}")

        print(f"\nAverage daily dispatches (last 30 days): {daily['dispatch_count'].tail(30).mean():.1f}")
        print(f"Average daily energy (last 30 days): {daily['utilisation_mwh_req'].tail(30).mean():.2f} MWh")

        return daily

    def generate_summary_report(self):
        """Generate a comprehensive summary report"""
        print("\n" + "="*80)
        print("COMPREHENSIVE SUMMARY REPORT")
        print("UK Power Networks Flexibility Market Activations")
        print("="*80)

        print(f"\nReport Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Data Period: {self.df['start_time_local'].min()} to {self.df['start_time_local'].max()}")

        print("\n" + "-"*80)
        print("OVERALL STATISTICS")
        print("-"*80)
        print(f"Total Dispatches: {len(self.df):,}")
        print(f"Total Energy Dispatched: {self.df['utilisation_mwh_req'].sum():,.2f} MWh")
        print(f"Total Cost: £{self.df['total_cost'].sum():,.2f}")
        print(f"Average Cost per MWh: £{self.df['total_cost'].sum() / self.df['utilisation_mwh_req'].sum():.2f}")

        print(f"\nNumber of Flexibility Zones: {self.df['zone'].nunique()}")
        print(f"Number of Service Providers: {self.df['company_name'].nunique()}")
        print(f"Number of Flexible Units: {self.df['fu_id'].nunique()}")
        print(f"Number of Technology Types: {self.df['technology'].nunique()}")

        print("\n" + "-"*80)
        print("DISPATCH CHARACTERISTICS")
        print("-"*80)
        print(f"Average Dispatch Duration: {self.df['hours_requested'].mean():.2f} hours")
        print(f"Average Utilisation: {self.df['utilisation_mw_req'].mean():.2f} MW")
        print(f"Average Energy per Dispatch: {self.df['utilisation_mwh_req'].mean():.2f} MWh")
        print(f"Average Price: £{self.df[self.df['utilisation_price'] > 0]['utilisation_price'].mean():.2f}/MWh")

        # Run all analyses
        monthly, dow, hourly = self.analyze_temporal_patterns()
        zone_analysis = self.analyze_by_zone()
        tech_analysis = self.analyze_by_technology()
        product_analysis = self.analyze_by_product()
        provider_analysis = self.analyze_market_providers()
        price_data, tech_prices, product_prices = self.price_analysis()
        daily = self.growth_analysis()

        print("\n" + "="*80)
        print("ANALYSIS COMPLETE")
        print("="*80)

        return {
            'monthly': monthly,
            'dow': dow,
            'hourly': hourly,
            'zone': zone_analysis,
            'technology': tech_analysis,
            'product': product_analysis,
            'provider': provider_analysis,
            'daily': daily
        }


if __name__ == "__main__":
    # Create analyzer instance
    analyzer = FlexibilityMarketAnalyzer("ukpn_flexibility_dispatches.csv")

    # Run comprehensive analysis
    results = analyzer.generate_summary_report()

    print("\n\nAnalysis results saved in 'results' dictionary")
    print("Run visualize_flexibility_market.py to generate charts and graphs")
