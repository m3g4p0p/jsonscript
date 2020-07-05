from functools import partial
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
from .util import (
    assign,
    filter_dict,
    is_listable,
)
from .std import globals


class function:
    def __init__(self, context, source):
        self.context = context
        self.source = source

    def __call__(self, *params):
        return run(self.source, self.context, params)

    def bind(self, context):
        return function(context, self.source)


def init_context(context, path):
    context = (context or globals).copy()
    context.setdefault('__path__', path)
    return context


def get_params(source, params):
    return zip(source.get(
        '@params',
        map(str, range(len(params)))
    ), params)


def get_imports(source, context):
    result = {}

    for filename, imports in source.get('@import', {}).items():
        module = resolve_module(context['__path__'] / filename)
        exports = get_exports(module, run)
        result.update(filter_dict(exports, imports))

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
    if is_binding(key):
        func = context[key[1:]].bind(context)
    else:
        func = context[key]

    args = evaluate(context, params)
    return func(*args)


def run(source, context=None, params=()):
    source, path, exports = init_module(source)
    context = init_context(context, path)

    context.update(chain(
        get_params(source, params),
        get_imports(source, context)
    ))

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

    if exports is not None:
        update_exports(source, context, exports)

    return None
