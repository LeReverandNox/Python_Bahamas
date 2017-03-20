import threading as t

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
        print('YOLO ON RUN LE SERVEUR')