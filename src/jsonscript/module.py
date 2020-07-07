import json
from pathlib import Path

from .util import get_items

modules = {}


def get_exports(module, initializer=None):
    if module not in modules and initializer is not None:
        initializer(module)

    return modules.setdefault(module, {})


def update_exports(source, context):
    if '__module__' not in context:
        return

    exports = get_items(context, source.get('@export', ()))
    get_exports(context['__module__']).update(exports)


def resolve_module(filename):
    path = Path() / filename
    return path.resolve().with_suffix('.json')


def init_module(source):
    if isinstance(source, (str, Path)):
        module = resolve_module(source)
        parent = module.parent

        with open(module) as file:
            source = json.load(file)

    else:
        module = None
        parent = Path.cwd()

    return source, parent, module
