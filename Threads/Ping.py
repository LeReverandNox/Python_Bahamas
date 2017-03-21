import threading as t
from datetime import datetime
from time import sleep

class Ping(t.Thread):
    def __init__(self, socket, parentThread):
        t.Thread.__init__(self)
        self.isRunning = True
        self.socket = socket
        self.parentThread = parentThread

    def stop(self):
        self.isRunning = False

    def run(self):
        while self.isRunning:
            try:
                self.socket.send('ping'.encode())
            except Exception as e:
                self.stop()
                self.parentThread.die()
            sleep(1)

