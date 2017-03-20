import threading as t

class HandleConnection(t.Thread):
    def __init__(self, lock):
        t.Thread.__init__(self)

        self.lock = lock
        self.isRunning = True

    def stop(self):
        self.isRunning = False

    def run(self):
        print('On recois une connexion')