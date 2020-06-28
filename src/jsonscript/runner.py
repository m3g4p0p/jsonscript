from functools import partial

from .prefix import (
    PREFIXES,
    is_assignment,
    is_directive,
    is_binding,
)
from .std import STD


class function:
    def __init__(self, context, source):
        self.context = context
        self.source = source

    def __call__(self, *params):
        return run(self.source, self.context, *params)

    def bind(self, context):
        return function(context, self.source)


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

    if is_binding(value):
        return context[value[1:]]

    return value


def assign(context, key, value):
    context[key] = value


def call(context, key, params):
    if is_binding(key):
        func = context[key[1:]].bind(context)
    else:
        func = context[key]

    args = evaluate(context, params)

    return func(*args)


def run(json, context=None, *params):
    params = get_params(json, params)
    context = init_scope(context, params)

    for key, value in json.items():
        prefix, func_name = key[:1], key[1:]

        if prefix in PREFIXES:
            if func_name:
                result = call(context, func_name, value)
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

        else:
            assign(context, key, function(context, value))

    return None
