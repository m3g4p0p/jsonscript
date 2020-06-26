from functools import partial

from .prefix import is_assignment, is_directive, is_reference
from .std import STD

STATEMENTS = ('#', '?', '!')


def is_listable(value):
    return isinstance(value, (list, tuple))


def get_params(json, params):
    return zip(json.get(
        '@params',
        map(str, range(len(params)))
    ), params)


def init_scope(context=None, params=()):
    context = (context or STD).copy()

    for key, value in params:
        assign(context, key, value)

    return context


def evaluate(context, value):
    if is_listable(value):
        return list(map(partial(evaluate, context), value))

    if isinstance(value, dict):
        return run(value, context)

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
        prefix, func = key[:1], key[1:]

        if prefix in STATEMENTS and (not func or func in context):
            if func:
                result = call(context, func, value)
            else:
                result = evaluate(context, value)

            if prefix == '#' or prefix == '?' and result is not None:
                return result

        elif is_directive(key):
            pass

        elif is_assignment(key):
            assign(context, key[1:], evaluate(context, value))

        elif is_listable(value):
            return call(context, key, value)

        elif is_reference(key):
            assign(context, key[1:], value)

        else:
            assign(context, key, partial(run, value, context))

    return None
