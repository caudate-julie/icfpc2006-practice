from .lexer import *
import pytest


def test_integers():
    lexer = Lexer('123 4 987 0')
    result = lexer.parse()
    assert result == [Lexeme(type = LexemeType.INTEGER_NUMERAL, value = 123),
                       Lexeme(type = LexemeType.INTEGER_NUMERAL, value = 4),
                       Lexeme(type = LexemeType.INTEGER_NUMERAL, value = 987),
                       Lexeme(type = LexemeType.INTEGER_NUMERAL, value = 0)]


@pytest.mark.skip(reason="in progress")
def test_all():
    lexer = Lexer('abc12_3 += 31--5.4)')
    result = lexer.parse()
    assert lexemes == [Lexeme(type = LexemeType.IDENTIFIER, value = 'abc12_3'),
                       Lexeme(type = LexemeType.OPERATOR, value = '+='),
                       Lexeme(type = LexemeType.INTEGER_NUMERAL, value = 31),
                       Lexeme(type = LexemeType.OPERATOR, value = '-'),
                       Lexeme(type = LexemeType.OPERATOR, value = '-'),
                       Lexeme(type = LexemeType.FLOAT_NUMERAL, value = 5.4),
                       Lexeme(type = LexemeType.BRACKET, value = ')')]
