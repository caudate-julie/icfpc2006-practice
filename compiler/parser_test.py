from .parser import *
import pytest


def test_smoke():
    s = 'y = (26 + 5) * x'
    lexemes = Lexer(s).parse()
    ast = Parser(lexemes).parse()
    assert ast.value == '='


@pytest.mark.xfail(reason='Waiting for todo-ed start and end recomputation')
def test_starts_ends():
    s = 'y = (26 + 5) * x'
    ast = Parser(Lexer(s).parse()).parse()
    assert ast.starts == 0
    assert ast.ends == len(s)
    assert ast.right.starts == 4
    assert ast.right.ends == len(s)
