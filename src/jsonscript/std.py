STD = {
    'if': lambda condition, if_true, if_false=None: (
        if_true if condition else if_false
    ),
    'print': lambda *params: print(' '.join(map(str, params))),
    'or': lambda x, y: x or y,
    'and': lambda x, y: x and y,
    'not': lambda x: not x,
    'is': lambda x, y: x == y,
    '+': lambda x, y: x + y,
    '-': lambda x, y: x - y,
    '*': lambda x, y: x * y,
    '/': lambda x, y: x / y,
}
