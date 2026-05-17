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
Connected BigQuery database to Looker Studio and built an interactive dashboard tracking service reliability KPIs, wait time trends, incident patterns, and station-level performance across all Metro lines. Link to Looker/ Data Studio dashboard [here.](https://datastudio.google.com/reporting/13d75f44-a299-4b11-b8f6-5c53e15df264)

<img width="1195" height="895" alt="image" src="https://github.com/user-attachments/assets/57d66370-63cb-4298-9f62-a896c8ef1d55" />

## Key Insights

- **Morning rush has the highest wait times**: The hour-of-day line chart shows a sharp spike around hour 8, with average wait times peaking near 35+ minutes during the morning rush, then dropping significantly through midday and evening hours
- **Silver Line has the longest average wait**: At approximately 6-7 minutes on average, the Silver Line consistently outpaces other lines, likely due to its longer route stretching to Ashburn and the frequency gaps at end-of-line stations
- **End-of-line stations experience the highest delays**: McLean, Greenbelt, Tysons, Loudoun Gateway, Ashburn, and Herndon dominate the top 6 highest wait time stations. These are all terminus or near terminus Silver line stops
- **L'Enfant Plaza is the busiest station**: With the highest prediction volume across all snapshots, L'Enfant Plaza serves as the system's highest-traffic interchange. This can change over time as the pipeline keeps updating.

## Recommendations

- **Increase Silver Line frequency at terminus stations**: McLean, Ashburn, and Loudoun Gateway consistently show the longest wait times, suggesting scheduling gaps at turnaround points that could be reduced with more frequent service
- **Prioritize single tracking resolution on Red and Silver Lines**: Both lines are disproportionately affected by single tracking incidents, which compound already long wait times during peak hours. This is based off early data, and can change as historical data updates over time.
- **Add service capacity during morning rush hours**: The sharp morning peak suggests demand significantly outpaces supply during this window across all lines. Targeted frequency increases during 7-9 AM could meaningfully reduce average wait times
- **Monitor end-of-line station performance as a reliability benchmark**: These stations consistently underperform system averages and should be tracked as leading indicators of overall service health
