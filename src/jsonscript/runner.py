from functools import partial

from .directives import get_params
from .prefix import is_directive, is_maybe, is_reference, is_variable, is_void
from .std import STD


def is_callable(value):
    return callable(value) or isinstance(value, dict)


def prefix(key, value):
    if is_callable(value) or is_variable(key):
        return key

    return f'${key}'


def init_scope(context=None, params=()):
    context = (context or STD).copy()

    for key, value in params:
        assign(context, prefix(key, value), value)

    return context


def evaluate(context, value):
    if isinstance(value, (tuple, list)):
        return list(map(partial(evaluate, context), value))

    if isinstance(value, dict):
        return run(value, context)

    if is_variable(value):
        return context[value]

    if is_reference(value):
        return context[value[1:]]

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
    params = get_params(json, params)
    context = init_scope(context, params)

    for key, value in json.items():
        if key == '#':
            return evaluate(context, value)

        if key == '?':
            result = evaluate(context, value)

            if result:
                return result

        elif is_directive(key):
            pass

        elif is_variable(key):
            assign(context, key, evaluate(context, value))

        elif isinstance(value, dict):
            if is_reference(key):
                assign(context, key[1:], value)
            else:
                assign(context, key, partial(run, value, context))

        elif isinstance(value, (list, tuple)):
            if is_void(key) or is_maybe(key):
                result = call(context, key[1:], value)

                if is_maybe(key) and result:
                    return result
            else:
                return call(context, key, value)

        else:
            raise SyntaxError(f'Invalid function declaration {key}: {value}')

    return None
