from arithmp.parser import Parser

def test_add():
    parse = Parser().parse
    assert parse("1 + 1") == 2
    assert parse("0 + 3") == 3