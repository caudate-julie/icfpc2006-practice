from .lexer import *
import pytest


def test_integers():
    lexer = Lexer('123 4 987 0')
    result = [(x.type, x.value) for x in lexer.parse()]
    assert result == [(LexemeType.INTEGER_NUMERAL, 123),
                      (LexemeType.INTEGER_NUMERAL, 4),
                      (LexemeType.INTEGER_NUMERAL, 987),
                      (LexemeType.INTEGER_NUMERAL, 0),
                      (LexemeType.EOF, None)]


def test_all():
    lexer = Lexer('abc12_3 +=if 31 if4k--\n5.4)')
    result = [(x.type, x.value) for x in lexer.parse()]
    assert result == [(LexemeType.IDENTIFIER, 'abc12_3'),
                       (LexemeType.OPERATOR, '+='),
                       (LexemeType.KEYWORD, 'if'),
                       (LexemeType.INTEGER_NUMERAL, 31),
                       (LexemeType.IDENTIFIER, 'if4k'),
                       (LexemeType.OPERATOR, '-'),
                       (LexemeType.OPERATOR, '-'),
                       (LexemeType.NEWLINE, None),
                       (LexemeType.FLOAT_NUMERAL, 5.4),
                       (LexemeType.BRACKET, ')'),
                       (LexemeType.EOF, None)]


def test_endings():
    lexer = Lexer('1 2')
    result = [(x.type, x.value) for x in lexer.parse()]
    assert result[-2] == (LexemeType.INTEGER_NUMERAL, 2)

    lexer = Lexer('1 abc')
    result = [(x.type, x.value) for x in lexer.parse()]
    assert result[-2] == (LexemeType.IDENTIFIER, 'abc')

    lexer = Lexer('1 3.')
    result = [(x.type, x.value) for x in lexer.parse()]
    assert result[-2] == (LexemeType.FLOAT_NUMERAL, 3.0)

    lexer = Lexer('(1 2)')
    result = [(x.type, x.value) for x in lexer.parse()]
    assert result[-2] == (LexemeType.BRACKET, ')')

    lexer = Lexer('1+=')
    result = [(x.type, x.value) for x in lexer.parse()]
    assert result[-2] == (LexemeType.OPERATOR, '+=')

    lexer = Lexer('1+=\n')
    result = [(x.type, x.value) for x in lexer.parse()]
    assert result[-2] == (LexemeType.NEWLINE, None)


def test_position():
    s = 'a+b_1\n(45.6'
    lexer = Lexer(s)
    r = lexer.parse()
    assert s[r[0].position : r[0].position + 1] == 'a'
    assert s[r[1].position : r[1].position + 1] == '+'
    assert s[r[2].position : r[2].position + len('b_1')] == 'b_1'
    assert s[r[3].position : r[3].position + 1] == '\n'
    assert s[r[4].position : r[4].position + 1] == '('
    assert s[r[5].position : r[5].position + len('45.6')] == '45.6'
    
    


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

