def sanjiao(x):
    for i in range(x):
        for j in range(x-i):
            print(" ",end="")
        for k in range(i+1):
            print("* ",end="")
        print()

sanjiao(8)