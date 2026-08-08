"""
generate_systems.py
--------------------
Erzeugt alle kanonisch verschiedenen Relationssysteme (Größe 2 und 3) mit
Variablen a, b, c, d, wobei jede Seite einer Relation eine Multimenge mit
maximal 3 Symbolen ist (Wiederholungen erlaubt, z. B. a+a+b).

Für jedes System wird mit dem LP-basierten Algorithmus aus validate_systems.py
geprüft, ob ein eindeutiges Maximum existiert. Nur solche Systeme werden in
unique_systems.json gespeichert.

Kanonische Form
---------------
Zwei Systeme gelten als strukturell gleich, wenn eines durch Umbenennung der
Variablen (Permutation von {a,b,c,d}) aus dem anderen hervorgeht. Es wird nur
die lexikographisch kleinste Darstellung gespeichert.

Laufzeit
--------
- Größe 2: ~1,47 Mio. Systempaare, einige Minuten.
- Größe 3: ~842 Mio. Systemtripel, sehr lange. Mit --size 2 nur Größe 2 testen.

Verwendung
----------
    python generate_systems.py                    # Größe 2 und 3
    python generate_systems.py --size 2           # nur Größe 2
    python generate_systems.py --out my.json      # andere Ausgabedatei
"""

import json
import sys
import time
from collections import Counter
from itertools import combinations, combinations_with_replacement, permutations

from validate_systems import has_unique_maximum, VARS

# ---------------------------------------------------------------------------
# Seiten und Relationen generieren
# ---------------------------------------------------------------------------

MAX_SIDE = 3  # maximale Symbole pro Seite
OPS = ['<', '=']  # > ist redundant durch Tauschen


def all_sides() -> list[tuple[str, ...]]:
    """Alle Multimengen aus {a,b,c,d} der Länge 1..MAX_SIDE (sortiert)."""
    result = []
    for size in range(1, MAX_SIDE + 1):
        result.extend(combinations_with_replacement(VARS, size))
    return result


def side_to_str(side: tuple[str, ...]) -> str:
    return '+'.join(side)


def all_relations(sides: list[tuple]) -> list[tuple]:
    """
    Alle kanonischen Relationen (L, op, R) als Tupel.
    Für '<': L und R beliebig, L != R (L < L ist stets falsch).
    Für '=': nur L <= R (lexikografisch), da L = R äquivalent zu R = L.
    Relationen wie a < a (Summe gleich) werden ausgefiltert, da sie stets
    falsch sind und das System inkonsistent machen würden.
    """
    rels = []
    for L in sides:
        for R in sides:
            # '<': L != R erforderlich; außerdem sum(L)==sum(R) würde a<b+... nie erfüllbar machen
            # wir lassen alle zu und vertrauen auf den LP-Filter
            if L != R:
                rels.append((L, '<', R))
            # '=': kanonisch L <= R; L == R wäre trivial wahr (keine Information)
            if L < R:
                rels.append((L, '=', R))
    return rels


# ---------------------------------------------------------------------------
# Kanonische Form eines Systems
# ---------------------------------------------------------------------------

# Alle 24 Permutationen der Variablen
_PERMS = list(permutations(VARS))


def _apply_perm(perm: tuple, rel: tuple) -> tuple:
    """Wende eine Variablen-Permutation auf eine Relation (L, op, R) an."""
    mapping = dict(zip(VARS, perm))
    L, op, R = rel
    new_L = tuple(sorted(mapping[v] for v in L))
    new_R = tuple(sorted(mapping[v] for v in R))
    # Normalise: for <, keep as-is; for =, ensure L <= R
    if op == '=' and new_L > new_R:
        new_L, new_R = new_R, new_L
    return (new_L, op, new_R)


def canonical_form(system: frozenset) -> frozenset | None:
    """
    Gibt die kanonisch kleinste (lexikografisch) Darstellung des Systems
    unter allen Variablen-Permutationen zurück.
    Gibt None zurück, wenn das System unter einer Permutation eine
    inkonsistente Relation enthält (L < L).
    """
    best = None
    sys_list = sorted(system)
    for perm in _PERMS:
        mapped = frozenset(_apply_perm(perm, r) for r in sys_list)
        # Check for trivially false relations: (L, '<', L)
        if any(L == R and op == '<' for L, op, R in mapped):
            continue
        if best is None or sorted(mapped) < sorted(best):
            best = mapped
    return best


def system_to_strings(system: frozenset) -> list[str]:
    """Konvertiere ein System von Relation-Tupeln in lesbare Strings."""
    result = []
    for L, op, R in sorted(system):
        result.append(f"{side_to_str(L)} {op} {side_to_str(R)}")
    return result


# ---------------------------------------------------------------------------
# Hauptgenerator
# ---------------------------------------------------------------------------

def generate(max_size: int = 3, out_path: str = 'unique_systems.json') -> None:
    sides = all_sides()
    rels = all_relations(sides)
    print(f"Mögliche Seiten:    {len(sides)}")
    print(f"Mögliche Relationen: {len(rels)}")

    seen: set[frozenset] = set()
    unique_systems: list[dict] = []
    total_checked = 0
    t0 = time.time()

    def process_system(system_tuple: tuple) -> None:
        nonlocal total_checked
        total_checked += 1

        raw = frozenset(system_tuple)
        canon = canonical_form(raw)
        if canon is None or canon in seen:
            return
        seen.add(canon)

        rel_strings = system_to_strings(canon)
        unique, max_var = has_unique_maximum(rel_strings)
        if unique:
            unique_systems.append({
                'relations': rel_strings,
                'size': len(canon),
                'unique_max': max_var,
            })

    def report(size: int) -> None:
        elapsed = time.time() - t0
        print(f"  Größe {size}: {total_checked:>12,} geprüft, "
              f"{len(seen):>10,} kanonisch verschieden, "
              f"{len(unique_systems):>8,} mit eindeutigem Max  "
              f"({elapsed:.0f}s)")

    for size in range(2, max_size + 1):
        print(f"\nGeneriere Systeme der Größe {size} ...")
        checked_before = total_checked
        for system_tuple in combinations(rels, size):
            process_system(system_tuple)
            if total_checked % 500_000 == 0:
                report(size)
        report(size)
        print(f"  → {total_checked - checked_before:,} Kombinationen der Größe {size} geprüft.")

    # Write output
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(unique_systems, f, indent=2, ensure_ascii=False)

    elapsed = time.time() - t0
    print(f"\n{'=' * 60}")
    print(f"Gesamt geprüft:              {total_checked:>10,}")
    print(f"Kanonisch verschieden:       {len(seen):>10,}")
    print(f"Mit eindeutigem Maximum:     {len(unique_systems):>10,}")
    print(f"Laufzeit:                    {elapsed:.1f}s")
    print(f"Gespeichert in:              {out_path}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    args = sys.argv[1:]
    max_size = 3
    out_path = 'unique_systems.json'

    if '--size' in args:
        idx = args.index('--size')
        max_size = int(args[idx + 1])
    if '--out' in args:
        idx = args.index('--out')
        out_path = args[idx + 1]

    generate(max_size=max_size, out_path=out_path)
