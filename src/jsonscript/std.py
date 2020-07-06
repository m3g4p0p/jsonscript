def ternary(condition, if_true, if_false=None):
    if condition:
        return if_true

    return if_false


def number(value):
    try:
        return int(value)
    except ValueError:
        return float(value)


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
    # Casting
    'number': number,
    'string': str,
    'boolean': bool,
    # Lists
    'length': lambda list: len(list),
    'push': lambda list, value: list.append(value),
    'pop': lambda list: list.pop(),
    'slice': lambda list, start=None, end=None: list[start:end],
    'get': lambda list, index: list[index],
    'set': lambda list, index, value: list.__setitem__(index, value),
    'copy': lambda list: list.copy(),
    # I/O
    'print': print,
    'input': input,
    'read': read,
    'write': write
}
