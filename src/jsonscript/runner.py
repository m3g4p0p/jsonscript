from functools import partial

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


def init_scope(context=None, params=()):
    context = (context or STD).copy()

    for index, value in enumerate(params):
        assign(context, f'${index}', value)

    return context


def starts_with(value, char):
    return isinstance(value, str) and value.startswith(char)


def is_variable(value):
    return starts_with(value, '$')


def is_side_effect(value):
    return starts_with(value, '&')


def evaluate(context, value):
    if isinstance(value, (tuple, list)):
        return list(map(partial(evaluate, context), value))

    if isinstance(value, dict):
        return run(value, context)

    if is_variable(value):
        return context[value]

    return value


def assign(context, key, value):
    context[key] = value


def call(context, key, params):
    func = context[key]
    args = evaluate(context, params)

    if callable(func):
        return func(*args)

    return run(func, context, *args)


def run(json, context=None, *params):
    context = init_scope(context, params)

    for key, value in json.items():
        if key == '#':
            return evaluate(context, value)

        if is_variable(key):
            assign(context, key, evaluate(context, value))

        elif isinstance(value, dict):
            assign(context, key, partial(run, value, context))

        elif isinstance(value, (list, tuple)):
            if is_side_effect(key):
                call(context, key[1:], value)
            else:
                return call(context, key, value)

        else:
            raise SyntaxError(f'Invalid function declaration {key}: {value}')

    return None
