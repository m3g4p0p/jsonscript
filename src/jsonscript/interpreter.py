from functools import partial, reduce
from itertools import chain

from .module import (
    get_exports,
    update_exports,
    resolve_module,
    init_module
)
from .prefix import (
    resolve_prefix,
    is_assignment,
    is_directive,
    is_binding,
)
from .std import std
from .util import (
    assign,
    get_items,
    is_listable,
)


class scoped(dict):
    def __init__(self, parent, module):
        self.parent = parent
        self.module = module

    def __getitem__(self, key):
        if super().__contains__(key):
            return super().__getitem__(key)

        return self.parent[key]

    def __contains__(self, key):
        return super().__contains__(key) or key in self.parent


class function:
    def __init__(self, context, source):
        self.context = context
        self.source = source

    def __call__(self, *params):
        return run(self.source, self.context, params)

    def bind(self, context):
        return function(context, self.source)


def init_context(source, parent):
    parent = parent or scoped(std, None)
    source, module = init_module(source, parent)
    context = scoped(parent, module)

    return source, context


def get_params(source, params):
    if params is None:
        return ()

    return chain(zip(source.get(
        '@params',
        map(str, range(len(params)))
    ), params), (('args', params),))


def get_imports(source, context):
    result = {}

    for filename, imports in source.get('@import', {}).items():
        module = resolve_module(filename, context)
        exports = get_exports(module, run)

        if imports is True:
            result.update(exports)
        else:
            result.update(get_items(exports, imports))

    return result.items()


def get_scoped(source, context):
    result = {}

    for scoped in source.get('@use', ()):
        result.update(context[scoped])

    return result.items()


def evaluate(context, value):
    if is_listable(value):
        return list(map(partial(evaluate, context), value))

    if isinstance(value, dict):
        return run(value, context)

    if is_binding(value):
        return context[value[1:]]

    return value


def call(context, key, params):
    if '|' in key:
        return pipe(context, key, params)

    if is_binding(key):
        func = context[key[1:]].bind(context)
    else:
        func = context[key]

    args = evaluate(context, params)
    return func(*args)


def pipe(context, key, params):
    keys = key.split('|')

    return reduce(lambda result, current: [
        call(context, current, result)
    ], keys, params)[0]


def process(source, context):
    for key, value in source.items():
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

    return None


def run(source, context=None, params=None):
    source, context = init_context(source, context)

    context.update(chain(
        get_imports(source, context),
        get_scoped(source, context),
        get_params(source, params),
        (('this', context),)
    ))

    result = process(source, context)
    update_exports(source, context)

    return result
