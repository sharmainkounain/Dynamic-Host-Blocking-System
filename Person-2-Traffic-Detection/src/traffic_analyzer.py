"""Read and count TCP SYN packets from the CSV dataset."""

import pandas as pd


def load_traffic_data(file_path):
    """Read the CSV and check that required columns are present."""
    data = pd.read_csv(file_path)

    required_columns = [
        "timestamp",
        "source_ip",
        "destination_ip",
        "protocol",
        "tcp_flags",
    ]

    missing_columns = [
        column for column in required_columns
        if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            "CSV is missing required columns: "
            + ", ".join(missing_columns)
        )

    # Convert timestamps to date/time values. Invalid timestamps become empty.
    data["timestamp"] = pd.to_datetime(
        data["timestamp"], errors="coerce"
    )

    # Standardize text so values such as "tcp" and "TCP" match.
    for column in ["source_ip", "protocol", "tcp_flags"]:
        data[column] = (
            data[column].astype("string").str.strip()
        )

    data["protocol"] = data["protocol"].str.upper()
    data["tcp_flags"] = data["tcp_flags"].str.upper()

    # Remove rows missing information needed for detection.
    data = data.dropna(
        subset=["timestamp", "source_ip", "protocol", "tcp_flags"]
    )

    return data


def count_syn_packets(data, time_window_seconds):
    """Count plain TCP SYN packets per source IP in fixed time windows."""
    tcp_data = data[data["protocol"] == "TCP"].copy()

    # This starter version counts rows whose flag is exactly SYN.
    # SYN-ACK is not counted as a plain SYN packet.
    syn_data = tcp_data[tcp_data["tcp_flags"] == "SYN"].copy()

    if syn_data.empty:
        return pd.DataFrame(
            columns=["source_ip", "window_start", "syn_count"]
        )

    # Make fixed, clock-aligned windows, e.g. 10:00:00, 10:00:10, ...
    syn_data["window_start"] = syn_data["timestamp"].dt.floor(
        f"{time_window_seconds}s"
    )

    counts = (
        syn_data.groupby(["source_ip", "window_start"])
        .size()
        .reset_index(name="syn_count")
    )

    return counts
