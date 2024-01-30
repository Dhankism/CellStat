

import serial, time, math, os
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

PORT_BOARD = "COM"                     # for PC CPU
BAUD_RATE =  115200
TIME_OUT = 30
                
EMPTY    = ""
BOARD    = "BOARD"




BOARD_DETECTED = " board detected on "
ARDUINO  = "Arduino"
TEENSY   = "Teensy"
NEW_LINE = "\n"
COMMA    = ","
ACQ_START  = "Acquisition Started"
ACQ_END    = "Acquisition Ended "
TRA_START  = "Tracing Started "
TRA_END    = "Tracing Ended "
INVITE = ">>"
QUOTE  = '"'
EQUAL  = '='
UNDEFINED = "-"
WARNING = [EMPTY,EMPTY,EMPTY,EMPTY,EMPTY,EMPTY,EMPTY,EMPTY]
WARNING[0]  ="********************************************************************" 
WARNING[1]  ="*   WARNING - You have reached the MAXIMUM number of acquisition   *" 
WARNING[2]  ="*   WARNING -    You can't set up a new acquisition right now      *"
WARNING[3]  ="*   WARNING -        Your FILES will be overwritten                *"
WARNING[4]  ="*   WARNING -            Your DATA will be LOST                    *"
WARNING[5]  ="*   WARNING - Consider CLOSING this program and OPENNING it again  *"
WARNING[6]  ="*   WARNING -        The only available Command is TRA             *"
WARNING[7]  ="********************************************************************" + self.NEW_LINE
MAX_ACQ     = 16
MAX_CYCLE   = 3
NB_PARAM    = 5
acq_time=""
DELAY_01s = 0.1
DELAY_1s  = 1
CODE_STEP = 1

QUANT_PWM           = 0.0200513
OFFSET_PWM          = 128.
QUANT_DAC_ARDUINO   = 5./4096.
OFFSET_DAC_ARDUINO  = 2048
QUANT_ADC_ARDUINO   = 5./4095
OFFSET_ADC_ARDUINO  = 2048
COEFF_CONV_ARDUINO  = 1.0
CONV_PERIOD_ARDUINO = 1000.             # in order to convert in ms
DELAY_STAB_ARDUINO  = 2.0

QUANT_DAC_TEENSY    = 1./800       # extracted from calibration process
OFFSET_DAC_TEENSY   = 2093           # extracted from calibration process
QUANT_ADC_TEENSY    = 3.3/4095
OFFSET_ADC_TEENSY   = 2045.0
COEFF_CONV_TEENSY   = 1.51              # inverse of the output voltage divider
CONV_PERIOD_TEENSY  = 1.0 * 1000000.    # in order to convert in micros and take care of the first stage gain
DELAY_STAB_TEENSY   = 2.0

R10k         = 10000.0
RTIA_ARDUINO =  1000.0                   # to be change to the right value
RTIA_TEENSY  =  100000.0
KOHM         =  1000.0
CODE_MAX_RTIA = 255
CODE_MIN_RTIA =  12

COEFF_mA     =          1000.0             # scale in mA
COEFF_microA =       1000000.0             # scale in microA
COEFF_nA     =    1000000000.0             # scale in nA
COEFF_pA     = 1000000000000.0             # scale in pA



class window1(QWidget):
        def __init__(self):# declaration du constructeur
                #**************************
                # declaration des atribue *
                #**************************
                #################################################"
                #self.PORT_ARDUINO = "/dev/cu.usbmodem641"
                #self.PORT_TEENSY  = "/dev/cu.usbmodem6837991"
                #self.PORT_BOARD = "/dev/cu.usbmodem"         # for MAC CPU
                #self.PORT_BOARD="/dev/ttyACM"                # for linux
                
                self.input=[UNDEFINED,UNDEFINED,UNDEFINED,UNDEFINED,UNDEFINED,UNDEFINED,UNDEFINED,UNDEFINED,UNDEFINED] #[ V1, V2, T1,T2,scanrate,ncycles,rita, cap]
		self.folder_name="NAN"
		self.cycle_i=0
		self.folder_i=0
								
                self.resistorlabels = ["±2mA", "±.2mA", "±20 uA", "±2uA", "±.2uA", "±67uA", "±20nA", "±2nA"]
                self.resistorvalues = [value*self.KOHM for value in [1, 10, 100, 1000, 10000, 30000, 100000, 1000000]]
                self.Capacitorlabels = ["2p", "20p", "50p", "100p", "200p", "1n", "50n", "100n"]
                self.capindex=0
                self.ritaindex=0
		self.num_pwm =6
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
                
                self.lpotential1 = QLabel(text=" Enter the first potential in V") # creation du qlabel
                self.userV1 = QLineEdit() # creation de QlineEdit pour rentrer les information
                
                self.lpotential2 = QLabel(text=" Enter the second potential in V") # creation du qlabel
                self.userV2 = QLineEdit() # creation de QlineEdit pour rentrer les information
                
                self.lvoltagechangerate = QLabel(text=" Enter voltage change time in seconds") # creation du qlabel
                self.voltagechangerate = QLineEdit() # creation de QlineEdit pour rentrer les information
                
                self.lrefreshrate = QLabel(text=" Enter wait time in seconds") # creation du qlabel
                self.downtime = QLineEdit() # creation de QlineEdit pour rentrer les information
                
                self.lscantime = QLabel(text=" Enter scan rate") # creation du qlabel
                self.scanrate = QLineEdit() # creation de QlineEdit pour rentrer les information

                self.lcycle = QLabel(text=" Enter cycle rate") # creation du qlabel
                self.ncycles = QLineEdit() # creation de QlineEdit pour rentrer les information


                self.figure = plt.Figure() # creation de la figure
                self.canvas = FigureCanvas(self.figure) # creation du canvas qui prend comme argument la figure
                self.ax = self.figure.add_subplot(111) # creation des ax
                
                layout = QGridLayout() # creation du layoutgrid
                # création du bouton
                self.bouton = QPushButton("Start")
                self.bouton.clicked.connect(self.principal) # relier le boutton avec la fonction principal qui s'excute quand on clic sur le boutton
                
                # création du bouton
                self.stop = QPushButton("Stop")
                self.stop.clicked.connect(self.stop_running)
                #self.stop.clicked.connect(s) # relier le boutton avec la fonction principal qui s'excute quand on clic sur le boutton
                


                self.button = QPushButton("Save")
                self.button.clicked.connect(self.save)# on connecter l'action a la fonction save si il y une action sur save action on declanche la fonction save
      
                self.image = QImage(self.size(), QImage.Format_RGB32) # creation d'une image format_RGB32
                self.image.fill(Qt.white)
                
                topLayout = QVBoxLayout() # creation  du QVBoxLayout
                topLayout.addWidget(self.lpotential1) # ajouter le label6 a ce layout
                topLayout.addWidget(self.lpotential2)
                topLayout.addWidget(self.lvoltagechangerate) # ajouter le label7 a ce layout
                topLayout.addWidget(self.lrefreshrate) # ajouter le label8 a ce layout
                topLayout.addWidget(self.lscantime) # ajouter le label9 a ce layout
                topLayout.addWidget(self.lcycle)
                
                topLayout1 = QVBoxLayout() # creation  du QVBoxLayout
                topLayout1.addWidget(self.userV1) 
                topLayout1.addWidget(self.userV2) # ajouter le champ6 ( qLinEedit ) a ce layout
                topLayout1.addWidget(self.voltagechangerate) # ajouter le champ7 ( qLinEedit ) a ce layout
                topLayout1.addWidget(self.downtime) # ajouter le champ8 ( qLinEedit ) a ce layout
                topLayout1.addWidget(self.scanrate)
                topLayout1.addWidget(self.ncycles)

                topLayout4 = QVBoxLayout() # creation  du QVBoxLayout
                topLayout4.addWidget(self.luserportnumber) # ajouter le label a ce layout
                topLayout4.addWidget(self.lirange)
                topLayout4.addWidget(self.lcaprange) # ajouter le label2 a ce layout
                topLayout4.addWidget(self.lcurrentunit) # ajouter le label3 a ce layout
                topLayout4.addWidget(self.lfilename) # ajouter le label5 a ce layout
                
                topLayout5 = QVBoxLayout() # creation  du QVBoxLayout
                topLayout5.addWidget(self.userportnumber) 

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
                self.setWindowTitle("Method OCV") # titre de la fenetre
        
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
                    if (self.userportnumber.text()!="" and self.userV1.text()!="" and self.userV2.text()!="" and self.scanrate.text()!="" and self.voltagechangerate.text()!="" and self.downtime.text()!="" and self.ncycles.text()!="" ):
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
                       self.ritaindex = 3
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
        #*********************************
        #* Function to set up UNIT       *
        #********************************* 
        def set_input_data(self,board):
		global pwm_count=0,V1_dac=0,V2_dac=0, aqctime=0
                V1_dac =int(round( self.userV1 /(self.QUANT_PWM ) + self.OFFSET_PWM))
		V2_dac=int(round( self.userV2 /(self.QUANT_PWM ) + self.OFFSET_PWM))
		pwn_count=round(self.voltagechangerate.text()/self.scanrate.text())
		aqctime=self.voltagechangerate.text()*self.num_pwm 
		input[0] = str(V1_dac)   # compute the DAC code for V1
                input[1] = str(V2_dac)   # compute the DAC code for V2
                input[2]=str(pwm_count)
                input[3]=str(self.downtime.text())
                input[4]=str(self.scanrate.text())
                input[5]=str(self.ncycles.text())
                input[6]=str( self.ritaindex )
                input[7]=str( self.capindex )

        
        
        #end of set_unit function
        
  
                                    
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
                
                if self.downtime.text()>self.champ9.text():
                    self.ax.set_title("Acquisition " + str(self.index_acq) +"\n" + "Cycles with a scan rate of " + self.champ10.text() + " V/s \n Range["+ self.champ9.text()+ " V, " + self.downtime.text() + " V]")            # Title
                else  :
                    self.ax.set_title("Acquisition " + str(self.index_acq) +"\n" + "Cycles with a scan rate of " + self.champ10.text() + " V/s \n Range["+ self.downtime.text()+ " V, " + self.champ9.text() + " V]")            # Title

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
                          self.set_rtia(board)
                          self.set_cap(board)
                          self.set_unit(board)
                          self.set_input_data(board)

                          # Check if the folder already exists
			  global folder_name
                          if not os.path.exists(self.userfilename):
                          # If it doesn't exist, create it
                            os.makedirs(self.userfilename)
                            folder_name =f"{self.userfilename}"
                            print(f"Folder '{self.userfilename}' created.")
                          else:
                          # If it exists, find a new name by adding a number
                            i = 1
                            while os.path.exists(f"{self.userfilename}_{i}"):
                            i += 1
                            os.makedirs(f'{self.userfilename}_{i}')
			    folder_name =f'{self.userfilename}_{i}'
                          print(f'{folder_name}_created.')
 													
                          transmit = ','.join(input) 
                          transmit = msg.encode(self.UTF_8)
                          self.Arduino_Serial.write( transmit)
			  time.sleep(self.DELAY_1s) 
			  print(f'{transmit}')
			  #tell it ot run the commands
			  message="ACQ"
                          message = msg.encode(self.UTF_8)
                          self.Arduino_Serial.write(message)
			  print('acq_start')
			  time.sleep(self.DELAY_1s) 
			  #get the results and put it into a file 
			  sleep.(aqctime+2)# wait this much time for the rady read be outputed
			  data_array = []

  			   try:
        	           line_count = 0
			   time=0
       				while True:
       				 line = arduino.readline().decode('utf-8').strip()
      			         if not line:
              			   break  # Exit the loop if there's nothing left to read

      			        # Split each line into three segments based on commas
       				 segments = line.split(',')
				 val_v = (int(segment[0]) - offset_DAC) * gain * quant_DAC
                                 val_c = (int(segment[1]) - offset_ADC) * quant_ADC * coeff_conv * (c_unit/self.rtia_val)
				 time =time+1/self.scanrate.text()
     				 # Append 
     				 data_array.append((line_count, val_v,val_c,time))
     				 line_count += 1

 			   file_path = os.path.join(folder_name, f'{self.userfilename})

    			   with open(file_path, 'w') as file:
    			   for index, segments in data_array:
     			   file.write(f"Line {index}: {segments}\n")

			   #
			   #put into a graph and save
 			   self.ax.clear()
                        for i_cycle in range(self.nb_cycle):
                        self.x = self.x_data[index_acq][i_cycle]
                        self.y = self.y_data[index_acq][ i_cycle]
                        self.ax.plot(self.x, self.y, self.gra_color[i_cycle],label = "Cycle" + str(i_cycle + 1)) 
                self.flat_x_data = [item for sublist in self.x_data[index_acq] for item in sublist]
                self.flat_y_data = [item for sublist in self.y_data[index_acq] for item in sublist]

                self.ax.set_xlim(min(self.flat_x_data), max(self.flat_x_data))        # set x limits
                self.ax.set_ylim(min(self.flat_y_data), max(self.flat_y_data))        # set y limits    
                
                if self.downtime.text()>self.champ9.text():
                    self.ax.set_title("Acquisition " + str(self.index_acq) +"\n" + "Cycles with a scan rate of " + self.champ10.text() + " V/s \n Range["+ self.champ9.text()+ " V, " + self.downtime.text() + " V]")            # Title
                else  :
                    self.ax.set_title("Acquisition " + str(self.index_acq) +"\n" + "Cycles with a scan rate of " + self.champ10.text() + " V/s \n Range["+ self.downtime.text()+ " V, " + self.champ9.text() + " V]")            # Title

                self.ax.set_xlabel("E (V)")
                if (self.str_unit == self.EMPTY or self.str_unit == "uA"):
                            self.str_unit = "µA"
                self.ax.set_ylabel("I (" + self.str_unit + ")")            # y labels
                
                self.ax.grid(True)
                self.ax.legend()
                # refresh canvas
                self.canvas.draw()
                
			  #set command to repeat ntimes
						 							


        def stop_running(self)  
                                     
                              

if __name__ == '__main__':
        app = QApplication.instance() 
        if not app:
                app = QApplication(sys.argv)
        fen = window1()
        fen.show()
        app.exec_()
