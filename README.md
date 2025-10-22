# Flexibility Market Analysis - Multi-Country

Comprehensive analysis of electricity flexibility market activations across different countries/regions.

**Author**: Emil Mahler Larsen, CTO, Utiligize
**Date**: October 2025

## Overview

This project analyzes flexibility dispatch data from Distribution Network Operators (DNOs) and Transmission System Operators (TSOs) to understand:
- When and where flexibility is dispatched
- What technologies provide flexibility services
- Market dynamics, pricing, and provider competition
- Tender success rates and procurement efficiency
- Comparison between different market models

## Countries/Regions

### 🇬🇧 Great Britain (GB)

**Status**: ✅ Complete with full analysis (23,607 dispatches)

UK Power Networks (UKPN) flexibility market - complete DNO-level analysis.

**Data Source**: [UK Power Networks Open Data Portal](https://ukpowernetworks.opendatasoft.com/)

**Key Findings**:
- **£13.1M market value**, 28.5 GWh dispatched (Apr 2023 - Oct 2025)
- **10% tender success rate** (90% of zones unactivated)
- **56% EV charging** (predominantly home chargers aggregated by retailers)
- **48% monopoly zones** (single provider only)
- **158 active zones**, 31 providers, 439 flexible units
- **Distribution-level**: 86% at 33/11kV substations
- **Top provider**: Octopus Energy (£3.2M), followed by Ørsted (£2.3M wind)
- **Contract length**: 6.4 months average (seasonal/annual mix)
- **Jackpot events**: 15% of revenue from £4k-40k/MWh peak prices

[📁 See GB folder for complete analysis](./GB/)

---

### 🇳🇱 Netherlands (NL)

**Status**: ✅ Complete analysis (959 clearing events)

GOPACS (Grid Operators Platform for Congestion Solutions) flexibility market data.

**Data Source**: [GOPACS Public API](https://public-reporting.gopacs-services.eu/clearedbuckets)

**Key Findings**:
- **959 clearing events**, 14,912 PTU records (Dec 2018 - Oct 2025)
- **TSO-dominated**: TenneT 99.9% of volume (transmission-level)
- **DSO minimal**: Only 0.1% of market (682 MWh over 7 years)
- **4 operators**: TenneT (TSO), Liander, Enexis, Stedin (DSOs)
- **15-minute PTUs** (standard Dutch market structure)
- **Peak 2021-2022**, significant decline since 2023
- **Average volume**: 145.6 MW per PTU (transmission-scale)

**Comparison**: NL is transmission-focused (TSO), GB is distribution-focused (DNO)
- NL DSOs: 100 MWh/year
- GB UKPN alone: 11,193 MWh/year (25% of GB market)
- **UKPN is 112x larger; Full GB estimated ~450x larger** than NL DSOs

[📁 See NL folder for complete analysis](./NL/)

---

## Key Comparison: GB vs NL

| Aspect | 🇬🇧 Great Britain (UKPN) | 🇳🇱 Netherlands (GOPACS) |
|--------|--------------------------|--------------------------|
| **Market Focus** | DNO distribution-level | TSO transmission-level |
| **Avg Capacity** | 0.44 MW | 145.6 MW |
| **Dominant Tech** | EV home chargers (56%) | N/A (cleared buckets) |
| **Market Type** | Retailer-aggregated residential | Grid-level congestion |
| **Granularity** | Hourly dispatches | 15-minute PTUs |
| **DSO Activity** | Very active (28.5 GWh) | Minimal (0.7 GWh) |
| **Trend** | Growing 4x (2023-2025) | Declining (peak 2021-2022) |

**Key Insight**: GB leads Europe in distribution-level flexibility markets, while NL focuses on transmission-level congestion management.

---

## Project Structure

```
uk-open-data/
├── .gitignore                    # Excludes CSV data files
├── README.md                     # This file
├── GB/                          # Great Britain (UK) analysis
│   ├── README.md                # GB-specific documentation
│   ├── ANALYSIS_SUMMARY.md      # Complete findings report
│   ├── DETAILED_FINDINGS.md     # Q&A on specific topics
│   ├── CONTRACT_STRUCTURE_EXPLAINED.md
│   ├── TENDER_STRUCTURE_EXPLAINED.md
│   ├── POST_CORRECTIONS.md
│   ├── fetch_flexibility_data.py
│   ├── fetch_all_data.py        # Bypass 10k API limit
│   ├── analyze_flexibility_market.py
│   ├── analyze_tender_success.py
│   ├── analyze_peak_pricing.py
│   ├── visualize_flexibility_market.py
│   ├── create_square_graphs.py
│   ├── requirements.txt
│   ├── *.png                    # 10+ visualization outputs
│   └── square_graphs/          # 10 SVG graphs (1000x1000px)
└── NL/                          # Netherlands analysis
    ├── README.md                # NL findings and comparison
    ├── fetch_gopacs_data.py
    ├── analyze_gopacs_market.py
    ├── visualize_gopacs_market.py
    ├── requirements.txt
    └── *.png                    # 5 visualization outputs
```

## Common Analysis Framework

Both country analyses provide:

1. **Temporal Patterns**: Monthly, weekly, daily, and hourly dispatch trends
2. **Geographic Distribution**: Zones with highest flexibility needs
3. **Technology Breakdown**: Asset types providing flexibility
4. **Market Dynamics**: Provider competition and market concentration
5. **Pricing Analysis**: Cost trends by technology, product, and dispatch type
6. **Success Metrics**: Market effectiveness and utilization rates
7. **Growth Trajectory**: Market development over time

## Requirements

### Python Dependencies

```bash
pip install pandas numpy matplotlib seaborn requests
```

### API Authentication

**GB (UKPN)**: Register at [UKPN Open Data Portal](https://ukpowernetworks.opendatasoft.com/), then set:
```bash
export UKPN_API_KEY=your_key_here
```

**NL (GOPACS)**: No authentication required - public API

## Quick Start

### GB (Great Britain)

```bash
cd GB/

# Set API key
export UKPN_API_KEY=your_key_here

# Fetch all data (bypasses 10k limit with date filtering)
python fetch_all_data.py

# Run analysis
python analyze_flexibility_market.py
python visualize_flexibility_market.py
python analyze_tender_success.py
python analyze_peak_pricing.py

# Or generate publication graphs (10 square SVGs, 1000x1000px)
python create_square_graphs.py
```

### NL (Netherlands)

```bash
cd NL/

# Fetch data (no API key needed)
python fetch_gopacs_data.py

# Run analysis
python analyze_gopacs_market.py
python visualize_gopacs_market.py
```

## Use Cases

- **DNOs/TSOs**: Benchmark flexibility procurement efficiency across countries
- **Flexibility Providers**: Market intelligence and opportunity identification
- **Researchers**: Study DSO vs TSO flexibility market evolution
- **Policymakers**: Compare market designs (GB's DNO model vs NL's TSO model)
- **Investors**: Evaluate flexibility service opportunities
- **Energy Retailers**: Understand residential EV aggregation potential

## Key Insights

### GB Market Model
- **Distribution-focused** (DNO level, 33/11kV substations)
- **Home EV aggregation** via energy retailers (Octopus, OVO, Ohme)
- **56% residential charging** paused during peak demand
- **Growing rapidly** (4x growth 2023-2025)
- **High failure rate** (90% of tenders unsuccessful)
- **Jackpot pricing** (£20-40k/MWh during winter emergencies = 15% revenue)

### NL Market Model
- **Transmission-focused** (TSO level, TenneT)
- **Grid-level congestion** management
- **DSO activity minimal** (0.1% of market)
- **Declining trend** (peak 2021-2022, down 93% since)
- **15-minute PTUs** (standard Dutch market structure)

### GB's Massive Lead in Distribution Flexibility

GB's distribution-level market is **vastly more developed** than NL's:
- **UKPN alone** (25% of GB): 112x larger than all NL DSOs combined
- **Full GB estimated**: ~450x larger than NL DSOs
- NL DSOs activate only 100 MWh/year vs GB's ~45,000 MWh/year

This shows GB's clear leadership in DNO-level flexibility services, while NL focuses on TSO transmission-level congestion.

## Data Licenses

- **GB**: CC BY 4.0 (UK Power Networks)
- **NL**: Public data (GOPACS platform)

## Contributing

To add a new country/region:

1. Create a new folder (e.g., `DE/` for Germany, `FR/` for France)
2. Add README with data source and API details
3. Implement fetch, analyze, and visualize scripts
4. Document findings in ANALYSIS_SUMMARY.md
5. Update this main README with key findings

## Related Resources

### UK
- [UKPN DSO Flexibility Hub](https://dso.ukpowernetworks.co.uk/flexibility)
- [UKPN Tender Hub](https://dso.ukpowernetworks.co.uk/flexibility/tender-hub)
- [UKPN Open Data Portal](https://ukpowernetworks.opendatasoft.com/)

### Netherlands
- [GOPACS Platform](https://www.gopacs.eu)
- [GOPACS Public Reporting](https://public-reporting.gopacs-services.eu/clearedbuckets)
- [TenneT Transparency Dashboard](https://www.tennet.eu/electricity-market/transparency)

### Europe-Wide
- [ENTSO-E Transparency Platform](https://transparency.entsoe.eu/)
- [EU DSO Entity](https://www.edsoforsmartgrids.eu/)

## Publications & Outputs

Analysis and visualizations ready for:
- Social media posts (10 square SVG graphs in GB/square_graphs/)
- Academic papers
- Policy reports
- Market intelligence briefings
- Presentations and conferences

Contact Emil Mahler Larsen (Utiligize) for collaboration or data sharing.

---

**Project Started**: 2025-10-21
**Last Updated**: 2025-10-21
**Datasets**: GB 23,607 dispatches | NL 959 events
**Coverage**: GB Apr 2023 - Oct 2025 | NL Dec 2018 - Oct 2025
