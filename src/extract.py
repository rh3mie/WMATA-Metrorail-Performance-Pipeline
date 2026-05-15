import requests
import pandas as pd
from datetime import datetime, UTC
import os
from dotenv import load_dotenv

load_dotenv()

WMATA_API_KEY = os.getenv("WMATA_API_KEY")
BASE_URL = "https://api.wmata.com"
HEADERS = {"api_key": WMATA_API_KEY}

def extract_stations():
    """Pull static list of all rail stations."""
    url = f"{BASE_URL}/Rail.svc/json/jStations"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    
    stations = response.json()["Stations"]
    df = pd.DataFrame(stations)
    df = df[["Code", "Name", "LineCode1", "LineCode2", "LineCode3", "LineCode4", "Lat", "Lon"]]
    df.columns = ["station_code", "station_name", "line_code_1", "line_code_2", "line_code_3", "line_code_4", "latitude", "longitude"]
    
    print(f"✅ Extracted {len(df)} stations")
    return df

def extract_predictions():
    """Pull real-time train arrival predictions for all stations."""
    url = f"{BASE_URL}/StationPrediction.svc/json/GetPrediction/All"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    
    trains = response.json()["Trains"]
    df = pd.DataFrame(trains)
    df = df[["LocationCode", "LocationName", "Line", "Car", "Destination", "DestinationName", "Min"]]
    df.columns = ["station_code", "station_name", "line_code", "car", "destination_code", "destination_name", "minutes_to_arrival"]
    df["snapshot_timestamp"] = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"✅ Extracted {len(df)} train predictions")
    return df

def extract_incidents():
    """Pull active rail incidents and delays."""
    url = f"{BASE_URL}/Incidents.svc/json/Incidents"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    
    incidents = response.json()["Incidents"]
    if not incidents:
        print("✅ No active incidents")
        return pd.DataFrame()
    
    df = pd.DataFrame(incidents)
    df = df[["IncidentID", "IncidentType", "LinesAffected", "Description", "DateUpdated"]]
    df.columns = ["incident_id", "incident_type", "lines_affected", "description", "date_updated"]
    df["snapshot_timestamp"] = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"✅ Extracted {len(df)} incidents")
    return df

if __name__ == "__main__":
    stations_df = extract_stations()
    predictions_df = extract_predictions()
    incidents_df = extract_incidents()
    
    print("\n--- Stations Sample ---")
    print(stations_df.head(3))
    print("\n--- Predictions Sample ---")
    print(predictions_df.head(3))
    print("\n--- Incidents Sample ---")
    print(incidents_df.head(3))