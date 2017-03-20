#!/usr/bin/env python3
# pylint: disable=line-too-long

import tkinter as tk
import tkinter.messagebox as msgbox
from threading import Thread

class Server(Thread):
    def __init__(self):
        Thread.__init__(self)
        # Attributes
        self.statusLabel = None
        self.serverPortVar = None
        self.startButton = None
        self.stopButton = None

        self.status = 'offline'
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
        self.statusLabel.grid()

    def addCommandBlock(self, parentFrame):
        commandsLabelFrame = tk.LabelFrame(parentFrame, text="Commands", padx=20, pady=20)
        commandsLabelFrame.grid(sticky='WE')

        # Label and Entry for the server port
        serverPortLabel = tk.Label(commandsLabelFrame, text='Port :')
        self.serverPortVar = tk.IntVar()
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

    def startGUI(self):
        self._gui.mainloop()

    def startServer(self):
        self.startButton.config(state=tk.DISABLED)
        self.stopButton.config(state=tk.NORMAL)
        self.start()
        print('On veut run le serveur sur le port {}'.format(self.serverPortVar.get()))

    def stopServer(self):
        self.stopButton.config(state=tk.DISABLED)
        self.startButton.config(state=tk.NORMAL)
        print('On stoppe le serveur')

    def exitApp(self):
        self._gui.destroy()

    def displayAbout(self):
        msgbox.showinfo('About', 'Powered by laidet_r & cherbi_r\nSDM 2017 All rights reserved')


server = Server()
server.startGUI()