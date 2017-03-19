#!/usr/bin/env python3

from tkinter import *
import tkinter.messagebox as msgbox
from threading import Thread

class Server(Thread):
    def __init__(self):
        self._gui = self.createGUI()


    def createGUI(self):
        gui = Tk()

        gui.wm_title('Python_Bahamas Server')

        # Set guiMenubar as the window menu
        guiMenubar = self.createMenu(gui)
        gui.config(menu=guiMenubar)

        # Display the server status
        self.status = StringVar()
        self.status.set('offline')
        self.displayServerStatus(gui)

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

    def displayServerStatus(self, gui):
        l = LabelFrame(gui, text="Server status", padx=20, pady=20)
        l.pack(fill="both", expand="yes")

        Label(l, text="The Python_Bahamas Server is currently").grid(row=0, column=0)
        Label(l, textvariable=self.status).grid(row=0, column=1)

    def startGUI(self):
        self._gui.mainloop()

    def exitServer(self):
        self._gui.destroy()

    def displayAbout(self):
        msgbox.showinfo('About', 'Powered by laidet_r & cherbi_r\nSDM 2017 All rights reserved')


server = Server()
server.startGUI()