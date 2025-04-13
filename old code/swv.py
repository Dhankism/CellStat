






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


#**********************************************************
#* declaratoin de la class qui herite de la class Qwidget *
#**********************************************************
class Fenetre(QWidget):
        def __init__(self): # declaration du constructeur
                #**************************
                # declaration des atribue *
                #**************************
                #self.PORT_ARDUINO = "/dev/cu.usbmodem641"
                #self.PORT_TEENSY  = "/dev/cu.usbmodem6837991"
                #PORT_BOARD = "/dev/cu.usbmodem"         # for MAC CPU
                self.PORT_BOARD = "COM"                     # for PC CPU
                #self.PORT_BOARD="/dev/ttyACM"                # for linux
                self.BAUD_RATE =  115200
                self.TIME_OUT = 30
                self.MINUTE   = 60
                self.index_file=0
                self.index_acq=0
                self.EMPTY    = ""
                self.BOARD    = "BOARD"
                #************************************************
                self.ACQ      = "ACQ"
                self.CMD_ACQ  ="  = Start Acquisition"
                #************************************************
                self.CMD      = "CMD"
                self.CMD_CMD  = "  = Pr Commands available"
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
                self.MODE      = "MODE"
                self.CMD_MODE  = " = Select number of summing samples"
                #************************************************
                self.EXIT     = "EXIT"
                self.CMD_EXIT = " = Exit the script "
                #************************************************
                
                self.sauvegarde=""
                self.fichier=""
                
                
                self.CMD_KEY = {self.ACQ: self.CMD_ACQ, self.CMD: self.CMD_CMD, self.FILE: self.CMD_FILE, self.PAR: self.CMD_PAR, self.TRA: self.CMD_TRA, self.RTIA: self.CMD_RTIA, self.UNIT: self.CMD_UNIT, self.DEF: self.EMPTY, self.MODE: self.CMD_MODE, self.EXIT: self.CMD_EXIT}
                self.CMD_AVA = {self.ACQ: self.CMD_ACQ, self.CMD: self.CMD_CMD, self.FILE: self.CMD_FILE, self.PAR: self.CMD_PAR, self.TRA: self.CMD_TRA, self.RTIA: self.CMD_RTIA, self.UNIT: self.CMD_UNIT, self.DEF: self.EMPTY, self.MODE: self.CMD_MODE, self.EXIT: self.CMD_EXIT}
                self.CMD_AVA.pop(self.ACQ) # Command ACQ not available at start up
                self.CMD_AVA.pop(self.TRA) # Command TRA not available at start up
                #print(CMD_AVA)
                self.cmd_code = self.EMPTY
                
                self.BOARD_DETECTED = " board detected on "
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
                self.NB_PARAM    = 6
                self.ARDUINO  = "Arduino"
                self.TEENSY   = "Teensy"
                self.DELAY_01s = 0.1
                self.DELAY_1s  = 1
                self.CODE_STEP = 1
                
                self.QUANT_DAC_TEENSY    = 1./830.725        # extracted from calibration process
                self.OFFSET_DAC_TEENSY   = 2085.0            # extracted from calibration process
                self.QUANT_ADC_TEENSY    = 3.3/4095
                self.OFFSET_ADC_TEENSY   = 2070.0
                self.COEFF_CONV_TEENSY   = 1.51              # inverse of the output voltage divider
                self.CONV_PERIOD_TEENSY  = 1.0 * 1000000.    # in order to convert in micros and take care of the first stage gain
                self.DELAY_STAB_TEENSY   = 2.0
                
                self.R10k         = 10000.0                 # to be change to the right value
                self.RTIA_TEENSY  =  4700.0
                self.KOHM         =  1000.0
                self.CODE_MAX_RTIA = 255
                self.CODE_MIN_RTIA =  12
                
                self.COEFF_mA     =          1000.0             # scale in mA
                self.COEFF_microA =       1000000.0             # scale in microA
                self.COEFF_nA     =    1000000000.0             # scale in nA
                self.COEFF_pA     = 1000000000000.0             # scale in pA
                
                self.COEFF_mV     =          1000.0
                self.NB_ECH_MAX   = 11 * 1024
                
                #***********************
                #* File name to modify *
                #***********************
                self.FILE_NAME_TEENSY   = "testSWV"
                self.FILE_EXTENT = ".txt"
                self.READ_MODE  = "r"
                self.WRITE_MODE = "w"
                self.UTF_8      = "utf-8"
                self.sauvegarde=""
                self.fichier=""
                
                #****************************
                #* Array for data from file 
                #****************************
                self.x = []
                self.y = []
                self.x_data = [[] for i in range(self.MAX_ACQ)]
                self.y_data = [[] for i in range(self.MAX_ACQ)]
                        
                #****************************
                #* Array phases and colors 
                #****************************        
                self.gra_color =["r","b","g"]
                
                #****************************
                #* Array for PARAMETERS     *
                #****************************
                self.params = [self.UNDEFINED,self.UNDEFINED,self.UNDEFINED,self.UNDEFINED,self.UNDEFINED,self.UNDEFINED]
                self.param  = [[self.UNDEFINED,self.UNDEFINED,self.UNDEFINED,self.UNDEFINED,self.UNDEFINED,self.UNDEFINED] for  i in range(self.MAX_ACQ)]   # maximum 16 sets of parameters
                #*******************************************************#
                self.port_board=""
                self.acq_time=0
                self.cmd_status = False
                #**********************************************************#
                QWidget.__init__(self) # initialisation du qwidget
                self.toolBar = QToolBar() # creation du toolbar
                
                self.label =QLabel(" Enter the port's number (Return => default port) : ") # creation du qlabel
                self.champ = QLineEdit() # creation de QlineEdit pour rentrer les information
                
                self.label2 = QLabel(" Enter the RTIA value in kΩ (Return => 100 kΩ) : ") # creation du qlabel
                self.champ2 = QLineEdit() # creation de QlineEdit pour rentrer les information      
                
                self.label3 = QLabel(text=" Enter the curent unit (mA, uA, nA or pA) (Return => uA) : ") # creation du qlabel
                self.champ3 = QLineEdit() # creation de QlineEdit pour rentrer les information


                #self.label4 = QLabel(text=" Enter a number for the starting of indexing file (Return => 0) : ")
                #self.champ4 = QLineEdit()

                self.label5 = QLabel(text=" Enter the file name ( test is the default name )") # creation du qlabel
                self.champ5 = QLineEdit() # creation de QlineEdit pour rentrer les information
                
                self.label6 = QLabel(text=" Enter the starting potential") # creation du qlabel
                self.champ6 = QLineEdit() # creation de QlineEdit pour rentrer les information
                
                self.label7 = QLabel(text=" Enter the final potential") # creation du qlabel
                self.champ7 = QLineEdit() # creation de QlineEdit pour rentrer les information
                
                self.label8 = QLabel(text=" Enter the increment size") # creation du qlabel
                self.champ8 = QLineEdit() # creation de QlineEdit pour rentrer les information
                
                self.label9 = QLabel(text=" Enter the pulse height") # creation du qlabel
                self.champ9 = QLineEdit() # creation de QlineEdit pour rentrer les information
                
                self.label10 = QLabel(text=" Enter the scan speed") # creation du qlabel
                self.champ10 = QLineEdit() # creation de QlineEdit pour rentrer les information

                self.label11 = QLabel(text=" Enter the average number of points") # creation du qlabel
                self.champ11 = QLineEdit() # creation de QlineEdit pour rentrer les information



           
                self.figure = plt.Figure() # creation de la figure
                self.canvas = FigureCanvas(self.figure) # creation du canvas qui prend comme argument la figure
                self.ax = self.figure.add_subplot(111) # creation des ax
                
                layout = QGridLayout() # creation du layoutgrid
                # création du bouton
                self.bouton = QPushButton("Start")
                self.bouton.clicked.connect(self.principal) # relier le boutton avec la fonction principal qui s'excute quand on clic sur le boutton
                
                                
                topLayout = QVBoxLayout() # creation  du QVBoxLayout
                topLayout.addWidget(self.label6) # ajouter le label6 a ce layout
                topLayout.addWidget(self.label7) # ajouter le label7 a ce layout
                topLayout.addWidget(self.label8) # ajouter le label8 a ce layout
                topLayout.addWidget(self.label9) # ajouter le label9 a ce layout
                topLayout.addWidget(self.label10) # ajouter le label10 a ce layout
                topLayout.addWidget(self.label11) # ajouter le label11 a ce layout
                
                topLayout1 = QVBoxLayout() # creation  du QVBoxLayout
                topLayout1.addWidget(self.champ6)  # ajouter le champ6 ( qLinEedit ) a ce layout
                topLayout1.addWidget(self.champ7) # ajouter le champ7 ( qLinEedit ) a ce layout
                topLayout1.addWidget(self.champ8) # ajouter le champ8 ( qLinEedit ) a ce layout
                topLayout1.addWidget(self.champ9) # ajouter le champ9 ( qLinEedit ) a ce layout
                topLayout1.addWidget(self.champ10) # ajouter le champ10 ( qLinEedit ) a ce layout
                topLayout1.addWidget(self.champ11) # ajouter le champ11 ( qLinEedit ) a ce layout
            
                menubar = QMenuBar() # creation du Qmenubar
                fileMenu = menubar.addMenu("file") # ajouter un menu qui s'appel file a ce menu bar
                saveAction = QAction("Save", self) # creation d'une action 
                fileMenu.addAction(saveAction) # ajouter l'action au menu file
                saveAction.triggered.connect(self.save) # on connecter l'action a la fonction save si il y une action sur save action on declanche la fonction save
                self.image = QImage(self.size(), QImage.Format_RGB32) # creation d'une image format_RGB32
                self.image.fill(Qt.white)
                
                
                topLayout4 = QVBoxLayout() # creation  du QVBoxLayout
                topLayout4.addWidget(menubar) # ajouter le label a ce layout
                topLayout4.addWidget(menubar) # ajouter le label a ce layout

                topLayout4.addWidget(self.label) # ajouter le label a ce layout
                topLayout4.addWidget(self.label2) # ajouter le label2 a ce layout
                topLayout4.addWidget(self.label3) # ajouter le label3 a ce layout
                topLayout4.addWidget(self.label5) # ajouter le label5 a ce layout
                
                topLayout5 = QVBoxLayout() # creation  du QVBoxLayout
                topLayout5.addWidget(menubar) # ajouter le label a ce layout

                topLayout5.addWidget(self.champ) # ajouter le champ ( qLinEedit ) a ce layout
                topLayout5.addWidget(self.champ2) # ajouter le champ2 ( qLinEedit ) a ce layout
                topLayout5.addWidget(self.champ3) # ajouter le champ3 ( qLinEedit ) a ce layout
                topLayout5.addWidget(self.champ5) # ajouter le champ5 ( qLinEedit ) a ce layout


                
                layout.addLayout(topLayout4, 1, 0) # ajouter le QVBoxLayout a la position (1,0) 
                layout.addLayout(topLayout5, 1, 1) # ajouter le QVBoxLayout a la position (1,3) 
                layout.addLayout(topLayout,  1, 2) # ajouter le QVBoxLayout a la position (1,3) 
                layout.addLayout(topLayout1, 1, 3) # ajouter le QVBoxLayout a la position (1,3) 

                layout.addWidget(self.bouton,2,0,1,4) # ajouter le boutton a la position (2,0) et prend toute la largeur
                layout.addWidget(self.canvas,3,0,1,4) # ajouter le canvas la position (3,0) et prend toute la largeur

                #☺layout.addWidget(self.bouton1)
                self.setLayout(layout) # affiche le layout qui contient touts les layout
                self.setWindowTitle("Methode SWV") # titre de la fenetre
            
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
                    if (self.champ.text()!="" and self.champ6.text()!="" and self.champ7.text()!="" and self.champ8.text()!="" and self.champ9.text()!="" and self.champ10.text()!=""):
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
            global index_acq, board, index_param, nb_sum
            ctrl_while = True
            
            # on entre dans la boucle on envoi un message Board et on lire les information de l'arduino si on reçoit
            # "teensy" c'est a dire le nom de la carte on sort de la boucle
            while (ctrl_while):
                    message = self.BOARD.encode(self.UTF_8)
                    self.Arduino_Serial.write(message)
                    time.sleep(2*self.DELAY_1s)
                    received = self.Arduino_Serial.readline()[:-2]  # reads line from Arduino/Teensy and strips out NL + CR
                    received_utf8 = received.decode(self.UTF_8)
                    print (received_utf8)
                    if (received_utf8 == self.TEENSY):                                       
                            ctrl_while = False      # to break the loop
                            board =  received_utf8  
                            print (self.NEW_LINE + board + self.BOARD_DETECTED + self.QUOTE + self.port_board + self.QUOTE + self.NEW_LINE)
                            index_acq   = 0
                            index_param = 0
                            nb_sum      = 1
        #end of board detection function
        
        #*********************************
        #* Function to set up constants  *
        #********************************* 
        def set_contants(self):
                global quant_DAC, offset_DAC, quant_ADC, offset_ADC,coeff_conv,conv_period, rtia, delay_stab, gain
                quant_DAC   = self.QUANT_DAC_TEENSY
                offset_DAC  = self.OFFSET_DAC_TEENSY
                quant_ADC   = self.QUANT_ADC_TEENSY
                offset_ADC  = self.OFFSET_ADC_TEENSY 
                coeff_conv  = self.COEFF_CONV_TEENSY
                conv_period = self.CONV_PERIOD_TEENSY
                rtia        = self.RTIA_TEENSY
                delay_stab  = self.DELAY_STAB_TEENSY
                gain        = -1.0
        #end of set_constants function
                        
        #*********************************
        #* Function to set up RTIA       *
        #********************************* 
        def set_rtia(self):
                global rtia_val
                #str_rtia = input(" Enter the RTIA value in kΩ (Return => 4.7 kΩ) : ")
                
                #si on entre la valeur de la resistance on la stock quand rtia_val sinon on stock la valeur par default
                str_rtia = self.champ2.text()
                if (str_rtia == self.EMPTY):
                        rtia_val = self.RTIA_TEENSY
                else:
                        rtia_val = float(str_rtia) * self.KOHM
        #end of set_rtia function
        
        #*********************************
        #* Function to set up UNIT       *
        #********************************* 
        def set_unit(self):
                global str_unit, c_unit
                #str_unit = input(" Enter the curent unit (mA, uA, nA or pA) (Return => mA) : ")
                str_unit = self.champ3.text()
                #si on entre la l'unité du courant on la stock quand c_unit sinon on stock la valeur par default
                if (str_unit == self.EMPTY or str_unit == "mA"):
                        c_unit = self.COEFF_mA
                elif (str_unit == "uA"):
                        c_unit = self.COEFF_microA
                elif (str_unit == "nA"):
                        c_unit = self.COEFF_nA
                elif (str_unit == "pA"):
                        c_unit = self.COEFF_pA
        #end of set_unit function
                        
        #****************************************
        #* Function test the command received   *
        #****************************************
        def tst_cmd(self,received):
                # on cherche si l'argument est dans le contenaire CMD_AVA puis es qu'il est dans CMD_KEY et on lui donne la valeur approprier au cmd_stuts et cmd_code sinon on ecrit un message d'erreur
                if (received not in self.CMD_AVA):
                        if (received in self.CMD_KEY):
                                print ("Command not available")
                                self.cmd_status = False
                        else:
                                self.cmd_code = self.SET
                                self.cmd_status = True
                else:
                        self.cmd_code = received
                        self.cmd_status = True
        #end of tst_cmd function
                        
        #****************************************
        #* Function to set up acquisition size  *
        #**************************************** 
        def set_acq_size(self):
                global nb_ph, nb_ech, nb_ech_tot
                nb_ph = abs(int(round(float(code_Estart - code_Estop)/float(code_dE))))
                nb_ech_tot = nb_ph * 2 * nb_ech  
                #print (nb_ph, nb_ech_tot)
                if(nb_ech_tot > self.NB_ECH_MAX):
                        print("**************************")
                        print("* ERROR: to many samples *")
                        print("**************************")
                   
        #end of set_acq_size function
                                        
        #***************************************
        #* Function to set up ACQ values       *
        #***************************************
        def set_acq_value(self):
                global code_Estart, code_Estop, code_dE, code_Esw, period, nb_ech
                code_Estart = int(round( Estart/(quant_DAC * gain) + offset_DAC))       # compute the DAC code for Estart
                code_Estop  = int(round(  Estop/(quant_DAC * gain) + offset_DAC))       # compute the DAC code for Estop
                if( code_Estart > code_Estop ):    
                        code_dE  = - int(round(  dE/(self.COEFF_mV * quant_DAC)))                           # compute the DAC code for dE
                        code_Esw = - int(round( Esw/(self.COEFF_mV * quant_DAC)))                           # compute the DAC code for Esw
                else:
                        code_dE  = int(round(  dE/(self.COEFF_mV * quant_DAC)))
                        code_Esw = int(round( Esw/(self.COEFF_mV * quant_DAC)))
                period = int(round(float(abs(code_dE)) * quant_DAC * self.CONV_PERIOD_TEENSY/(eq_srate * 2 * nb_ech)))
                #print(period)
                str_Estart = str(code_Estart)   
                str_Estop  = str(code_Estop)    
                str_dE     = str(code_dE)  
                str_Esw    = str(code_Esw) 
                str_period = str(period)        # compute code of period in µs
                str_nb_ech = str(nb_ech)                 
                transmit = str_Estart + self.COMMA + str_Estop + self.COMMA + str_dE + self.COMMA + str_Esw + self.COMMA + str_period + self.COMMA + str_nb_ech
                message = transmit.encode(self.UTF_8)
                self.Arduino_Serial.write(message)
                print ("You Transmitted :", transmit)
                #print ()               
        #end of set_acq_value function
                                        
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
                        self.fichier=self.champ5.text()
                        self.index_file+=1

                        if self.fichier == self.EMPTY :     
                            file_name = "testSWV" + str(self.index_file ) + self.FILE_EXTENT 
                            file = open( file_name, self.WRITE_MODE,encoding = self.UTF_8)   # create a new file
                            print(file_name)
                        else:
                            if self.fichier==self.sauvegarde:
                                file_name = self.fichier + str(self.index_file) + self.FILE_EXTENT 
                                file = open( file_name, self.WRITE_MODE,encoding = self.UTF_8)   # createe a new file
                                print(file_name)
                            else:
                                self.index_file=0
                                file_name = self.fichier + self.FILE_EXTENT 
                                file = open( self.fichier+self.FILE_EXTENT, self.WRITE_MODE,encoding = self.UTF_8)   # create a new fileee
        #************************************
        #* Function to handle acquisition   *
        #************************************ 
        def get_acq(self): 
               
                
                global index_acq, index_param
                i_ech = 0
                ctrl_while = True
                nb_minute = 0
                iacq_time = int(self.acq_time - 1) # to avoid a long time out for the serial link
                if (iacq_time > self.MINUTE):
                        nb_minute = (iacq_time//self.MINUTE)
                        for i_sleep in range(nb_minute):
                                time.sleep(self.MINUTE)
                                print("Elapsed time",i_sleep + 1,"minute")
                remaining = int(iacq_time - nb_minute * self.MINUTE) + 1
                print("Remaining ",remaining,"seconds")
                time.sleep(remaining)
                while (ctrl_while):
                        data = self.Arduino_Serial.readline()[:-2]  # reads line from Arduino and stips out NL + CR
                        data_utf8 = data.decode(self.UTF_8)
                        if ( data_utf8 != "" ):                          
                                line = data_utf8
                                #print(index_acq)
                                val_c = (int(line) - offset_ADC) * quant_ADC * coeff_conv * (c_unit/rtia_val) # select COEFF_mA or COEFF_microA                                                
                                self.y_data[index_acq].append(val_c)
                                i_ech = i_ech + 1
                                if (i_ech == nb_ech_tot):
                                        ctrl_while = False
                index_acq   += 1
                index_param += 1

                self.CMD_AVA[self.TRA] = self.CMD_TRA
                self.Arduino_Serial.close()
                #print(CMD_AVA)
        #end of get_acq function
                
        #****************************************
        #* Function to set parameters           *
        #****************************************
        def set_param(self):
                global Estart, Estop, dE, Esw, eq_srate, nb_ech, index_acq
                for i in range(self.NB_PARAM):
                        if (i == 0):
                                if (self.params[i] != self.EMPTY):
                                        self.param[index_acq][0] = self.params[0]
                                else:
                                        self.params[0] = self.param[index_acq - 1][0]
                                        self.param[index_acq][0] = self.params[0]
                                Estart = float(self.params[0])
         
                        elif (i == 1):
                                if (self.params[i] !=self.EMPTY):
                                        self.param[index_acq][1] = self.params[1]
                                else:
                                        self.params[1] = self.param[index_acq - 1][1]
                                        self.param[index_acq][1] = self.params[1]
                                Estop = float(self.params[1])
                        
                        elif (i == 2):
                                if (self.params[i] != self.EMPTY):
                                        self.param[index_acq][2] = self.params[2]
                                else:
                                        self.params[2] = self.param[index_acq - 1][2]
                                        self.param[index_acq][2] = self.params[2]
                                dE = float(self.params[2])
                                
                        elif (i == 3):
                                if (self.params[i] != self.EMPTY):
                                        self.param[index_acq][3] = self.params[3]
                                else:
                                        self.params[3] = self.param[index_acq - 1][3]
                                        self.param[index_acq][3] = self.params[3]
                                Esw = float(self.params[3])        # extracts the Esw in mV
                                
                        elif (i == 4):
                                if (self.params[i] != self.EMPTY):
                                        self.param[index_acq][4] = self.params[4]
                                else:
                                        self.params[4] = self.param[index_acq - 1][4]
                                        self.param[index_acq][4] = self.params[4]
                                eq_srate= float(self.params[4])        # extracts the eq_srate value in V/s
        
                        elif (i == 5) :
                                if (self.params[i] != self.EMPTY):
                                        self.param[index_acq][5] = self.params[5]
                                else:
                                        self.params[5] = self.param[index_acq - 1][5]
                                        self.param[index_acq][5] = self.params[5]
                                nb_ech = int(self.params[5])        # extracts the number of point
                                                                                   
        #print(param[index_acq])
                                                            
        #**************************************
        #* Function to plot acquisition       *
        #**************************************
        def plot_acq (self,index_acq_graph, nb_ph, nb_ech):
                global code_Estart, code_Estop, code_dE, code_Esw, period, str_unit, nb_sum

                self.ax.clear()
                #print(index_acq_graph, nb_ph, nb_ech)
                f_Estart = float(self.param[index_acq_graph][0])
                f_Estop  = float(self.param[index_acq_graph][1])
                if( f_Estart < f_Estop):
                        f_dE =  + float(self.param[index_acq_graph][2])/self.COEFF_mV
                        x = [ (f_Estart + j * f_dE) for j in range(nb_ph)]
                else:
                        f_dE = - float(self.param[index_acq_graph][2])/self.COEFF_mV
                        x = [ (f_Estart + j * f_dE) for j in range(nb_ph)]              
                
                for i_curr in range(3):
                        if (i_curr == 0):
                                y_for = [0 for j in range(nb_ph)]
                                for j in range(nb_ph):
                                        for k in range(nb_sum):
                                                y_for[j] += self.y_data[index_acq_graph][nb_ech - k - 1 + j * 2 * nb_ech]
                                for j in range(nb_ph):
                                        y_for[j]= y_for[j]/nb_sum
                                plt.plot(x, y_for, self.gra_color[i_curr],label = "Forward current")
                                self.ax.plot(x, y_for, self.gra_color[i_curr],label = "Forward current")
              
                        elif (i_curr == 1):
                                y_rev = [0 for j in range(nb_ph)]
                                for j in range(nb_ph):
                                        for k in range(nb_sum):
                                                y_rev[j] += self.y_data[index_acq_graph][2*nb_ech - k - 1 + j * 2 * nb_ech]
                                for j in range(nb_ph):
                                        y_rev[j]= y_rev[j]/nb_sum
                                plt.plot(x, y_rev, self.gra_color[i_curr],label = "Reverse current")
                                self.ax.plot(x, y_rev, self.gra_color[i_curr],label = "Reverse current")
         
                        elif (i_curr == 2):
                                y_diff = [0 for j in range(nb_ph)]
                                for j in range(nb_ph):
                                        for k in range(nb_sum):
                                                l = nb_ech - k - 1  + j * 2 * nb_ech
                                                y_diff[j] += self.y_data[index_acq_graph][l] - self.y_data[index_acq_graph][ l + nb_ech]
                                for j in range(nb_ph):
                                        y_diff[j]= y_diff[j]/nb_sum
                                        data_file = (f"{x[j]:.6f}") + self.COMMA + (f"{y_diff[j]:.6f}") # six decimals
                                        nbytes = file.write(data_file + self.NEW_LINE)   # write data from Arduino in the file + NL  
                                file.flush()            # Don't forget to flush before closing the file
                                file.close
                                plt.plot(x, y_diff , self.gra_color[i_curr],label = "Difference current")
                                self.ax.plot(x, y_diff , self.gra_color[i_curr],label = "Difference current")
                                
                flat_x_data = x
                flat_y_data = (y_diff + y_for + y_rev)
                plt.xlim(min(flat_x_data), max(flat_x_data))        # set x limits
                plt.ylim(min(flat_y_data), max(flat_y_data))        # set y limits    
               
                self.ax.set_xlim(min(flat_x_data), max(flat_x_data))        # set x limits
                self.ax.set_ylim(min(flat_y_data), max(flat_y_data)) 
                
                if self.champ6.text()>self.champ7.text():
                    self.ax.set_title("Acquisition " + str(index_acq) +"\n" + "Cycles with a scan rate of " +  self.champ10.text() + " V/s \n Range["+ self.champ7.text()+ " V, " + self.champ6.text() + " V]")            # Title
                else  :
                    self.ax.set_title("Acquisition " + str(index_acq) +"\n" + "Cycles with a scan rate of " + self.champ10.text() + " V/s \n Range["+ self.champ6.text()+ " V, " + self.champ7.text() + " V]")            # Title
                
                self.ax.set_xlabel("E (V)")
                
                if (str_unit == self.EMPTY or str_unit == "uA"):
                            str_unit = "µA"
                self.ax.set_ylabel("I (" + str_unit + ")")            # y labels
                
                self.ax.grid(True)
                self.ax.legend()
                # refresh canvas
                self.canvas.draw()
                
                
                plt.title("Acquisition " + str(index_acq_graph) +"\n" + "Equivalent scan rate of " + self.param[index_acq_graph][4] + " V/s \n Range["+ self.param[index_acq_graph][0]+ " V, " + self.param[index_acq_graph][1] + " V]")            # Title
                plt.xlabel("E (V)")             # x labels
                if (str_unit  == "uA"):
                            str_unit = "µA"
                plt.ylabel("I (" + str_unit + ")")            # y labels
                plt.legend()
                plt.show()          # Show graph on screen
        # end of function
        
                                        
        #********************************
        #* Entering the modem's number  *
        #********************************
        def principal(self):
            
            # on verifie si les champ obligatoire son rempli sinon on affiche un message d'erreur
             if self.champ6.text()!="" and self.champ7.text()!="" and self.champ8.text()!="" and self.champ9.text()!="" and self.champ10.text()!="" and self.champ11.text()!="":
              # on definie ici les vecteur d'acquisition pour qu'a chaque fois on execute la fonction on reinitialise les valeur
                self.x_data = [[] for i in range(self.MAX_ACQ)]
                self.y_data = [[] for i in range(self.MAX_ACQ)]
                                
                modem_number = self.champ.text()
                if (modem_number == self.EMPTY):
                        self.port_board = self.PORT_TEENSY
                        #port_board = PORT_ARDUINO
                else:
                        modem_number = str(modem_number)
                        self.port_board = self.PORT_BOARD + modem_number
                       
                #********************************
                #* Openning of the serial link  *
                #********************************
                self.Arduino_Serial = serial.Serial(self.port_board, self.BAUD_RATE, timeout=self.TIME_OUT)
                time.sleep(self.DELAY_1s) #give the connection a second to settle
                msg="SquareWave"
                message = msg.encode(self.UTF_8)
                self.Arduino_Serial.write(message)
                time.sleep(self.DELAY_1s)      
                #****************************************
                #* Board detection  & set up constants  *
                #****************************************
                self.board_detection()
                self.set_contants()
                
                #********************************
                #* RTIA set-up & UNIT           *
                #********************************
                self.set_rtia()
                self.set_unit()
                        
                #********************************
                #* Printing of input message    *
                #********************************
                print ("Enter Parameters like 0.6,-0.2,5,50,21,20 then ACQ to start acquisition and TRA to graph the data \n")
                         
                #********************************
                #* Infinite loop                *
                #********************************
                i=0                
                while True:
                        if (index_acq == self.MAX_ACQ):            # setting WARNING message
                                for w in range(8):
                                        print(self.WARNING[w])
                                self.CMD_AVA = {self.CMD: self.CMD_CMD, self.PAR: self.CMD_PAR, self.TRA: self.CMD_TRA, self.DEF: self.EMPTY, self.MODE: self.CMD_MODE, self.EXIT: self.CMD_EXIT}
                 # au debut on envoit les donner à l'arduino puis ACQ puis TRA puis EXIT
                        if i==0 :
                                    received = self.champ6.text()+","+self.champ7.text()+","+self.champ8.text()+","+self.champ9.text()+","+self.champ10.text()+","+self.champ11.text()
                        elif i==1:
                                            received="ACQ"
                        elif i==2:
                                            received="TRA"
                        elif i==3:
                                            received="EXIT"
                        self.tst_cmd(received)
                        #accepts input puts it in variable 'received'
                        if ( self.cmd_code == self.SET and self.cmd_status == True): #in case you entered "1,-1.25,1.25,5"
                                #print ("You Entered :", received)   
                                self.params = [name.strip() for name in received.split(self.COMMA)]
                                self.set_param()
                                #print(Estart, Estop, eq_srate)                                                     
                                self.acq_time = abs((2*nb_ech * ((Estart - Estop)/(eq_srate * 2 * nb_ech)))) + delay_stab # add the delay to stabilize Estart
                                iacq_time = int(self.acq_time)
                                if (iacq_time > self.MINUTE):
                                        i_minute = iacq_time // self.MINUTE
                                        i_second = iacq_time % self.MINUTE
                                        print( "The acquisition will take roughly : ", i_minute, "minutes and",i_second,"seconds" )
                                else:
                                        print( "The acquisition will take roughly : ", (f"{self.acq_time:.2f}"), " seconds")
                                self.set_acq_value()
                                self.set_acq_size()
                                time.sleep(10*self.DELAY_01s)
                                self.CMD_AVA[self.ACQ] = self.CMD_ACQ
                                i=1
                #********************************
                #* "ACQ" is received            *
                #********************************
                        if (  self.cmd_code == self.ACQ and self.cmd_status == True):                                 #if input is "ACQ"
                                message = received.encode(self.UTF_8)
                                self.Arduino_Serial.write(message)                                                                    
                                print(self.ACQ_START)
                                self.set_up_file(self.index_file)
                                time.sleep(self.DELAY_01s)                
                                self.set_acq_size()
                                self.set_param()
                                self.get_acq()
                                time.sleep(self.DELAY_01s)                
                                print (self.ACQ_END)
                                i=2
                #end of first if loop
                     
                
                #********************************
                #* "TRA" is received            *
                #********************************
                        if (  self.cmd_code == self.TRA and self.cmd_status == True):                                 #if input is "TRA"                                                                    
                                #acq_graph = input( "Enter the acquisition's number to graph [0," + str(index_acq -1) +"] (Return => last acq) : ")
                                #acq_graph=self.champ4.text()
                                acq_graph=""
                                if (acq_graph == self.EMPTY):
                                        index_acq_graph = index_acq - 1
                                else:
                                        index_acq_graph = int(acq_graph)
                                print(self.TRA_START)
                                time.sleep(self.DELAY_01s)
                                self.plot_acq (index_acq_graph, nb_ph, nb_ech)
                                print(self.TRA_END)
                                i=3
                        #end of if statement              
                
                 
                #*******************************
                #* "RTIA" is received   *
                #*******************************
                        if (  self.cmd_code == self.RTIA and self.cmd_status == True):
                                self.set_rtia()
                        # end of if statement
                
                #*******************************
                #* "UNIT" is received           *
                #*******************************
                        if (  self.cmd_code == self.UNIT and self.cmd_status == True):
                                self.set_unit()
                        # end of if statement
                
                #*******************************
                #* "PAR" is received           *
                #*******************************
                        if (  self.cmd_code == self.PAR and self.cmd_status == True):
                                #print (index_param)
                                for i in range(self.MAX_ACQ):                       
                                        str_param = "Acq " + str(i) + " :" + self.param[i][0]
                                        if ( i > (index_param - 1)):
                                                str_param = self.UNDEFINED
                                                for j in range(self.NB_PARAM - 1):
                                                        str_param += self.COMMA + self.UNDEFINED
                                                print (str_param)
                                        else:
                                                for j in range(self.NB_PARAM - 1):
                                                        str_param += self.COMMA + self.param[i][j+1]
                                                print (str_param)
                                      
                #********************************
                #* "FILE" is received           *
                #********************************
                        if (  self.cmd_code == self.FILE and self.cmd_status == True ):
                                #str_file_index = input(" Enter a number for the starting of indexing file (Return => 0) : ")
                                str_file_index =self.champ5.text()
                                if (str_file_index == self.EMPTY):
                                        str_file_index = "0"
                                self.index_file = int(str_file_index)
                                self.set_up_file(self.index_file)
                                           
                # end of infinite loop
                
                #********************************
                #* "CMD" or "" is received      *
                #********************************
                        if ( self.cmd_code == self.CMD or  self.cmd_code == self.DEF) and self.cmd_status == True:
                                for key in self.CMD_AVA:
                                        if (key != self.EMPTY):
                                                print(key, self.CMD_AVA[key])
                
                #********************************
                #* "MODE" or "" is received      *
                #********************************
                        if ( self.cmd_code == self.MODE and self.cmd_status == True):
                                str_nb_sum = input(" Enter the number of summing samples (Return => 1) : ")
                                if (str_nb_sum == self.EMPTY):
                                       str_nb_sum = "1"
                                nb_sum = int(str_nb_sum)
                                           
                #********************************
                #* "EXIT" is received           *
                #********************************
                        if ( self.cmd_code == self.EXIT):
                                self.Arduino_Serial.close()
                                break


             else:
                                 #message d'erreur sur les champs obligatoir
                                 msg = QMessageBox()
                                 msg.setIcon(QMessageBox.Critical)
                                 msg.setText("Error")
                                 msg.setInformativeText('please enter at least the link port, the number of cycles, the start potential, the two insertion potentials, and the scan speed')
                                 msg.setWindowTitle("Error")  
                                 msg.setWindowTitle('Quit')

                                 msg.exec_()

