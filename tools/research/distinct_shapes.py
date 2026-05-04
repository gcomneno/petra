import json
import sys

from collections import Counter


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

path = sys.argv[1]
with open(path) as f:
    for line in f:
        row = json.loads(line)

        shape = normalize(row["pet"])
        shapes[shape] += 1


print("distinct shapes:", len(shapes))
print()

total = sum(shapes.values())

for shape,count in shapes.most_common(10):
    pct = 100 * count / total
    print()
    print(f"{count:8d}  {pct:6.2f}%")
    print(shape)
