import threading as t
from datetime import datetime
from time import sleep
import json
import struct

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
                jsonPing = json.dumps({
                    'action': 'ping',
                    'data': False
                }).encode('utf-8')
                pingLength = len(jsonPing)
                self.socket.sendall(struct.pack('!I', pingLength))
                self.socket.sendall(jsonPing)
            except Exception as e:
                self.stop()
                self.parentThread.die()
            sleep(1)

