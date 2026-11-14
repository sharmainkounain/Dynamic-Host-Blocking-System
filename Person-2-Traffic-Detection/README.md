# Person 2 – Traffic Detection

This folder contains the traffic analysis and suspicious host detection components of the Dynamic Host Blocking System.

## Components

- `traffic_analyzer.py` – Reads and analyses TCP traffic from the CSV dataset.
- `detector.py` – Identifies hosts exceeding the configured SYN threshold.
- `detector.py.py` – Additional detection implementation.
- `blocklist.py` – Exports suspicious IP candidates to JSON.
- `logger.py` – Records detection results.
- `main.py` – Runs the traffic detection pipeline.
- `config.py` – Defines detection thresholds and file paths.

## Data and Results

- `data/traffic.csv` – Input traffic dataset.
- `output/suspicious_ips.json` – Suspicious IP candidates.
- `output/detection.log` – Detection log.

## Dependencies

Install the required Python package using:

`pip install -r requirements.txt`

## Python Dependency

- pandas
