"""
validate_systems.py
--------------------
Algorithmus zur Prüfung, ob ein Relationssystem (mit Variablen a, b, c, d >= 1)
ein eindeutiges Maximum besitzt.

Ablauf des Validierungsalgorithmus (LP-basiert)
------------------------------------------------
Gegeben: Eine Liste von Relationen der Form "L op R",
  wobei L und R Multimengen aus {a, b, c, d} mit maximal 3 Symbolen sind
  (ein Symbol darf mehrfach vorkommen, z. B. a+a+b) und op ∈ {<, >, =}.
  Alle Variablen sind natürliche Zahlen >= 1.

Für jede Kandidatenvariable x und jeden Gegner y wird geprüft, ob das
lineare Programm

    Minimiere  x - y          (wir suchen ob y >= x möglich ist)
    unter:     alle Relationen des Systems als lineare (Un-)Gleichungen
               a, b, c, d >= 1

unerfüllbar ist oder ein Minimum > 0 hat. Falls x - y > 0 für alle y != x
zwingend gilt, ist x das eindeutige Maximum.

Technisch: scipy.optimize.linprog prüft Erfüllbarkeit von
  "Gibt es a,b,c,d >= 1 mit den Systemrelationen UND y >= x?"
Falls das LP unbeschränkt/unerfüllbar ist, gilt x > y zwingend.

Da die Variablen natürliche Zahlen sind (diskret), reicht LP hier aus:
Wenn y >= x für reelle Zahlen unmöglich ist (unter den gegebenen linearen
Constraints), ist es für ganzzahlige Zahlen erst recht unmöglich.
"""

import numpy as np
from scipy.optimize import linprog

VARS = ['a', 'b', 'c', 'd']
VAR_IDX = {v: i for i, v in enumerate(VARS)}

# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def parse_side(s: str) -> tuple[int, ...]:
    """Parse 'a+b+c' into a sorted tuple of variable indices."""
    return tuple(sorted(VAR_IDX[v.strip()] for v in s.split('+')))


def parse_relation(rel_str: str) -> tuple[tuple, str, tuple]:
    """
    Parse 'a+b < c' or 'a = b+c+d'.
    Returns (L, op, R) with L, R as sorted index tuples and op in {'<','>','='}.
    """
    for op in ('<=', '>=', '<', '>', '='):
        if op in rel_str:
            parts = rel_str.split(op, 1)
            L = parse_side(parts[0])
            R = parse_side(parts[1])
            return L, op.strip(), R
    raise ValueError(f"Unbekannte Relation: {rel_str!r}")


def normalise(L, op, R):
    """Convert > to < by swapping sides."""
    if op == '>':
        return R, '<', L
    return L, op, R


# ---------------------------------------------------------------------------
# LP-based feasibility check
# ---------------------------------------------------------------------------

def _build_lp_constraints(relations: list[tuple]):
    """
    Convert the relation system into LP constraint matrices.

    Variables: x = [a, b, c, d]  (indices 0–3)
    All variables >= 1  (encoded as lower bounds).

    Returns (A_ub, b_ub, A_eq, b_eq) for scipy.linprog.
      A_ub @ x <= b_ub   (strict < is approximated by <= -eps, see caller)
      A_eq @ x  = b_eq
    """
    A_ub, b_ub, A_eq, b_eq = [], [], [], []

    for L, op, R in relations:
        # coefficient vector for  sum(L) - sum(R)
        coeff = [0, 0, 0, 0]
        for v in L:
            coeff[v] += 1
        for v in R:
            coeff[v] -= 1

        if op == '<':
            # sum(L) < sum(R)  ⟺  coeff · x < 0  ⟺  coeff · x <= -1
            # (integers: strictly less means at most -1)
            A_ub.append(coeff)
            b_ub.append(-1)
        elif op == '=':
            A_eq.append(coeff)
            b_eq.append(0)

    return (
        np.array(A_ub, dtype=float) if A_ub else None,
        np.array(b_ub, dtype=float) if b_ub else None,
        np.array(A_eq, dtype=float) if A_eq else None,
        np.array(b_eq, dtype=float) if b_eq else None,
    )


def _is_infeasible(relations: list[tuple], extra_ub: list[int]) -> bool:
    """
    Check if the LP  {system relations} ∧ {extra_ub · x <= 0} ∧ {x >= 1}
    is infeasible.

    extra_ub is a coefficient vector for an additional constraint
    extra_ub · x <= 0, i.e.  "y >= x"  encoded as  x - y <= 0.

    Returns True if infeasible (meaning x > y is certain).
    """
    A_ub, b_ub, A_eq, b_eq = _build_lp_constraints(relations)

    # Add the extra constraint
    row = np.array(extra_ub, dtype=float).reshape(1, 4)
    rhs = np.array([0.0])
    if A_ub is not None:
        A_ub = np.vstack([A_ub, row])
        b_ub = np.append(b_ub, rhs)
    else:
        A_ub, b_ub = row, rhs

    # Bounds: all variables >= 1, no upper bound
    bounds = [(1, None)] * 4

    # Minimise a dummy constant (just check feasibility)
    result = linprog(
        c=[0, 0, 0, 0],
        A_ub=A_ub,
        b_ub=b_ub,
        A_eq=A_eq,
        b_eq=b_eq,
        bounds=bounds,
        method='highs',
        options={'disp': False},
    )

    # status 2 = infeasible
    return result.status == 2


# ---------------------------------------------------------------------------
# Main validation function
# ---------------------------------------------------------------------------

def has_unique_maximum(relation_strings: list[str]) -> tuple[bool, str | None]:
    """
    Check whether the relation system has a unique maximum for all a,b,c,d >= 1.

    For each candidate x and each rival y:
      Ask: "Is there a solution with y >= x?"
      If the LP is infeasible → x > y is certain.
    If x beats all rivals → x is the unique maximum.

    Parameters
    ----------
    relation_strings : list[str]
        E.g. ['a = b+c+d', 'b = c'].

    Returns
    -------
    (unique, name)
    """
    parsed = [normalise(*parse_relation(r)) for r in relation_strings]

    candidates = []
    for x in range(4):
        beats_all = True
        for y in range(4):
            if y == x:
                continue
            # Extra constraint: y >= x  ⟺  x - y <= 0
            extra = [0, 0, 0, 0]
            extra[x] = 1
            extra[y] = -1
            if not _is_infeasible(parsed, extra):
                beats_all = False
                break
        if beats_all:
            candidates.append(x)

    if len(candidates) == 1:
        return True, VARS[candidates[0]]
    return False, None


# ---------------------------------------------------------------------------
# Entry point: check a single system from command line
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Verwendung: python validate_systems.py 'a+a < b' 'a = b+c+d'")
        sys.exit(1)

    rels = sys.argv[1:]
    unique, max_var = has_unique_maximum(rels)
    if unique:
        print(f"Eindeutiges Maximum: {max_var}")
    else:
        print("Kein eindeutiges Maximum.")
