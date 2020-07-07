class scope(dict):
    def __init__(self, context, iterable=()):
        self.context = context
        super().__init__(iterable)

    def __getitem__(self, key):
        if super().__contains__(key):
            return super().__getitem__(key)

        return self.context[key]

    def __contains__(self, key):
        return super().__contains__(key) or key in self.context

    def setdefault(self, key, default):
        if key in self.context:
            return self.context[key]

        return super().setdefault(key, default)
