import sys
class Dummy:


    def __init__(self):
        return 

    
    def add(a,b):
        return a+b


    def square_nat(a):
        res = 0
        for i in range(0,a):
            res += i + (i+1)
        return res


print(Dummy.square_nat(5))
print(sys.executable)