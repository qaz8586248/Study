f=open('test')
content=[]

for lines in f:
    content.append(lines)

print(content)
s="".join(content)
print(s)

f.close()

