import threading as t

class HandleConnection(t.Thread):
    def __init__(self, server, lock, socket):
        t.Thread.__init__(self)

        self.server = server
        self.lock = lock
        self.socket = socket
        self.isRunning = True

    def stop(self):
        self.isRunning = False

    def run(self):
        print('On recois une connexion du socket {}'.format(self.socket))