# Dutch Flexibility Market Analysis - GOPACS

Analysis of cleared flexibility market buckets from the Netherlands via the GOPACS platform.

## Status: ✅ Complete Analysis

Successfully fetched and analyzed 959 clearing events (14,912 PTU records) from Dec 2018 to Oct 2025.

## Data Source

- **Platform**: GOPACS (Grid Operators Platform for Congestion Solutions)
- **API Endpoint**: https://public-reporting.gopacs-services.eu/clearedbuckets
- **Data Type**: Cleared buckets (matched buy/sell orders)
- **Coverage**: December 2018 - October 2025 (almost 7 years)
- **License**: Public data

## Key Findings

### Overall Statistics
- **Total Clearing Events**: 959
- **Total PTU Records**: 14,912 (15-minute intervals)
- **Total Volume**: 2,171,618 MW (buy/sell matched)
- **Average PTU Volume**: 145.63 MW
- **Average Event Duration**: 4.4 hours (median: 3 hours)

### Grid Operators (4 total)

| Operator | Type | Events | Avg Volume (MW) | Total Volume (MW) |
|----------|------|--------|-----------------|-------------------|
| **TenneT** | TSO | 697 | 169.34 | 2,168,892 |
| **Liander** | DSO | 161 | 1.06 | 987 |
| **Enexis** | DSO | 86 | 1.42 | 1,464 |
| **Stedin** | DSO | 15 | 1.91 | 275 |

**Key Insight**: TSO (TenneT) dominates with 73% of events and 99.9% of total volume. DSO volumes are ~130x smaller.

### Temporal Patterns

**Peak Years**:
- 2021: 315 events, 576,142 MW
- 2022: 147 events, 727,834 MW
- 2020: 120 events, 215,862 MW

**Recent Trend**: ⚠️ Significant decline since 2023
- 2024: 110 events (-93.5% volume decline)
- 2025: 79 events (partial year)

**Weekly Pattern**:
- Weekdays dominate (90% of activity)
- Tuesday highest (170 events)
- Weekend activity minimal

**Hourly Pattern**:
- Peak hours: 8 AM - 6 PM (business hours)
- Top hour: 11 AM (291 events)
- Minimal night activity

### Market Characteristics

**Event Duration Distribution**:
- < 1 hour: 296 events (31%)
- 1-2 hours: 138 events (14%)
- 2-4 hours: 216 events (23%)
- 4-8 hours: 167 events (17%)
- 8-24 hours: 142 events (15%)

**PTU Structure**: All records use 15-minute Program Time Units (PTUs), standard in Dutch electricity markets.

## Comparison with UK Market

| Metric | 🇳🇱 Netherlands (GOPACS) | 🇬🇧 UK (UKPN) |
|--------|-------------------------|---------------|
| **Records** | 959 events, 14,912 PTUs | 10,000 dispatches |
| **Time Range** | Dec 2018 - Oct 2025 (7 years) | Apr 2023 - Oct 2025 (2.5 years) |
| **Operators** | 4 (1 TSO, 3 DSOs) | 1 DNO (UKPN) |
| **Avg Volume** | 145.6 MW | 0.50 MW |
| **Market Type** | TSO-dominated, larger grid-level | DNO-level, distributed assets |
| **Granularity** | 15-min PTUs | Hourly dispatches |
| **Data Structure** | Cleared buckets (matched orders) | Individual dispatches |

**Key Difference**: Dutch market shows TSO (transmission) level congestion management, while UK shows DNO (distribution) level flexibility services.

## Scripts

### 1. `fetch_gopacs_data.py`
Downloads all cleared bucket records and flattens PTU data.

```bash
python fetch_gopacs_data.py
```

**Output**: `gopacs_cleared_buckets.csv`

### 2. `analyze_gopacs_market.py`
Comprehensive statistical analysis of the flexibility market.

```bash
python analyze_gopacs_market.py
```

**Analyses**:
- Temporal patterns (yearly, monthly, weekly, hourly)
- Grid operator comparison (TSO vs DSO)
- Volume distributions and statistics
- Event characteristics and duration
- Market growth trends

### 3. `visualize_gopacs_market.py`
Generates comprehensive visualizations of the flexibility market.

```bash
python visualize_gopacs_market.py
```

**Outputs** (5 PNG files):
- `yearly_trends.png` - Annual events, volume, energy, TSO vs DSO split
- `operator_comparison.png` - Grid operator comparison charts
- `temporal_patterns.png` - Day of week, hourly, monthly trends, duration distribution
- `dso_detail.png` - Detailed DSO analysis and comparison
- `volume_analysis.png` - Volume distributions, TSO vs DSO trends, cumulative energy

### 4. `requirements.txt`
Python dependencies (pandas, numpy, matplotlib, seaborn, requests)

## Installation

```bash
pip install -r requirements.txt
```

## Data Structure

### Clearing Event
- `clearingEventId`: Unique event identifier
- `organisationName`: Grid operator (TenneT, Liander, Enexis, Stedin)
- `buyVolumeInMWh`: Total buy volume for event
- `sellVolumeInMWh`: Total sell volume for event
- `startTime`, `endTime`: Event timespan

### PTU (Program Time Unit)
- 15-minute intervals within each event
- `buyVolumeInMW`, `sellVolumeInMW`: Power for this PTU
- `ptuStartTime`, `ptuEndTime`: PTU timespan

## Notable Observations

1. **TSO vs DSO**: Transmission-level congestion (TenneT) is ~130x larger than distribution-level (Liander/Enexis/Stedin)

2. **Market Maturity**: Peak activity in 2021-2022, followed by decline. Possible reasons:
   - Network reinforcements reducing congestion
   - Changes in market design or participation
   - Shift to other congestion management tools

3. **Business Hours Focus**: 90% weekday activity, 8 AM - 6 PM peak, suggests operational/trading hour constraints

4. **PTU Standardization**: Consistent 15-minute intervals align with Dutch electricity market standards (EPEX, day-ahead)

## Resources

- **GOPACS Platform**: https://www.gopacs.eu
- **Public Data**: https://app.gopacs.eu/public/clearedbuckets
- **TenneT Transparency**: https://www.tennet.eu/electricity-market/transparency
- **ENTSO-E**: https://transparency.entsoe.eu/

---

**Analysis Date**: 2025-10-21
**Data Coverage**: 2018-12-19 to 2025-10-10
**Total Events**: 959
**Total PTUs**: 14,912
