import json
import sys
from pathlib import Path
from collections import Counter

INPUT_FILE = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("docs/reports/data/scan-2-1000000.jsonl")

height_dist = Counter()

with INPUT_FILE.open(encoding="utf-8") as f:
    for line in f:
        row = json.loads(line)
        height_dist[row["metrics"]["height"]] += 1

total = sum(height_dist.values())

print("height distribution")
print()

for h in sorted(height_dist):
    pct = 100 * height_dist[h] / total
    print(h, height_dist[h], f"{pct:.2f}%")
