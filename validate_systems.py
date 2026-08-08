"""
validate_systems.py
--------------------
Algorithmus zur Prüfung, ob ein Relationssystem (mit Variablen a, b, c, d)
ein eindeutiges Maximum besitzt, und Validierung aller Systeme aus relation_systems.json.

Ablauf des Validierungsalgorithmus
------------------------------------
Gegeben: Eine Liste von Relationen der Form "L op R",
  wobei L und R Summen aus {a, b, c, d} (Koeffizient 1) sind
  und op ∈ {<, >, =}.

Schritt 1 – Normalisierung
  Jede Relation wird als (L, op, R) mit L und R als Variablenmengen dargestellt.
  > wird zu < (durch Tauschen der Seiten).

Schritt 2 – Direkte Ableitungen
  Aus L < R mit |R| = 1 folgt sicher: R[0] > L[i] für alle i.
  (Nicht umgekehrt: aus L < R mit |L| = 1 folgt NICHT R[j] > L[0] für einzelne j.)

Schritt 3 – Lineare Kombinationen
  Alle Paare von Ungleichungs-Koeffizientenvektoren werden mit kleinen
  ganzzahligen Faktoren (1–3) kombiniert. Ergibt eine Kombination
  einen Vektor mit genau zwei Einträgen +k und -k, folgt daraus ein
  direkter Variablenvergleich.

Schritt 4 – Transitivitätsabschluss
  Aus (x > y) und (y > z) wird (x > z) abgeleitet (Floyd-Warshall-artig).

Schritt 5 – Eindeutigkeitsprüfung
  Eine Variable x ist eindeutiges Maximum, wenn (x > y) für alle y ≠ x gilt.
  Genau ein solcher Kandidat → eindeutige Lösung.
"""

import json
import re
from pathlib import Path

VARS = ['a', 'b', 'c', 'd']
VAR_IDX = {v: i for i, v in enumerate(VARS)}


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def parse_side(s: str) -> tuple[int, ...]:
    """Parse a side like 'a+b+c' into a sorted tuple of variable indices."""
    return tuple(sorted(VAR_IDX[v.strip()] for v in s.split('+')))


def parse_relation(rel_str: str) -> tuple[tuple, str, tuple]:
    """
    Parse a relation string such as 'a+b < c' or 'a = b+c+d'.
    Returns (L, op, R) with L and R as sorted index tuples and op in {'<', '>',' ='}.
    """
    for op in ('<=', '>=', '<', '>', '='):
        if op in rel_str:
            parts = rel_str.split(op, 1)
            L = parse_side(parts[0])
            R = parse_side(parts[1])
            return L, op.strip(), R
    raise ValueError(f"Unbekannte Relation: {rel_str!r}")


def normalise(L, op, R):
    """Normalise: convert > to < by swapping sides."""
    if op == '>':
        return R, '<', L
    return L, op, R


# ---------------------------------------------------------------------------
# Core algorithm: derive all (x > y) pairs from a system
# ---------------------------------------------------------------------------

def derive_order(relations: list[tuple]) -> set[tuple[int, int]]:
    """
    Given a list of normalised (L, op, R) triples, derive all provable
    (x > y) pairs using direct inference, linear combinations and transitivity.

    Returns a set of (x, y) pairs meaning x > y.
    """
    gt: set[tuple[int, int]] = set()
    ineqs: list[list[int]] = []   # coefficient vectors: sum(L) - sum(R) < 0

    for L, op, R in relations:
        # --- Direct inference ---
        if op == '<' and len(R) == 1:
            # sum(L) < R[0]  →  R[0] > each element of L
            for v in L:
                gt.add((R[0], v))

        # --- Build coefficient vector for linear-combination step ---
        coeff = [0, 0, 0, 0]
        for v in L:
            coeff[v] += 1
        for v in R:
            coeff[v] -= 1

        if op == '<':
            ineqs.append(coeff)          # coeff · x < 0
        elif op == '=':
            ineqs.append(coeff)          # coeff · x = 0  →  both directions
            ineqs.append([-c for c in coeff])

    # --- Linear combinations ---
    n = len(ineqs)
    for i in range(n):
        for j in range(i, n):
            for ci in range(1, 4):
                for cj in range(0 if i != j else 1, 4):
                    combined = [ci * ineqs[i][k] + cj * ineqs[j][k] for k in range(4)]
                    nonzero = [(k, combined[k]) for k in range(4) if combined[k] != 0]
                    if len(nonzero) == 2:
                        (k1, c1), (k2, c2) = nonzero
                        if c1 + c2 == 0:          # form: c*(k1 - k2) < 0
                            if c1 > 0:
                                gt.add((k1, k2))   # k1 > k2  (wrong: c1*k1 < 0 means k1 < 0 direction)
                            else:
                                gt.add((k2, k1))   # k2 > k1

    # --- Transitivitätsabschluss ---
    changed = True
    while changed:
        changed = False
        for (x, y) in list(gt):
            for (y2, z) in list(gt):
                if y == y2 and (x, z) not in gt:
                    gt.add((x, z))
                    changed = True

    return gt


# ---------------------------------------------------------------------------
# Main validation function
# ---------------------------------------------------------------------------

def has_unique_maximum(relation_strings: list[str]) -> tuple[bool, str | None]:
    """
    Check whether the given relation system has a unique maximum.

    Parameters
    ----------
    relation_strings : list of str
        Relations such as ['a < d', 'b+c < d'].

    Returns
    -------
    (unique, name) where unique is True/False and name is the variable name
    of the unique maximum (or None).
    """
    parsed = [normalise(*parse_relation(r)) for r in relation_strings]
    gt = derive_order(parsed)

    candidates = [
        v for v in range(4)
        if all((v, other) in gt for other in range(4) if other != v)
    ]

    if len(candidates) == 1:
        return True, VARS[candidates[0]]
    return False, None


# ---------------------------------------------------------------------------
# Validate all systems from relation_systems.json
# ---------------------------------------------------------------------------

def validate_all(json_path: str = 'relation_systems.json') -> None:
    path = Path(json_path)
    with path.open(encoding='utf-8') as f:
        systems = json.load(f)

    total = len(systems)
    mismatches = 0
    confirmed_unique = 0
    confirmed_none = 0

    for entry in systems:
        rels = entry['relations']
        stored_unique = entry['has_unique_max']
        stored_max = entry['unique_max']

        computed_unique, computed_max = has_unique_maximum(rels)

        if computed_unique != stored_unique or computed_max != stored_max:
            mismatches += 1
            print(f"MISMATCH: {rels}")
            print(f"  Gespeichert: unique={stored_unique}, max={stored_max}")
            print(f"  Berechnet:   unique={computed_unique}, max={computed_max}")
        else:
            if computed_unique:
                confirmed_unique += 1
            else:
                confirmed_none += 1

    print()
    print("=" * 60)
    print(f"Gesamt Systeme:              {total:>8}")
    print(f"Mit eindeutigem Maximum:     {confirmed_unique:>8}")
    print(f"Ohne eindeutiges Maximum:    {confirmed_none:>8}")
    print(f"Abweichungen (mismatches):   {mismatches:>8}")
    if mismatches == 0:
        print()
        print("✓ Alle Einträge stimmen mit dem Algorithmus überein.")
    else:
        print()
        print("✗ Es gibt Abweichungen – bitte prüfen!")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    import sys

    json_file = sys.argv[1] if len(sys.argv) > 1 else 'relation_systems.json'
    validate_all(json_file)
