from .lexer import *
import pytest


def test_integers():
    lexer = Lexer('123 4 987 0')
    result = lexer.parse()
    assert result == [Lexeme(type = LexemeType.INTEGER_NUMERAL, value = 123),
                       Lexeme(type = LexemeType.INTEGER_NUMERAL, value = 4),
                       Lexeme(type = LexemeType.INTEGER_NUMERAL, value = 987),
                       Lexeme(type = LexemeType.INTEGER_NUMERAL, value = 0)]


def test_all():
    lexer = Lexer('abc12_3 +=if 31 if4k--5.4)')
    result = lexer.parse()
    assert result == [Lexeme(type = LexemeType.IDENTIFIER, value = 'abc12_3'),
                       Lexeme(type = LexemeType.OPERATOR, value = '+='),
                       Lexeme(type = LexemeType.KEYWORD, value = 'if'),
                       Lexeme(type = LexemeType.INTEGER_NUMERAL, value = 31),
                       Lexeme(type = LexemeType.IDENTIFIER, value = 'if4k'),
                       Lexeme(type = LexemeType.OPERATOR, value = '-'),
                       Lexeme(type = LexemeType.OPERATOR, value = '-'),
                       Lexeme(type = LexemeType.FLOAT_NUMERAL, value = 5.4),
                       Lexeme(type = LexemeType.BRACKET, value = ')')
    ]

@pytest.mark.skip
def teststuff():
    lexer = Lexer('+ \n')
    result = lexer.parse()
