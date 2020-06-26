import re


def matches(pattern, value):
    return isinstance(value, str) and re.match(pattern, value)


def is_assignment(value):
    return matches(r'=\w', value)


def is_reference(value):
    return matches(r'&\w', value)


def is_directive(value):
    return matches(r'@\w', value)
