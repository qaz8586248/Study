def sanjiao(x):
    for i in range(x+1):
        for j in range(x+1-i):
            print("*",end=" ")
        print()

sanjiao(10)