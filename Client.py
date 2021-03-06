#!/usr/bin/env python3
# pylint: disable=line-too-long

import tkinter as tk
import tkinter.messagebox as msgbox
import socket as s
from misc.Tools import Tools as t
import json
from Threads.HandleClientTCPSocket import HandleClientTCPSocket as hCTCPS
from Threads.HandleServerConnection import HandleServerConnection as hSC
from Threads.HandleToClientConnection import HandleToClientConnection as hTCC

class Client:
    def __init__(self):
        # Attributes
        # GUI
        self.serverStatusLabel = None
        self.serverErrorLabel = None
        self.serverAddrVar = None
        self.serverPortVar = None
        self.serverConnectButton = None
        self.serverDisconnectButton = None
        self.joinChannelButton = None
        self.channelList = None
        self.channelNameVar = None
        self.createChannelButton = None
        self.chatInfosLabel = None
        self.usersList = None
        self.messagesList = None
        self.messageVar = None
        self.sendMessageButton = None
        self.tcpPortVar = None
        self.udpPortVar = None
        self.usernameVar = None

        # Server
        self.serverSocket = None
        self.tcpSocket = None
        self.hCTCPS = None
        self.udpSocket = None
        self.hSC = None
        self.ports = []
        self.username = None

        # Clients and Channels
        self.channels = {}
        self.channelsSockets = {}
        self.channelsMessages = {}
        self.currChannel = None
        self.hasChannelChange = False

        self._gui = self.createGUI()
    def verifyPorts(self):
        try:
            tcpPort = t.isPortValid(self.tcpPortVar.get().strip(), 'tcp')
            udpPort = t.isPortValid(self.udpPortVar.get().strip(), 'udp')
            if tcpPort == udpPort:
                raise Exception('UDP and TCP port can\'t be identical.')
        except Exception as e:
            self.displayError(str(e))
            return False
        else:
            return (tcpPort, udpPort)

    def verifyUsername(self):
        username = self.usernameVar.get().strip()
        if len(username) < 1:
            self.displayError('Please choose a username !')
            return False
        return username

    def startClientSockets(self, ports):
        tcpAddrPort = ('0.0.0.0', ports[0])
        self.tcpSocket = s.socket(s.AF_INET, s.SOCK_STREAM)
        self.tcpSocket.bind(tcpAddrPort)
        self.tcpSocket.listen(5)
        self.hCTCPS = hCTCPS(self, self.tcpSocket)
        self.hCTCPS.start()

        return True

    def connectToServer(self):
        self.cleanError()
        if self.serverSocket != None:
            self.displayError('You are already connected to the server')
            return

        self.ports = self.verifyPorts()
        self.username = self.verifyUsername()
        if self.ports and self.username:
            try:
                serverAddrPort = ((self.serverAddrVar.get().strip() or 'null'), int(self.serverPortVar.get().strip() or 0))
                self.serverSocket = s.socket(s.AF_INET, s.SOCK_STREAM)
                self.serverSocket.connect(serverAddrPort)
                self.hSC = hSC(self, self.serverSocket)
                self.hSC.start()
            except Exception as e:
                print(e)
                self.displayError('Can\'t establish a connection to the server : {}'.format(str(e)))
                self.serverSocket = None
            else:
                self.serverConnectButton.config(state=tk.DISABLED)
                self.serverDisconnectButton.config(state=tk.NORMAL)

                self.startClientSockets(self.ports)

    def disconnectFromServer(self):
        self.hSC.die()
        self.hSC = None
        self.serverSocket.close()
        self.serverSocket = None

        self.cleanChannelList()
        self.currChannel = None

        self.serverConnectButton.config(state=tk.NORMAL)
        self.serverDisconnectButton.config(state=tk.DISABLED)

    def joinChannel(self):
        curSelec = self.channelList.curselection()
        if not curSelec:
            return False

        channelIndex = curSelec[0]

        i = -1
        for channelName in self.channels:
                i += 1
                if i == channelIndex:
                    break
        self.hSC.joinChannel(channelName)

    def createChannel(self):
        self.cleanInfo()

        channelName = self.channelNameVar.get().strip()
        if (len(channelName)) < 1:
            self.displayInfo('Please enter a name to create a channel')
            return False
        if not self.hSC:
            self.displayInfo('You must be connected to create a channel')
            return False

        self.hSC.createChannel(channelName)

    def setCurrChannel(self, data, socket):
        channelName = data['name']

        if not self.currChannel == channelName:
            self.currChannel = data['name']
            self.hasChannelChange = True
            self.cleanMessages()
        else:
            self.currChannel = data['name']
            self.hasChannelChange = True

    def startPeers(self, data, socket):
        # if self.hasChannelChange:
        self.hasChannelChange = False
        self.stopCurrPeers()
        self.startNewPeers()

    def stopCurrPeers(self):
        print('On stop les anciens peers')
        pass

    def startNewPeers(self):
        clients = self.channels[self.currChannel]['clients']
        for client in clients:
            if not self.isItMe(client):
                toClient = client.copy()
                try:
                    toClientAddPort = (client['ip'], int(client['tcpPort']))
                    socket = s.socket(s.AF_INET, s.SOCK_STREAM)

                    toClient['socket'] = socket
                    self.channelsSockets[self.currChannel] = []
                    self.channelsSockets[self.currChannel].append(toClient)

                    socket.connect(toClientAddPort)
                    toClient['connection'] = hTCC(self, socket)
                    toClient['connection'].start()
                except Exception as e:
                    print(e)
                    self.displayError('Can\'t establish a connection to the client {}:{} : {}'.format(client['ip'], client['tcpPort'], str(e)))
                else:
                    print('OK on est connecte a {}'.format(toClient['username']))
                    print(self.channelsSockets)


    def isItMe(self, client):
        if self.username == client['username'] and self.ports[0] == client['tcpPort']:
            return True
        return False

    def displayChannelList(self, data, socket):
        self.channels = data
        self.cleanChannelList()

        i = -1
        loop = True
        for channelName in data:
            self.channelList.insert(tk.END, channelName)
            if loop:
                i += 1
                if channelName == self.currChannel:
                    print('currChannel = {}'.format(channelName))
                    loop = False

        print('currChannel = {}'.format(i))
        self.channelList.select_set(i)
        self.displayUsersList()

    def cleanChannelList(self):
        self.channelList.delete(0, tk.END)


    def displayUsersList(self):
        self.cleanUsersList()
        clients = self.channels[self.currChannel]['clients']
        for client in clients:
            self.usersList.insert(tk.END, '{} ({}:{})'.format(client['username'], client['ip'], client['tcpPort']))

    def cleanUsersList(self):
        self.usersList.delete(0, tk.END)

    def sendMessage(self):
        message = self.messageVar.get().strip()
        if len(message) < 1:
            return False

        jsonMsg = json.dumps({
            'action': 'incomingMessage',
            'data': {
                'username': self.username,
                'channel': self.currChannel,
                'message': message,
                'tcpPort': self.ports[0]
            }
        })

        if not self.currChannel in self.channelsMessages:
            self.channelsMessages[self.currChannel] = []

        self.channelsMessages[self.currChannel].append('<{}> : {}'.format(self.username, message))
        self.displayMessages()

        if self.currChannel in self.channelsSockets:
            for client in self.channelsSockets[self.currChannel]:
                client['connection'].sendTextMessage(jsonMsg)

    def receiveMessage(self, data, socket):
        if self.currChannel == data['channel']:
            if not self.currChannel in self.channelsMessages:
                self.channelsMessages[data['channel']] = []
            self.channelsMessages[data['channel']].append('<{} {}:{}> : {}'.format(data['username'], socket.getpeername()[0], data['tcpPort'], data['message']))
            self.displayMessages()

    def displayMessages(self):
        self.messagesList.insert(tk.END, self.channelsMessages[self.currChannel][-1])

    def cleanMessages(self):
        self.messagesList.delete(0, tk.END)

    # GUI
    def createGUI(self):
        gui = tk.Tk()
        gui.wm_title('Python_Bahamas Client')
        gui.columnconfigure(0, weight=1)
        gui.rowconfigure(0, weight=1)

        # Set guiMenubar as the window menu
        guiMenubar = self.createMenu(gui)
        gui.config(menu=guiMenubar)

        # Create a parent frame to hold the content
        parentFrame = tk.Frame(gui)
        parentFrame.grid(padx=25, pady=10, sticky='NSWE', row=0, column=0)
        parentFrame.columnconfigure(0, weight=1)
        parentFrame.rowconfigure(1, weight=1)

        # Create a frame to hold the server block
        self.addHeadBlock(parentFrame)

        # Create a frame to hold the big block
        self.addBigBlock(parentFrame)

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

    def exitApp(self):
        self._gui.destroy()

    def displayAbout(self):
        msgbox.showinfo('About', 'Powered by laidet_r & cherbi_r\nSDM 2017 All rights reserved')

    def addServerBlock(self, parentFrame):
        serverLabelFrame = tk.LabelFrame(parentFrame, text="Server", padx=10, pady=5, bg="green")
        parentFrame.columnconfigure(1, weight=1)
        serverLabelFrame.grid(sticky='NSWE', row=0, column=1)

        # Label and Entry for the server addr
        serverAddrLabel = tk.Label(serverLabelFrame, text='Address :')
        self.serverAddrVar = tk.StringVar()
        self.serverAddrVar.set('127.0.0.1')
        serverAddrEntry = tk.Entry(serverLabelFrame, textvariable=self.serverAddrVar)
        serverAddrLabel.grid(row=0, column=0)
        serverAddrEntry.grid(row=0, column=1)

        # Label and Entry for the server port
        serverPortLabel = tk.Label(serverLabelFrame, text='Port :')
        self.serverPortVar = tk.StringVar()
        self.serverPortVar.set(4200)
        serverPortEntry = tk.Entry(serverLabelFrame, textvariable=self.serverPortVar)
        serverPortLabel.grid(row=0, column=2)
        serverPortEntry.grid(row=0, column=3)


        # Buttons to command the server
        self.serverConnectButton = tk.Button(serverLabelFrame, text='Connect', command=self.connectToServer)
        self.serverDisconnectButton = tk.Button(serverLabelFrame, text='Disconnect', state=tk.DISABLED, command=self.disconnectFromServer)
        self.serverConnectButton.grid(row=0, column=4)
        self.serverDisconnectButton.grid(row=0, column=5)

        self.serverStatusLabel = tk.Label(serverLabelFrame, text="")
        self.serverStatusLabel.grid(sticky='W', row=1, columnspan=10)

        self.serverErrorLabel = tk.Label(serverLabelFrame, text="")
        self.serverErrorLabel.grid(sticky='W', row=2, columnspan=10)

    def addHeadBlock(self, parentFrame):
        headBlockFrame = tk.Frame(parentFrame, bg="green")
        headBlockFrame.grid(sticky='WE', row=0, column=0)

        self.addSettingsBlock(headBlockFrame)
        self.addServerBlock(headBlockFrame)

    def addSettingsBlock(self, parentFrame):
        settingsLabelFrame = tk.LabelFrame(parentFrame, text="Settings", padx=10, pady=5, bg="green")
        parentFrame.columnconfigure(0, weight=1)
        settingsLabelFrame.grid(sticky='NSWE', row=0, column=0)

        # Label and Entry for the server addr
        tcpPortLabel = tk.Label(settingsLabelFrame, text='TCP port :')
        self.tcpPortVar = tk.StringVar()
        self.tcpPortVar.set('5000')
        tcpPortEntry = tk.Entry(settingsLabelFrame, textvariable=self.tcpPortVar)
        tcpPortLabel.grid(row=0, column=0)
        tcpPortEntry.grid(row=0, column=1)

        # Label and Entry for the server port
        udpPortLabel = tk.Label(settingsLabelFrame, text='UDP port :')
        self.udpPortVar = tk.StringVar()
        self.udpPortVar.set('5001')
        udpPortEntry = tk.Entry(settingsLabelFrame, textvariable=self.udpPortVar)
        udpPortLabel.grid(row=1, column=0)
        udpPortEntry.grid(row=1, column=1)

        # Label and Entry for the username
        usernameLabel = tk.Label(settingsLabelFrame, text='Username :')
        self.usernameVar = tk.StringVar()
        self.usernameVar.set('Bobby')
        usernameEntry = tk.Entry(settingsLabelFrame, textvariable=self.usernameVar)
        usernameLabel.grid(row=2, column=0)
        usernameEntry.grid(row=2, column=1)


    def addBigBlock(self, parentFrame):
        bigBlockFrame = tk.Frame(parentFrame, bg="red")
        bigBlockFrame.grid(sticky='NSWE', row=1, column=0)
        bigBlockFrame.rowconfigure(0, weight=1)

        self.addLeftBLock(bigBlockFrame)
        self.addRightBlock(bigBlockFrame)

    def addLeftBLock(self, parentFrame):
        leftBlockFrame = tk.Frame(parentFrame, bg="blue")
        parentFrame.columnconfigure(0, weight=1)
        leftBlockFrame.grid(sticky="NSWE", row=0, column=0, padx=10, pady=10)
        leftBlockFrame.columnconfigure(0, weight=1)

        self.addChannelsBlock(leftBlockFrame)
        self.addAddChannelsBlock(leftBlockFrame)

    def addChannelsBlock(self, parentFrame):
        channelsFrame = tk.Frame(parentFrame, bg="pink")
        parentFrame.rowconfigure(0, weight=4)
        channelsFrame.grid(sticky="NSWE", row=0, column=0)

        # Title of the block
        channelsLabel = tk.Label(channelsFrame, text="Channels", padx=10, pady=5, bg="green")
        channelsFrame.columnconfigure(0, weight=1)
        channelsLabel.grid(sticky="WE", row=0, column=0)

        # Channel list
        self.channelList = tk.Listbox(channelsFrame, selectmode='Single')
        channelsFrame.rowconfigure(1, weight=1)
        self.channelList.grid(sticky="NSWE", row=1, column=0)

        # Join button
        self.joinChannelButton = tk.Button(channelsFrame, text="Join", command=self.joinChannel)
        self.joinChannelButton.grid(row=2, column=0)

    def addAddChannelsBlock(self, parentFrame):
        addChannelsFrame = tk.Frame(parentFrame, bg="magenta")
        parentFrame.rowconfigure(1, weight=0)
        addChannelsFrame.grid(sticky='NSWE', row=1, column=0)

        addChannelsLabelFrame = tk.LabelFrame(addChannelsFrame, text="Create a channel")
        addChannelsFrame.columnconfigure(0, weight=1)
        addChannelsFrame.rowconfigure(0, weight=1)
        addChannelsLabelFrame.grid(row=0, column=0)

        self.channelNameVar = tk.StringVar()
        channelNameEntry = tk.Entry(addChannelsLabelFrame, textvariable=self.channelNameVar)
        self.createChannelButton = tk.Button(addChannelsLabelFrame, text="Create", command=self.createChannel)
        channelNameEntry.grid(row=0, column=0)
        self.createChannelButton.grid(row=0, column=1)

    def addRightBlock(self, parentFrame):
        rightBlockFrame = tk.Frame(parentFrame, bg="yellow")
        parentFrame.columnconfigure(1, weight=4)
        rightBlockFrame.grid(sticky="NSWE", row=0, column=1)

        self.addChatInfosBlock(rightBlockFrame)
        self.addChatBlock(rightBlockFrame)
        self.addChatInputBlock(rightBlockFrame)

    def addChatInfosBlock(self, parentFrame):
        chatInfosBlockFrame = tk.Frame(parentFrame, bg='orange', padx=10, pady=10)
        parentFrame.columnconfigure(0, weight=1)
        chatInfosBlockFrame.grid(sticky='NSWE', row=0, column=0)

        chatInfosLabelFrame = tk.LabelFrame(chatInfosBlockFrame, text="Chat infos")
        chatInfosBlockFrame.columnconfigure(0, weight=1)
        chatInfosLabelFrame.grid(sticky='NSEW', row=0, column=0)
        self.chatInfosLabel = tk.Label(chatInfosLabelFrame, text="")
        self.chatInfosLabel.grid(sticky='W')

    def addChatBlock(self, parentFrame):
        chatBlockFrame = tk.Frame(parentFrame, padx=10, pady=5)
        parentFrame.rowconfigure(1, weight=1)
        chatBlockFrame.grid(sticky='NSEW', row=1, column=0)

        chatBlockFrame.rowconfigure(0, weight=1)
        self.addChatUsersBlock(chatBlockFrame)
        self.addChatMessagesBlock(chatBlockFrame)

    def addChatUsersBlock(self, parentFrame):
        chatUsersBlockFrame = tk.Frame(parentFrame)
        parentFrame.columnconfigure(0, weight=1)
        chatUsersBlockFrame.grid(sticky='NSEW', row=0, column=0)

        # Title of the block
        usersLabel = tk.Label(chatUsersBlockFrame, text="Users", padx=10, pady=5, bg="green")
        chatUsersBlockFrame.columnconfigure(0, weight=1)
        usersLabel.grid(sticky="WE", row=0, column=0)

        # Users list
        self.usersList = tk.Listbox(chatUsersBlockFrame, selectmode='Single')
        chatUsersBlockFrame.rowconfigure(1, weight=1)
        self.usersList.grid(sticky="NSWE", row=1, column=0)

    def addChatMessagesBlock(self, parentFrame):
        chatMessagesBlockFrame = tk.Frame(parentFrame, bg='limegreen')
        parentFrame.columnconfigure(1, weight=8)
        chatMessagesBlockFrame.grid(sticky='NSEW', row=0, column=1)

        # Title of the block
        messagesLabel = tk.Label(chatMessagesBlockFrame, text="Messages", padx=10, pady=5, bg="brown")
        chatMessagesBlockFrame.columnconfigure(0, weight=1)
        messagesLabel.grid(sticky="WE", row=0, column=0)

        # Users list
        self.messagesList = tk.Listbox(chatMessagesBlockFrame, selectmode='Single')
        chatMessagesBlockFrame.rowconfigure(1, weight=1)
        self.messagesList.grid(sticky="NSWE", row=1, column=0)

    def addChatInputBlock(self, parentFrame):
        chatInputBlockFrame = tk.Frame(parentFrame, bg='cyan', padx=15, pady=5)
        chatInputBlockFrame.grid(sticky='NSWE', row=2, column=0)

        self.messageVar = tk.StringVar()
        messageEntry = tk.Entry(chatInputBlockFrame, textvariable=self.messageVar)
        self.sendMessageButton = tk.Button(chatInputBlockFrame, text="Send", command=self.sendMessage)
        chatInputBlockFrame.columnconfigure(0, weight=1)
        messageEntry.grid(sticky='EW', row=0, column=0)
        self.sendMessageButton.grid(row=0, column=1)

    def displayError(self, message):
        self.serverErrorLabel.config(text='ERROR: {}'.format(message))

    def cleanError(self):
        self.serverErrorLabel.config(text='')

    def displayInfo(self, message):
        self.chatInfosLabel.config(text=message)

    def cleanInfo(self):
        self.chatInfosLabel.config(text='')


    def startGUI(self):
        self._gui.mainloop()

client = Client()
client.startGUI()