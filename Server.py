#!/usr/bin/env python3

from tkinter import *
import tkinter.messagebox as msgbox
from threading import Thread

class Server(Thread):
    def __init__(self):
        Thread.__init__(self)

        self.status = 'offline'
        self._gui = self.createGUI()

    def createGUI(self):
        gui = Tk()
        gui.wm_title('Python_Bahamas Server')
        gui.grid_columnconfigure(0, weight=1)

        # Set guiMenubar as the window menu
        guiMenubar = self.createMenu(gui)
        gui.config(menu=guiMenubar)

        # Create a parent frame to hold the content
        parentFrame = Frame(gui)
        parentFrame.grid(padx=25, pady=10, sticky=N+S+W+E)
        parentFrame.grid_columnconfigure(0, weight=1)

        # Create a frame to hold the server status
        self.addServerStatus(parentFrame)

        # Create the command block
        self.addCommandBlock(parentFrame)

        return gui

    def createMenu(self, gui):
        # Create the main GUI menu, to hold tabs
        guiMenubar= Menu(gui)

        # Create and add the File menu
        fileMenu = self.createFileMenu(guiMenubar)
        guiMenubar.add_cascade(label='File', menu=fileMenu)

        # Create and add the Help menu
        helpMenu = self.createHelpMenu(guiMenubar)
        guiMenubar.add_cascade(label='Help', menu=helpMenu)

        return guiMenubar

    def createFileMenu(self, menubar):
        fileMenu = Menu(menubar, tearoff=0)
        fileMenu.add_command(label='Quit', command=self.exitServer)

        return fileMenu

    def createHelpMenu(self, menubar):
        helpMenu = Menu(menubar, tearoff=0)
        helpMenu.add_command(label='About', command=self.displayAbout)

        return helpMenu

    def addServerStatus(self, parentFrame):
        self.statusLabelFrame = LabelFrame(parentFrame, text="Server status", padx=20, pady=20)
        self.statusLabelFrame.grid(sticky=W+E)

        self.statusLabel = Label(self.statusLabelFrame, text="The Python_Bahamas Server is currently {}".format(self.status))
        self.statusLabel.grid(row=0, column=0)

    def addCommandBlock(self, parentFrame):
        print('Wallah')

    def updateStatus(self, message):
        self.statusLabel.config(text=message)

    def startGUI(self):
        self._gui.mainloop()

    # def startServer(self):
        # self.start()

    def exitServer(self):
        self._gui.destroy()

    def displayAbout(self):
        msgbox.showinfo('About', 'Powered by laidet_r & cherbi_r\nSDM 2017 All rights reserved')


server = Server()
server.startGUI()