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


def is_valid_prefix(context, prefix, key):
    return prefix in PREFIXES and (not key or key.lstrip('&') in context)
