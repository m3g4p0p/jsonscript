def starts_with(value, char):
    return isinstance(value, str) and value.startswith(char)


def is_variable(value):
    return starts_with(value, '$')


def is_reference(value):
    return starts_with(value, '&')


def is_directive(value):
    return starts_with(value, '@')


def is_return(value):
    return starts_with(value, '#')


def is_maybe(value):
    return starts_with(value, '?')


def is_void(value):
    return starts_with(value, '!')
