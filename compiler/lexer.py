from collections import namedtuple
from enum import Enum, auto

class LexemeType(Enum):
    KEYWORD = auto()            # get_identifier
    IDENTIFIER = auto()         # get_identifier
    INTEGER_NUMERAL = auto()    # get_numeral
    FLOAT_NUMERAL = auto()      # get_numeral
    OPERATOR = auto()           # get_operator
    BRACKET = auto()            # get_bracket

keywords = ['if']
operators = ['+', '-', '*', '/', '=', '+=', '-=', '*=', '/=']
brackets = '(){}[]'
Lexeme = namedtuple('Lexeme', ['type', 'value'])

class LexerError(Exception):
    def __init__(self, arg):
        self.message = arg

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
            elif c == ' ':
                # TODO: stub!
                self.index += 1
            else:
                self.lexemes.append(self.get_operator())
        return self.lexemes


    def current(self):
        return self.code[self.index]

    # ----------------------------------------- #
    # Parsers for separate lexemes.
    # ----------------------------------------- #

    def get_numeral(self) -> Lexeme:
        result = []
        is_integer = True

        while self.index < len(self.code):
            c = self.current()
            if c == '.':
                if not is_integer:
                    raise LexerError(f'Cannot parse second point in {"".join(result)}.')
                is_integer = False
                
            if c.isdigit() or c == '.':
                result.append(c)
                self.index += 1
                        
            # TODO : exponential?
            else:
                break

        # numeral is over
        result = ''.join(result)
        if is_integer:
            return Lexeme(type=LexemeType.INTEGER_NUMERAL, value=int(result))
        else:
            return Lexeme(type=LexemeType.FLOAT_NUMERAL, value=float(result))

    
    def get_identifier(self):
        assert not self.current().isdigit()
        result = []

        while self.index < len(self.code):
            c = self.current()
            if not c.isalpha() and not c.isdigit() and not c == '_':
                break
            result.append(c)
            self.index += 1
            
        result = ''.join(result)
        if result in keywords:
            return Lexeme(type=LexemeType.KEYWORD, value=result)
        else:
            return Lexeme(type=LexemeType.IDENTIFIER, value=result)


    def get_bracket(self) -> Lexeme:
        result = Lexeme(type=LexemeType.BRACKET, value=self.current())
        self.index += 1
        return result


    def get_operator(self) -> Lexeme:
        size = 1
        is_prefix = True
        candidate = None
        pattern = ''

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
            raise LexerError(f'no operator matches {pattern!r}')
        self.index -= (len(pattern) - len(candidate))
        return Lexeme(type=LexemeType.OPERATOR, value = candidate)

# -------------------------------------------

if __name__ == '__main__':
    lexer = Lexer('+')
    result = lexer.parse()
    print (result)