import json
import math
import sys
from pathlib import Path
from collections import Counter

INPUT_FILE = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("docs/reports/data/scan-2-1000000.jsonl")


def normalize(node_list):
    shape = []

    for node in node_list:
        exp = node["e"]

        if exp is None:
            shape.append(("p", None))
        else:
            shape.append(("p", normalize(exp)))

    return tuple(sorted(shape, key=str))


shapes = Counter()

with INPUT_FILE.open(encoding="utf-8") as f:
    for line in f:
        row = json.loads(line)

        shape = normalize(row["pet"])
        shapes[shape] += 1


total = sum(shapes.values())

H = 0

for count in shapes.values():
    p = count / total
    H -= p * math.log(p)

print("shape entropy:", H)
print("max entropy:", math.log(len(shapes)))
