"""Decide which hosts exceed the configured SYN threshold."""


def detect_suspicious_hosts(counts, syn_threshold, time_window_seconds):
    """Return counts with a status and a human-readable reason."""
    results = counts.copy()

    if results.empty:
        results["status"] = []
        results["reason"] = []
        return results

    # Use > rather than >=: a host is flagged only when it EXCEEDS the limit.
    results["status"] = results["syn_count"].apply(
        lambda count: (
            "SUSPICIOUS" if count > syn_threshold else "NORMAL"
        )
    )

    results["reason"] = results["syn_count"].apply(
        lambda count: (
            f"More than {syn_threshold} SYN packets in "
            f"{time_window_seconds} seconds"
            if count > syn_threshold
            else "At or below the configured threshold"
        )
    )

    return results
