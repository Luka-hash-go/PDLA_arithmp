from arithmp.parser import Parser

def test_add():
    parse = Parser().parse
    assert parse(None, "1 + 1") == 2
    assert parse(None, "0 + 3") == 3

def test_variable_assignement():
    parse = Parser().parse
    #test pour assignation variables

    assert parse(None,"a = 4") == 4

    # test reutilisation var

    assert parse(None, "a + 6") == 10

    #test reassignation

    assert parse(None,"a = a * 2") == 8

def test_fonction_call():
    parse = Parser().parse

    #test fonction abs
    assert parse(None,"abs(-4)") == 4

    #test fonction round

    assert parse(None,"round(2.7)") == 3

    #test avec plusieurs arg

    assert parse(None,"max(10,20)")  == 20 