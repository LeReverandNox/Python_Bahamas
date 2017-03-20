#!/usr/bin/env python3
# pylint: disable=line-too-long

import tkinter as tk
import tkinter.messagebox as msgbox
import socket as s
from Tools import Tools as t
from Threads.HandleSocket import HandleSocket as hS

class Server:
    def __init__(self):
        # Attributes
        # GUI
        self.statusLabel = None
        self.errorLabel = None
        self.serverPortVar = None
        self.startButton = None
        self.stopButton = None

        # Server
        self.serverSocket = None
        self.status = 'offline'
        self.hS = None
        self.addrPort = ()

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
            port = t.isPortValid(self.serverPortVar.get())
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

        self.stopButton.config(state=tk.DISABLED)
        self.startButton.config(state=tk.NORMAL)

        self.status = 'offline'
        self.updateStatus('The Python_Bahamas Server is currently {}'.format(self.status))

    def exitApp(self):
        self._gui.destroy()

    def displayAbout(self):
        msgbox.showinfo('About', 'Powered by laidet_r & cherbi_r\nSDM 2017 All rights reserved')


server = Server()
server.startGUI()