from dummy import Dummy
from wikidataquery import WikidataQuery

def test_addition():
    y=Dummy.add(3,8)
    assert(y==11)

def test_square_nat():
    y = Dummy.square_nat(37)
    assert(y == 37*37)

def test_query():
    assert(True)
