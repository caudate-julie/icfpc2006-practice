from lexer import *
from terminals import *

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class ASTNode:
    value: Any
    position: int
    
    @classmethod
    def from_lexeme(cls, x: Lexeme):
        return cls(value = x.value, position = x.position)

    # Both methods return a new tree with current tree as
    # left/right child; current tree, if new root is None
    def sink_left(self, root: Optional['ASTBinary']):
        if root is None:
            return self
        root.left = self
        return root
    
    def sink_right(self, root: Optional['ASTBinary']):
        if root is None:
            return self
        root.right = self
        return root

@dataclass
class ASTBinary(ASTNode):
    left: ASTNode = None
    right: ASTNode = None

@dataclass
class ASTUnary(ASTNode):
    child: ASTNode = None

@dataclass
class ASTLeaf(ASTNode):
    pass

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
        return self.lexemes[self.index]
    
    def take(self):
        self.index += 1
        return self.lexemes[self.index - 1]
    
    def is_current_level_operator(self, level):
        return self.peek().type == LexemeType.OPERATOR \
            and self.peek().value in operator_levels[level]
    
    # ----------------------------------------- #
    # Parse!
    # ----------------------------------------- #

    def parse(self):
        return self.parse_binary(0)
    
    # ----------------------------------------- #
    # Parsers for separate levels.
    # ----------------------------------------- #

    def parse_binary(self, level):
        assert self.index < len(self.lexemes)
        ast = None

        while self.peek().type != LexemeType.EOF:
            if level == len(operator_levels):
                return self.parse_atom()

            term = self.parse_binary(level + 1)
            ast = term.sink_right(ast)

            if self.peek().value not in operator_levels[level]:
                return ast
            
            node = ASTBinary.from_lexeme(self.take())
            ast = ast.sink_left(node)


    # TERM = <numeral> | <identifier> | (SUMMATION)
    def parse_atom(self):
        assert self.index < len(self.lexemes)

        lex = self.take()
        if lex.type == LexemeType.BRACKET:
            if lex.value != '(':
                raise NotImplementedError()

            leaf = self.parse_binary(0)
            lex = self.take()
            if lex.type != LexemeType.BRACKET or lex.value != ')':
                raise ParserError('closing bracket not found', self.index)
            return leaf

        return ASTLeaf.from_lexeme(lex)


if __name__ == '__main__':
    s = 'y = 26 + 5 * x'
    lexemes = Lexer(s).parse()
    print(lexemes)
    ast = Parser(lexemes).parse()
    print(ast)