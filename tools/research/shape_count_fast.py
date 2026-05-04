import math
from collections import defaultdict

PRIMES = [
2,3,5,7,11,13,17,19,23,29,
31,37,41,43,47,53,59,61,67,71,
73,79,83,89,97
]

shape_cache = {}

def shape_exp(e):

    if e == 1:
        return None

    if e in shape_cache:
        return shape_cache[e]

    factors = []
    x = e
    p = 2

    while p*p <= x:
        count = 0
        while x % p == 0:
            x //= p
            count += 1
        if count:
            factors.append(shape_exp(count))
        p += 1

    if x > 1:
        factors.append(None)

    s = tuple(sorted(factors, key=str))
    shape_cache[e] = s
    return s


def width_distribution(N):

    shapes = set()
    width_counts = defaultdict(int)

    def dfs(i, last_exp, current_n, exps):

        if current_n > N:
            return

        if exps:

            shape = tuple(sorted((shape_exp(e) for e in exps), key=str))

            if shape not in shapes:
                shapes.add(shape)
                width_counts[len(exps)] += 1

        if i >= len(PRIMES):
            return

        p = PRIMES[i]

        for e in range(last_exp, 0, -1):

            new_n = current_n * (p ** e)

            if new_n > N:
                continue

            dfs(i+1, e, new_n, exps + [e])

    max_e = int(math.log2(N)) + 1
    dfs(0, max_e, 1, [])

    return shapes, width_counts


N = 10**24

shapes, width_counts = width_distribution(N)

print("total shapes:", len(shapes))
print()

for w in sorted(width_counts):
    print("width", w, width_counts[w])
