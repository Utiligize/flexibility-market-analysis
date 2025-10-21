# UK Power Networks Flexibility Market Analysis

Comprehensive analysis of flexibility market activations at the DNO (Distribution Network Operator) level for UK Power Networks.

## Overview

This project analyzes UKPN's flexibility dispatch data, providing insights into:
- **Temporal patterns** - When flexibility is dispatched (hourly, daily, monthly trends)
- **Geographic distribution** - Which zones require the most flexibility services
- **Technology analysis** - What types of assets provide flexibility (batteries, EVs, demand response, etc.)
- **Market dynamics** - Provider market share, pricing trends, product performance
- **Growth analysis** - How the flexibility market is evolving over time

## Data Source

Data is sourced from [UK Power Networks Open Data Portal](https://ukpowernetworks.opendatasoft.com/) via their public API.

**Dataset**: Flexibility Dispatches
**Coverage**: April 2023 onwards (23,607+ records as of Oct 2025)
**Update Frequency**: Monthly
**License**: CC BY 4.0

### Key Data Fields

- **Zone**: Flexibility zone where dispatch occurred
- **Product**: Flexibility product type (Secure, Dynamic, Day-Ahead, Long-Term Utilisation)
- **Technology**: Asset type (Battery, Flexible Site Demand, Solar, Wind, etc.)
- **Dispatch Type**: Direction of flexibility (demand_turn_up, demand_turn_down, generation_turn_up, generation_turn_down)
- **Capacity & Energy**: MW and MWh requested
- **Pricing**: Availability and utilisation prices
- **Timing**: Start/end times, duration
- **Provider**: Company operating the flexible unit

## Scripts

### 1. `fetch_flexibility_data.py`

Downloads all flexibility dispatch records from the UKPN API and saves to CSV.

**Usage:**
```bash
python fetch_flexibility_data.py
```

**Output:**
- `ukpn_flexibility_dispatches.csv` - All dispatch records
- Console summary of key statistics

### 2. `analyze_flexibility_market.py`

Performs comprehensive statistical analysis of the flexibility market.

**Usage:**
```bash
python analyze_flexibility_market.py
```

**Analyses Include:**
- Temporal patterns (monthly, weekly, hourly)
- Zone-level statistics
- Technology breakdown
- Product analysis
- Provider market share
- Price analysis
- Market growth metrics

### 3. `visualize_flexibility_market.py`

Generates comprehensive visualizations of the flexibility market.

**Usage:**
```bash
python visualize_flexibility_market.py
```

**Outputs:**
- `temporal_trends.png` - Monthly dispatch volumes, energy, and costs
- `daily_weekly_patterns.png` - Day of week and hour of day patterns
- `zone_analysis.png` - Top zones by various metrics
- `technology_analysis.png` - Technology breakdown and comparison
- `product_analysis.png` - Product type comparison
- `provider_analysis.png` - Top service providers
- `price_distribution.png` - Price distribution and trends
- `cumulative_growth.png` - Market growth over time

### 4. `run_analysis.py`

Convenience script to run the entire analysis pipeline.

**Usage:**
```bash
python run_analysis.py
```

## Installation

### Requirements

```bash
pip install pandas numpy matplotlib seaborn requests
```

Or use the requirements file:

```bash
pip install -r requirements.txt
```

### Python Version

Python 3.8 or higher recommended.

## Quick Start

1. **Set your API key:**
   ```bash
   export UKPN_API_KEY=your_api_key_here
   ```

   To get an API key, register at [UKPN Open Data Portal](https://ukpowernetworks.opendatasoft.com/)

2. **Fetch the data:**
   ```bash
   python fetch_flexibility_data.py
   ```

3. **Run analysis:**
   ```bash
   python analyze_flexibility_market.py
   ```

4. **Generate visualizations:**
   ```bash
   python visualize_flexibility_market.py
   ```

Or run everything at once:
```bash
python run_analysis.py
```

## Example Insights

From the data, you can discover:

- **Peak dispatch times**: When during the day/week flexibility is most needed
- **Zone hotspots**: Which areas have the most constraint issues
- **Technology preferences**: Which asset types are most utilized
- **Pricing trends**: How flexibility prices vary by technology, zone, and product
- **Market concentration**: Which providers dominate the market
- **Growth trajectory**: How the flexibility market is expanding

## Understanding Flexibility Products

- **Secure**: Committed availability and utilisation service
- **Dynamic**: Optional utilisation service
- **Day-Ahead**: Daily auction for flexibility
- **Long-Term Utilisation**: Longer-term flexibility contracts
- **Sustain**: Availability-only product (not dispatched, not in this dataset)

## API Information

**API Endpoint**: `https://ukpowernetworks.opendatasoft.com/api/v2/catalog/datasets/ukpn-flexibility-dispatches/records`

**Rate Limiting**: Be respectful of API limits (scripts include 0.1s delays between requests)

**API Key**: Provided in the scripts (replace with your own if needed)

## Use Cases

- **DNO planning**: Understanding constraint patterns
- **Flexibility providers**: Market intelligence for service offerings
- **Researchers**: Studying DSO flexibility markets
- **Policymakers**: Assessing flexibility market development
- **Investors**: Evaluating flexibility service opportunities

## Data Notes

- Requested volumes may not match delivered volumes (baseline-dependent)
- Actual delivery data available in annual Procurement Statements
- Historic data may be updated when errors are identified
- Data from April 2023 onwards only

## Links

- [UKPN Open Data Portal](https://ukpowernetworks.opendatasoft.com/)
- [UKPN DSO Flexibility Hub](https://dso.ukpowernetworks.co.uk/flexibility)
- [UKPN Tender Hub](https://dso.ukpowernetworks.co.uk/flexibility/tender-hub)

## License

Scripts: MIT License
Data: CC BY 4.0 (from UK Power Networks)

## Author

Created: 2025-10-21
Contact: Emil Larsen, Utiligize

## Contributing

Contributions welcome! Please feel free to submit issues or pull requests.
