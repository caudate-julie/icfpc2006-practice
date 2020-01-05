from .parser import *
from .precommands import *

from typing import List
from functools import singledispatch

free_registers = [True] * 8
class NoFreeRegisterError(Exception):
    def __init__(self):
        self.message = 'no available registers'


def get_free_register():
    if not any(free_registers):
        raise NoFreeRegisterError()

    i = free_registers.index(True)
    free_registers[i] = False
    return i


@singledispatch
def get_precommand(ast: ASTNode):
    raise NotImplementedError()


@get_precommand.register
def _(ast: ASTLeaf):
    index = get_free_register()
    return [OrthographyCmd(index, ast.value)]


@get_precommand.register
def _(ast: ASTBinary) -> List[PreCommand]:
    commands_left = get_precommand(ast.left)
    commands_right = get_precommand(ast.right)

    A = get_free_register()
    B = commands_left[-1].result
    C = commands_right[-1].result
    if ast.value == '+':
        cmd = AdditionCmd(A, B, C)
    elif ast.value == '*':
        cmd = MultiplicationCmd(A, B, C)
    else:
        assert False, ast.value

    free_registers[B] = free_registers[C] = True
    return commands_left + commands_right + [cmd]


def wrap_in_print(insns):
    return insns + [OutputCmd(insns[-1].result)]


if __name__ == '__main__':
    s = '(26 + 5) * 2'
    ast = Parser(Lexer(s).parse()).parse()
    for insn in wrap_in_print(get_precommand(ast)):
        print (insn)