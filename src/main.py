import sys
import os
sys.path.append(os.path.dirname(__file__))

from extract import extract_stations, extract_predictions, extract_incidents
from transform import (
    transform_stations,
    transform_predictions,
    transform_incidents,
    build_dim_line
)
from load import (
    load_dim_station,
    load_dim_line,
    load_fact_predictions,
    load_fact_incidents
)

def run_pipeline():
    print("🚇 Starting WMATA ETL Pipeline...\n")

    print("--- Step 1: Extracting ---")
    stations_raw = extract_stations()
    predictions_raw = extract_predictions()
    incidents_raw = extract_incidents()

    print("\n--- Step 2: Transforming ---")
    stations_clean = transform_stations(stations_raw)
    predictions_clean = transform_predictions(predictions_raw)
    incidents_clean = transform_incidents(incidents_raw)
    dim_line = build_dim_line()

    print("\n--- Step 3: Loading ---")
    load_dim_station(stations_clean)
    load_dim_line(dim_line)
    load_fact_predictions(predictions_clean)
    load_fact_incidents(incidents_clean)

    print("\n✅ Pipeline run complete!")

if __name__ == "__main__":
    run_pipeline()