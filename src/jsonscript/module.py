import json
from pathlib import Path

from .util import get_items

modules = {}


def get_exports(module, initializer=None):
    if module not in modules and initializer is not None:
        initializer(module)

    return modules.setdefault(module, {})


def update_exports(source, context):
    if context.module is None:
        return

    exports = get_items(context, source.get('@export', ()))
    get_exports(context.module).update(exports)


def get_path(context):
    if context.module is not None:
        return context.module.parent

    return Path.cwd()


def resolve_module(filename, context):
    path = get_path(context) / filename
    return path.resolve().with_suffix('.json')


def init_module(source, context):
    if isinstance(source, (str, Path)):
        module = resolve_module(source, context)

        with open(module) as file:
            source = json.load(file)

    else:
        module = context.module

    return source, module
