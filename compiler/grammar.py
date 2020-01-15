
keywords = ['if']

operator_levels = [
                    ['=', '+=', '-=', '*=', '/='],
                    ['+', '-'],
                    ['*', '/'],
                    ['&&'],
                    ['.']
            ]
operators = sum(operator_levels, [])

def level(op):
    for i, x in enumerate(operator_levels):
        if op in x: return i
    assert False, op

brackets = '(){}[]'
whitespaces = ' \n\t\r'

closing = { '(' : ')', '{' : '}', '[' : ']'}
