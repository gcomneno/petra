"""
tools/cluster_families.py

Analisi di clustering delle famiglie aritmetiche note usando
distance() e structural_distance() di PET-Algebra.

Famiglie analizzate:
  - Primorials
  - Hamming (5-smooth)
  - Highly composite
  - Perfect

Per ogni famiglia: matrice delle distanze, diametro, raggio.
Poi: distanze inter-famiglia (min/mean/max).
Infine: test di separabilità (gap inter-min > max intra-diam).
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pet import encode, PET
from pet.algebra import distance, structural_distance

# ── Famiglie ────────────────────────────────────────────────────────────────

FAMILIES = {
    "Primorials": [2, 6, 30, 210, 2310, 30030, 510510],
    "Hamming":    [2, 4, 6, 8, 12, 16, 18, 24, 25, 27, 32, 36, 48, 60, 72,
                   96, 100, 120, 125, 128, 144, 150, 180, 192, 216, 225,
                   240, 243, 250, 256],
    "HighlyComposite": [2, 4, 6, 12, 24, 36, 48, 60, 120, 180, 240, 360,
                        720, 840, 1260, 1680, 2520, 5040, 7560, 10080,
                        15120, 20160, 25200, 27720, 45360, 50400, 55440,
                        83160, 110880, 166320, 221760, 277200, 332640,
                        498960, 554400, 665280, 720720],
    "Perfect":    [6, 28, 496, 8128],
}

# ── Utilità ─────────────────────────────────────────────────────────────────

def dist_matrix(members, dfunc):
    """Restituisce dizionario (i,j) -> distanza per i<j."""
    n = len(members)
    trees = [encode(m) for m in members]
    mat = {}
    for i in range(n):
        for j in range(i + 1, n):
            mat[(i, j)] = dfunc(trees[i], trees[j])
    return mat

def diameter(mat):
    return max(mat.values()) if mat else 0.0

def radius(members, mat):
    """Raggio = min su i di max_j dist(i,j)."""
    n = len(members)
    if n <= 1:
        return 0.0
    eccentricities = []
    for i in range(n):
        ecc = max(
            mat.get((min(i, j), max(i, j)), 0.0)
            for j in range(n) if j != i
        )
        eccentricities.append(ecc)
    return min(eccentricities)

def mean_dist(mat):
    vals = list(mat.values())
    return sum(vals) / len(vals) if vals else 0.0

def print_matrix(members, mat, label, width=7):
    n = len(members)
    print(f"\n  Matrice {label} ({n}x{n}):")
    header = " " * 8 + "".join(f"{m:>{width}}" for m in members)
    print(header)
    for i in range(n):
        row = f"  {members[i]:>5}  "
        for j in range(n):
            if i == j:
                row += f"{'0.00':>{width}}"
            else:
                key = (min(i, j), max(i, j))
                row += f"{mat[key]:>{width}.2f}"
        print(row)

def print_matrix_compact(members, mat, label):
    """Versione compatta per famiglie grandi: statistiche per riga."""
    n = len(members)
    print(f"\n  {label} — statistiche per elemento (n={n}):")
    print(f"  {'n':>8}  {'min':>6}  {'mean':>6}  {'max':>6}")
    for i in range(n):
        dists = [mat.get((min(i, j), max(i, j)), 0.0)
                 for j in range(n) if j != i]
        if dists:
            print(f"  {members[i]:>8}  {min(dists):>6.2f}  "
                  f"{sum(dists)/len(dists):>6.2f}  {max(dists):>6.2f}")

# ── Analisi intra-famiglia ───────────────────────────────────────────────────

def analyze_family(name, members):
    print(f"\n{'='*60}")
    print(f"  {name}  ({len(members)} elementi)")
    print(f"{'='*60}")

    dmat = dist_matrix(members, distance)
    smat = dist_matrix(members, structural_distance)

    compact = len(members) > 12

    if compact:
        print_matrix_compact(members, dmat, "distance")
        print_matrix_compact(members, smat, "structural_distance")
    else:
        print_matrix(members, dmat, "distance")
        print_matrix(members, smat, "structural_distance")

    print(f"\n  Riassunto:")
    print(f"    distance            → diam={diameter(dmat):.2f}  "
          f"rad={radius(members, dmat):.2f}  "
          f"mean={mean_dist(dmat):.2f}")
    print(f"    structural_distance → diam={diameter(smat):.2f}  "
          f"rad={radius(members, smat):.2f}  "
          f"mean={mean_dist(smat):.2f}")

    return dmat, smat

# ── Analisi inter-famiglia ───────────────────────────────────────────────────

def inter_family_distances(families_data, dfunc, label):
    names = list(families_data.keys())
    print(f"\n{'='*60}")
    print(f"  Distanze INTER-famiglia — {label}")
    print(f"{'='*60}")
    print(f"  {'Famiglia A':<20}  {'Famiglia B':<20}  "
          f"{'min':>6}  {'mean':>6}  {'max':>6}")
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            na, nb = names[i], names[j]
            ma = [encode(m) for m in families_data[na]]
            mb = [encode(m) for m in families_data[nb]]
            dists = [dfunc(a, b) for a in ma for b in mb]
            print(f"  {na:<20}  {nb:<20}  "
                  f"{min(dists):>6.2f}  "
                  f"{sum(dists)/len(dists):>6.2f}  "
                  f"{max(dists):>6.2f}")

# ── Separabilità ────────────────────────────────────────────────────────────

def separability_report(families_data, dfunc, label):
    names = list(families_data.keys())
    print(f"\n  Separabilità ({label}):")
    print(f"  {'Coppia':<42}  {'gap_inter_min':>13}  {'max_intra':>9}  {'separato?':>9}")

    diams = {}
    for name, members in families_data.items():
        mat = dist_matrix(members, dfunc)
        diams[name] = diameter(mat)

    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            na, nb = names[i], names[j]
            ma = [encode(m) for m in families_data[na]]
            mb = [encode(m) for m in families_data[nb]]
            inter_min = min(dfunc(a, b) for a in ma for b in mb)
            max_intra = max(diams[na], diams[nb])
            sep = "✓ SÌ" if inter_min > max_intra else "✗ NO"
            coppia = f"{na} vs {nb}"
            print(f"  {coppia:<42}  {inter_min:>13.2f}  "
                  f"{max_intra:>9.2f}  {sep:>9}")

# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("PET — Clustering famiglie aritmetiche")
    print("distance() e structural_distance()")

    for name, members in FAMILIES.items():
        analyze_family(name, members)

    inter_family_distances(FAMILIES, distance,            "distance")
    inter_family_distances(FAMILIES, structural_distance, "structural_distance")

    print(f"\n{'='*60}")
    print("  SEPARABILITÀ  (gap inter-min > max intra-diam?)")
    print(f"{'='*60}")
    separability_report(FAMILIES, distance,            "distance")
    separability_report(FAMILIES, structural_distance, "structural_distance")

    print(f"\n{'='*60}")
    print("  Fine analisi.")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
