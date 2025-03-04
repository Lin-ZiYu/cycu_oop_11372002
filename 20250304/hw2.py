def gcd(a, b):
    if b == 0:
        return a
    else:
        return gcd(b, a % b)


x = 11
y = 121
print(f"{x} 和 {y} 的最大公因數是 {gcd(x, y)}")