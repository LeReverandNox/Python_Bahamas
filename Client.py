#!/usr/bin/env python3
# pylint: disable=line-too-long

import tkinter as tk
import tkinter.messagebox as msgbox
import socket as s

class Client:
    def __init__(self):
        # Attributes
        # GUI
        self.serverStatusLabel = None
        self.serverErrorLabel = None
        self.serverAddrVar = None
        self.serverPortVar = None
        self.serverConnectButon = None
        self.serverDisconnectButton = None
        self.joinChannelButton = None
        self.channelList = None
        self.channelNameVar = None
        self.createChannelButton = None

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
        self.addServerBlock(parentFrame)

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
        serverLabelFrame.grid(sticky='WE', row=0, column=0)

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
        self.serverConnectButon = tk.Button(serverLabelFrame, text='Connect', command=self.connectToServer)
        self.serverDisconnectButton = tk.Button(serverLabelFrame, text='Disconnect', state=tk.DISABLED, command=self.disconnectFromServer)
        self.serverConnectButon.grid(row=0, column=4)
        self.serverDisconnectButton.grid(row=0, column=5)

        self.serverStatusLabel = tk.Label(serverLabelFrame, text="")
        self.serverStatusLabel.grid(sticky='W')

        self.serverErrorLabel = tk.Label(serverLabelFrame, text="")
        self.serverErrorLabel.grid(sticky='W')

    def connectToServer(self):
        pass
    def disconnectFromServer(self):
        pass

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

    def joinChannel(self):
        pass
    def createChannel(self):
        pass

    def startGUI(self):
        self._gui.mainloop()

client = Client()
client.startGUI()