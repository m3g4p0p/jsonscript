import json
from pathlib import Path

from .util import filter_dict

modules = {}


def get_exports(module, initializer=None):
    if module not in modules and initializer is not None:
        initializer(module)

    return modules.setdefault(module, {})


def update_exports(source, context):
    module = context.get('__module__')

    if module is None:
        return

    exports = filter_dict(context, source.get('@export', ()))
    get_exports(module).update(exports)


def resolve_module(filename):
    path = Path() / filename
    return path.resolve().with_suffix('.json')


def init_module(source, context):
    if isinstance(source, (str, Path)):
        module = resolve_module(source)
        parent = module.parent

        with open(module) as file:
            source = json.load(file)

    else:
        module = None
        parent = Path.cwd()

    return source, parent, module
