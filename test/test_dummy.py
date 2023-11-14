from source/dummy import Dummy

def test_addition():
    y=Dummy.add(3,8)
    assert(y==11)

def test_square_nat():
    y = Dummy.square_nat(37)
    assert(y == 37*37)
