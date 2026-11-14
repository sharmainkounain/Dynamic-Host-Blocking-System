"""Set up and write detection log messages."""

import logging
from pathlib import Path


def setup_logger(log_path):
    """Create the log folder and configure logging."""
    log_path = Path(log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        force=True,
    )


def log_detection_results(results):
    """Write one log entry for each suspicious host/window."""
    suspicious_rows = results[
        results["status"] == "SUSPICIOUS"
    ]

    if suspicious_rows.empty:
        logging.info("Analysis finished; no hosts exceeded the threshold.")
        return

    for _, row in suspicious_rows.iterrows():
        logging.warning(
            "Suspicious candidate: IP=%s | window=%s | SYN count=%s | reason=%s",
            row["source_ip"],
            row["window_start"],
            row["syn_count"],
            row["reason"],
        )
