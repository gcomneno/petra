# Experiment 1 — scorecard

## Scope

This scorecard is the compact verdict layer for Experiment 1.

It summarizes the current bounded benchmark conservatively.
It does not claim hard separation or asymptotic conclusions.

## Families

- Perfect
- Primorials
- Hamming (5-smooth)
- HighlyComposite

## Family scorecard

| family | compactness | variability | distinctiveness | overlap risk | confidence | verdict |
|---|---|---|---|---|---|---|
| Perfect | high | low | medium | medium | medium | Tightest family in the current bounded benchmark, but not uniquely isolated by shape alone. |
| Primorials | medium | medium | medium | medium | medium | Moderately structured and reasonably separated on average, but not cleanly isolated. |
| Hamming | medium | medium | low | high | medium | Structurally broad enough to overlap with other families, especially HighlyComposite. |
| HighlyComposite | low | high | medium | high | medium | Widest and most internally varied family in the current bounded benchmark. |

## Pairwise scorecard

| pair | average separation | overlap risk | confidence | verdict |
|---|---|---|---|---|
| Perfect vs Primorials | medium | medium | medium | Some meaningful average separation, but no clean boundary. |
| Perfect vs Hamming | medium | high | medium | Average contrast exists, but shape overlap is real. |
| Perfect vs HighlyComposite | high | low | medium | Strongest average separation in the current bounded benchmark. |
| Primorials vs Hamming | medium | medium | medium | Partial contrast, but still mixed. |
| Primorials vs HighlyComposite | medium | medium | medium | Partial contrast without hard isolation. |
| Hamming vs HighlyComposite | high | high | medium | Large average separation coexists with real structural overlap. |

## Interpretation rules

Use the scorecard conservatively.

Rules:

1. high separation does not mean perfect classification
2. low minimum distance means real overlap risk, even when averages look good
3. bounded evidence should not be inflated into asymptotic claims
4. a mixed result is still a valid result

## Current bottom line

The current bounded benchmark supports a cautious positive claim:

- PET captures real structural differences between some classical integer families
- PET does not provide hard family separation in this setting
- overlap remains an essential part of the result, not a failure to hide
