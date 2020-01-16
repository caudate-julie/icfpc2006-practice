from .parser import *
import pytest
from textwrap import dedent


def test_arithmetics():
    s = '(26 + xyz) * (a3 + 4 * 6)'
    expected = dedent('''\
        Binary *
          Binary +
            Leaf 26
            Leaf xyz
          Binary +
            Leaf a3
            Binary *
              Leaf 4
              Leaf 6
        ''')
    lexemes = Lexer(s).parse()
    ast = parse_arithmetics_low(Parser(lexemes))
    assert ast.show() == expected, ast.show()


def test_unary():
    s = '-x * +5 - 3'
    expected = dedent('''\
        Binary -
          Binary *
            Unary -
              Leaf x
            Unary +
              Leaf 5
          Leaf 3
        ''')
    lexemes = Lexer(s).parse()
    ast = parse_arithmetics_low(Parser(lexemes))
    assert ast.show() == expected, '\n' + ast.show()


def test_smoke():
    s = 'y = (26 + 5) * x'
    lexemes = Lexer(s).parse()
    ast = Parser(lexemes).parse()
    assert ast.value == '='

def test_parser_errors():
    testcases = ['y = 6 *',
                 'z = 6 + * 7',
                 '3 = / 2',
                 ' 6 = = 3',
                 '+'
                #  'a += b += c',
                #  'a.(a + 2)',
                #  'a.123'
                ]

    for s in testcases:
        lexemes = Lexer(s).parse()
        with pytest.raises(ParserError):
            ast = Parser(lexemes).parse()


@pytest.mark.xfail(reason='Bracket problem')
def test_starts_ends():
    s = 'y = (26 + 5) * x'
    ender = (lambda x: str((x.starts, x.ends)))
    ast = Parser(Lexer(s).parse()).parse()
    assert ast.starts == 0
    assert ast.ends == len(s)
    assert ast.right.starts == 4, ast.show(ender)
    assert ast.right.ends == len(s)
