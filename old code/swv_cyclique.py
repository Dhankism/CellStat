# -*- coding: utf-8 -*-
"""
Created on Tue Jun 15 10:52:44 2021

@author: anis
"""

# If debug is enabled, do not attempt to open serial port
DEBUG = True

import serial, time, math
import time
import numpy as np
import matplotlib.pyplot as plt
import sys
from PyQt5.QtWidgets import * 
from PyQt5.QtGui import * 
from PyQt5.QtCore import * 
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


from volta import Fenetre1

from swv import Fenetre
#**********************************************************
#* declaratoin de la class qui herite de la class Qwidget *
#**********************************************************


class Fenetre2(QWidget):

    def __init__(self):
        #PORT_BOARD = "/dev/cu.usbmodem"         # for MAC CPU
        self.PORT_BOARD = "COM"                     # for PC CPU
        #self.PORT_BOARD="/dev/ttyACM"                # for linux
        self.BAUD_RATE =  115200
        self.TIME_OUT = 30
        #self.PORT_TEENSY  = "/dev/cu.usbmodem6837991"
        self.DELAY_1s  = 1

  
        QWidget.__init__(self) # initialisation du qwidget


        vbox = QVBoxLayout()
        hbox = QHBoxLayout()

        self.rb1 = QRadioButton("SWV", self)
        self.rb1.toggled.connect(self.updateLabel)

        self.rb2 = QRadioButton("CV", self)
        self.rb2.toggled.connect(self.updateLabel)

        #self.rb3 = QRadioButton("quite", self)
        #self.rb3.toggled.connect(self.updateLabel)
        
        #self.rb3.toggled.connect(self.close)
        
        # self.label =QLabel(" Enter the port's number (Return => default port) : ")
        # self.champ = QLineEdit()


        hbox.addWidget(self.rb1)
        hbox.addWidget(self.rb2)
        #hbox.addWidget(self.rb3)
        
        # vbox.addWidget(self.label)
        # vbox.addWidget(self.champ)
        vbox.addSpacing(10)
        
        layout = QGridLayout()
        layout.addLayout(hbox,0,0)
        layout.addLayout(vbox,0,1)
        self.setLayout(layout)

        self.setGeometry(300, 300, 350, 250)
        self.setWindowTitle('Choose Method')

    def updateLabel(self):
        global received,var

        if self.rb1.isChecked():
            received="SquareWave"
            self.close()
        if self.rb2.isChecked():
            received="VoltaCyclique"
            self.close()


            
            
            
var=""           
app = QApplication.instance() 
if not app:
            app = QApplication(sys.argv)
fen2 = Fenetre2()
fen2.show()
app.exec_()
time.sleep(2)
if received=="SquareWave":
    app = QApplication.instance() 
    if not app:
                app = QApplication(sys.argv)
    fen1 = Fenetre()
    fen1.show()
    app.exec_()
elif received=="VoltaCyclique":
        app = QApplication.instance() 
        if not app:
            app = QApplication(sys.argv)
        fen = Fenetre1()
        fen.show()
        app.exec_()

   
    