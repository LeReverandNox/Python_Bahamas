import threading as t
import json
from Threads.Ping import Ping
import struct

class HandleServerConnection(t.Thread):
    def __init__(self, client, socket):
        t.Thread.__init__(self)

        self.client = client
        self.socket = socket
        self.isRunning = True

        self.sayHello()

        Ping(socket, self).start()

    def stop(self):
        self.isRunning = False

    def die(self):
        print('Lien rompu avec le serveur')
        self.stop()

    def parseMessage(self, byteMessage):
        messageDict = json.loads(byteMessage.decode('utf-8'))
        print('Recu {}'.format(messageDict))
        action = messageDict['action']
        data = messageDict['data']

        def actionSwitch(action):
            switcher = {
                'channelList': self.client.displayChannelList
            }
            func = switcher.get(action, lambda foo, bar : "nothing")
            return func(data, self.socket)

        try:
            actionSwitch(action)
        except Exception as e:
            print(str(e))

    def recvSome(self, length):
        completeBuffer = b''
        while length:
            try:
                buffer = self.socket.recv(length)
            except Exception as e:
                pass
            else:
                if buffer:
                    completeBuffer += buffer
                    length -= len(buffer)
        return completeBuffer

    def run(self):
        while self.isRunning:
            binaryLength = self.recvSome(4)
            messageLength, = struct.unpack('!I', binaryLength)
            binaryMessage = self.recvSome(messageLength)

            self.parseMessage(binaryMessage)

    def sayHello(self):
        jsonMsg = json.dumps({
            'action': 'welcome',
            'data': {
                'username': self.client.usernameVar.get(),
                'tcpPort': int(self.client.tcpPortVar.get()),
                'udpPort': int(self.client.udpPortVar.get())
            }
        })
        self.sendMessage(jsonMsg)


    def getChannelList(self):
        jsonMsg = json.dumps({
            'action': 'getChannelList',
            'data': False
        })
        self.sendMessage(jsonMsg)

    def createChannel(self, name):
        jsonMsg = json.dumps({
            'action': 'createChannel',
            'data': {
                'name': name
            }
        })
        self.sendMessage(jsonMsg)

    def sendMessage(self, json):
        data = json.encode('utf-8')
        dataLength = len(data)
        self.socket.sendall(struct.pack('!I', dataLength))
        self.socket.sendall(data)