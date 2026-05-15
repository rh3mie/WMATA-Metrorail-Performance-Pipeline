# WMATA Metrorail Performance Pipeline

An automated ETL pipeline that collects, transforms, and visualizes real-time Washington DC Metro (WMATA) train performance data to support transit reliability analysis and operational decision-making.

## Business Problem

Transit agencies and commuters lack easy access to historical train performance data. WMATA's real-time API only shows current conditions — once a moment passes, that data is gone. This pipeline captures and stores every snapshot, enabling trend analysis, delay pattern detection, and service reliability reporting that would otherwise be impossible.

## Solution

An end-to-end data pipeline that captures live WMATA Metrorail data every 15 minutes, transforms it into an analytics-ready star schema in Google BigQuery, and visualizes key performance indicators in a Looker Studio dashboard — enabling data-driven insights into service reliability, wait times, and incident patterns across all 6 Metro lines.

## Business Impact

- **Operational visibility** — Identifies which Metro lines and stations experience the most delays and longest wait times, supporting infrastructure prioritization decisions
- **Commuter impact analysis** — Quantifies peak hour wait times by station and line, revealing where service gaps most affect riders
- **Incident trend reporting** — Tracks frequency and duration of service disruptions by line and incident type, enabling pattern detection over time
- **Data-driven planning** — Provides historical performance benchmarks that transit planners can use to evaluate service improvements

## Dashboard KPIs

- Average wait time by Metro line and station
- Incident frequency and category breakdown by line
- Peak vs. off-peak wait time comparison by hour of day
- Weekly service reliability trends
- Top stations by average delay

## Architecture
WMATA API → extract.py → transform.py → load.py → BigQuery → Looker Studio
↑
GitHub Actions (every 15 min)

## Tech Stack

| Tool | Purpose |
|---|---|
| Python | Data extraction and transformation |
| SQL | Deduplication and data modeling in BigQuery |
| Google BigQuery | Cloud data warehouse |
| Looker Studio | BI dashboard and data visualization |
| GitHub Actions | Pipeline orchestration and scheduling |

## Data Model

**Fact Tables**
- `fact_train_predictions` — one row per train prediction snapshot (station, line, wait time, timestamp)
- `fact_incidents` — one row per service incident (type, lines affected, description, duration)

**Dimension Tables**
- `dim_station` — station name, line, coordinates
- `dim_line` — line code, full name, color
- `dim_date` — date attributes derived from snapshot timestamp

## Pipeline Details

- Pulls data from 3 WMATA API endpoints every 15 minutes during operating hours
- Handles special arrival statuses (BRD, ARR) and null resolution logic
- Deduplicates fact tables on each run to prevent double-counting
- Stores credentials securely via GitHub Secrets — no hardcoded keys

## Setup

1. Clone the repo
2. Create a GCP project and enable the BigQuery API
3. Create a BigQuery dataset called `wmata_transit`
4. Add a service account with BigQuery Editor and Job User roles
5. Get a free WMATA API key at developer.wmata.com
6. Add `WMATA_API_KEY` and `GCP_SERVICE_ACCOUNT_KEY` as GitHub Secrets
7. The pipeline will run automatically via GitHub Actions

## Local Development

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env      # Fill in your credentials
python src/main.py
```