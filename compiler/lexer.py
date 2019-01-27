from collections import namedtuple
from enum import Enum, auto

class LexemeType(Enum):
    KEYWORD = auto()            # get_identifier
    IDENTIFIER = auto()         # get_identifier
    INTEGER_NUMERAL = auto()    # get_numeral
    FLOAT_NUMERAL = auto()      # get_numeral
    OPERATOR = auto()           # get_operator
    BRACKET = auto()            # get_bracket

keywords = []
operators = ['+', '-', '*', '/', '=', '+=', '-=', '*=', '/=']
brackets = '(){}[]'
Lexeme = namedtuple('Lexeme', ['type', 'value'])

class LexerError(Exception):
    def __init__(self, arg):
        self.args = arg

class Lexer:
    def __init__(self, code):
        self.code = code
        self.index = 0
        self.lexemes = []


    def parse(self) -> list:
        # TODO: yield
        while self.index < len(self.code):
            c = self.code[self.index]

            if c.isdigit():
                self.lexemes.append(self.get_numeral())
            # elif c.isalpha() or c == '_':
            #     index = get_identifier(s, index, lexemes)
            # elif c in brackets:
            #     index = get_bracket(s, index, lexemes)
            # elif c in operators:
            #     index = get_operator(s, index, lexemes)
            # # TODO: whitespaces, comments, quotes, non-numerical dots
            elif c == ' ':
                # TODO: stub!
                self.index += 1
            else:
                print(self.lexemes)
                assert False, s[index]
        return self.lexemes


    def get_numeral(self) -> Lexeme:
        result = []
        is_integer = True

        while self.index < len(self.code):
            c = self.code[self.index]
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


# identifier so far : letter or _, then letters, numbers or _.
# def get_identifier(s: str, index: int, lexemes) -> int:
#     assert not s[index].isdigit()
#     result = []
#     while index < len(s):
#         c = s[index]
#         if not c.isalpha() and not c.isdigit() and not c == '_':
#             break
#         result.append(c)
#         index += 1
        
#     result = ''.join(result)
#     if result in keywords:
#         lexemes.append(Lexeme(type=LexemeType.KEYWORD,
#                                 value=result))
#     else:
#         lexemes.append(Lexeme(type=LexemeType.IDENTIFIER,
#                                 value=result))
#     return index


# def get_bracket(s: str, index: int, lexemes) -> int:
#     assert index < len(s)
#     lexemes.append(Lexeme(type=LexemeType.BRACKET, value=s[index]))
#     return index + 1


# def get_operator(s: str, index: int, lexemes) -> int:
#     size = 1
#     has_matches = True
#     candidate = None
#     while index + size < len(s) and has_matches:
#         has_matches = False
#         pattern = s[index : index+size]
#         for op in operators:
#             if len(op) < size: continue
#             if op[:size] == pattern:
#                 has_matches = True
#             if len(op) == size:
#                 candidate = op
#         size += 1
#     if candidate is None:
#         raise LexerError(f'no operator matches { pattern }')
#     lexemes.append(Lexeme(type=LexemeType.OPERATOR, value = pattern))
#     return index + size

# -------------------------------------------

if __name__ == '__main__':
    s = 'abc12_3 += 31--5.4)'
    lexemes = lexer_pass(s)
    print (lexemes)