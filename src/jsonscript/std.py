STD = {
    # Control flow
    'if': lambda condition, if_true, if_false=None: (
        if_true if condition else if_false
    ),
    # Logical operators
    'or': lambda x, y: x or y,
    'and': lambda x, y: x and y,
    'not': lambda x: not x,
    # Comparisons
    'is': lambda x, y: x == y,
    # Arithmetics
    '+': lambda x, y: x + y,
    '-': lambda x, y: x - y,
    '*': lambda x, y: x * y,
    '/': lambda x, y: x / y,
    # Lists
    'push': lambda list, value: list.append(value),
    'pop': lambda list: list.pop(),
    'length': lambda list: len(list),
    'copy': lambda list: list.copy(),
    # Miscellaneous
    'print': lambda *params: print(' '.join(map(str, params))),
}
