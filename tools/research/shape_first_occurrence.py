import math

PRIMES = [
2,3,5,7,11,13,17,19,23,29,
31,37,41,43,47
]

shape_cache = {}

def shape_exp(e):
    if e == 1:
        return None
    if e in shape_cache:
        return shape_cache[e]

    x = e
    p = 2
    factors = []

    while p*p <= x:
        cnt = 0
        while x % p == 0:
            x //= p
            cnt += 1
        if cnt:
            factors.append(shape_exp(cnt))
        p += 1

    if x > 1:
        factors.append(None)

    s = tuple(sorted(factors, key=str))
    shape_cache[e] = s
    return s


def enumerate_shapes(N):

    shapes = {}
    
    def dfs(i, last_exp, current_n, exps):

        if current_n > N:
            return

        if exps:
            shape = tuple(sorted((shape_exp(e) for e in exps), key=str))
            if shape not in shapes:
                shapes[shape] = current_n

        if i >= len(PRIMES):
            return

        p = PRIMES[i]

        for e in range(last_exp, 0, -1):

            new_n = current_n * (p ** e)

            if new_n > N:
                continue

            dfs(i+1, e, new_n, exps + [e])

    dfs(0, 60, 1, [])

    return shapes


N = 10**12

shapes = enumerate_shapes(N)

items = sorted(shapes.items(), key=lambda x: x[1])

for i,(shape,n) in enumerate(items,1):
    print(f"{i:4d}  {n:12d}  {shape}")
