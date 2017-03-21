import threading as t
import json

class HandleConnection(t.Thread):
    def __init__(self, server, lock, socket, ip):
        t.Thread.__init__(self)

        self.server = server
        self.lock = lock
        self.socket = socket
        self.ip = ip
        self.isRunning = True

        # Create the base Client, with just his socket and public ip.
        self.server.addClient(socket, ip)
    def stop(self):
        self.isRunning = False

    def parseMessage(self, byteMessage):
        messageDict = json.loads(byteMessage.decode('utf-8'))
        action = messageDict['action']
        data = messageDict['data']

        def actionSwitch(action):
            switcher = {
                'welcome': self.server.completeClient
            }
            func = switcher.get(action, lambda: "nothing")
            return func(data, self.socket)

        actionSwitch(action)

    def run(self):
        while self.isRunning:
            try:
                byteMessage = self.socket.recv(1024)
            except Exception as e:
                print('Lien rompu avec {}'.format(self.ip))
                print(e)
            else:
                if byteMessage:
                    self.parseMessage(byteMessage)