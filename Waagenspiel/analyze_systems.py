"""
analyze_systems.py
-------------------
Filtert aus relation_systems.json alle Systeme mit eindeutigem Maximum,
speichert sie in unique_systems.json und gibt ausführliche Statistiken aus.
"""

import json
from pathlib import Path
from collections import Counter


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def count_op(relations: list[str], op: str) -> int:
    return sum(1 for r in relations if f' {op} ' in r)


def term_sizes(side: str) -> int:
    """Number of variables on one side (count of '+' plus 1)."""
    return side.count('+') + 1


def relation_shape(rel: str) -> tuple[int, str, int]:
    """Return (|L|, op, |R|) for a relation string."""
    for op in ('<', '>', '='):
        if f' {op} ' in rel:
            L, R = rel.split(f' {op} ', 1)
            return term_sizes(L), op, term_sizes(R)
    raise ValueError(rel)


def max_side_size(rel: str) -> int:
    l, _, r = relation_shape(rel)
    return max(l, r)


def total_variables_used(relations: list[str]) -> int:
    """Number of distinct variables appearing in the system."""
    used = set()
    for r in relations:
        for ch in r:
            if ch in 'abcd':
                used.add(ch)
    return len(used)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(src: str = 'relation_systems.json',
         dst: str = 'unique_systems.json') -> None:

    with open(src, encoding='utf-8') as f:
        all_systems = json.load(f)

    unique = [s for s in all_systems if s['has_unique_max']]

    # Save filtered JSON
    with open(dst, 'w', encoding='utf-8') as f:
        json.dump(unique, f, indent=2, ensure_ascii=False)
    print(f"Gespeichert: {dst}  ({len(unique)} Systeme)\n")

    n = len(unique)

    # ------------------------------------------------------------------
    # 1. Systemgröße
    # ------------------------------------------------------------------
    size2 = sum(1 for s in unique if s['size'] == 2)
    size3 = sum(1 for s in unique if s['size'] == 3)

    print("=" * 60)
    print("1. ANZAHL RELATIONEN PRO SYSTEM")
    print(f"   2 Relationen : {size2:>6}  ({100*size2/n:.1f} %)")
    print(f"   3 Relationen : {size3:>6}  ({100*size3/n:.1f} %)")

    # ------------------------------------------------------------------
    # 2. Operatoren
    # ------------------------------------------------------------------
    has_eq   = sum(1 for s in unique if any('=' in r and '<' not in r and '>' not in r
                                             for r in s['relations']))
    only_ineq = sum(1 for s in unique if not any('=' in r and '<' not in r and '>' not in r
                                                   for r in s['relations']))
    all_eq   = sum(1 for s in unique if all('=' in r and '<' not in r and '>' not in r
                                             for r in s['relations']))

    eq_counts = Counter()
    for s in unique:
        c = sum(1 for r in s['relations'] if '=' in r and '<' not in r and '>' not in r)
        eq_counts[c] += 1

    lt_counts = Counter()
    for s in unique:
        c = sum(1 for r in s['relations'] if '<' in r)
        lt_counts[c] += 1

    print()
    print("=" * 60)
    print("2. OPERATOREN")
    print(f"   Systeme mit mind. 1 Gleichung (=) : {has_eq:>6}  ({100*has_eq/n:.1f} %)")
    print(f"   Systeme nur mit Ungleichungen (<>) : {only_ineq:>6}  ({100*only_ineq/n:.1f} %)")
    print(f"   Systeme ausschließlich Gleichungen : {all_eq:>6}  ({100*all_eq/n:.1f} %)")
    print()
    print("   Anzahl Gleichungen im System:")
    for k in sorted(eq_counts):
        print(f"     {k} Gleichungen : {eq_counts[k]:>6}  ({100*eq_counts[k]/n:.1f} %)")
    print()
    print("   Anzahl Ungleichungen (<) im System:")
    for k in sorted(lt_counts):
        print(f"     {k} Ungleichungen : {lt_counts[k]:>6}  ({100*lt_counts[k]/n:.1f} %)")

    # ------------------------------------------------------------------
    # 3. Seitengrößen
    # ------------------------------------------------------------------
    shape_counter = Counter()
    for s in unique:
        for r in s['relations']:
            shape_counter[relation_shape(r)] += 1

    print()
    print("=" * 60)
    print("3. FORM DER EINZELNEN RELATIONEN  (|L| op |R|)")
    for (l, op, r), cnt in sorted(shape_counter.items()):
        print(f"   {l} {op} {r}  :  {cnt:>6}")

    # ------------------------------------------------------------------
    # 4. Welche Variable ist das Maximum?
    # ------------------------------------------------------------------
    max_var_count = Counter(s['unique_max'] for s in unique)
    print()
    print("=" * 60)
    print("4. HÄUFIGKEIT DES MAXIMUMS")
    print("   (Hinweis: ungleichmäßig, da die kanonische Form die lexikographisch")
    print("    kleinste Umbenennung wählt → 'd' landet häufiger als Maximum)")
    for v in 'abcd':
        c = max_var_count[v]
        print(f"   {v} ist Maximum : {c:>6}  ({100*c/n:.1f} %)")

    # ------------------------------------------------------------------
    # 5. Komplexität: Gesamtzahl der Terme
    # ------------------------------------------------------------------
    def total_terms(s):
        t = 0
        for r in s['relations']:
            l, op, r2 = relation_shape(r)
            t += l + r2
        return t

    term_dist = Counter(total_terms(s) for s in unique)
    print()
    print("=" * 60)
    print("5. GESAMTZAHL DER TERME PRO SYSTEM (Summe aller |L|+|R|)")
    for k in sorted(term_dist):
        print(f"   {k:>2} Terme : {term_dist[k]:>6}  ({100*term_dist[k]/n:.1f} %)")

    # ------------------------------------------------------------------
    # 6. Systeme mit direkten 1-vs-1-Vergleichen
    # ------------------------------------------------------------------
    direct_chain = sum(
        1 for s in unique
        if any(relation_shape(r) in [(1,'<',1),(1,'>',1)] for r in s['relations'])
    )
    print()
    print("=" * 60)
    print("6. STRUKTURELLE BESONDERHEITEN")
    print(f"   Systeme mit mind. 1 direktem 1-vs-1 Vergleich : {direct_chain:>6}  ({100*direct_chain/n:.1f} %)")

    # Systems where the max appears on the right side of every inequality
    def max_always_right(s):
        mx = s['unique_max']
        for r in s['relations']:
            if '<' in r:
                _, rhs = r.split(' < ', 1)
                if mx not in rhs:
                    return False
        return True

    right_dominant = sum(1 for s in unique if max_always_right(s))
    print(f"   Max steht immer rechts bei <            : {right_dominant:>6}  ({100*right_dominant/n:.1f} %)")

    # ------------------------------------------------------------------
    # 7. Minimale Systeme (2 Relationen mit eindeutigem Maximum)
    # ------------------------------------------------------------------
    min_sys = [s for s in unique if s['size'] == 2]
    print()
    print("=" * 60)
    print(f"7. ALLE {len(min_sys)} MINIMALSYSTEME (2 Relationen)")
    for s in min_sys[:50]:
        print(f"   {s['relations']}  →  max={s['unique_max']}")
    if len(min_sys) > 50:
        print(f"   ... und {len(min_sys)-50} weitere")

    print()
    print("=" * 60)
    print(f"GESAMT: {n} Systeme mit eindeutigem Maximum")
    print(f"        (von {len(all_systems)} symmetrisch verschiedenen Systemen = {100*n/len(all_systems):.1f} %)")


if __name__ == '__main__':
    import sys
    src = sys.argv[1] if len(sys.argv) > 1 else 'relation_systems.json'
    dst = sys.argv[2] if len(sys.argv) > 2 else 'unique_systems.json'
    main(src, dst)
