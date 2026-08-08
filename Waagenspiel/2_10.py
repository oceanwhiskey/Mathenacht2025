
s = 18*18
f = 8/9
ds = s*f


c = (1.0-(8/9)**(100+1)) / (1.0-(8/9))
print(c*s)

for i in range(1, 10000):
    s, ds = s+ds, ds*f
    if s < i:
        print(i, s)
        break
else:
    print(s)



 