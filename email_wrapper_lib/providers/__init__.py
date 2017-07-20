from .google import Google
from .microsoft import Microsoft


class ProviderRegistry(tuple):
    def __init__(self, iterable):
        super(ProviderRegistry, self).__init__()

        self._providers_by_id = {p.id: p for p in iterable}
        self._providers_by_name = {p.name: p for p in iterable}
        self.choices = ((p.id, p.name) for p in iterable)

    def __contains__(self, y):
        if isinstance(y, int):
            return y in self._providers_by_id.keys()

        if isinstance(y, str) or isinstance(y, unicode):
            return y in self._providers_by_name.keys()

        raise ValueError('Unsupported type for registry lookup `%s`' % type(y))

    def __getitem__(self, y):
        if isinstance(y, int):
            return self._providers_by_id.get(y)

        if isinstance(y, str) or isinstance(y, unicode):
            return self._providers_by_name.get(y)

        raise ValueError('Unsupported type for registry lookup `%s`' % type(y))


registry = ProviderRegistry([Google, Microsoft])
