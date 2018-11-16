def sanjiao(x):
    for i in range(x):
        if i==0 or i==1 or i==x-1:
            for j in range(i+1):
                print("*",end=" ")
            print()
        else:
            for j in range(i+1):
                if j==0 or j==i:
                    print("*",end=" ")
                else:
                    print(" ",end=" ")
            print()
sanjiao(5)
