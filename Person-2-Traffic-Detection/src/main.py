"""Run the complete traffic analysis and detection process."""

from pathlib import Path
import sys

# Add the project folder to Python's import path so config.py can be found.
PROJECT_FOLDER = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_FOLDER))

from config import (
    DATASET_PATH,
    DETECTION_LOG_PATH,
    OUTPUT_FOLDER,
    SUSPICIOUS_IPS_PATH,
    SYN_THRESHOLD,
    TIME_WINDOW_SECONDS,
)
from src.traffic_analyzer import load_traffic_data, count_syn_packets
from src.detector import detect_suspicious_hosts
from src.blocklist import save_suspicious_ips
from src.logger import setup_logger, log_detection_results


def main():
    dataset_file = PROJECT_FOLDER / DATASET_PATH
    output_folder = PROJECT_FOLDER / OUTPUT_FOLDER
    suspicious_file = PROJECT_FOLDER / SUSPICIOUS_IPS_PATH
    log_file = PROJECT_FOLDER / DETECTION_LOG_PATH

    output_folder.mkdir(parents=True, exist_ok=True)
    setup_logger(log_file)

    print("\n=== Dynamic Host Blocking: Traffic Detection ===")

    try:
        # 1. Read the CSV dataset.
        data = load_traffic_data(dataset_file)
        print(f"Dataset loaded. Valid records: {len(data)}")

        # 2. Count SYN packets by IP and time window.
        counts = count_syn_packets(data, TIME_WINDOW_SECONDS)

        # 3. Decide which hosts exceed the threshold.
        results = detect_suspicious_hosts(
            counts, SYN_THRESHOLD, TIME_WINDOW_SECONDS
        )

        print(f"Time window: {TIME_WINDOW_SECONDS} seconds")
        print(f"SYN threshold: more than {SYN_THRESHOLD} packets")
        print("\n=== Results ===")

        if results.empty:
            print("No plain TCP SYN packets found.")
        else:
            print(results.to_string(index=False))

        # 4. Save suspicious candidates and log the results.
        suspicious_ips = save_suspicious_ips(results, suspicious_file)
        log_detection_results(results)

        print("\n=== Suspicious IP candidates ===")
        if suspicious_ips:
            for ip in suspicious_ips:
                print(ip)
        else:
            print("None")

        print(f"\nJSON output: {suspicious_file}")
        print(f"Detection log: {log_file}")
        print("\nFinished. This program does not apply firewall rules.")

    except FileNotFoundError:
        print(f"ERROR: Dataset not found: {dataset_file}")
        print("Put the CSV file in the data folder with the expected name.")
    except Exception as error:
        print(f"ERROR: {error}")


if __name__ == "__main__":
    main()
