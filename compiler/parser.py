from .lexer import *
from .grammar import *

from dataclasses import dataclass
from typing import Any, Optional, List


@dataclass
class ASTNode:
    lexeme: Lexeme
    # level: int
    starts: int
    ends: int
    
    @property
    def value(self):
        return self.lexeme.value

    @staticmethod
    def get_bounds(lex: Lexeme, *children):
        start = min(lex.starts, *(x.starts for x in children))
        end = max(lex.ends, *(x.ends for x in children))
        return (start, end)


@dataclass
class ASTLeaf(ASTNode):
    # no additional fields

    @classmethod
    def from_lexeme(self, lex: Lexeme):
        return ASTLeaf(lexeme=lex, starts=lex.starts, ends=lex.ends)

    def unparse(self):
        return str(self.value)


@dataclass
class ASTUnary(ASTNode):
    child: ASTNode = None

    @classmethod
    def from_lexeme(cls, lex: Lexeme, child):
        starts, ends = ASTNode.get_bounds(lex, child)
        return ASTUnary(lexeme=lex, starts=starts, ends=ends, child=child)

    def unparse(self):
        child_exp = self.child.unparse()
        if lower_precedence(self.child.value, self.value):
            child_exp = '(' + child_exp + ')'
        return self.value + ' ' + child_exp  


@dataclass
class ASTBinary(ASTNode):
    left: ASTNode
    right: ASTNode

    @classmethod
    def from_lexeme(cls, lex: Lexeme, left, right):
        start, end = ASTNode.get_bounds(lex, left, right)
        return ASTBinary(lexeme=lex, starts=start, ends=end, left=left, right=right)

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


@dataclass
class ASTBlock(ASTNode):
    expressions: List[ASTNode]
    terminated: bool

    # @classmethod
    # def from_lexeme(cls, lex: Lexeme, ....):
    #     start, end = ASTNode.get_bounds(lex, ...)
    #     return AST...(lexeme=lex, starts=start, ends=end, ....)


@dataclass
class ASTConditional(ASTNode):
    condition: ASTNode
    true_block: ASTBlock
    false_block: ASTBlock

    # @classmethod
    # def from_lexeme(cls, lex: Lexeme, ....):
    #     start, end = ASTNode.get_bounds(lex, ...)
    #     return AST...(lexeme=lex, starts=start, ends=end, ....)


@dataclass
class ASTCall(ASTNode):
    called: ASTNode
    arguments: List[ASTNode]

    # @classmethod
    # def from_lexeme(cls, lex: Lexeme, ....):
    #     start, end = ASTNode.get_bounds(lex, ...)
    #     return AST...(lexeme=lex, starts=start, ends=end, ....)


@dataclass
class ASTField(ASTNode):
    obj: ASTNode

    # @classmethod
    # def from_lexeme(cls, lex: Lexeme, ....):
    #     start, end = ASTNode.get_bounds(lex, ...)
    #     return AST...(lexeme=lex, starts=start, ends=end, ....)

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
        # self.ast = None 

    def peek(self):
        # assert self.index < len(self.lexemes)
        return self.lexemes[self.index]
    
    def take(self):
        # assert self.index < len(self.lexemes)
        self.index += 1
        return self.lexemes[self.index - 1]
    
    # def is_current_level_operator(self, level):
    #     return self.peek().type == LexemeType.OPERATOR \
    #         and self.peek().value in operator_levels[level]
    
    # ----------------------------------------- #
    # Parse!
    # ----------------------------------------- #

    def parse(self):
        return parse_assignment(self)
    
# ----------------------------------------- #
# Parsers for separate levels.
# ----------------------------------------- #


def parse_binary(parser, operators, next_level):
    ast = next_level(parser)
    while parser.peek().type is LexemeType.OPERATOR and parser.peek().value in operators:
        ast_left = ast
        lex = parser.take()
        ast_right = next_level(parser)
        ast = ASTBinary.from_lexeme(lex, ast_left, ast_right)
    
    return ast
    # exception if no operand for operator    

def parse_assignment(parser):
    return parse_binary(parser, ['='], parse_arithmetics_low)
    
def parse_arithmetics_low(parser):
    return parse_binary(parser, ['+', '-'], parse_arithmetics_high)

def parse_arithmetics_high(parser):
    return parse_binary(parser, ['*', '/'], parse_atom)


# TERM = <numeral> | <identifier> | (SUMMATION)
def parse_atom(parser):
    lex = parser.take()
    if lex.type == LexemeType.BRACKET:
        if lex.value != '(':
            raise NotImplementedError()

        leaf = parse_arithmetics_low(parser)
        lex = parser.take()
        if lex.type != LexemeType.BRACKET or lex.value != ')':
            raise ParserError('closing bracket not found', parser.index)
        return leaf

    return ASTLeaf.from_lexeme(lex)




    # def parse_binary(self, level):
    #     if level == len(operator_levels):
    #         return self.parse_atom()

    #     ast = self.parse_binary(level + 1)

    #     while self.peek().value in operator_levels[level]:
    #         ast_left = ast
    #         node = self.take()
    #         ast_right = self.parse_binary(level + 1)
    #         ast = ASTBinary.from_lexeme(node)
    #         ast.left = ast_left
    #         ast.right = ast_right  # !!! TODO
        
    #     return ast
    # exception - no operand for binary operator


    # # TERM = <numeral> | <identifier> | (SUMMATION)
    # def parse_atom(self):
    #     assert self.index < len(self.lexemes)

    #     lex = self.take()
    #     if lex.type == LexemeType.BRACKET:
    #         if lex.value != '(':
    #             raise NotImplementedError()

    #         leaf = self.parse_binary(0)
    #         lex = self.take()
    #         if lex.type != LexemeType.BRACKET or lex.value != ')':
    #             raise ParserError('closing bracket not found', self.index)
    #         return leaf

    #     return ASTLeaf.from_lexeme(lex)



if __name__ == '__main__':
    s = 'y = (26 + 5) * x'
    lexemes = Lexer(s).parse()
    print(lexemes)
    ast = Parser(lexemes).parse()
    print(ast)
    print(ast.unparse())