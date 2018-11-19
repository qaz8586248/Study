import random
import string

code=[]
code.append(random.choice(string.ascii_lowercase))
code.append(random.choice(string.ascii_uppercase))
code.append(random.choice(string.digits))

while len(code)<6:
    code.append(random.choice(string.ascii_uppercase+string.ascii_lowercase+string.digits))

q="".join(code)
print(q)