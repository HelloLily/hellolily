class Promise(object):
    """
    A simple promise-like object used for batched requests.
    """
    def __init__(self):
        self._data = None
        self.resolved = False

    @property
    def data(self):
        if not self.resolved:
            raise ValueError('Promise object has not been resolved yet.')

        return self._data

    def resolve(self, data):
        if self.resolved:
            raise ValueError('Promise object has already been resolved.')

        self.resolved = True
        self._data = data
