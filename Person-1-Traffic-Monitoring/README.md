# Person 1 – TCP Traffic Monitoring

This folder contains the TCP traffic monitoring and packet capture components of the Dynamic Host Blocking System.

## Project Overview

The traffic monitoring component captures and analyses TCP SYN packet activity to provide traffic data for the suspicious host detection module.

## Files

- `tcp_rate_monitor.py` – Analyses TCP SYN packet rates using packet information from a CSV dataset.
- `tcp_rate_results.txt` – Contains sample TCP monitoring results.
- `syn_packets.csv` – Contains extracted SYN packet information.
- `tcp_capture.pcapng` – Wireshark packet capture file.

## Tools Used

- Python
- Wireshark
- CSV-based traffic analysis

## Monitoring Workflow

1. Capture network packets using Wireshark.
2. Extract TCP SYN packet information.
3. Store the extracted information in CSV format.
4. Analyse packet counts and TCP SYN rates.
5. Generate monitoring results for further traffic analysis.

## Running the Monitoring Script

Run the following command from this folder:

```bash
python tcp_rate_monitor.py
```

The script uses `syn_packets.csv` as its input dataset.

## Integration with Person 2

The extracted SYN packet information can be used as input for the traffic analysis and suspicious host detection component.

## Team Contribution

**Shivani Shrivastava – TCP Traffic Monitoring**
