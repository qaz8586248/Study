import pickle

#a = [102, 'liudan3ab', "i loves wangxiaojing", [185, 80]]

#with open(r'test01.txt', 'ab') as f:
#    pickle.dump(a, f)

#with open(r'test01.txt', 'rb') as f:
#    a  = pickle.load(f)
#    print(a)
#    b = pickle.load(f)
#    print(b)

with open(r'test01.txt', 'rb') as f:
    while True:
        try:
            print(pickle.load(f))
        except Exception as e:
            break