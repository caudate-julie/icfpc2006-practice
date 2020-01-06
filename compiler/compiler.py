from .parser import *
from . import asm

from typing import List
from functools import singledispatch


class NoFreeRegisterError(Exception):
    def __init__(self):
        self.message = 'no available registers'

class Context:
    def __init__(self):
        self.registers = [True] * 8

    def get_register(self):
        if not any(self.registers):
            raise NoFreeRegisterError()
        i = self.registers.index(True)
        self.registers[i] = False
        return i


@singledispatch
def get_asm_insn(ast: ASTNode, context: Context):
    raise NotImplementedError()


@get_asm_insn.register
def _(ast: ASTLeaf, context: Context):
    index = context.get_register()
    return [asm.OrthographyInsn(index, ast.value)]


@get_asm_insn.register
def _(ast: ASTBinary, context: Context) -> List[asm.AsmInsn]:
    insns_left = get_asm_insn(ast.left, context)
    insns_right = get_asm_insn(ast.right, context)

    A = context.get_register()
    B = insns_left[-1].result_stored()
    C = insns_right[-1].result_stored()
    if ast.value == '+':
        insn = asm.AdditionInsn(A, B, C)
    elif ast.value == '*':
        insn = asm.MultiplicationInsn(A, B, C)
    else:
        assert False, ast.value

    context.registers[B] = context.registers[C] = True
    return insns_left + insns_right + [insn]


def wrap_in_print(insns):
    return insns + [asm.OutputInsn(insns[-1].result_stored())]


def compile(code: str):
    ast = Parser(Lexer(code).parse()).parse()
    insns = get_asm_insn(ast, Context())
    insns = wrap_in_print(insns)  # TODO: remove
    umcode = asm.encode_instructions(insns)
    return umcode


if __name__ == '__main__':
    s = '(26 + 5) * 2'
    ast = Parser(Lexer(s).parse()).parse()
    for insn in wrap_in_print(get_asm_insn(ast, Context())):
        print (insn)
