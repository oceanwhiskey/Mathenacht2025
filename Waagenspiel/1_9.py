from itertools import combinations

def paare_der_kardinalitaet_n(s: set, n: int):
    for y in combinations(s, n):
        yield set(y)

def zweier_teilmengen(x: set):
    yield from paare_der_kardinalitaet_n(x, 2)

def fuenfer_teilmengen(x: set):
    yield from paare_der_kardinalitaet_n(x, 5)

def isSpannend(s: set[int]):
    for a in zweier_teilmengen(s):
        for b in zweier_teilmengen(s.difference(a)):
            if sum(a) == sum(b):
                return False
    return True

for s in fuenfer_teilmengen([1, 2, 3, 4, 5, 6, 7, 8]):
    if isSpannend(set(s)):
        print(s)

