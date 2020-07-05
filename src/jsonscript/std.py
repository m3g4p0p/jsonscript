def ternary(condition, if_true, if_false=None):
    if condition:
        return if_true

    return if_false


def read(filename):
    with open(filename) as f:
        return f.read()


def write(filename, data):
    with open(filename, 'w') as f:
        return f.write(data)


globals = {
    # Control flow
    'if': ternary,
    # Logical operators
    'or': lambda x, y: x or y,
    'and': lambda x, y: x and y,
    'not': lambda x: not x,
    # Comparisons
    '==': lambda x, y: x == y,
    '<': lambda x, y: x < y,
    '>': lambda x, y: x > y,
    '<=': lambda x, y: x <= y,
    '>=': lambda x, y: x >= y,
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
    # I/O
    'print': print,
    'input': input,
    'read': read,
    'write': write
}
