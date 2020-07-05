def assign(context, key, value):
    context[key] = value


def filter_dict(source, keys):
    return dict(map(lambda key: (key, source.get(key)), keys))


def is_listable(value):
    return isinstance(value, (list, tuple))
