#!/usr/bin/env python3
# pylint: disable=line-too-long

import tkinter as tk
import tkinter.messagebox as msgbox
import socket as s
from Threads.HandleSocket import HandleSocket as hS
from misc.Tools import Tools as t
from misc.ChannelNameGenerator import ChannelNameGenerator
import json
import struct

# DEBUG
import pprint
import time
pp = pprint.PrettyPrinter(indent=4)

class Server:
    def __init__(self):
        # Attributes
        # GUI
        self.statusLabel = None
        self.loadLabel = None
        self.errorLabel = None
        self.serverPortVar = None
        self.startButton = None
        self.stopButton = None

        # Server
        self.serverSocket = None
        self.status = 'offline'
        self.hS = None
        self.addrPort = ()
        self.MAX_CHANNEL_SIZE = 2

        # Clients and Channels
        self.clients = {}
        self.channels = {}

        self._gui = self.createGUI()

    def createGUI(self):
        gui = tk.Tk()
        gui.wm_title('Python_Bahamas Server')
        gui.grid_columnconfigure(0, weight=1)

        # Set guiMenubar as the window menu
        guiMenubar = self.createMenu(gui)
        gui.config(menu=guiMenubar)

        # Create a parent frame to hold the content
        parentFrame = tk.Frame(gui)
        parentFrame.grid(padx=25, pady=10, sticky='NSWE')
        parentFrame.grid_columnconfigure(0, weight=1)

        # Create a frame to hold the server status
        self.addServerStatus(parentFrame)

        # Create a frame to hold the server user load
        self.addServerLoad(parentFrame)

        # Create the command block
        self.addCommandBlock(parentFrame)

        return gui

    def createMenu(self, gui):
        # Create the main GUI menu, to hold tabs
        guiMenubar= tk.Menu(gui)

        # Create and add the File menu
        fileMenu = self.createFileMenu(guiMenubar)
        guiMenubar.add_cascade(label='File', menu=fileMenu)

        # Create and add the Help menu
        helpMenu = self.createHelpMenu(guiMenubar)
        guiMenubar.add_cascade(label='Help', menu=helpMenu)

        return guiMenubar

    def createFileMenu(self, menubar):
        fileMenu = tk.Menu(menubar, tearoff=0)
        fileMenu.add_command(label='Quit', command=self.exitApp)

        return fileMenu

    def createHelpMenu(self, menubar):
        helpMenu = tk.Menu(menubar, tearoff=0)
        helpMenu.add_command(label='About', command=self.displayAbout)

        return helpMenu

    def addServerStatus(self, parentFrame):
        statusLabelFrame = tk.LabelFrame(parentFrame, text="Server status", padx=20, pady=20)
        statusLabelFrame.grid(sticky='WE')

        self.statusLabel = tk.Label(statusLabelFrame, text="The Python_Bahamas Server is currently {}".format(self.status))
        self.statusLabel.grid(sticky='W')

        self.errorLabel = tk.Label(statusLabelFrame, text="")
        self.errorLabel.grid(sticky='W')

    def addServerLoad(self, parentFrame):
        loadLabelFrame = tk.LabelFrame(parentFrame, text="Server load", padx=20, pady=20)
        loadLabelFrame.grid(sticky='WE')

        self.loadLabel = tk.Label(loadLabelFrame, text="There is no connected user.")
        self.loadLabel.grid(sticky='W')

    def addCommandBlock(self, parentFrame):
        commandsLabelFrame = tk.LabelFrame(parentFrame, text="Commands", padx=20, pady=20)
        commandsLabelFrame.grid(sticky='WE')

        # Label and Entry for the server port
        serverPortLabel = tk.Label(commandsLabelFrame, text='Port :')
        self.serverPortVar = tk.StringVar()
        self.serverPortVar.set(4200)
        serverPortEntry = tk.Entry(commandsLabelFrame, textvariable=self.serverPortVar)
        serverPortLabel.grid(row=0, column=0)
        serverPortEntry.grid(row=0, column=1)

        # Buttons to command the server
        self.startButton = tk.Button(commandsLabelFrame, text='Start', command=self.startServer)
        self.stopButton = tk.Button(commandsLabelFrame, text='Stop', state=tk.DISABLED, command=self.stopServer)
        self.startButton.grid(row=0, column=2)
        self.stopButton.grid(row=0, column=3)


    def updateStatus(self, message):
        self.statusLabel.config(text=message)

    def updateLoad(self):
        nbClients = len(self.clients)
        if nbClients == 1:
            self.loadLabel.config(text='There is 1 user online')
        elif nbClients > 1:
            self.loadLabel.config(text='There is {} users online'.format(nbClients))
        else:
            self.loadLabel.config(text='There is no connected user.')


    def displayError(self, message):
        self.errorLabel.config(text='ERROR: {}'.format(message))

    def cleanError(self):
        self.errorLabel.config(text='')

    def startGUI(self):
        self._gui.mainloop()

    def startServer(self):
        self.cleanError()
        if self.serverSocket != None:
            self.displayError('The server is already running')
            return

        try:
            port = t.isPortValid(self.serverPortVar.get(), 'server')
        except Exception as e:
            self.displayError(str(e))
        else:
            self.startButton.config(state=tk.DISABLED)
            self.stopButton.config(state=tk.NORMAL)

            self.addrPort = ('0.0.0.0', port)
            self.serverSocket = s.socket(s.AF_INET, s.SOCK_STREAM)
            self.serverSocket.bind(self.addrPort)
            self.serverSocket.listen(5)

            self.hS = hS(self, self.serverSocket)
            self.hS.start()

            self.status = 'online'
            self.updateStatus('The Python_Bahamas Server is currently {} ({}:{})'.format(self.status, *self.addrPort))

    def stopServer(self):
        self.cleanError()

        self.hS.stop()
        self.serverSocket.shutdown(s.SHUT_RDWR)
        self.serverSocket.close()
        self.serverSocket = None

        self.clients = {}
        self.updateLoad()

        self.stopButton.config(state=tk.DISABLED)
        self.startButton.config(state=tk.NORMAL)

        self.status = 'offline'
        self.updateStatus('The Python_Bahamas Server is currently {}'.format(self.status))

    def exitApp(self):
        self._gui.destroy()

    def displayAbout(self):
        msgbox.showinfo('About', 'Powered by laidet_r & cherbi_r\nSDM 2017 All rights reserved')

    # Clients management
    def addClient(self, socket, ip):
        client = {
            'ip': ip[0]
        }
        self.clients[socket] = client
        self.updateLoad()
        print('Un client vient de se connecter depuis l\'ip {}'.format(ip[0]))

        channelNameGenerator = ChannelNameGenerator()
        channelName = channelNameGenerator.generate()
        while not self.isChannelNameAvailable(channelName):
            channelName = channelNameGenerator.generate()
        self.addChannel({'name': channelName}, socket)

        print('{} : LES CHANNELS'.format(time.strftime("%H:%M:%S")))
        pp.pprint(self.channels)
        return client, self.clients

    def completeClient(self, data, socket):
        client = self.clients[socket]
        client['username'] = data['username']
        client['tcpPort'] = data['tcpPort']
        client['udpPort'] = data['udpPort']

        self.updateChannelListToClients()

        print('{} : LES CHANNELS'.format(time.strftime("%H:%M:%S")))
        pp.pprint(self.channels)
        return client, self.clients

    def removeClient(self, socket):
        if socket in self.clients:
            channels = self.getClientChannels(socket)
            for key in channels:
                channel = channels[key]
                self.removeClientFromChannel(socket, channel)
                if self.isChannelEmpty(channel):
                    self.deleteChannel(key)
            username = self.clients[socket]['username']
            del self.clients[socket]
            self.updateLoad()
            self.updateChannelListToClients()

            print('Le client {} a ete supprime suite a sa deconnexion'.format(username))
            print('{} : LES CHANNELS'.format(time.strftime("%H:%M:%S")))
            pp.pprint(self.channels)
            return True
        return False

    # Channels management
    def addChannel(self, data, socket):
        name = data['name']
        if self.isChannelNameAvailable(name):
            client = self.clients[socket]
            channel = {
                'name': name,
                'isFull': False,
                'clients': {
                    socket: client
                }
            }
            self.channels[name] = channel

            self.setClientCurrChannel(socket, name)
            if 'username' in client:
                self.updateChannelListToClients()

            print('Le channel {} a ete cree'.format(name))
            print('{} : LES CHANNELS'.format(time.strftime("%H:%M:%S")))
            pp.pprint(self.channels)
            return channel, self.channels
        else:
            raise Exception('This channel already exist.')

    def deleteChannel(self, channelName):
        if self.doesChannelExist(channelName):
            if not self.channels[channelName]['clients']:
                del self.channels[channelName]
                print('Le channel {} est vide, il a ete supprime'.format(channelName))
                return True
        return False

    def getClientChannels(self, socket):
        channels = {}
        for key in self.channels:
            if socket in self.channels[key]['clients']:
                channels[key] = self.channels[key]
        return channels

    def isChannelNameAvailable(self, name):
        if name not in self.channels:
            return True
        else:
            return False
    def isChannelEmpty(self, channel):
        if not channel['clients']:
            return True
        return False

    def doesChannelExist(self, channelName):
        if channelName in self.channels:
            return True
        return False

    def isClientInChannel(self, socket, channel):
        if socket in channel['clients']:
            return True
        return False

    def removeClientFromChannel(self, socket, channel):
        if socket in channel['clients']:
            del channel['clients'][socket]
            print('Le client {} a quitter le channel {}'.format(self.clients[socket]['username'], channel['name']))
            return True
        return False

    def joinChannel(self, data, socket):
        channelName = data['name']
        if self.doesChannelExist(channelName):
            channel = self.channels[channelName]
            if not self.isClientInChannel(socket, channel):
                user = self.clients[socket]
                channel['clients'][socket] = user

                self.setClientCurrChannel(socket, channelName)
                self.updateChannelListToClients()

                print('Le client {} a rejoint le channel {}'.format(user['username'], channelName))
                print('{} : LES CHANNELS'.format(time.strftime("%H:%M:%S")))
                pp.pprint(self.channels)
                return True
            return False
        print('Le channel {} nexoste pas'.format(channelName))
        return False

    def setClientCurrChannel(self, socket, channel):
        jsonMsg = json.dumps({
            'action': 'setCurrChannel',
            'error': False,
            'data': {
                'name': channel
            }
        })
        self.sendMessage(socket, jsonMsg)

    def updateChannelListToClients(self):
        for socket in self.clients:
            self.getChannelList(False, socket)

    def getChannelList(self, data, toSocket):
        channels = {}

        for channelName in self.channels:
            channel = self.channels[channelName]
            channelClients = channel['clients']

            clients = []
            for socket in channelClients:
                client = channelClients[socket]
                clients.append({
                    'username': client['username'],
                    'ip': client['ip'],
                    'tcpPort': client['tcpPort'],
                    'udpPort': client['udpPort'],
                })

            channels[channelName] = {
                'name': channelName,
                'isFull': channel['isFull'],
                'clients': clients
            }

        jsonMsg = json.dumps({
            'action': 'channelList',
            'error': False,
            'data': channels
        })

        self.sendMessage(toSocket, jsonMsg)

    def sendMessage(self, socket, json):
        try:
            data = json.encode('utf-8')
            dataLength = len(data)
            socket.sendall(struct.pack('!I', dataLength))
            socket.sendall(data)
        except Exception as e:
            print('Erreur lors de l\'envoie du message : {}'.format(json))
            print(str(e))

server = Server()
server.startGUI()