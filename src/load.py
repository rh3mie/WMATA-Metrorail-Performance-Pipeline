import os
import pandas as pd
from google.cloud import bigquery
from dotenv import load_dotenv

load_dotenv()

PROJECT = os.getenv("GCP_PROJECT")
DATASET = os.getenv("BQ_DATASET")
CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = CREDENTIALS_PATH

client = bigquery.Client(project=PROJECT)

def load_table(df, table_name, write_mode="WRITE_APPEND"):
    """Generic function to load a DataFrame into a BigQuery table."""
    if df.empty:
        print(f"Skipping {table_name}, df empty")
        return

    table_id = f"{PROJECT}.{DATASET}.{table_name}"

    job_config = bigquery.LoadJobConfig(
        write_disposition=write_mode,
        autodetect=True
    )

    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()

    print(f"Loaded {len(df)} rows into {table_id}")

def load_dim_station(df):
    """Load stations as a replaced table."""
    load_table(df, "dim_station", write_mode="WRITE_TRUNCATE")

def load_dim_line(df):
    """Load line dimension as a replaced table."""
    load_table(df, "dim_line", write_mode="WRITE_TRUNCATE")

def load_fact_predictions(df):
    """Append predictions, then deduplicate in BigQuery."""
    if df.empty:
        print("Skipping fact_train_predictions, no predictions to load")
        return
    
    load_table(df, "fact_train_predictions", write_mode="WRITE_APPEND")
    
    dedup_query = f"""
        CREATE OR REPLACE TABLE `{PROJECT}.{DATASET}.fact_train_predictions` AS
        SELECT * EXCEPT(row_num)
        FROM (
            SELECT *,
                ROW_NUMBER() OVER (
                    PARTITION BY station_code, line_code, destination_code, snapshot_timestamp
                    ORDER BY snapshot_timestamp
                ) AS row_num
            FROM `{PROJECT}.{DATASET}.fact_train_predictions`
        )
        WHERE row_num = 1
    """
    client.query(dedup_query).result()
    print(f"Deduplicated fact_train_predictions")

def load_fact_incidents(df):
    """Append incidents, then deduplicate in BigQuery."""
    if df.empty:
        print("Skipping fact_incidents, no incidents to load")
        return
    
    load_table(df, "fact_incidents", write_mode="WRITE_APPEND")

    dedup_query = f"""
        CREATE OR REPLACE TABLE `{PROJECT}.{DATASET}.fact_incidents` AS
        SELECT * EXCEPT(row_num)
        FROM (
            SELECT *,
                ROW_NUMBER() OVER (
                    PARTITION BY incident_id, date_updated
                    ORDER BY snapshot_timestamp
                ) AS row_num
            FROM `{PROJECT}.{DATASET}.fact_incidents`
        )
        WHERE row_num = 1
    """
    client.query(dedup_query).result()
    print(f"Deduplicated fact_incidents")

if __name__ == "__main__":
    from extract import extract_stations, extract_predictions, extract_incidents
    from transform import (
        transform_stations,
        transform_predictions,
        transform_incidents,
        build_dim_line
    )

    print("--- Loading dimension tables ---")
    load_dim_station(transform_stations(extract_stations()))
    load_dim_line(build_dim_line())

    print("\n--- Loading fact tables ---")
    load_fact_predictions(transform_predictions(extract_predictions()))
    load_fact_incidents(transform_incidents(extract_incidents()))

    print("\n All tables loaded successfully!")