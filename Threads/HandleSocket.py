import threading as t
from Threads.HandleConnection import HandleConnection as hC

class HandleSocket(t.Thread):
    def __init__(self, server, socket):
        t.Thread.__init__(self)
        self.server = server
        self.socket = socket

        self.isRunning = True
        self.lock = t.RLock()

    def stop(self):
        self.isRunning = False

    def run(self):
        while self.isRunning:
            try:
                clientSocket, clientIp = self.socket.accept()
            except OSError:
                pass
            else:
                toto = hC(self.server, self.lock, clientSocket, clientIp)
                toto.start()
                # TODO: watch if socket is still alive (ping ?)