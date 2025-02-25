import math
#1
r = 6
volume = math.pow(5,3) *math.pi*4/3
print('part 1 volume = ',volume)

#2
x = 42
v = math.sin(x) **2 + math.cos(x)**2
print('part 2 =',v)

#3

e_squared_1 = math.e ** 2
print('part 3 (method 1) e^2 =', e_squared_1)


e_squared_2 = math.pow(math.e, 2)
print('part 3 (method 2) e^2 =', e_squared_2)

e_squared_3 = math.exp(2)
print('part 3 (method 3) e^2 =', e_squared_3)