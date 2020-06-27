import re

PREFIXES = ('#', '?', '!')


def matches(pattern, value):
    return isinstance(value, str) and re.match(pattern, value)


def is_assignment(value):
    return matches(r'=\w', value)


def is_reference(value):
    return matches(r'&\w', value)


def is_directive(value):
    return matches(r'@\w', value)


def is_valid_prefix(context, prefix, func):
    return prefix in PREFIXES and (not func or func.lstrip('&') in context)
