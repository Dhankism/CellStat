

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
                self.TIME_OUT = 30
                
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
                
                self.QUANT_DAC_TEENSY    = 1./800       # extracted from calibration process
                self.OFFSET_DAC_TEENSY   = 2093           # extracted from calibration process
                self.QUANT_ADC_TEENSY    = 3.3/4095
                self.OFFSET_ADC_TEENSY   = 2045.0
                self.COEFF_CONV_TEENSY   = 1.51              # inverse of the output voltage divider
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
                
                self.resistorlabels = ["±2mA", "±.2mA", "±20 uA", "±2uA", "±.2uA", "±67uA", "±20nA", "±2nA"]
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
                
                self.luserportnumber =QLabel(" Enter the port's number (Return => default port) : ") # creation du qlabel
                self.userportnumber = QLineEdit() # creation de QlineEdit pour rentrer les information
                
                self.lirange = QLabel(" Enter the i range (Return => ±20uA) : ") # creation du qlabel
               # self.champ2 = QLineEdit() # creation de QlineEdit pour rentrer les information
                
                self.radioGroup = QButtonGroup()  # Create a button group for radio buttons
                self.radioButtons = []  # List to store the radio buttons
                # Create 8 radio buttons and add them to the button group
              
                for i , label in enumerate(self.resistorlabels):
                        radioBtn = QRadioButton(label)
                        self.radioGroup.addButton(radioBtn)
                        self.radioButtons.append(radioBtn)
                
                self.lcaprange = QLabel(" Enter the Cap value in F (Return => 200 pF): ") # creation du qlabel
          
                self.radioGroup1 = QButtonGroup()  # Create a button group for radio buttons
                self.radioButtons1 = []  # List to store the radio buttons
                # Create 8 radio buttons and add them to the button group
                
                for i, label in enumerate(self.Capacitorlabels):
                        radioBtn1 = QRadioButton(label)
                        self.radioGroup1.addButton(radioBtn1)
                        self.radioButtons1.append(radioBtn1)

                
                
                self.lcurrentunit = QLabel(text=" Enter the curent unit (mA, uA, nA or pA) (Return => uA) : ") # creation du qlabel
                self.usercurrentunit = QLineEdit()# creation de QlineEdit pour rentrer les information


                #self.label4 = QLabel(text=" Enter a number for the starting of indexing file (Return => 0) : ")
                #self.champ4 = QLineEdit()

                self.lfilename = QLabel(text=" Enter the file name ( test is the default name )") # creation du qlabel
                self.userfilename = QLineEdit() # creation de QlineEdit pour rentrer les information
                
                self.lpotential = QLabel(text=" Enter the potential in V") # creation du qlabel
                self.userV = QLineEdit() # creation de QlineEdit pour rentrer les information
                
                self.lscanrate = QLabel(text=" Enter scan rate in scan per min") # creation du qlabel
                self.userscanrate = QLineEdit() # creation de QlineEdit pour rentrer les information
                
                self.lrefreshrate = QLabel(text=" Enter refresh rate per min ") # creation du qlabel
                self.userrefreshrate = QLineEdit() # creation de QlineEdit pour rentrer les information
                
                self.lscantime = QLabel(text=" Enter scan time") # creation du qlabel
                self.usertime = QLineEdit() # creation de QlineEdit pour rentrer les information



                self.figure = plt.Figure() # creation de la figure
                self.canvas = FigureCanvas(self.figure) # creation du canvas qui prend comme argument la figure
                self.ax = self.figure.add_subplot(111) # creation des ax
                
                layout = QGridLayout() # creation du layoutgrid
                # création du bouton
                self.bouton = QPushButton("Start")
                self.bouton.clicked.connect(self.principal) # relier le boutton avec la fonction principal qui s'excute quand on clic sur le boutton
                
               # self.bouton.clicked.connect() # 
                


                self.button = QPushButton("Save")
                self.button.clicked.connect(self.save)# on connecter l'action a la fonction save si il y une action sur save action on declanche la fonction save
      
                self.image = QImage(self.size(), QImage.Format_RGB32) # creation d'une image format_RGB32
                self.image.fill(Qt.white)
                
                topLayout = QVBoxLayout() # creation  du QVBoxLayout
                topLayout.addWidget(self.lpotential) # ajouter le label6 a ce layout
                topLayout.addWidget(self.lscanrate) # ajouter le label7 a ce layout
                topLayout.addWidget(self.lrefreshrate) # ajouter le label8 a ce layout
                topLayout.addWidget(self.lscantime) # ajouter le label9 a ce layout
                
                topLayout1 = QVBoxLayout() # creation  du QVBoxLayout
                topLayout1.addWidget(self.userV)  # ajouter le champ6 ( qLinEedit ) a ce layout
                topLayout1.addWidget(self.userscanrate) # ajouter le champ7 ( qLinEedit ) a ce layout
                topLayout1.addWidget(self.userrefreshrate) # ajouter le champ8 ( qLinEedit ) a ce layout
                topLayout1.addWidget(self.usertime)
              
                topLayout4 = QVBoxLayout() # creation  du QVBoxLayout
                topLayout4.addWidget(self.luserportnumber) # ajouter le label a ce layout
                topLayout4.addWidget(self.lirange)
                topLayout4.addWidget(self.lcaprange) # ajouter le label2 a ce layout
                topLayout4.addWidget(self.lcurrentunit) # ajouter le label3 a ce layout
                topLayout4.addWidget(self.lfilename) # ajouter le label5 a ce layout
                
                topLayout5 = QVBoxLayout() # creation  du QVBoxLayout
                topLayout5.addWidget(self.userportnumber) # ajouter le champ ( qLinEedit ) a ce layout

                topLayout6 = QHBoxLayout()
                for i, radioBtn in enumerate(self.radioButtons):
                        topLayout6.addWidget(radioBtn)
               
                topLayout5.addLayout(topLayout6)

                topLayout7 = QHBoxLayout()
                for i, radioBtn1 in enumerate(self.radioButtons1):
                        topLayout7.addWidget(radioBtn1)
               
                topLayout5.addLayout(topLayout7)


               # topLayout5.addWidget(self.champ2) # ajouter le champ2 ( qLinEedit ) a ce layout
                topLayout5.addWidget(self.usercurrentunit) # ajouter le champ3 ( qLinEedit ) a ce layout
                #topLayout5.addWidget(self.champ4)
                topLayout5.addWidget(self.userfilename) # ajouter le champ5 ( qLinEedit ) a ce layou

               
                
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
                    if (self.userportnumber.text()!="" and self.userV.text()!="" and self.userscanrate.text()!="" and self.userrefreshrate.text()!=""  ):
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
                else:      
                        self.rtia_val = self.resistorvalues[ selected_indices[0]]
                        self.ritaindex = selected_indices[0]
       
        #end of set_rtia function
         #*********************************
        #* Function to set up CAP      *
        #********************************* 
        def set_cap(self,board):
                
                selected_indices = [i for i, radio_btn in enumerate(self.radioButtons1) if radio_btn.isChecked()]
                
                if not selected_indices:
                        print("no radio button selected defaulted to 200pF")
                        self.capindex=3 # Index of "200pF"
                else:   
                        self.capindex=selected_indices[0]        
         #end of set_cap function        

        #*********************************
        #* Function to set up UNIT       *
        #********************************* 
        def set_unit(self,board):
                global  c_unit
                self.str_unit = self.usercurrentunit.text()
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
  
        #************************************
        #* Function to set up file          *
        #************************************ 
        def set_up_file(self,board):
                global file_name, file
                if (board == self.ARDUINO):
                        file_name = self.FILE_NAME_ARDUINO
                else:
                        file_name = self.FILE_NAME_TEENSY  
                self.sauvegarde=self.fichier
                self.fichier=self.userfilename.text()
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
                
                if self.userrefreshrate.text()>self.champ9.text():
                    self.ax.set_title("Acquisition " + str(self.index_acq) +"\n" + "Cycles with a scan rate of " + self.champ10.text() + " V/s \n Range["+ self.champ9.text()+ " V, " + self.userrefreshrate.text() + " V]")            # Title
                else  :
                    self.ax.set_title("Acquisition " + str(self.index_acq) +"\n" + "Cycles with a scan rate of " + self.champ10.text() + " V/s \n Range["+ self.userrefreshrate.text()+ " V, " + self.champ9.text() + " V]")            # Title

                self.ax.set_xlabel("E (V)")
                if (self.str_unit == self.EMPTY or self.str_unit == "uA"):
                            self.str_unit = "µA"
                self.ax.set_ylabel("I (" + self.str_unit + ")")            # y labels
                
                self.ax.grid(True)
                self.ax.legend()
                # refresh canvas
                self.canvas.draw()
                
              
                
                
                
                                      
        def principal(self):
                                #********************************
                                #* Entering the modem's number  *
                                #********************************
                                
                                modem_number = self.userportnumber.text()
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
                                msg="OCV"
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


                                transmit = f"{}" + self.COMMA +  + self.COMMA + str_vstop + self.COMMA+ str_vstop1 + self.COMMA + str_period + self.COMMA + f"{self.ritaindex}"+ self.COMMA + f"{self.capindex}"
                                message = msg.encode(self.UTF_8)
                                self.Arduino_Serial.write(message)

                                )  # ajouter le champ6 ( qLinEedit ) a ce layout
                topLayout1.addWidget(self.userscanrate) # ajouter le champ7 ( qLinEedit ) a ce layout
                topLayout1.addWidget(self.userrefreshrate) # ajouter le champ8 ( qLinEedit ) a ce layout
                topLayout1.addWidget(self.usertime)



                                        
                                #********************************
                                #* Printing of input message    *
                                #********************************

                                       
                              

if __name__ == '__main__':
        app = QApplication.instance() 
        if not app:
                app = QApplication(sys.argv)
        fen = Fenetre1()
        fen.show()
        app.exec_()
