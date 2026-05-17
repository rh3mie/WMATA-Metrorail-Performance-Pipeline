# WMATA Metrorail Performance Pipeline
*By Rhey Mar De Vera*

## Business Problem

Transit agencies and commuters lack easy access to historical train performance data. WMATA's real-time API only shows current conditions, so once a moment passes, that data is gone. Without a system to capture and store these snapshots into train operations and incidents over time, it's impossible to identify delay patterns, evaluate service reliability trends, or understand how incidents impact commuter wait times across different lines and stations.

## Solution/ Project Overview

This project builds an end-to-end automated ETL pipeline that captures live WMATA train predictions and service incidents every 15 minutes during business hours. Then, it transforms them into an analytics-ready star schema in Google BigQuery, and visualizes KPIs in a Looker Studio (Data Studio) dashboard. This gives insights into train performance/ operations, such as:

- Train wait times by line and station
- Peak vs. off-peak service patterns
- Incident frequency and category trends
- Station-level performance and delay patterns

## Files

- ```src/extract.py```: Pulls data from 3 WMATA APIs (stations, train predictions, incidents)
- ```src/transform.py```: Cleans and transforms raw data into fact and dimension tables
- ```src/load.py```: Loads transformed data into BigQuery
- ```src/main.py```: Chains ETL scripts into one for a single pipeline run
- ```.github/workflows/pipeline.yml```: GitHub actions workflow for automated scheduling
- ```requirements.txt```: Python dependencies

## Google BigQuery Database
The data is structured into a star schema to optimize queries and support dashboard use in Looker. In total, there are 4 tables:

- ```fact_train_predictions```: For train prediction snapshots. Includes station, line, destination, minutes to arrival, and timestamp
- ```fact_incidents```: For service incidents. Includes incident type, lines effected, description, and categorization
- ```dim_station```: Station name, primary line, and geographic coordinates
- ```dim_line```: line code, full line name, and hex color code

With this star schema, the data has clear relationships through primary and foreign keys across time, station, and line dimensions. This keeps the model scalable, easy to maintain, and optimized for querying.

## Key Steps

### 1. Data Extraction
Connected to the WMATA API using a free developer key and pulled data from three endpoints: rail station information, real-time train arrival predictions, and active service incidents. Data is extracted during WMATA operating hours.

### 2. Data Transformation
Cleaned and shaped raw API responses using Python and Pandas. Key transformations include parsing timestamps, calculating minutes to arrival, standardizing line codes, and categorizing incidents by keywords.

### 3. Data Loading
Loaded transformed dataframes into BigQuery using the ```google-cloud-bigquery``` Python connection. Implemented SQL logic to prevent duplicate rows.

### 4. Pipeline Automation
Automated the ETL pipeline using GitHub actions on a cron schedule that aligns to WMATA operating hours for all 7 days. 

### 5. Dashboard Development
Connected BigQuery database to Looker Studio and built an interactive dashboard tracking service reliability KPIs, wait time trends, incident patterns, and station-level performance across all Metro lines.

## Key Insights

- **Peak hour congestion**: Morning and evening rush hours show the longest average wait times, with the Red Line consistently experiencing higher delays than other lines
- **Terminal station delays**: End-of-line stations such as Shady Grove and Greenbelt show the longest average wait times, suggesting scheduling gaps at turnaround points
- **Incident patterns**: Single tracking is the most common incident type, disproportionately affecting the Red and Blue/Orange/Silver Lines
- **Off-peak reliability**: Midday and weekend service shows significantly shorter and more consistent wait times across all lines

## Recommendations

- **Increase train frequency during peak hours** on the Red Line, which consistently shows the longest average wait times during morning and evening rush hours
- **Investigate terminal station scheduling** at high-delay end-of-line stations to reduce turnaround gaps that contribute to longer waits
- **Prioritize single tracking resolution** as the most frequent incident type. Faster resolution would have the highest impact on reducing commuter delays systemwide
- **Use off-peak performance as a reliability benchmark** to set service targets and evaluate where peak hour performance falls short
