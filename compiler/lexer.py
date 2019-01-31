from dataclasses import dataclass
from enum import Enum, auto
from typing import Union

class LexemeType(Enum):
    KEYWORD = auto()            # get_identifier
    IDENTIFIER = auto()         # get_identifier
    INTEGER_NUMERAL = auto()    # get_numeral
    FLOAT_NUMERAL = auto()      # get_numeral
    OPERATOR = auto()           # get_operator
    BRACKET = auto()            # get_bracket
    NEWLINE = auto()
    EOF = auto()

keywords = ['if']
operators = ['+', '-', '*', '/', '=', '+=', '-=', '*=', '/=', '.', '&&']
brackets = '(){}[]'
whitespaces = ' \n\t\r'

@dataclass
class Lexeme:
    type: LexemeType
    value: Union[None, int, float, str]
    position: int


class LexerError(Exception):
    def __init__(self, arg, position):
        self.message = arg
        self.position = position

class Lexer:
    def __init__(self, code):
        self.code = code
        self.index = 0
        self.lexemes = []


    def parse(self) -> list:
        # TODO: yield
        while self.index < len(self.code):
            c = self.current()

            if c.isdigit():
                self.lexemes.append(self.get_numeral())
            elif c.isalpha() or c == '_':
                self.lexemes.append(self.get_identifier())
            elif c in brackets:
                self.lexemes.append(self.get_bracket())
            # # TODO: whitespaces, comments, quotes, non-numerical dots
            elif c == '\n':
                self.lexemes.append(Lexeme(type=LexemeType.NEWLINE, 
                                           value=None, 
                                           position=self.index))
                self.index += 1
            elif c in whitespaces:
                # TODO: stub!
                self.index += 1
            else:
                self.lexemes.append(self.get_operator())
        self.lexemes.append(Lexeme(type=LexemeType.EOF,
                                   value=None, 
                                   position=self.index))
        return self.lexemes


    def current(self):
        return self.code[self.index]

    # ----------------------------------------- #
    # Parsers for separate lexemes.
    # ----------------------------------------- #

    def get_numeral(self) -> Lexeme:
        result = []
        is_integer = True
        position = self.index

        while self.index < len(self.code):
            c = self.current()
            if c == '.':
                if not is_integer:
                    raise LexerError('cannot parse numeral', self.index)
                is_integer = False
                
            if c.isdigit() or c == '.':
                result.append(c)
                self.index += 1
            
            elif c.isalpha() or c == '_':
                raise LexerError('cannot parse numeral', self.index)
            # TODO : exponential?
            else:
                break

        # numeral is over
        result = ''.join(result)
        if is_integer:
            return Lexeme(type=LexemeType.INTEGER_NUMERAL, 
                          value=int(result), 
                          position=position)
        else:
            return Lexeme(type=LexemeType.FLOAT_NUMERAL, 
                          value=float(result), 
                          position=position)

    
    def get_identifier(self):
        assert not self.current().isdigit()
        result = []
        position = self.index

        while self.index < len(self.code):
            c = self.current()
            if not c.isalpha() and not c.isdigit() and not c == '_':
                break
            result.append(c)
            self.index += 1
            
        result = ''.join(result)
        if result in keywords:
            return Lexeme(type=LexemeType.KEYWORD,
                          value=result, 
                          position=position)
        else:
            return Lexeme(type=LexemeType.IDENTIFIER,
                          value=result, 
                          position=position)


    def get_bracket(self) -> Lexeme:
        result = Lexeme(type=LexemeType.BRACKET, 
                        value=self.current(), 
                        position=self.index)
        self.index += 1
        return result


    def get_operator(self) -> Lexeme:
        size = 1
        is_prefix = True
        candidate = None
        pattern = ''
        position = self.index

        while self.index < len(self.code) and is_prefix:
            is_prefix = False
            pattern += self.current()

            for op in operators:
                if len(op) < size:
                    continue
                if op[:size] == pattern:
                    is_prefix = True
                    if len(op) == size:
                        candidate = op
            size += 1
            self.index += 1

        if candidate is None:
            raise LexerError(f'operator not found', self.index)
        self.index -= (len(pattern) - len(candidate))
        return Lexeme(type=LexemeType.OPERATOR, 
                      value = candidate, 
                      position=position)

# -------------------------------------------

__all__ = ['Lexeme', 'LexemeType', 'LexerError', 'Lexer']

if __name__ == '__main__':
    lexer = Lexer('+')
    result = lexer.parse()
    print (result)