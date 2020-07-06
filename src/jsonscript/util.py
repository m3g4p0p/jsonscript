def assign(context, key, value):
    context[key] = value


def get_items(dict, keys):
    return map(lambda key: (key, dict.get(key)), keys)


def is_listable(value):
    return isinstance(value, (list, tuple))
