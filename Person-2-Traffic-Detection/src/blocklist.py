"""Save flagged IP addresses for the blocking module to read."""

import json
from pathlib import Path


def save_suspicious_ips(results, output_path):
    """Write unique suspicious IP candidates to a JSON file."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if results.empty:
        suspicious_ips = []
    else:
        suspicious_ips = sorted(
            results.loc[
                results["status"] == "SUSPICIOUS", "source_ip"
            ].dropna().unique().tolist()
        )

    output_data = {
        "suspicious_ips": suspicious_ips,
        "note": (
            "These are detection candidates, not proof of malicious activity "
            "and not confirmation that a firewall block has been applied."
        ),
    }

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(output_data, file, indent=4)

    return suspicious_ips
