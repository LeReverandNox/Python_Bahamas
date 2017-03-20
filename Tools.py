class Singleton(type):
    _instances = {}
    def __call__(self, *args, **kwargs):
        if self not in self._instances:
            self._instances[self] = super(Singleton, self).__call__(*args, **kwargs)
        return self._instances[self]

class Tools(metaclass=Singleton):
    def castInt(nbr):
        try:
            int(nbr)
            return int(nbr)
        except ValueError:
            return 0
