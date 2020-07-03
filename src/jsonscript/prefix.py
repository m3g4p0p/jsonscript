import re

PREFIXES = ('#', '?', '!')


def matches(pattern, value):
    return isinstance(value, str) and re.match(pattern, value)


def is_assignment(value):
    return matches(r'=\w', value)


def is_binding(value):
    return matches(r'&\w', value)


def is_directive(value):
    return matches(r'@\w', value)


def resolve_prefix(key):
    prefix, name = key[:1], key[1:]

    if prefix in PREFIXES:
        return prefix, name

    return None, key
