import threading as t
from datetime import datetime
from time import sleep

class Ping(t.Thread):
    def __init__(self, socket):
        t.Thread.__init__(self)
        self.isRunning = True
        self.socket = socket

    def stop(self):
        self.isRunning = False

    def run(self):
        while self.isRunning:
            try:
                self.socket.send('ping'.encode())
            except Exception as e:
                self.stop()
            sleep(1)

