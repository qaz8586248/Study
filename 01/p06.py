s1 = {1,2,3,4,5,6}
s2 = {5,6,7,8,9}
print(id(s1))
print(s1)

s_1 = s1.intersection(s2)
print(s_1)

s_2 = s1.difference(s2)
print(s_2)

s_3 = s1.issubset(s2)
print(s_3)

s_4 = s1.difference_update(s2)
print(s1)
print(id(s1))