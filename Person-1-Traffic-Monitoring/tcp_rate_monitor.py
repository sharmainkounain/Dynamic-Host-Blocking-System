import csv
from collections import Counter
from pathlib import Path

csv_file = Path("syn_packets.csv")
if not csv_file.exists():
    raise SystemExit("ERROR: syn_packets.csv not found on Desktop.")

with csv_file.open(newline="", encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))

if not rows or "Time" not in rows[0]:
    raise SystemExit("ERROR: CSV is empty or missing the Time column.")

packets = []
for row in rows:
    try:
        timestamp = float(row["Time"])
    except (ValueError, TypeError):
        continue

    info = row.get("Info", "")
    packets.append({
        "time": timestamp,
        "source": row.get("Source", "unknown"),
        "destination": row.get("Destination", "unknown"),
        "info": info
    })

if not packets:
    raise SystemExit("ERROR: No valid packet timestamps found.")

start = min(p["time"] for p in packets)
windows = Counter()
sources = Counter()

for packet in packets:
    window = int((packet["time"] - start) // 10)
    windows[window] += 1
    sources[packet["source"]] += 1

duration = max(p["time"] for p in packets) - start

print("TCP SYN RATE MONITOR")
print("=" * 40)
print(f"CSV file: {csv_file}")
print(f"Packets analysed: {len(packets)}")
print(f"Observed time span: {duration:.3f} seconds")
print(f"Average rate: {len(packets) / duration:.3f} packets/second"
      if duration > 0 else "Average rate: insufficient time span")
print("\n10-second window statistics:")
for window in sorted(windows):
    count = windows[window]
    print(f"{window * 10:>4}-{(window + 1) * 10:>4} s: "
          f"{count} SYN packets ({count / 10:.2f} packets/second)")

print("\nSource IP counts:")
for source, count in sources.items():
    print(f"{source}: {count}")

print("\nNote: A high SYN rate alone does not prove malicious activity.")
