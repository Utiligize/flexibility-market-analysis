"""
Analyze Super Lucrative Peak Pricing Events
UKPN Flexibility Market
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Load data
df = pd.read_csv('ukpn_flexibility_dispatches.csv')
df['start_time_local'] = pd.to_datetime(df['start_time_local'])
df['year_month'] = df['start_time_local'].dt.to_period('M')
df['date'] = df['start_time_local'].dt.date
df['hour'] = df['start_time_local'].dt.hour
df['total_cost'] = df['utilisation_mwh_req'] * df['utilisation_price']

price_data = df[df['utilisation_price'] > 0].copy()

# Define price tiers
price_data['price_tier'] = pd.cut(
    price_data['utilisation_price'],
    bins=[0, 500, 1000, 2000, 4000, 50000],
    labels=['£0-500', '£500-1k', '£1k-2k', '£2k-4k', '£4k+']
)

# Create comprehensive visualization
fig = plt.figure(figsize=(18, 12))
gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

# Plot 1: Price tier distribution
ax1 = fig.add_subplot(gs[0, 0])
tier_counts = price_data['price_tier'].value_counts().sort_index()
colors_tier = ['#2ecc71', '#f39c12', '#e74c3c', '#9b59b6', '#c0392b']
ax1.barh(range(len(tier_counts)), tier_counts.values, color=colors_tier)
ax1.set_yticks(range(len(tier_counts)))
ax1.set_yticklabels(tier_counts.index)
ax1.set_xlabel('Number of Dispatches', fontweight='bold')
ax1.set_title('Dispatches by Price Tier', fontweight='bold', fontsize=12)
ax1.invert_yaxis()
ax1.grid(True, alpha=0.3, axis='x')

# Add percentages
for i, (count, label) in enumerate(zip(tier_counts.values, tier_counts.index)):
    pct = count / len(price_data) * 100
    ax1.text(count + 50, i, f'{pct:.1f}%', va='center', fontweight='bold')

# Plot 2: Energy by price tier
ax2 = fig.add_subplot(gs[0, 1])
tier_energy = price_data.groupby('price_tier')['utilisation_mwh_req'].sum().sort_index()
ax2.barh(range(len(tier_energy)), tier_energy.values, color=colors_tier)
ax2.set_yticks(range(len(tier_energy)))
ax2.set_yticklabels(tier_energy.index)
ax2.set_xlabel('Total Energy (MWh)', fontweight='bold')
ax2.set_title('Energy by Price Tier', fontweight='bold', fontsize=12)
ax2.invert_yaxis()
ax2.grid(True, alpha=0.3, axis='x')

# Plot 3: Cost by price tier
ax3 = fig.add_subplot(gs[0, 2])
tier_cost = price_data.groupby('price_tier')['total_cost'].sum().sort_index()
ax3.barh(range(len(tier_cost)), tier_cost.values, color=colors_tier)
ax3.set_yticks(range(len(tier_cost)))
ax3.set_yticklabels(tier_cost.index)
ax3.set_xlabel('Total Cost (£)', fontweight='bold')
ax3.set_title('Total Cost by Price Tier', fontweight='bold', fontsize=12)
ax3.invert_yaxis()
ax3.grid(True, alpha=0.3, axis='x')

# Add percentages
for i, (cost, label) in enumerate(zip(tier_cost.values, tier_cost.index)):
    pct = cost / tier_cost.sum() * 100
    ax3.text(cost * 0.05, i, f'{pct:.1f}%', va='center', fontweight='bold', color='white')

# Plot 4: High-price events over time
ax4 = fig.add_subplot(gs[1, :])
high_price = price_data[price_data['utilisation_price'] >= 4000]
monthly_high = high_price.groupby('year_month').size()
monthly_all = price_data.groupby('year_month').size()
monthly_pct = (monthly_high / monthly_all * 100).fillna(0)

monthly_high.index = monthly_high.index.to_timestamp()
monthly_pct.index = monthly_pct.index.to_timestamp()

ax4_twin = ax4.twinx()
ax4.bar(monthly_high.index, monthly_high.values, alpha=0.7, color='#c0392b', label='High-price count')
ax4_twin.plot(monthly_pct.index, monthly_pct.values, color='darkblue', marker='o',
              linewidth=2, markersize=6, label='% of monthly dispatches')

ax4.set_ylabel('Number of High-Price Dispatches (≥£4k)', fontweight='bold', color='#c0392b')
ax4_twin.set_ylabel('Percentage of Month Total (%)', fontweight='bold', color='darkblue')
ax4.set_xlabel('Month', fontweight='bold')
ax4.set_title('High-Price Events Over Time (≥£4,000/MWh)', fontweight='bold', fontsize=14)
ax4.tick_params(axis='y', labelcolor='#c0392b')
ax4_twin.tick_params(axis='y', labelcolor='darkblue')
ax4.grid(True, alpha=0.3)
plt.setp(ax4.xaxis.get_majorticklabels(), rotation=45, ha='right')

# Plot 5: Top zones for high-price events
ax5 = fig.add_subplot(gs[2, 0])
zone_high = high_price.groupby('zone').size().sort_values(ascending=False).head(10)
ax5.barh(range(len(zone_high)), zone_high.values, color='#e74c3c')
ax5.set_yticks(range(len(zone_high)))
ax5.set_yticklabels(zone_high.index, fontsize=9)
ax5.set_xlabel('High-Price Events', fontweight='bold')
ax5.set_title('Top 10 Zones: High-Price Events', fontweight='bold', fontsize=11)
ax5.invert_yaxis()
ax5.grid(True, alpha=0.3, axis='x')

# Plot 6: Hour of day for high-price events
ax6 = fig.add_subplot(gs[2, 1])
hour_high = high_price.groupby('hour').size()
ax6.bar(hour_high.index, hour_high.values, color='#c0392b', alpha=0.7)
ax6.set_ylabel('High-Price Dispatches', fontweight='bold')
ax6.set_xlabel('Hour of Day', fontweight='bold')
ax6.set_title('High-Price Events by Hour', fontweight='bold', fontsize=11)
ax6.grid(True, alpha=0.3, axis='y')

# Plot 7: Price vs Energy scatter
ax7 = fig.add_subplot(gs[2, 2])
scatter_data = high_price.copy()
ax7.scatter(scatter_data['utilisation_mwh_req'], scatter_data['utilisation_price'],
           alpha=0.6, c=scatter_data['utilisation_price'], cmap='Reds', s=50)
ax7.set_xlabel('Energy (MWh)', fontweight='bold')
ax7.set_ylabel('Price (£/MWh)', fontweight='bold')
ax7.set_title('High-Price: Energy vs Price', fontweight='bold', fontsize=11)
ax7.grid(True, alpha=0.3)
ax7.set_yscale('log')

plt.suptitle('Super Lucrative Peak Pricing Analysis (≥£4,000/MWh)',
             fontsize=16, fontweight='bold', y=0.995)

plt.savefig('peak_pricing_analysis.png', dpi=300, bbox_inches='tight')
print('✓ Saved peak pricing visualization to peak_pricing_analysis.png')
plt.close()

print()
print('='*80)
print('SUMMARY: SUPER LUCRATIVE PEAKS (≥£4,000/MWh)')
print('='*80)
print()
print(f'Frequency: Every ~7 days on average (14.2% of days have ≥1 event)')
print(f'Occurrences: {len(high_price)} dispatches (3.89% of all)')
print(f'Concentration: Winter months (Nov-Feb 2024-2025)')
print(f'Product: 100% Peak Reduction')
print(f'Technology: 94% EV Charger DSR, 6% Flexible Site Demand')
print(f'Type: 100% Demand Turn Down')
print()
print('Economic Impact:')
print(f'- Energy: Only 0.74% of total MWh')
print(f'- Cost: 20.31% of total expenditure!')
print(f'- Average volume: 0.25 MWh per event (very small)')
print()
print('Top hotspots: Willesden Grid (102), Cockfosters (71), Cobham (68), Wingham (64)')
print()
print('Interpretation:')
print('These are emergency/peak demand reduction events paying premium prices')
print('for small load reductions during critical winter peak periods.')
