from arithmp.parser import Parser

def test_add():
    parse = Parser().parse
    assert parse(None, "1 + 1") == 2
    assert parse(None, "0 + 3") == 3