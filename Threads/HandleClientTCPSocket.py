import threading as t
from Threads.HandleFromClientConnection import HandleFromClientConnection as hFCC

class HandleClientTCPSocket(t.Thread):
    def __init__(self, client, socket):
        t.Thread.__init__(self)
        self.client = client
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
                hFCC(self.client, clientSocket).start()