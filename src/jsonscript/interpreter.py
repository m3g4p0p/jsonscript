import json
from functools import partial
from itertools import chain
from pathlib import Path

from .prefix import (
    resolve_prefix,
    is_assignment,
    is_directive,
    is_binding,
)
from .std import STD

modules = {}


class function:
    def __init__(self, context, source):
        self.context = context
        self.source = source

    def __call__(self, *params):
        return run(self.source, self.context, params)

    def bind(self, context):
        return function(context, self.source)


def resolve_module(filename):
    filepath = Path() / filename
    return filepath.with_suffix('.json').resolve()


def load(filename):
    filepath = resolve_module(filename)
    exports = modules.setdefault(filepath, {})

    with open(filepath) as f:
        return json.load(f), exports


def is_listable(value):
    return isinstance(value, (list, tuple))


def get_params(json, params):
    return zip(json.get(
        '@params',
        map(str, range(len(params)))
    ), params)


def get_imports(json, path):
    result = {}

    for filename, imports in json.get('@import', {}).items():
        filepath = resolve_module(path / filename)

        if filepath not in modules:
            run(filepath)

        exports = modules.get(filepath, {})

        result.update(map(
            lambda key: (key, exports.get(key)),
            imports
        ))

    return result.items()


def update_exports(json, context, exports):
    exports.update(map(
        lambda key: (key, context.get(key)),
        json.get('@export', ())
    ))


def init_scope(context=None, updates=()):
    context = (context or STD).copy()
    context.update(updates)
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


def run(json, context=None, params=()):
    path = Path.cwd() / '__main__'
    exports = {}

    if isinstance(json, (str, Path)):
        path = (path.parent / json)
        json, exports = load(path)

    context = init_scope(context, chain(
        get_params(json, params),
        get_imports(json, path.parent)
    ))

    for key, value in json.items():
        prefix, name = resolve_prefix(key)

        if prefix:
            if name:
                result = call(context, name, value)
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

    update_exports(json, context, exports)

    return None
