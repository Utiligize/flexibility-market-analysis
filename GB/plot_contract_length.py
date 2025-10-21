"""
Plot Average Contract Length by Service Type
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
df = pd.read_csv('ukpn_flexibility_dispatches.csv')
df['start_time_local'] = pd.to_datetime(df['start_time_local'])

# Calculate dispatch window for each FU
fu_activity = df.groupby(['fu_id', 'product'])['start_time_local'].agg(['min', 'max', 'count'])
fu_activity['days_window'] = (fu_activity['max'] - fu_activity['min']).dt.days
fu_activity['months_window'] = fu_activity['days_window'] / 30

# Average by product
product_windows = fu_activity.reset_index().groupby('product')['months_window'].agg(['mean', 'median', 'max', 'count'])
product_windows = product_windows.sort_values('mean', ascending=True)

# Estimate actual contract length (dispatch window + buffer)
# Seasonal/availability contracts are typically full calendar periods
contract_estimates = {
    'Day Ahead': 0.5,  # Daily/weekly, no long-term
    'Dynamic': 9,  # Flexible, ~6-12 months
    'Secure': 12,  # Annual with availability
    'Peak Reduction': 9,  # Seasonal, 6-12 months (summer/winter)
    'Long-Term Utilisation': 12,  # Annual
    'Scheduled Availability': 9  # Seasonal, 6-12 months
}

product_windows['estimated_contract_months'] = product_windows.index.map(contract_estimates)

# Create visualization
fig, axes = plt.subplots(1, 2, figsize=(14, 8))

# Plot 1: Dispatch Window vs Estimated Contract Length
ax1 = axes[0]
x = range(len(product_windows))
width = 0.35

bars1 = ax1.barh([i - width/2 for i in x], product_windows['mean'], width,
                 label='Avg Dispatch Window', color='skyblue', edgecolor='black')
bars2 = ax1.barh([i + width/2 for i in x], product_windows['estimated_contract_months'], width,
                 label='Est. Contract Length', color='darkblue', edgecolor='black')

ax1.set_yticks(x)
ax1.set_yticklabels(product_windows.index)
ax1.set_xlabel('Duration (Months)', fontweight='bold', fontsize=12)
ax1.set_title('Dispatch Window vs Estimated Contract Length\nby Product Type',
             fontweight='bold', fontsize=13)
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3, axis='x')

# Add values on bars
for i, (dispatch_val, contract_val) in enumerate(zip(product_windows['mean'], product_windows['estimated_contract_months'])):
    ax1.text(dispatch_val + 0.3, i - width/2, f'{dispatch_val:.1f}mo',
            va='center', fontsize=9, fontweight='bold')
    ax1.text(contract_val + 0.3, i + width/2, f'{contract_val:.0f}mo',
            va='center', fontsize=9, fontweight='bold')

# Plot 2: Number of FUs by product
ax2 = axes[1]
colors = sns.color_palette("husl", len(product_windows))
ax2.barh(x, product_windows['count'], color=colors, edgecolor='black')
ax2.set_yticks(x)
ax2.set_yticklabels(product_windows.index)
ax2.set_xlabel('Number of Flexible Units', fontweight='bold', fontsize=12)
ax2.set_title('Flexible Units by Product Type\n(Sample from 10,000 dispatches)',
             fontweight='bold', fontsize=13)
ax2.grid(True, alpha=0.3, axis='x')

# Add values
for i, val in enumerate(product_windows['count']):
    ax2.text(val + 2, i, f'{int(val)}',
            va='center', fontsize=10, fontweight='bold')

plt.suptitle('UKPN Flexibility Market Contract Duration Analysis',
            fontsize=14, fontweight='bold', y=0.98)

# Add watermark
fig.text(0.98, 0.02, 'Utiligize', fontsize=12, fontweight='bold',
         color='#6B46C1', alpha=0.7, ha='right', va='bottom',
         bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='#6B46C1',
                  linewidth=2, alpha=0.8))

plt.tight_layout(rect=[0, 0.05, 1, 0.96])
plt.savefig('contract_length_by_product.png', dpi=300, bbox_inches='tight')
print('✓ Saved contract_length_by_product.png')
plt.close()

# Print summary
print()
print('='*80)
print('CONTRACT LENGTH SUMMARY')
print('='*80)
print()
print('By Product Type:')
for product, row in product_windows.iterrows():
    mean_val = row['mean']
    median_val = row['median']
    contract_val = row['estimated_contract_months']
    count_val = row['count']
    print(f'{product}:')
    print(f'  Dispatch window: {mean_val:.1f} months (avg), {median_val:.1f} months (median)')
    print(f'  Estimated contract: {contract_val:.0f} months')
    print(f'  Flexible Units: {int(count_val)}')
    print()

# Calculate weighted average
total_fus = product_windows['count'].sum()
weighted_contract = (product_windows['estimated_contract_months'] * product_windows['count']).sum() / total_fus

print(f'WEIGHTED AVERAGE CONTRACT LENGTH: {weighted_contract:.1f} months')
print(f'(Based on {int(total_fus)} flexible units across all products)')
