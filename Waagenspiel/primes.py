
import itertools as it

def primes_sieve(limit):
    a = [True] * limit
    a[0] = a[1] = False
    for n in range(4, limit, 2):
        a[n] = False
    root_limit = int(limit**.5)+1
    for i in range(3,root_limit):
        if a[i]:
            for n in range(i*i, limit, 2*i):
                a[n] = False
    return a

def generate_primes():
    D = { 9: 3, 25: 5 }
    yield 2
    yield 3
    yield 5
    MASK= 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0,
    MODULOS= frozenset( (1, 7, 11, 13, 17, 19, 23, 29) )

    for q in it.compress(
            it.islice(it.count(7), 0, None, 2),
            it.cycle(MASK)):
        p = D.pop(q, None)
        if p is None:
            D[q*q] = q
            yield q
        else:
            x = q + 2*p
            while x in D or (x%30) not in MODULOS:
                x += 2*p
            D[x] = p

def generate_primes_between(a, b):
    for x in generate_primes():
        if x < a:
            pass
        if a <= x <= b:
            yield x
        if x > b:
            return

ub = 200
for p in generate_primes_between(2, ub):
    for q in generate_primes_between(p, ub):
        for r in generate_primes_between(q, ub):
            if p*q*r == 101*(p+q+r):
                print(p, q, r)