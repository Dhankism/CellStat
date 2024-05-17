

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
WARNING[7]  ="********************************************************************" 
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

QUANT_DAC_TEENSY    = 1./830       # extracted from calibration process
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
                
                self.input=[UNDEFINED,UNDEFINED,UNDEFINED,UNDEFINED,UNDEFINED,UNDEFINED,UNDEFINED,UNDEFINED] #[ V1, V2, T1,T2,scanrate,ncycles,rita, cap]
                self.folder_name="NAN"
                self.cycle_i=0
                self.folder_i=0
                self.pwm_count = 0
                self.V1_dac=0
                self.V2_dac=0 
                self.aqctime=0
								
                self.resistorlabels = ["±2.5mA", "±.25mA", "±25uA", "±2.5uA", "±.25uA", "±72uA", "±25nA", "±2.5nA"]
                self.resistorvalues = [value*KOHM for value in [1, 10, 100, 1000, 10000, 30000, 100000, 1000000]]
                self.Capacitorlabels = ["2p", "20p", "50p", "100p", "200p", "1n", "50n", "100n"]
                self.capindex=0
                self.ritaindex=0
                self.num_pwm =6
                self.flag=False
                
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
                self.x_data = []
                self.y_data = []
                     
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
                
                self.lT1 = QLabel(text=" Enter starting time in seconds") # creation du qlabel
                self.T1 = QLineEdit() # creation de QlineEdit pour rentrer les information
                
              #  self.lrefreshrate = QLabel(text=" Enter pulse time seconds") # creation du qlabel
               # self.downtime = QLineEdit() # creation de QlineEdit pour rentrer les information
                
                self.lscantime = QLabel(text=" Enter scan rate") # creation du qlabel
                self.scanrate = QLineEdit() # creation de QlineEdit pour rentrer les information

              #  self.lcycle = QLabel(text=" Enter cycle rate") # creation du qlabel
               # self.ncycles = QLineEdit() # creation de QlineEdit pour rentrer les information


                self.figure = plt.Figure() # creation de la figure
                self.canvas = FigureCanvas(self.figure) # creation du canvas qui prend comme argument la figure
                self.ax = self.figure.add_subplot(111) # creation des ax
                
                layout = QGridLayout() # creation du layoutgrid
                # création du bouton
                self.bouton = QPushButton("Start")
                self.bouton.clicked.connect(self.principal) # relier le boutton avec la fonction principal qui s'excute quand on clic sur le boutton
                
                # création du bouton
               # self.stop = QPushButton("Stop")
               # self.stop.clicked.connect(self.stop_running)
                #self.stop.clicked.connect(s) # relier le boutton avec la fonction principal qui s'excute quand on clic sur le boutton
                


                self.button = QPushButton("Save")
                self.button.clicked.connect(self.save)# on connecter l'action a la fonction save si il y une action sur save action on declanche la fonction save
      
                self.image = QImage(self.size(), QImage.Format_RGB32) # creation d'une image format_RGB32
                self.image.fill(Qt.white)
                
                topLayout = QVBoxLayout() # creation  du QVBoxLayout
                topLayout.addWidget(self.lpotential1) # ajouter le label6 a ce layout
                topLayout.addWidget(self.lpotential2)
                topLayout.addWidget(self.lT1) # ajouter le label7 a ce layout
               # topLayout.addWidget(self.lrefreshrate) # ajouter le label8 a ce layout
                topLayout.addWidget(self.lscantime) # ajouter le label9 a ce layout
               # topLayout.addWidget(self.lcycle)
                
                topLayout1 = QVBoxLayout() # creation  du QVBoxLayout
                topLayout1.addWidget(self.userV1) 
                topLayout1.addWidget(self.userV2) # ajouter le champ6 ( qLinEedit ) a ce layout
                topLayout1.addWidget(self.T1) # ajouter le champ7 ( qLinEedit ) a ce layout
                # topLayout1.addWidget(self.downtime) # ajouter le champ8 ( qLinEedit ) a ce layout
                topLayout1.addWidget(self.scanrate)
                # topLayout1.addWidget(self.ncycles)

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

                layout.addWidget(self.bouton,2,0,1,3)
              # layout.addWidget(self.stop,2,2,1,3) # ajouter le boutton a la position (2,0) et prend toute la largeur
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
                 time.sleep(DELAY_1s) 
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

                    if (self.userportnumber.text()!="" and self.userV1.text()!="" and self.userV2.text()!="" and self.scanrate.text()!="" and self.T1.text()!="" and self.downtime.text()!="" and self.ncycles.text()!="" ):
                        self.principal()
                    else:
                        # message d'erreur qui indique que les champs obligatoire ne sont par rempli
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Critical)
                        msg.setText("Error")
                        msg.setInformativeText('please enter at least the link port, the Voltage values, the scan rate, the the voltage change rate, and the cyc amount')
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
                    message = BOARD.encode(self.UTF_8)
                    self.Arduino_Serial.write(message)
                    while self.Arduino_Serial.in_waiting == 0:
                           pass
                    received = self.Arduino_Serial.readline()[:-2]  # reads line from Arduino/Teensy and strips out NL + CR
                    received_utf8 = received.decode(self.UTF_8)
                    print (received_utf8)
                    if (received_utf8 == ARDUINO or received_utf8 == TEENSY):                                       
                            ctrl_while = False      # to break the loop
                            board =  received_utf8  
                            print (NEW_LINE + board + BOARD_DETECTED + QUOTE + self.port_board + QUOTE + NEW_LINE)
                            self.index_acq   = 0
                            index_param = 0
        
        
        #end of board detection function

        #*********************************
        #* Function to set up constants  *
        #********************************* 
        def set_contants(self,board):
                global quant_DAC, offset_DAC, quant_ADC, offset_ADC,coeff_conv,conv_period, rtia, delay_stab, gain
                if ( board == ARDUINO):
                        quant_DAC   = QUANT_DAC_ARDUINO
                        offset_DAC  = OFFSET_DAC_ARDUINO
                        quant_ADC   = QUANT_ADC_ARDUINO
                        offset_ADC  = OFFSET_ADC_ARDUINO
                        coeff_conv  = COEFF_CONV_ARDUINO
                        conv_period = CONV_PERIOD_ARDUINO
                        rtia = RTIA_ARDUINO
                        delay_stab  = DELAY_STAB_ARDUINO
                        gain = +1.0
                
                elif (board == TEENSY):
                        quant_DAC   = QUANT_DAC_TEENSY
                        offset_DAC  = OFFSET_DAC_TEENSY
                        quant_ADC   = QUANT_ADC_TEENSY
                        offset_ADC  = OFFSET_ADC_TEENSY 
                        coeff_conv  = COEFF_CONV_TEENSY
                        conv_period = CONV_PERIOD_TEENSY
                        rtia = RTIA_TEENSY
                        delay_stab  = DELAY_STAB_TEENSY
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
                if (self.str_unit == EMPTY or self.str_unit == "uA"):
                        c_unit = COEFF_microA
                elif (self.str_unit == "mA"):
                        c_unit = COEFF_mA
                elif (self.str_unit == "nA"):
                        c_unit = COEFF_nA
                elif (self.str_unit == "pA"):
                        c_unit = COEFF_pA
                else:
                        print("unit not found used uA as default")
                        c_unit = COEFF_microA
        
        #end of set_unit function
        #*********************************
        #* Function to set up UNIT       *
        #********************************* 
        def set_input_data(self,board):
                
                self.V1_dac =int(round( float(self.userV1.text()) /(quant_DAC * gain) + offset_DAC))
                self.V2_dac=int(round( float(self.userV2.text()) /(quant_DAC * gain) + offset_DAC))

                self.pwm_count=int(round(float(self.T1.text())*float(self.scanrate.text())))

                self.aqctime=round(float(self.T1.text())*self.num_pwm) 
                self.input[0] = str(self.V1_dac)   # compute the DAC code for V1
                self.input[1] = str(self.V2_dac)   # compute the DAC code for V2
                self.input[2] = str(self.pwm_count)
                self.input[3] = str(00)
                self.input[4] = str(round((1/float(self.scanrate.text()))*1000))
                self.input[5] = str(00)
                self.input[6] = str( self.ritaindex )
                self.input[7] = str( self.capindex )
                self.aqctime=round(float(self.T1.text())*self.num_pwm) 

        
        
        #end of set_unit function
        
  
                                    
        #print(param[index_acq])
                                                           
        
              
        def run_data(self):


                msg = ','.join(self.input) 
                transmit = msg.encode(self.UTF_8)
                self.Arduino_Serial.write(transmit)
                time.sleep(DELAY_1s) 

                print(f'{transmit}')
		        #tell it to run the commands
                msg="ACQ"
                message = msg.encode(self.UTF_8)
                self.Arduino_Serial.write(message)
                print('acq_start')
                print( "The acquisition will take roughly : ", (f"{self.aqctime:.2f}"), " seconds")
		       
                #get the results and put it into a file 
                time.sleep(self.aqctime*2+10)# wait this much time for the ready read be outputed
                data_array = []

                
                line_count = 0
                scantime=0
                xdata = []
                ydata = []
               # start_time = time.time()
                while True:
                        line = self.Arduino_Serial.readline().decode('utf-8').strip()
                        
                       # print(line) 
                        if (line_count+1>=self.pwm_count*2):
                                break  # Exit the loop if there's nothing left to read
                        if not line:
                               continue

      			# Split each line into three segments based on commas

                        val_c = (int(line) - offset_ADC) * quant_ADC * coeff_conv * (c_unit/self.rtia_val)
                        scantime =scantime+(1/float(self.scanrate.text()))

                        xdata.append(float(scantime))
                        ydata.append(float(val_c))
                        print(line_count, (f"{val_c:.6f}"), (f"{scantime:.6f}"),self.pwm_count*2)	 # Append 
                        data_array.append((line_count, (f"{val_c:.6f}"), (f"{scantime:.6f}")))
                        line_count += 1

                       
                        
                file_name= str(f'{self.userfilename.text()}')  + ".txt"
                
                with open( file_name , 'w') as file:
                        for index, segments in enumerate(data_array):
                                file.write((f"{segments[0]} ,{segments[1]} ,{segments[2]} \n"))
                              #  print((f"{segments[0]} ,{segments[1]} ,{segments[2]} \n"))
			   
                
                file.close


               # end_time= time.time() 
                #duration = end_time - start_time
               # print("Loop duration:", duration, "seconds")

                self.ax.clear()
               
                self.ax.plot(xdata, ydata ) 


                self.ax.set_xlim(min(xdata) , max(xdata) )       # set x limits
                self.ax.set_ylim(min(ydata), max(ydata))        # set y limits    
                
                # Title
                self.ax.set_title("Acquisition for "+ self.userV1.text()+" V to " + self.userV2.text() + " V " + "for "+self.T1.text()+ "s")      
                self.ax.set_xlabel("time (s)")
                if (self.str_unit == EMPTY or self.str_unit == "uA"):
                            self.str_unit = "µA"
                self.ax.set_ylabel("I (" + self.str_unit + ")")            # y labels
                self.ax.grid(True)
                
                # refresh canvas
                self.canvas.draw()

                
                       
                      
                                      
        def principal(self):
                #********************************
                #* Entering the modem's number  *
                 #********************************
                modem_number = self.userportnumber.text()
                if (modem_number == EMPTY):
                                        
                        self.port_board = self.PORT_TEENSY
                                      #  port_board = PORT_ARDUINO
                else:
                        modem_number = str(modem_number)
                        self.port_board = PORT_BOARD + modem_number
                        self.liason=False
                                    
                               
                #********************************
                #* Openning of the serial link  *
                #********************************
                                
                self.Arduino_Serial = serial.Serial(self.port_board, BAUD_RATE, timeout=TIME_OUT)
                     
                time.sleep(DELAY_1s) #give the connection a second to settle
                msg="PULSE"
                message = msg.encode(self.UTF_8)
                self.Arduino_Serial.write(message)
                time.sleep(DELAY_1s)      
                #****************************************
                #* Board detection  & set up constants  *
                #****************************************
                self.board_detection()
                self.set_contants(board)
                self.set_rtia(board)
                self.set_cap(board)
                self.set_unit(board)
                self.set_input_data(board)
										
                self.run_data()# run a test now

                self.Arduino_Serial.close() 

        
			  #set command to repeat ntimes
						 							



                                     
                              

if __name__ == '__main__':
        app = QApplication.instance() 
        if not app:
                app = QApplication(sys.argv)
        fen = window1()
        fen.show()
        app.exec_()
