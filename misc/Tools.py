import socket

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

    def isPortValid(nbr, portType):
        port = Tools.castInt(nbr)
        if port == 0:
            raise TypeError('Please enter a numeric {} port value'.format(portType))
        if port < 1024 or port > 65535:
            raise ValueError('The {} port must be in the range 1024-65535'.format(portType))
        if not Tools.isPortAvailable(port, portType):
            pass

        return port

    def isPortAvailable(port, portType):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind(('0.0.0.0', port))
        except socket.error as e:
            s.close()
            if e.errno == 98:
                raise ValueError('This {} port is already taken'.format(portType))
            else:
                print(e)
                raise Exception('Unknow Error, please contact an administrator (Code {})'.format(e.errno))
        else:
            s.close()
            return True
