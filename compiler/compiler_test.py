from run import run_compiled
from .compiler import compile
from .asm import encode_instructions


def test_expressions():
    testcases = [('25 + 3 * 4', 37),
                 ('(21 + 3) * 10', 240),
                 ('(((1 + 2) * 3) + 4) * 5 + 6', 71)]
    
    for t, expected in testcases:
        result = run_compiled(compile(t), binary=True)
        result = int.from_bytes(result, byteorder='big')
        assert result == expected, result


if __name__ == '__main__':
    test_expressions()