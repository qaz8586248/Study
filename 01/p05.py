def digui(num):
    print('$'+str(num))
    if num>0:
        digui(num-1)
    else:
        print("="*20)
    print(num)

digui(4)