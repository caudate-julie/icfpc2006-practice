from .lexer import *
from .grammar import *

from dataclasses import dataclass
from typing import Any, Optional, List

def default_printer(ast): return ''


@dataclass
class ASTNode:
    # level: int
    starts: int
    ends: int
    
    def show(self, printer=default_printer, depth=0):
        raise NotImplementedError()


@dataclass
class ASTLeaf(ASTNode):
    # no additional fields

    @staticmethod
    def create(lex: Lexeme):
        if lex.type == LexemeType.INTEGER_NUMERAL:
            return ASTIntNumeral.create(lex)
        if lex.type == LexemeType.FLOAT_NUMERAL:
            return ASTFloatNumeral.create(lex)
        # if lex.type == LexemeType.BOOL_NUMERAL:
        #     return ASTBoolNumeral.create(lex)
        if lex.type == LexemeType.IDENTIFIER:
            return ASTIdentifier.create(lex)
        assert False, lex.type

    def unparse(self):
        # TODO: distinguish string literal from everything else
        return str(self.value)

    def show(self, printer=default_printer, depth=0):
        offset = ' ' * (depth * 2)
        return offset + f'Leaf {self.value}' + printer(self) + '\n'


@dataclass
class ASTIntNumeral(ASTLeaf):
    value: int

    @staticmethod
    def create(lex: Lexeme):
        assert lex.type == LexemeType.INTEGER_NUMERAL
        return ASTIntNumeral(value=lex.value, starts=lex.starts, ends=lex.ends)

@dataclass
class ASTFloatNumeral(ASTLeaf):
    value: float

    @staticmethod
    def create(lex: Lexeme):
        assert lex.type == LexemeType.FLOAT_NUMERAL
        return ASTFloatNumeral(value=lex.value, starts=lex.starts, ends=lex.ends)

@dataclass
class ASTBoolNumeral(ASTLeaf):
    value: bool

    @staticmethod
    def create(lex: Lexeme):
        assert lex.type == LexemeType.BOOL_NUMERAL
        return ASTBoolNumeral(value=lex.value, starts=lex.starts, ends=lex.ends)

@dataclass
class ASTIdentifier(ASTLeaf):
    value: str

    @staticmethod
    def create(lex: Lexeme):
        assert lex.type == LexemeType.IDENTIFIER
        return ASTIdentifier(value=lex.value, starts=lex.starts, ends=lex.ends)


@dataclass
class ASTUnary(ASTNode):
    value: str
    child: ASTNode = None

    @staticmethod
    def create(lex: Lexeme, child):
        starts = min(lex.starts, child.starts)
        ends = min(lex.ends, child.ends)
        return ASTUnary(value=lex.value, starts=starts, ends=ends, child=child)

    def unparse(self):
        child_exp = self.child.unparse()
        if lower_precedence(self.child.value, self.value):
            child_exp = '(' + child_exp + ')'
        return self.value + ' ' + child_exp  

    def show(self, printer=default_printer, depth=0):
        offset = ' ' * (depth * 2)
        return offset + f'Unary {self.value}' + printer(self) + '\n' \
             + self.child.show(printer, depth + 1)


@dataclass
class ASTBinary(ASTNode):
    value: str
    left: ASTNode
    right: ASTNode

    @staticmethod
    def create(lex: Lexeme, left, right):
        return ASTBinary(value=lex.value, starts=left.starts, ends=right.ends, left=left, right=right)

    def unparse(self):
        left_exp = self.left.unparse()
        right_exp = self.right.unparse()
        # TODO: associativity
        # TODO: unary
        if isinstance(self.left, ASTBinary) and level(self.left.value) < level(self.value):
            left_exp = '(' + left_exp + ')'
        if isinstance(self.right, ASTBinary) and level(self.right.value) < level(self.value):
            right_exp = '(' + right_exp + ')'
        return left_exp + ' ' + self.value + ' ' + right_exp

    def show(self, printer=default_printer, depth=0):
        offset = ' ' * (depth * 2)
        return offset + f'Binary {self.value}' + printer(self) + '\n' \
             + self.left.show(printer, depth + 1) + self.right.show(printer, depth + 1)


@dataclass
class ASTBlock(ASTNode):
    expressions: List[ASTNode]
    terminated: bool

    # @staticmethod
    # def create(lex: Lexeme, ....):
    #     start, end = ASTNode.get_bounds(lex, ...)
    #     return AST...(lexeme=lex, starts=start, ends=end, ....)

    # @staticmethod
    # def get_bounds(lex: Lexeme, *children):
    #     start = min(lex.starts, *(x.starts for x in children))
    #     end = max(lex.ends, *(x.ends for x in children))
    #     return (start, end)


    def show(self, printer=default_printer, depth=0):
        offset = ' ' * (depth * 2)
        return offset + 'Block' + printer() + '\n' \
             + ''.join(x.show(printer, depth + 1) for x in self.expressions)


@dataclass
class ASTConditional(ASTNode):
    condition: ASTNode
    true_block: ASTBlock
    false_block: ASTBlock

    # @staticmethod
    # def create(lex: Lexeme, ....):
    #     start, end = ASTNode.get_bounds(lex, ...)
    #     return AST...(lexeme=lex, starts=start, ends=end, ....)

    def show(self, depth=0):
        offset = ' ' * (depth * 2)
        return offset + 'if' + printer(self) + '\n' + self.condition.show(printer, depth + 1) \
             + offset + 'then\n' + self.true_block.show(printer, depth + 1) \
             + offset + 'else\n' + self.false_block.show(printer, depth + 1)


@dataclass
class ASTCall(ASTNode):
    called: ASTNode
    arguments: List[ASTNode]

    # @staticmethod
    # def create(lex: Lexeme, ....):
    #     start, end = ASTNode.get_bounds(lex, ...)
    #     return AST...(lexeme=lex, starts=start, ends=end, ....)

    def show(self, depth=0):
        offset = ' ' * (depth * 2)
        return offset + 'Call ' + self.value + closing(self.value) + printer(self) + '\n' \
               + self.called.show(printer, depth + 1) \
               + ''.join(x.show(printer, depth + 1) for x in self.arguments) \


@dataclass
class ASTField(ASTNode):
    obj: ASTNode
    identifier: str

    # @staticmethod
    # def create(lex: Lexeme, ....):
    #     start, end = ASTNode.get_bounds(lex, ...)
    #     return AST...(lexeme=lex, starts=start, ends=end, ....)

    def show(self, depth=0):
        offset = ' ' * (depth * 2)
        return offset + 'Field access' + printer(self) + '\n' \
             + obj.show(printer, depth + 1) \
             + offset + f'.{self.value}\n'

# --------------------------------------------- #

class ParserError(Exception):
    def __init__(self, arg, position):
        self.message = arg
        self.position = position

# --------------------------------------------- #

class Parser:
    def __init__(self, lexemes):
        self.lexemes = lexemes
        self.index = 0

    def peek(self):
        # assert self.index < len(self.lexemes)
        return self.lexemes[self.index]
    
    def take(self):
        # assert self.index < len(self.lexemes)
        self.index += 1
        return self.lexemes[self.index - 1]
    
    def parse(self):
        return parse_assignment(self)
    
# ----------------------------------------- #
# Parsers for separate levels.
# ----------------------------------------- #

# General binary parser
def parse_binary(parser, operators, next_level):
    ast = next_level(parser)
    while parser.peek().type is LexemeType.OPERATOR and parser.peek().value in operators:
        ast_left = ast
        lex = parser.take()
        ast_right = next_level(parser)
        ast = ASTBinary.create(lex, ast_left, ast_right)
    
    return ast
    # exception if no operand for operator

# def parse_block(parser):
#     left = parser.take()
#     if left.type != LexemeType.BRACKET or left.value != '{':
#         raise ParserError('Block without opening bracket', left.starts)

    # ast = next_level(parser)
    # while parser.peek().type is LexemeType.OPERATOR and parser.peek().value in operators:
    #     ast_left = ast
    #     lex = parser.take()
    #     ast_right = next_level(parser)
    #     ast = ASTBinary.create(lex, ast_left, ast_right)
    
    # return ast

def parse_assignment(parser):
    return parse_binary(parser, ['='], parse_arithmetics_low)
    
def parse_arithmetics_low(parser):
    return parse_binary(parser, ['+', '-'], parse_arithmetics_high)

def parse_arithmetics_high(parser):
    return parse_binary(parser, ['*', '/'], parse_unary)

def parse_unary(parser):
    operators = ['+', '-']
    lex = parser.peek()
    if lex.type == LexemeType.OPERATOR and lex.value in operators:
        parser.take()
    else:
        lex = None
    
    ast = parse_atom(parser)
    if lex is not None:
        ast = ASTUnary.create(lex, ast)
    return ast

# TERM = <numeral> | <identifier> | (SUMMATION)
def parse_atom(parser):
    lex = parser.take()
    if lex.type == LexemeType.EOF:
        raise ParserError('Unexpected EOF reached', parser.index)

    if lex.type == LexemeType.BRACKET:
        if lex.value != '(':
            raise NotImplementedError()

        leaf = parse_arithmetics_low(parser)
        lex = parser.take()
        if lex.type != LexemeType.BRACKET or lex.value != ')':
            raise ParserError('Closing bracket not found', parser.index)
        return leaf

    if not lex.type.is_term():
        raise ParserError('Unexpected type of lexeme', parser.index)

    return ASTLeaf.create(lex)


if __name__ == '__main__':
    s = 'y = (26 + 5) * x'
    lexemes = Lexer(s).parse()
    print(lexemes)
    ast = Parser(lexemes).parse()
    print(ast)
    print(ast.show())
    print(ast.unparse())