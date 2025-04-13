

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

class Fenetre1(QWidget):
        def __init__(self):# declaration du constructeur
                #**************************
                # declaration des atribue *
                #**************************
                #################################################"
                #self.PORT_ARDUINO = "/dev/cu.usbmodem641"
                #self.PORT_TEENSY  = "/dev/cu.usbmodem6837991"
                #self.PORT_BOARD = "/dev/cu.usbmodem"         # for MAC CPU
                #self.PORT_BOARD="/dev/ttyACM"                # for linux
                self.PORT_BOARD = "COM"                     # for PC CPU
                self.BAUD_RATE =  115200
                self.TIME_OUT = 5
                
                self.EMPTY    = ""
                self.BOARD    = "BOARD"
                #************************************************
                self.ACQ      = "ACQ"
                self.CMD_ACQ  ="  = Start Acquisition"
                #************************************************
                self.CMD      = "CMD"
                self.CMD_CMD  = "  = Print Commands available"
                #************************************************
                self.FILE     = "FILE"
                self.CMD_FILE = " = Set File index"
                #************************************************
                self.PAR      = "PAR"
                self.CMD_PAR  = "  = Print Parameters"
                #************************************************
                self.TRA      = "TRA"
                self.CMD_TRA  = "  = Plot the acquisition data"
                #************************************************
                self.RTIA     = "RTIA"
                self.CMD_RTIA = " = Set RTIA value"
                #************************************************
                self.UNIT     = "UNIT"
                self.CMD_UNIT = " = Set current unit value"
                #************************************************
                self.SET      = "SET"
                self.DEF      = ""
                #************************************************
                self.EXIT     = "EXIT"
                self.CMD_EXIT = " = Exit the script "
                #************************************************
                
                self.CMD_KEY = {self.ACQ: self.CMD_ACQ, self.CMD: self.CMD_CMD, self.FILE: self.CMD_FILE, self.PAR: self.CMD_PAR, self.TRA: self.CMD_TRA, self.RTIA: self.CMD_RTIA, self.UNIT: self.CMD_UNIT, self.DEF: self.EMPTY, self.EXIT: self.CMD_EXIT}
                self.CMD_AVA = {self.ACQ: self.CMD_ACQ, self.CMD: self.CMD_CMD, self.FILE: self.CMD_FILE, self.PAR: self.CMD_PAR, self.TRA: self.CMD_TRA, self.RTIA: self.CMD_RTIA, self.UNIT: self.CMD_UNIT, self.DEF: self.EMPTY, self.EXIT: self.CMD_EXIT}
                self.CMD_AVA.pop(self.ACQ) # Command ACQ not available at start up
                self.CMD_AVA.pop(self.TRA) # Command TRA not available at start up
                #print(CMD_AVA)
                
                
                self.BOARD_DETECTED = " board detected on "
                self.ARDUINO  = "Arduino"
                self.TEENSY   = "Teensy"
                self.NEW_LINE = "\n"
                self.COMMA    = ","
                self.ACQ_START  = "Acquisition Started"
                self.ACQ_END    = "Acquisition Ended "
                self.TRA_START  = "Tracing Started "
                self.TRA_END    = "Tracing Ended "
                self.INVITE = ">>"
                self.QUOTE  = '"'
                self.EQUAL  = '='
                self.UNDEFINED = "-"
                self.WARNING = [self.EMPTY,self.EMPTY,self.EMPTY,self.EMPTY,self.EMPTY,self.EMPTY,self.EMPTY,self.EMPTY]
                self.WARNING[0]  ="********************************************************************" 
                self.WARNING[1]  ="*   WARNING - You have reached the MAXIMUM number of acquisition   *" 
                self.WARNING[2]  ="*   WARNING -    You can't set up a new acquisition right now      *"
                self.WARNING[3]  ="*   WARNING -        Your FILES will be overwritten                *"
                self.WARNING[4]  ="*   WARNING -            Your DATA will be LOST                    *"
                self.WARNING[5]  ="*   WARNING - Consider CLOSING this program and OPENNING it again  *"
                self.WARNING[6]  ="*   WARNING -        The only available Command is TRA             *"
                self.WARNING[7]  ="********************************************************************" + self.NEW_LINE
                self.MAX_ACQ     = 16
                self.MAX_CYCLE   = 3
                self.NB_PARAM    = 5
                self.acq_time=""
                self.DELAY_01s = 0.1
                self.DELAY_1s  = 1
                self.CODE_STEP = 1
                
                self.QUANT_PWM           = 0.0200513
                self.OFFSET_PWM          = 128.
                self.QUANT_DAC_ARDUINO   = 5./4096.
                self.OFFSET_DAC_ARDUINO  = 2048
                self.QUANT_ADC_ARDUINO   = 5./4095
                self.OFFSET_ADC_ARDUINO  = 2048
                self.COEFF_CONV_ARDUINO  = 1.0
                self.CONV_PERIOD_ARDUINO = 1000.             # in order to convert in ms
                self.DELAY_STAB_ARDUINO  = 2.0
                
                self.QUANT_DAC_TEENSY    = 1./800.33      # extracted from calibration process
                self.OFFSET_DAC_TEENSY   = 2069           # extracted from calibration process
                self.QUANT_ADC_TEENSY    = 3.33/4095
                self.OFFSET_ADC_TEENSY   = 2043.0
                self.COEFF_CONV_TEENSY   = 5/3.3              # inverse of the output voltage divider
                self.CONV_PERIOD_TEENSY  = 1.0 * 1000000.    # in order to convert in micros and take care of the first stage gain
                self.DELAY_STAB_TEENSY   = 2.0
                
                self.R10k         = 10000.0
                self.RTIA_ARDUINO =  1000.0                   # to be change to the right value
                self.RTIA_TEENSY  =  100000.0
                self.KOHM         =  1000.0
                self.CODE_MAX_RTIA = 255
                self.CODE_MIN_RTIA =  12
                
                self.COEFF_mA     =          1000.0             # scale in mA
                self.COEFF_microA =       1000000.0             # scale in microA
                self.COEFF_nA     =    1000000000.0             # scale in nA
                self.COEFF_pA     = 1000000000000.0             # scale in pA
                
                self.resistorlabels = ["±2.5mA", "±.25mA", "±25uA", "±2.5uA", "±.25uA", "±72uA", "±25nA", "±2.5nA"]
                self.resistorvalues = [value*self.KOHM for value in [1, 10, 100, 1000, 10000, 30000, 100000, 1000000]]
                self.Capacitorlabels = ["2p", "20p", "50p", "100p", "200p", "1n", "50n", "100n"]
                self.capindex=0
                self.ritaindex=0
                #***********************
                #* File name to modify *
                #***********************
                self.FILE_NAME_TEENSY   = "test"
                self.FILE_NAME_ARDUINO  = "/Users/eliecampagnolo/Documents/Python/Tst_Python_Arduino"
                self.FILE_EXTENT = ".txt"
                self.READ_MODE  = "r"
                self.WRITE_MODE = "w"
                self.UTF_8      = "utf-8"
                
                #****************************
                #* Array for data from file 
                #****************************
                self.x = []
                self.y = []
                self.x_data = [[[] for j in range(self.MAX_CYCLE)] for i in range(self.MAX_ACQ)]
                self.y_data = [[[] for j in range(self.MAX_CYCLE)] for i in range(self.MAX_ACQ)]
                     
                #****************************
                #* Array cycle and colors 
                #****************************        
                self.nb_mes_cycle = [0,0,0,0]
                self.nb_acq_cycle = [0,0,0,0]
                self.gra_color =["b","g","r"]
                
                #****************************
                #* Array for PARAMETERS     *
                #****************************
                self.params = [self.UNDEFINED,self.UNDEFINED,self.UNDEFINED,self.UNDEFINED,self.UNDEFINED,self.UNDEFINED,self.UNDEFINED]
                self.param  = [[self.UNDEFINED,self.UNDEFINED,self.UNDEFINED,self.UNDEFINED,self.UNDEFINED] for  i in range(self.MAX_ACQ)]   # maximum 16 sets of parameters
                self.rtia_val=""
                self.port_board=""
                self.cmd_code = ""
                self.nb_cycle=0
                self.index_file=0
                self.index_acq=0
                self.str_unit=""
                self.fichier=""
                self.liaison=True
                
                ##########################################################"
                QWidget.__init__(self) # initialisation du qwidget
                self.toolBar = QToolBar() # creation du toolbar
                
                self.label =QLabel(" Enter the port's number (Return => default port) : ") # creation du qlabel
                self.champ = QLineEdit() # creation de QlineEdit pour rentrer les information
                
                self.label2 = QLabel(" Enter the i range (Return => ±20uA) : ") # creation du qlabel
               # self.champ2 = QLineEdit() # creation de QlineEdit pour rentrer les information
                
                self.radioGroup = QButtonGroup()  # Create a button group for radio buttons
                self.radioButtons = []  # List to store the radio buttons
                # Create 8 radio buttons and add them to the button group
              
                for i , label in enumerate(self.resistorlabels):
                        radioBtn = QRadioButton(label)
                        self.radioGroup.addButton(radioBtn)
                        self.radioButtons.append(radioBtn)
                
                self.labelq = QLabel(" Enter the Cap value in F (Return => 200 pF): ") # creation du qlabel
          
                self.radioGroup1 = QButtonGroup()  # Create a button group for radio buttons
                self.radioButtons1 = []  # List to store the radio buttons
                # Create 8 radio buttons and add them to the button group
                
                for i, label in enumerate(self.Capacitorlabels):
                        radioBtn1 = QRadioButton(label)
                        self.radioGroup1.addButton(radioBtn1)
                        self.radioButtons1.append(radioBtn1)

                
                
                self.label3 = QLabel(text=" Enter the curent unit (mA, uA, nA or pA) (Return => uA) : ") # creation du qlabel
                self.champ3 = QLineEdit()# creation de QlineEdit pour rentrer les information


                #self.label4 = QLabel(text=" Enter a number for the starting of indexing file (Return => 0) : ")
                #self.champ4 = QLineEdit()

                self.label5 = QLabel(text=" Enter the file name ( test is the default name )") # creation du qlabel
                self.champ5 = QLineEdit() # creation de QlineEdit pour rentrer les information
                
                self.label6 = QLabel(text=" Enter the number of cycles") # creation du qlabel
                self.champ6 = QLineEdit() # creation de QlineEdit pour rentrer les information
                
                self.label7 = QLabel(text=" Enter the start potential") # creation du qlabel
                self.champ7 = QLineEdit() # creation de QlineEdit pour rentrer les information
                
                self.label8 = QLabel(text=" Enter the first inversion potential") # creation du qlabel
                self.champ8 = QLineEdit() # creation de QlineEdit pour rentrer les information
                
                self.label9 = QLabel(text=" Enter the second inversion potential") # creation du qlabel
                self.champ9 = QLineEdit() # creation de QlineEdit pour rentrer les information
                
                self.label10 = QLabel(text=" Enter the scan speed") # creation du qlabel
                self.champ10 = QLineEdit() # creation de QlineEdit pour rentrer les information

                self.figure = plt.Figure() # creation de la figure
                self.canvas = FigureCanvas(self.figure) # creation du canvas qui prend comme argument la figure
                self.ax = self.figure.add_subplot(111) # creation des ax
                
                layout = QGridLayout() # creation du layoutgrid
                # création du bouton
                self.bouton = QPushButton("Start")
                self.bouton.clicked.connect(self.principal) # relier le boutton avec la fonction principal qui s'excute quand on clic sur le boutton
                

               # menubar = QMenuBar() # creation du Qmenubar
                #fileMenu = menubar.addMenu("file") # ajouter un menu qui s'appel file a ce menu bar
                #saveAction = QAction("Save", self) # creation d'une action 
                #fileMenu.addAction(saveAction) # ajouter l'action au menu file
                #saveAction.triggered.connect(self.save) 

                self.button = QPushButton("Save")
                self.button.clicked.connect(self.save)# on connecter l'action a la fonction save si il y une action sur save action on declanche la fonction save
      
                self.image = QImage(self.size(), QImage.Format_RGB32) # creation d'une image format_RGB32
                self.image.fill(Qt.white)
                
                topLayout = QVBoxLayout() # creation  du QVBoxLayout
                topLayout.addWidget(self.label6) # ajouter le label6 a ce layout
                topLayout.addWidget(self.label7) # ajouter le label7 a ce layout
                topLayout.addWidget(self.label8) # ajouter le label8 a ce layout
                topLayout.addWidget(self.label9) # ajouter le label9 a ce layout
                topLayout.addWidget(self.label10) # ajouter le label10 a ce layout
                
                topLayout1 = QVBoxLayout() # creation  du QVBoxLayout
                topLayout1.addWidget(self.champ6)  # ajouter le champ6 ( qLinEedit ) a ce layout
                topLayout1.addWidget(self.champ7) # ajouter le champ7 ( qLinEedit ) a ce layout
                topLayout1.addWidget(self.champ8) # ajouter le champ8 ( qLinEedit ) a ce layout
                topLayout1.addWidget(self.champ9) # ajouter le champ9 ( qLinEedit ) a ce layout
                topLayout1.addWidget(self.champ10) # ajouter le champ10 ( qLinEedit ) a ce layout
              
                topLayout4 = QVBoxLayout() # creation  du QVBoxLayout
                #topLayout4.addWidget(menubar)   # ajouter menu bar a la position (0,0) et prend toute la largeur
                topLayout4.addWidget(self.label) # ajouter le label a ce layout
                topLayout4.addWidget(self.label2)
                topLayout4.addWidget(self.labelq) # ajouter le label2 a ce layout
                topLayout4.addWidget(self.label3) # ajouter le label3 a ce layout
                #topLayout4.addWidget(self.label4) 
                topLayout4.addWidget(self.label5) # ajouter le label5 a ce layout
                
                topLayout5 = QVBoxLayout() # creation  du QVBoxLayout
                #topLayout5.addWidget(menubar)   # ajouter menu bar a la position (0,0) et prend toute la largeur
                topLayout5.addWidget(self.champ) # ajouter le champ ( qLinEedit ) a ce layout
                

                topLayout6 = QHBoxLayout()
                for i, radioBtn in enumerate(self.radioButtons):
                        topLayout6.addWidget(radioBtn)
               
                topLayout5.addLayout(topLayout6)

                topLayout7 = QHBoxLayout()
                for i, radioBtn1 in enumerate(self.radioButtons1):
                        topLayout7.addWidget(radioBtn1)
               
                topLayout5.addLayout(topLayout7)


               # topLayout5.addWidget(self.champ2) # ajouter le champ2 ( qLinEedit ) a ce layout
                topLayout5.addWidget(self.champ3) # ajouter le champ3 ( qLinEedit ) a ce layout
                #topLayout5.addWidget(self.champ4)
                topLayout5.addWidget(self.champ5) # ajouter le champ5 ( qLinEedit ) a ce layou

               
                
                layout.addLayout(topLayout4, 1, 0) # ajouter le QVBoxLayout a la position (1,0) 
                layout.addLayout(topLayout5, 1, 1) # ajouter le QVBoxLayout a la position (1,3) 
                layout.addLayout(topLayout,  1, 2) # ajouter le QVBoxLayout a la position (1,3) 
                layout.addLayout(topLayout1, 1, 3) # ajouter le QVBoxLayout a la position (1,3) 

                layout.addWidget(self.bouton,2,0,1,3) # ajouter le boutton a la position (2,0) et prend toute la largeur
                layout.addWidget(self.button,2,3,1,3)
                layout.addWidget(self.canvas,3,0,1,4) # ajouter le canvas la position (3,0) et prend toute la largeur

                #☺layout.addWidget(self.bouton1)
                self.setLayout(layout) # affiche le layout qui contient touts les layout
                self.setWindowTitle("Method CV") # titre de la fenetre
        
        #************************************************************
        #* fonction qui s'excute lors de la fermeture de la fenetre *
        #************************************************************
        def closeEvent(self, event):
            close = QMessageBox() # creation de message box
            close.setText("Are you sure?") # le message qui s'affiche dans la fenetre du message box
            close.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel) # affichage des message yes et cancel dans la fenetre
            close = close.exec() # excution de la fenetre
            
            #*****************************************************************************************
            #* si on aooui sur yes on fermer la fenetre et la liaison arduino python sinon on ignore *
            #*****************************************************************************************
            if close == QMessageBox.Yes:
                 event.accept()
                 msg="fin"
                 message = msg.encode(self.UTF_8)
                 self.Arduino_Serial.write(message)
                 time.sleep(self.DELAY_1s) 
                 self.Arduino_Serial.close() # fermer la liaison serie entre l'arduino et le pc
            else:
                event.ignore()

        #***************************************************
        #* fonction save pour enregistre l'image du canvas *
        #***************************************************
        def save(self):   
            # sélection du chemin du fichier
            filePath, _ = QFileDialog.getSaveFileName(self, "Save Image", "",
                             "PNG(*.png);;JPEG(*.jpg *.jpeg);;All Files(*.*) ") #  creation de voite de dialog avec le titre save image et le type de fichier a enregistrer 
            # si le chemin du fichier est vide, retour en arrière
            if filePath == "":
                return
            # enregistrement de la toile au chemin souhaité
            self.figure.savefig(filePath)
        #****************************************************************
        #*la fonction se declanche sin il a un evenement sur le clavier *
        #****************************************************************
        def keyPressEvent(self, event):
            #******************************************************************
            #* on verifie si la touche presse est entrer ou retour a la ligne *
            #******************************************************************
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter :
                    #************************************************************************************************************************
                    #*on verifie si les champs obligatoire  son rempli on excute la fonction principal sinon on affiche un message d'erreur *
                    #************************************************************************************************************************
                    if (self.champ.text()!="" and self.champ6.text()!="" and self.champ7.text()!="" and self.champ8.text()!="" and self.champ9.text()!="" ):
                        self.principal()
                    else:
                        # message d'erreur qui indique que les champs obligatoire ne sont par rempli
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Critical)
                        msg.setText("Error")
                        msg.setInformativeText('please enter at least the link port, the number of cycles, the start potential, the two insertion potentials, and the scan speed')
                        msg.setWindowTitle("Error")             
                        msg.exec_()
                        
        #*********************************
        #* Function for board detection  *
        #*********************************
        def board_detection(self):
            global  board, index_param
            ctrl_while = True
            # on entre dans la boucle on envoi un message Board et on lire les information de l'arduino si on reçoit
            # "teensy" c'est a dire le nom de la carte on sort de la boucle
            while (ctrl_while):
                    message = self.BOARD.encode(self.UTF_8)
                    self.Arduino_Serial.write(message)
                    while self.Arduino_Serial.in_waiting == 0:
                           pass
                    received = self.Arduino_Serial.readline()[:-2]  # reads line from Arduino/Teensy and strips out NL + CR
                    received_utf8 = received.decode(self.UTF_8)
                    print (received_utf8)
                    if (received_utf8 == self.ARDUINO or received_utf8 == self.TEENSY):                                       
                            ctrl_while = False      # to break the loop
                            board =  received_utf8  
                            print (self.NEW_LINE + board + self.BOARD_DETECTED + self.QUOTE + self.port_board + self.QUOTE + self.NEW_LINE)
                            self.index_acq   = 0
                            index_param = 0
        
        
        #end of board detection function

        #*********************************
        #* Function to set up constants  *
        #********************************* 
        def set_contants(self,board):
                global quant_DAC, offset_DAC, quant_ADC, offset_ADC,coeff_conv,conv_period, rtia, delay_stab, gain
                if ( board == self.ARDUINO):
                        quant_DAC   = self.QUANT_DAC_ARDUINO
                        offset_DAC  = self.OFFSET_DAC_ARDUINO
                        quant_ADC   = self.QUANT_ADC_ARDUINO
                        offset_ADC  = self.OFFSET_ADC_ARDUINO
                        coeff_conv  = self.COEFF_CONV_ARDUINO
                        conv_period = self.CONV_PERIOD_ARDUINO
                        rtia = self.RTIA_ARDUINO
                        delay_stab  = self.DELAY_STAB_ARDUINO
                        gain = +1.0
                
                elif (board == self.TEENSY):
                        quant_DAC   = self.QUANT_DAC_TEENSY
                        offset_DAC  = self.OFFSET_DAC_TEENSY
                        quant_ADC   = self.QUANT_ADC_TEENSY
                        offset_ADC  = self.OFFSET_ADC_TEENSY 
                        coeff_conv  = self.COEFF_CONV_TEENSY
                        conv_period = self.CONV_PERIOD_TEENSY
                        rtia = self.RTIA_TEENSY
                        delay_stab  = self.DELAY_STAB_TEENSY
                        gain = -1.0
        #end of set_constants function
                        
        #*********************************
        #* Function to set up RTIA       *
        #********************************* 
        
        def set_rtia(self,board):
                
                selected_indices= [i for i, radio_btn in enumerate(self.radioButtons) if radio_btn.isChecked()]
                
                if not   selected_indices:
                       print("no radio button selected defaulted to 100k")
                       self.rtia_val=self.resistorvalues[3]  # Index of "100k"
                       self.ritaindex = selected_indices[3]
                else:      
                        self.rtia_val = self.resistorvalues[ selected_indices[0]]
                        self.ritaindex = selected_indices[0]
       
        #end of set_rtia function
        
        def set_cap(self,board):
                
                selected_indices = [i for i, radio_btn in enumerate(self.radioButtons1) if radio_btn.isChecked()]
                
                if not selected_indices:
                        print("no radio button selected defaulted to 200pF")
                        self.capindex=3 # Index of "200pF"
                else:   
                        self.capindex=selected_indices[0]        
                

        #*********************************
        #* Function to set up UNIT       *
        #********************************* 
        def set_unit(self,board):
                global  c_unit
                self.str_unit = self.champ3.text()
                #si on entre la l'unité du courant on la stock quand c_unit sinon on stock la valeur par default
                if (self.str_unit == self.EMPTY or self.str_unit == "uA"):
                        c_unit = self.COEFF_microA
                elif (self.str_unit == "mA"):
                        c_unit = self.COEFF_mA
                elif (self.str_unit == "nA"):
                        c_unit = self.COEFF_nA
                elif (self.str_unit == "pA"):
                        c_unit = self.COEFF_pA
                else:
                        print("unit not found used uA as default")
                        c_unit = self.COEFF_microA
        
        #end of set_unit function
                        
        #****************************************
        #* Function test the command received   *
        #****************************************
        def tst_cmd(self,received):
                global cmd_code, cmd_status
                # on cherche si l'argument est dans le contenaire CMD_AVA puis es qu'il est dans CMD_KEY et on lui donne la valeur approprier au cmd_stuts et cmd_code sinon on ecrit un message d'erreur
                if (received not in self.CMD_AVA):
                        if (received in self.CMD_KEY):
                                print ("Command not available")
                                cmd_status = False
                        else:
                                cmd_code = self.SET
                                cmd_status = True
                else:
                        cmd_code = received
                        cmd_status = True
        #end of tst_cmd function
                        
        #****************************************
        #* Function to set up acquisition size  *
        #**************************************** 
        def set_acq_size(self,board):
                        global  nb_acq_tot
                        if (board == self.TEENSY):
                                nb_acq_half_cycle =  abs(code_vstart - code_vstop)
                                nb_acq_half_cycle1 =  abs(code_vstop1 - code_vstop)
                                nb_acq_half_cycle2 =  abs(code_vstop1 - code_vstart)
                                if ( nb_acq_half_cycle < 0):
                                        nb_acq_half_cycle = - nb_acq_half_cycle  
                                if (self.nb_cycle == 1):
                                        self.nb_acq_cycle[0] = (nb_acq_half_cycle2+nb_acq_half_cycle1 + nb_acq_half_cycle) + 1
                                        nb_acq_tot = self.nb_acq_cycle[0]
                                if (self.nb_cycle == 2):
                                        self.nb_acq_cycle[0] = (nb_acq_half_cycle2+nb_acq_half_cycle1 + nb_acq_half_cycle) 
                                        self.nb_acq_cycle[1] = self.nb_acq_cycle[0] + 1
                                        nb_acq_tot = self.nb_acq_cycle[0] + self.nb_acq_cycle[1] 
                                if (self.nb_cycle == 3):
                                        self.nb_acq_cycle[0] = (nb_acq_half_cycle2+nb_acq_half_cycle1 + nb_acq_half_cycle)
                                        self.nb_acq_cycle[1] = self.nb_acq_cycle[0]
                                        self.nb_acq_cycle[2] = self.nb_acq_cycle[0] + 1
                                        nb_acq_tot = self.nb_acq_cycle[0] + self.nb_acq_cycle[1] + self.nb_acq_cycle[2]
                        
                        print (nb_acq_tot, self.nb_acq_cycle[0], self.nb_acq_cycle[1], self.nb_acq_cycle[2]) 

        #end of set_acq_size function
                                        
        #***************************************
        #* Function to set up ACQ values       *
        #***************************************
        def set_acq_value(self,board):
                global code_vstart, code_vstop,code_vstop1
               
                period = int(round(conv_period * quant_DAC/srate))           # compute the period according to srate
                str_vstart = str(int(round( vstart/(quant_DAC * gain) + offset_DAC)))   # compute the DAC code for Vstart
                str_vstop  = str(int(round(  vstop/(quant_DAC * gain) + offset_DAC)))   # compute the DAC code for Vstop
                str_vstop1  = str(int(round(  vstop1/(quant_DAC * gain) + offset_DAC)))   # compute the DAC code for Vstop
                str_period = str(period)       
                transmit = str_cycle + self.COMMA + str_vstart + self.COMMA + str_vstop + self.COMMA+ str_vstop1 + self.COMMA + str_period + self.COMMA + f"{self.ritaindex}"+ self.COMMA + f"{self.capindex}"
                message = transmit.encode(self.UTF_8)
                self.Arduino_Serial.write(message)
                print ("You Transmitted :", transmit)
                print ("Acquisition number/cycle :", 2*(int(str_vstart) - int(str_vstop) + 1))               
                self.nb_cycle  = int(str_cycle)              
                code_vstart = int(str_vstart)
                code_vstop  = int(str_vstop)
                code_vstop1  = int(str_vstop1)
        #end of set_acq_value function
                                        
        #************************************
        #* Function to set up file          *
        #************************************ 
        def set_up_file(self,board):
                global file_name, file
                file_name = self.FILE_NAME_TEENSY  
                self.sauvegarde=self.fichier
                self.fichier=self.champ5.text()
                self.index_file +=1
                if self.fichier == self.EMPTY :     
                    file_name = "test" + str(self.index_file ) + self.FILE_EXTENT 
                    file = open( file_name, self.WRITE_MODE,encoding = self.UTF_8)   # create a new file
                    print(file_name)
                else:
                    if self.fichier==self.sauvegarde:
                        file_name = self.fichier + str(self.index_file ) + self.FILE_EXTENT 
                        file = open( file_name, self.WRITE_MODE,encoding = self.UTF_8)   # create a new file
                        print(file_name)
                    else:
                        self.index_file=0
                        file_name = self.fichier + self.FILE_EXTENT 
                        file = open( self.fichier+self.FILE_EXTENT, self.WRITE_MODE,encoding = self.UTF_8)   # create a new file
                        print(file_name)
                time.sleep(self.DELAY_01s)
                
        #end of set_up_file function 
        
        #************************************
        #* Function to handle acquisition   *
        #************************************ 
        def get_acq(self):
                
                
                global  index_param
                i_acq = 0
                ctrl_while = True
                # time.sleep(self.acq_time + 10 ) # to avoid a long time out for the serial link

                # start_time = time.time()
                # while (self.Arduino_Serial.in_waiting == 0 and (time.time() - start_time) > self.acq_time + 10):
                #        pass
                start_time = time.time()
                while (ctrl_while):
                        
                        while (self.Arduino_Serial.in_waiting == 0 and (time.time() - start_time) >self .acq_time*1.2):
                                pass

                        # reads line from Arduino and 
                        raw_data = self.Arduino_Serial.readline()
                        # while raw_data[-1]!=0x0A: # Hangs indefinitely because it never receives anymore data at some point
                        #        raw_data += self.Arduino_Serial.readline()

                        data = raw_data[:-2]  # stips out NL + CR
                        data_utf8 = data.decode(self.UTF_8)
                        if ( data_utf8 != "" ):                          
                                line = data_utf8.split(self.COMMA)
                                
                                if len(line) != 2:
                                       print(f"The incoming data is incomplete of length: {len(line)}")
                                       print(f"\tReceived data is: {raw_data}")
                                       break

                                print (i_acq,",",nb_acq_tot,",",data_utf8)
                              
                                if ( i_acq >= 0 and i_acq < self.nb_acq_cycle[0]):
                                        i_cycle = 0
                                if ( i_acq >= self.nb_acq_cycle[0] and i_acq < nb_acq_tot ):
                                        i_cycle = 1
                                if ( i_acq >= (self.nb_acq_cycle[0] + self.nb_acq_cycle[1]) and i_acq < nb_acq_tot ):
                                        i_cycle = 2
                                #print(index_acq, i_cycle)
                                val_v = (int(line[0]) - offset_DAC) * gain * quant_DAC
                                val_c = ((int(line[1])-2045) *5/4095 * (c_unit/self.rtia_val)) # select COEFF_mA or COEFF_microA
                                self.x_data[self.index_acq][i_cycle].append(val_v)                                                
                                self.y_data[self.index_acq][i_cycle].append(val_c)
                                
                                
                                data_file = (f"{val_v:.6f}") + self.COMMA + (f"{val_c:.6f}") # six decimals
                                file.write(data_file + self.NEW_LINE)   # write data from Arduino in the file + NL 
                                i_acq = i_acq + 1

                                
                                if (i_acq == nb_acq_tot):
                                        ctrl_while = False
                        else:
                                print(f"amount of time passed: { (time.time() - start_time)/60 } min")

                index_param += 1
                self.index_acq   += 1
                file.flush  # Don't forget to flush before closing the file
                file.close
                self.CMD_AVA[self.TRA] = self.CMD_TRA
                self.Arduino_Serial.close()
                #print(CMD_AVA)
        #end of get_acq function
                
        #****************************************
        #* Function to set acquisition limits   *
        #****************************************
        def set_acq_limits(self,params):
                global f_cycle, str_cycle, vstart, vstop, srate , vstop1
                for i in range(self.NB_PARAM) :
                        if (i == 0 ):
                            if (params[i] != self.EMPTY):
                                 self.param[self.index_acq][0] = params[0]
                            else:
                                params[0] = self.param[self.index_acq - 1][0]
                                self.param[self.index_acq][0] = params[0]
                            f_cycle = float(params[0])
                            str_cycle  = params[0]
         
                        elif (i == 1) :
                            if (params[i] != self.EMPTY):
                                self.param[self.index_acq][1] = params[1]
                            else:
                                params[1] = self.param[self.index_acq - 1][1]
                                self.param[self.index_acq][1] = params[1]
                            vstart  = float(params[1])
                        
                        elif (i == 2) :
                            if (params[i] != self.EMPTY):
                                self.param[self.index_acq][2] = params[2]
                            else:
                                params[2] = self.param[self.index_acq - 1][2]
                                self.param[self.index_acq][2] = params[2]
                            vstop   = float(params[2])
                        elif (i == 3) :
                            if (params[i] != self.EMPTY):
                                self.param[self.index_acq][3] = params[3]
                            else:
                                params[3] = self.param[self.index_acq - 1][3]
                                self.param[self.index_acq][3] = params[3]
                            vstop1   = float(params[3])        # extracts the srate value in V/s
                                                          
                            
                        elif (i == 4) :
                            if (params[i] != self.EMPTY):
                                self.param[self.index_acq][4] = params[4]
                            else:
                                params[4] = self.param[self.index_acq - 1][4]
                                self.param[self.index_acq][4] = params[4]
                            srate   = float(params[4])        # extracts the srate value in V/s
                                                                                    
        #print(param[index_acq])
                                                           
        #********************************
        #* Function to plot cycle       *
        #********************************
        def plot_cycle (self,index_acq):
                self.ax.clear()
                for i_cycle in range(self.nb_cycle):
                        self.x = self.x_data[index_acq][i_cycle]
                        self.y = self.y_data[index_acq][ i_cycle]
                        self.ax.plot(self.x, self.y, self.gra_color[i_cycle],label = "Cycle" + str(i_cycle + 1)) 
                self.flat_x_data = [item for sublist in self.x_data[index_acq] for item in sublist]
                self.flat_y_data = [item for sublist in self.y_data[index_acq] for item in sublist]

                self.ax.set_xlim(min(self.flat_x_data), max(self.flat_x_data))        # set x limits
                self.ax.set_ylim(min(self.flat_y_data), max(self.flat_y_data))        # set y limits    
                
                if self.champ8.text()>self.champ9.text():
                    self.ax.set_title("Acquisition " + str(self.index_acq) +"\n" + "Cycles with a scan rate of " + self.champ10.text() + " V/s \n Range["+ self.champ9.text()+ " V, " + self.champ8.text() + " V]"+ "")            # Title
                else  :
                    self.ax.set_title("Acquisition " + str(self.index_acq) +"\n" + "Cycles with a scan rate of " + self.champ10.text() + " V/s \n Range["+ self.champ8.text()+ " V, " + self.champ9.text() + " V]"+ "")            # Title

                self.ax.set_xlabel("E (V)")
                if (self.str_unit == self.EMPTY or self.str_unit == "uA"):
                            self.str_unit = "µA"
                self.ax.set_ylabel("I (" + self.str_unit + ")")            # y labels
                
                self.ax.grid(True)
                self.ax.legend()
                # refresh canvas
                self.canvas.draw()
                
              
                
                
                
                                      
        def principal(self):
                # on verifie si les champ obligatoire son rempli sinon on affiche un message d'erreur
                if self.champ6.text()!="" and self.champ7.text()!="" and self.champ8.text()!="" and self.champ9.text()!="" and self.champ10.text()!="":
                        # on verifie que le nombre de cycle et entre 1 et 3 si c'est le cas on verifi la valeur min et max des potentiel son correcte
                         if float(self.champ6.text())>3 or float(self.champ6.text())<=0 :   
                             # message d'erreur sur le nombre de cycle
                             msg = QMessageBox()
                             msg.setIcon(QMessageBox.Critical)
                             msg.setText("Error")
                             msg.setInformativeText('Max number of cycles equal to 3')
                             msg.setWindowTitle("Error")
                             msg.setWindowTitle('Quit')

                             msg.exec_()
                         elif (float(self.champ7.text())>2.50 or float(self.champ7.text())<=-2.50) or (float(self.champ8.text())>2.5 or float(self.champ8.text())<=-2.5) or (float(self.champ9.text())>2.5 or float(self.champ9.text())<=-2.5) :
                             # message d'erreur la valeur du potentiel min et max
                             msg = QMessageBox()
                             msg.setIcon(QMessageBox.Critical)
                             msg.setText("Error")
                             msg.setInformativeText('the Voltage supplied by the card is between -2.5 and 2.5 please use a smaller value ')
                             msg.setWindowTitle("Error")
                             msg.setWindowTitle('Quit')

                             msg.exec_()
                         else:
                            # on verifie si les potentiel son correctement initaliser     
                             if (float(self.champ7.text())<=float(self.champ8.text()) and float(self.champ9.text())<=float(self.champ8.text()) and float(self.champ9.text())<=float(self.champ7.text())) or (float(self.champ7.text())>=float(self.champ8.text()) and float(self.champ9.text())>=float(self.champ8.text()) and float(self.champ9.text())>=float(self.champ7.text())):
                                 # on definie ici les vecteur d'acquisition pour qu'a chaque fois on execute la fonction on reinitialise les valeur
                                self.x_data = [[[] for j in range(self.MAX_CYCLE)] for i in range(self.MAX_ACQ)]
                                self.y_data = [[[] for j in range(self.MAX_CYCLE)] for i in range(self.MAX_ACQ)]
                                
                                #********************************
                                #* Entering the modem's number  *
                                #********************************
                                
                                modem_number = self.champ.text()
                                if (modem_number == self.EMPTY):
                                        
                                        
                                        self.port_board = self.PORT_TEENSY
                                        
                                      #  port_board = PORT_ARDUINO
                                else:
                                        modem_number = str(modem_number)
                                        self.port_board = self.PORT_BOARD + modem_number
                                        self.liason=False
                                       
                                #********************************
                                #* Openning of the serial link  *
                                #********************************
                                
                                self.Arduino_Serial = serial.Serial(self.port_board, self.BAUD_RATE, timeout=self.TIME_OUT)
                                time.sleep(self.DELAY_1s) #give the connection a second to settle
                                msg="VoltaCyclique"
                                message = msg.encode(self.UTF_8)
                                self.Arduino_Serial.write(message)
                                time.sleep(self.DELAY_1s)      
                                #****************************************
                                #* Board detection  & set up constants  *
                                #****************************************
                                self.board_detection()
                                self.set_contants(board)
                                
                                #********************************
                                #* RTIA set-up & UNIT           *
                                #********************************
                                self.set_rtia(board)
                                self.set_cap(board)
                                self.set_unit(board)
                                        
                                #********************************
                                #* Printing of input message    *
                                #********************************
                              #  print ("Enter Parameters like 2,-1.25,1.25,0.5 then ACQ to start acquisition and TRA to graph the data \n")
                                i=0       
                                #********************************
                                #* Infinite loop                *
                                #********************************                
                                while True:
                                        if (self.index_acq == self.MAX_ACQ):            # setting WARNING message
                                                for w in range(8):
                                                        print(self.WARNING[w])
                                                self.CMD_AVA = {self.CMD: self.CMD_CMD, self.PAR: self.CMD_PAR, self.TRA: self.CMD_TRA, self.DEF: self.EMPTY, self.EXIT: self.CMD_EXIT}
                                        
                                        
                                        # au debut on envoit les donner à l'arduino puis ACQ puis TRA puis EXIT
                                        if i==0 :
                                                received = self.champ6.text()+","+self.champ7.text()+","+self.champ8.text()+","+self.champ9.text()+","+self.champ10.text()
                                        elif i==1:
                                            received="ACQ"
                                        elif i==2:
                                            received="TRA"
                                        elif i==3:
                                            received="EXIT"
                                            
                                        self.tst_cmd(received)
                                        #accepts input puts it in variable 'received'
                                        if (cmd_code == self.SET and cmd_status == True): #in case you entered "1,-1.25,1.25,5"
                                                #print ("You Entered :", received)   
                                                self.params = [name.strip() for name in received.split(self.COMMA)]
                                                self.set_acq_limits(self.params)
                                                #print(f_cycle, vstart, vstop, srate)                                                     
                                                self.acq_time = ( f_cycle * (abs(vstart - vstop) + abs(vstop-vstop1)+abs(vstop1-vstart))/srate) + delay_stab # add the delay to stabilize vstart
                                                timeinmins=self.acq_time/60
                                                print( "The acquisition will take roughly : ", (f"{timeinmins:.2f}"), " minuits")              
                                                self.set_acq_value(board)
                                                time.sleep(10*self.DELAY_01s)
                                                self.CMD_AVA[self.ACQ] = self.CMD_ACQ
                                                i=1 # pour passer à l'acquesition
                                #********************************
                                #* "ACQ" is received            *
                                #********************************
                                        if ( cmd_code == self.ACQ and cmd_status == True):                                 #if input is "ACQ"
                                                message = received.encode(self.UTF_8)
                                                self.Arduino_Serial.write(message)                                                                    
                                                print(self.ACQ_START)
                                                self.set_up_file(board)
                                                time.sleep(self.DELAY_01s)                
                                                self.set_acq_size(board)
                                                self.set_acq_limits(self.params)
                                                self.get_acq()
                                                print (self.ACQ_END)
                                                i=2  # pour passer au tracer
                                #end of first if loop
                                     
                                
                                #********************************
                                #* "TRA" is received            *
                                #********************************
                                        if ( cmd_code == self.TRA and cmd_status == True):                                 #if input is "TRA"                                                                    
                                                #acq_graph = input( "Enter the acquisition's number to graph [0," + str(index_acq -1) +"] (Return => last acq) : ")
                                                #acq_graph=self.champ4.text()
                                                acq_graph=""
                                                if (acq_graph == self.EMPTY):
                                                        index_acq_graph = self.index_acq - 1
                                                else:
                                                        index_acq_graph = int(acq_graph)
                                                
                                                print(self.TRA_START)
                                                time.sleep(self.DELAY_01s)
                                                self.plot_cycle (index_acq_graph)
                                                print(self.TRA_END)
                                                i=3  # pour sortir de la boucle
                                        #end of if statement              
                                
                                 
                                #*******************************
                                #* "RTIA" is received           *
                                #*******************************
                                        if ( cmd_code == self.RTIA and cmd_status == True):
                                                self.set_rtia(board)
                                        # end of if statement
                                
                                #*******************************
                                #* "UNIT" is received           *
                                #*******************************
                                        if ( cmd_code == self.UNIT and cmd_status == True):
                                                self.set_unit(board)
                                        # end of if statement
                                
                                #*******************************
                                #* "PAR" is received           *
                                #*******************************
                                        if ( cmd_code == self.PAR and cmd_status == True):
                                                #print (index_param)
                                                for i in range(self.MAX_ACQ):                       
                                                        str_param = "Acq " + str(i) + " :" + self.param[i][0]
                                                        if ( i > (index_param - 1)):
                                                                str_param = self.UNDEFINED
                                                                for j in range(3):
                                                                        str_param += self.COMMA + self.UNDEFINED
                                                                print (str_param)
                                                        else:
                                                                for j in range(3):
                                                                        str_param += self.COMMA + self.param[i][j+1]
                                                                print (str_param)
                                                      
                                #********************************
                                #* "FILE" is received           *
                                #********************************
                                        if ( cmd_code == self.FILE and cmd_status == True ):
                                                str_file_index =self.champ5.text()
                                                if (str_file_index == self.EMPTY):
                                                        str_file_index = "0"
                                                self.index_file = int(str_file_index)
                                                self.set_up_file(board)
                                                           
                                # end of infinite loop
                                
                                #********************************
                                #* "CMD" or "" is received      *
                                #********************************
                                        if (cmd_code == self.CMD or cmd_code == self.DEF) and cmd_status == True:
                                                for key in self.CMD_AVA:
                                                        if (key != self.EMPTY):
                                                                print(key, self.CMD_AVA[key])
                                                                
                                #********************************
                                #* "EXIT" is received           *
                                #********************************
                                        if (cmd_code == self.EXIT):
                                                self.Arduino_Serial.close()
                                                break
                             else:
                                 # message d'erreur sur les potentiels
                                 msg = QMessageBox()
                                 msg.setIcon(QMessageBox.Critical)
                                 msg.setText("Error")
                                 msg.setInformativeText('Incorrect potential input')
                                 msg.setWindowTitle("Error")
                                 msg.setWindowTitle('Quit')

                                 msg.exec_()
                else:
                                #message d'erreur sur les champs obligatoire
                                 msg = QMessageBox()
                                 msg.setIcon(QMessageBox.Critical)
                                 msg.setText("Error")
                                 msg.setInformativeText('please enter at least the link port, the number of cycles, the start potential, the two insertion potentials, and the scan speed')
                                 msg.setWindowTitle("Error")      
                                 msg.setWindowTitle('Quit')

                                 msg.exec_()

if __name__ == '__main__':
        app = QApplication.instance() 
        if not app:
                app = QApplication(sys.argv)
        fen = Fenetre1()
        fen.show()
        app.exec_()