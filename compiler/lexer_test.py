from .lexer import *
import pytest


def test_integers():
    lexer = Lexer('123 4 987 0')
    result = lexer.parse()
    assert result == [Lexeme(type = LexemeType.INTEGER_NUMERAL, value = 123),
                       Lexeme(type = LexemeType.INTEGER_NUMERAL, value = 4),
                       Lexeme(type = LexemeType.INTEGER_NUMERAL, value = 987),
                       Lexeme(type = LexemeType.INTEGER_NUMERAL, value = 0),
                       Lexeme(type = LexemeType.EOF, value = None)]


def test_all():
    lexer = Lexer('abc12_3 +=if 31 if4k--\n5.4)')
    result = lexer.parse()
    assert result == [Lexeme(type = LexemeType.IDENTIFIER, value = 'abc12_3'),
                       Lexeme(type = LexemeType.OPERATOR, value = '+='),
                       Lexeme(type = LexemeType.KEYWORD, value = 'if'),
                       Lexeme(type = LexemeType.INTEGER_NUMERAL, value = 31),
                       Lexeme(type = LexemeType.IDENTIFIER, value = 'if4k'),
                       Lexeme(type = LexemeType.OPERATOR, value = '-'),
                       Lexeme(type = LexemeType.OPERATOR, value = '-'),
                       Lexeme(type = LexemeType.NEWLINE, value = None),
                       Lexeme(type = LexemeType.FLOAT_NUMERAL, value = 5.4),
                       Lexeme(type = LexemeType.BRACKET, value = ')'),
                       Lexeme(type = LexemeType.EOF, value = None)]

def test_endings():
    lexer = Lexer('1 2')
    result = lexer.parse()
    assert result[-2] == Lexeme(type = LexemeType.INTEGER_NUMERAL, value = 2)

    lexer = Lexer('1 abc')
    result = lexer.parse()
    assert result[-2] == Lexeme(type = LexemeType.IDENTIFIER, value = 'abc')

    lexer = Lexer('1 3.')
    result = lexer.parse()
    assert result[-2] == Lexeme(type = LexemeType.FLOAT_NUMERAL, value = 3.0)

    lexer = Lexer('(1 2)')
    result = lexer.parse()
    assert result[-2] == Lexeme(type = LexemeType.BRACKET, value = ')')

    lexer = Lexer('1+=')
    result = lexer.parse()
    assert result[-2] == Lexeme(type = LexemeType.OPERATOR, value = '+=')

    lexer = Lexer('1+=\n')
    result = lexer.parse()
    assert result[-2] == Lexeme(type = LexemeType.NEWLINE, value = None)


def test_errors():
    lexer = Lexer('1abc')
    with pytest.raises(LexerError, match='cannot parse numeral'):
        lexer.parse()
    
    lexer = Lexer('1.2.3')
    with pytest.raises(LexerError, match='cannot parse numeral'):
        lexer.parse()
    
    lexer = Lexer('a & b')
    with pytest.raises(LexerError, match='operator not found'):
        lexer.parse()

