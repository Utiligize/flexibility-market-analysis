# Flexibility Market Analysis - Multi-Country

Comprehensive analysis of electricity flexibility market activations across different countries/regions.

## Overview

This project analyzes flexibility dispatch data from Distribution Network Operators (DNOs) to understand:
- When and where flexibility is dispatched
- What technologies provide flexibility services
- Market dynamics, pricing, and provider competition
- Tender success rates and procurement efficiency

## Countries/Regions

### 🇬🇧 Great Britain (GB)

**Status**: ✅ Complete with full analysis

UK Power Networks (UKPN) flexibility market analysis with 10,000+ dispatch records.

**Data Source**: [UK Power Networks Open Data Portal](https://ukpowernetworks.opendatasoft.com/)

**Key Findings**:
- £6M market value, 11.4 GWh dispatched (Apr 2023 - Oct 2025)
- 6.5% tender procurement success rate
- EV charging DSR dominates (60% of dispatches)
- 157 active zones, 31 providers, 413 flexible units

[📁 See GB folder for complete analysis](./GB/)

---

### 🇳🇱 Netherlands (NL)

**Status**: ⚠️ API endpoint identification needed

GOPACS (Grid Operators Platform for Congestion Solutions) flexibility market data.

**Platform**: [GOPACS](https://app.gopacs.eu/public/clearedbuckets)

**Next Steps**:
- Identify backend API endpoint through browser DevTools
- Document API structure and authentication
- Develop data fetching and analysis scripts

[📁 See NL folder for details](./NL/)

---

## Project Structure

```
uk-open-data/
├── .gitignore              # Excludes CSV data files
├── README.md              # This file
├── GB/                    # Great Britain (UK) analysis
│   ├── README.md          # GB-specific documentation
│   ├── ANALYSIS_SUMMARY.md  # Detailed findings report
│   ├── fetch_flexibility_data.py
│   ├── analyze_flexibility_market.py
│   ├── analyze_tender_success.py
│   ├── visualize_flexibility_market.py
│   ├── run_analysis.py
│   ├── requirements.txt
│   └── *.png             # 9 visualization outputs
└── NL/                    # Netherlands analysis
    └── README.md          # Status and next steps
```

## Common Analysis Framework

Both country analyses will provide:

1. **Temporal Patterns**: Monthly, weekly, daily, and hourly dispatch trends
2. **Geographic Distribution**: Zones with highest flexibility needs
3. **Technology Breakdown**: Asset types providing flexibility
4. **Market Dynamics**: Provider competition and market concentration
5. **Pricing Analysis**: Cost trends by technology, product, and dispatch type
6. **Success Metrics**: Tender-to-contract conversion rates
7. **Growth Trajectory**: Market development over time

## Requirements

### Python Dependencies

```bash
pip install pandas numpy matplotlib seaborn requests
```

### API Authentication

Each country may require API keys or authentication:

- **GB (UKPN)**: Register at [UKPN Open Data Portal](https://ukpowernetworks.opendatasoft.com/), then set:
  ```bash
  export UKPN_API_KEY=your_key_here
  ```

- **NL (GOPACS)**: TBD - API access method to be determined

## Quick Start (GB Example)

```bash
# Navigate to GB folder
cd GB/

# Set API key
export UKPN_API_KEY=your_key_here

# Run complete analysis
python run_analysis.py

# Or run individual steps:
python fetch_flexibility_data.py
python analyze_flexibility_market.py
python visualize_flexibility_market.py
python analyze_tender_success.py
```

## Use Cases

- **DNOs/TSOs**: Benchmark flexibility procurement efficiency
- **Flexibility Providers**: Market intelligence and opportunity identification
- **Researchers**: Study DSO flexibility market evolution
- **Policymakers**: Assess market design effectiveness
- **Investors**: Evaluate flexibility service opportunities

## Data Licenses

- **GB**: CC BY 4.0 (UK Power Networks)
- **NL**: TBD (GOPACS platform terms)

## Contributing

To add a new country/region:

1. Create a new folder (e.g., `DE/` for Germany)
2. Add README with data source and API details
3. Implement fetch, analyze, and visualize scripts
4. Document findings in ANALYSIS_SUMMARY.md
5. Update this main README

## Related Resources

### UK
- [UKPN DSO Flexibility Hub](https://dso.ukpowernetworks.co.uk/flexibility)
- [UKPN Tender Hub](https://dso.ukpowernetworks.co.uk/flexibility/tender-hub)

### Netherlands
- [GOPACS Platform](https://www.gopacs.eu)
- [TenneT Transparency Dashboard](https://www.tennet.eu/electricity-market/transparency)

### Europe-Wide
- [ENTSO-E Transparency Platform](https://transparency.entsoe.eu/)
- [EU DSO Entity](https://www.edsoforsmartgrids.eu/)

---

**Project Started**: 2025-10-21
**Last Updated**: 2025-10-21
**Maintainer**: Utiligize
