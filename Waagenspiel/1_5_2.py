import math

for t in range(2, 100000):
    if t/math.log10(t) > 10 * (t * math.log10(t))**0.5:
        print(t)
        break