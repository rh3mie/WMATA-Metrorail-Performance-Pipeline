import pandas as pd

LINE_CODE_MAP = {
    "RD": "Red",
    "BL": "Blue",
    "GR": "Green",
    "OR": "Orange",
    "SV": "Silver",
    "YL": "Yellow"
}

def transform_stations(df):
    """Clean and shape stations data into dim_station."""
    df = df.copy()

    # fill missing line codes with None
    for col in ["line_code_1", "line_code_2", "line_code_3", "line_code_4"]:
        df[col] = df[col].replace("", None)

    # use primary line code for line name
    df["line_name"] = df["line_code_1"].map(LINE_CODE_MAP)

    print(f"Transformed {len(df)} stations")
    return df

def transform_predictions(df):
    """Clean and shape predictions into fact_train_predictions."""
    if df.empty:
        print("No predictions to transform")
        return df
    df = df.copy()

    # map line codes to full names
    df["line_name"] = df["line_code"].map(LINE_CODE_MAP)

    # convert minutes_to_arrival to numeric
    # WMATA returns "BRD" (boarding), "ARR" (arriving), "---" (no data)
    df["arrival_status"] = df["minutes_to_arrival"].apply(
        lambda x: x if x in ["BRD", "ARR", "---"] else "scheduled"
    )
    df["minutes_to_arrival_clean"] = pd.to_numeric(
        df["minutes_to_arrival"], errors="coerce"
    )

    # drop rows with no useful arrival info
    df = df[df["minutes_to_arrival"] != "---"]

    # add hour of day
    df["snapshot_timestamp"] = pd.to_datetime(df["snapshot_timestamp"])
    df["hour_of_day"] = df["snapshot_timestamp"].dt.hour
    df["day_of_week"] = df["snapshot_timestamp"].dt.day_name()
    df["date"] = df["snapshot_timestamp"].dt.date.astype(str)

    print(f"Transformed {len(df)} train predictions")
    return df

def transform_incidents(df):
    """Clean and shape incidents into fact_incidents."""
    if df.empty:
        print("No incidents to transform")
        return df

    df = df.copy()

    # parse date_updated as datetime
    df["date_updated"] = pd.to_datetime(df["date_updated"], utc=True)

    # clean up lines_affected
    df["lines_affected_clean"] = (
        df["lines_affected"]
        .str.replace(";", ",")
        .str.strip()
        .str.rstrip(",")
    )

    # categorize incident type by keyword
    def categorize_incident(description):
        description = str(description).lower()
        if "delay" in description:
            return "Delay"
        elif "single" in description or "track" in description:
            return "Single Tracking"
        elif "equipment" in description:
            return "Equipment Issue"
        elif "medical" in description:
            return "Medical Emergency"
        else:
            return "Other"

    df["incident_category"] = df["description"].apply(categorize_incident)
    df["snapshot_timestamp"] = pd.to_datetime(df["snapshot_timestamp"])

    print(f"Transformed {len(df)} incidents")
    return df

def build_dim_line():
    """Build a static dimension table for Metro lines."""
    data = {
        "line_code": ["RD", "BL", "GR", "OR", "SV", "YL"],
        "line_name": ["Red", "Blue", "Green", "Orange", "Silver", "Yellow"],
        "hex_color": ["#BF0000", "#009CDE", "#00B140", "#F7941D", "#919D9D", "#FFD700"]
    }
    df = pd.DataFrame(data)
    print(f"Built dim_line with {len(df)} lines")
    return df

if __name__ == "__main__":
    from extract import extract_stations, extract_predictions, extract_incidents

    stations_df = transform_stations(extract_stations())
    predictions_df = transform_predictions(extract_predictions())
    incidents_df = transform_incidents(extract_incidents())
    dim_line_df = build_dim_line()

    print("\n--- Transformed Stations Sample ---")
    print(stations_df.head(3))
    print("\n--- Transformed Predictions Sample ---")
    print(predictions_df.head(3))
    print("\n--- Transformed Incidents Sample ---")
    print(incidents_df.head(3))
    print("\n--- Dim Line ---")
    print(dim_line_df)