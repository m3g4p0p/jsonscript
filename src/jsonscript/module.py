import json
from pathlib import Path

from .util import filter_dict

modules = {}


def get_exports(module, initializer=None):
    if module not in modules and initializer is not None:
        initializer(module)

    return modules.setdefault(module, {})


def update_exports(source, context, exports):
    exports.update(filter_dict(context, source.get('@export', ())))


def resolve_module(filename):
    path = Path() / filename
    return path.resolve().with_suffix('.json')


def init_module(source):
    if isinstance(source, (str, Path)):
        module = resolve_module(source)

        with open(module) as file:
            source = json.load(file)

        path = module.parent
        exports = get_exports(module)

    else:
        source = source
        path = Path.cwd()
        exports = None

    return source, path, exports
