#include <TimerOne.h>
#include <ADC.h>
#include <ADC_util.h>
#include <SPI.h> 

ADC *adc = new ADC(); // adc object;

#define TEENSY_BOARD "Teensy"
#define BAUD_RATE  9600
#define NB_PARAM   8
#define NB_PARAM1 7
#define NB_PARAM2 8
#define COMMA ','
#define EQUAL '='

#define IDDLE_STATE     0
#define ACTIVE_STATE    1

#define CODE_STEP       1
#define MAX_DAC      4095         // Maximum code for DAC
#define DAC_VZERO       0
#define DAC_V1V65    2048
#define V5V             5.00
#define ADC_12BITS    12
#define ADC_AVG        8
#define ADC_IN        A0
#define DAC_12BITS    12
#define DAC_OUT      A21
#define PERIOD        10  // Period of 10 µs
#define PIN_MARK       6  // To synchronise an Oscilloscope
#define PIN_CTRL       5

#define DELAY_1s     1000
#define DELAY_1ms    1000
#define DELAY_BLK     200
#define PER_BLK       1012

#define MIN_CYCLE       1
#define MAX_CYCLE       1
#define MAX_CYCLE1       3

#define PULSE_CYCLE      3
#define ERROR_INDEX     -1   // Indicateur d'erreur si l'entrée de la chaîne de caractères n'est pas une de celles qui est attendue
#define OK              true // Simple transposition du booléen true
#define ERROR_INPUT     false// Idem pour false

#define resistor_portA  27
#define resistor_portB  28
#define resistor_portC  29
#define cap_port1       24
#define cap_port2       25
#define cap_port3       26

unsigned long time_init, time_final ;
int cur[11*1024] ;
int val[MAX_CYCLE1][12000]={0} ;
int  index_acq1, index_acq1_up[MAX_CYCLE1], index_acq1_up1[MAX_CYCLE1], index_acq1_down[MAX_CYCLE1], index_acq1_down1[MAX_CYCLE1] ;
int code_DAC1, code_DAC1_vstart , code_DAC1_vstop,code_DAC1_vstop1 ;
int code_DAC1_end[MAX_CYCLE1] ;
unsigned long param1[NB_PARAM1] ;

int i, index_acq, index_acq_cycle ;
int nb_cycle, i_cycle ;
int code_DAC, code_DAC_Estart , code_DAC_Estop, code_DAC_dE, code_DAC_Esw ;
int i_ph, nb_ech, nb_ph;
int code_high, code_low, code_DAC_end[MAX_CYCLE] ;
int i_blk, code_step ;
int datacount;

int V1,V2,nb_cyc;
unsigned short adcread[10153]={0} ;
unsigned long param2[NB_PARAM2] ;
int resis_index, cap_index;

volatile boolean state = IDDLE_STATE; // for the ISR subroutine
volatile byte  counter = 0;

int received_length, received_pos_comma, received_pos_equal ;
unsigned long param[NB_PARAM] ;
unsigned long period ;
String received, received_param ;
boolean status_input ; 
boolean statusInputParam ;
boolean statusInputAcq ;
boolean blk, ox ;

int choix;

void rita(int index);
void cap(int index);
/****************************************************************************/
/*              Setup pins                                                  */
/****************************************************************************/
void setup(void) {
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(DAC_OUT,OUTPUT) ;   // for DAC
  pinMode(ADC_IN, INPUT);     // for ADC
  pinMode(PIN_MARK, OUTPUT) ; // To synchronise an Oscilloscope
  pinMode(PIN_CTRL, OUTPUT) ; // To switch on/off the cell

  pinMode(LED_BUILTIN, OUTPUT);
  
  pinMode(resistor_portA, OUTPUT); // for resistor mux
  pinMode(resistor_portB, OUTPUT); // for resistor mux
  pinMode(resistor_portC, OUTPUT); // for resistor mux
  pinMode(cap_port1, OUTPUT); // for capcitor mux
  pinMode(cap_port2, OUTPUT); // for  capcitor mux
  pinMode(cap_port3, OUTPUT); // for  capcitor mux
  /****************************************************************************/
  /*              Setup ADC parameters                                        */
  /****************************************************************************/
  digitalWrite(PIN_CTRL, LOW) ;
  state = IDDLE_STATE ;
  analogWriteResolution(DAC_12BITS);
  analogReadResolution (ADC_12BITS) ;
  adc->adc0->setReference(ADC_REFERENCE::REF_3V3);
  adc->adc0->setAveraging(ADC_AVG); // set number of averages ;
  adc->adc0->setConversionSpeed(ADC_CONVERSION_SPEED::HIGH_SPEED); // change the conversion speed
  adc->adc0->setSamplingSpeed(ADC_SAMPLING_SPEED::HIGH_SPEED); // change the sampling speed
    
  /****************************************************************************/
  /*              Print message and wait 2 s                                  */
  /****************************************************************************/
  Serial.begin(BAUD_RATE);
  delay(2*DELAY_1s);              // wait for 3 seconds

  status_input     = ERROR_INPUT ;
  statusInputParam  = ERROR_INPUT ;
  statusInputAcq    = ERROR_INPUT ;
  delay(DELAY_1s);              // Wait for 1 second
  
  choix=true;
}

/****************************************************************************/
/*    The main program will print the data to the Arduino Serial Monitor    */
/****************************************************************************/

void loop(void) {
  time_init = micros();
  /****************************************************************************/
  /*              Test input character                                        */
  /****************************************************************************/
  if (Serial.available() > 0) { // If Serial data available
     received = Serial.readString() ;       // Get Serial string
    // Serial.println("received:"+ received);
    if (received=="SquareWave"){
        choix=0;
      }
    if (received=="VoltaCyclique"){
          choix=1;
      }
    if (received=="OCV"){
        choix=2;
     }
    if (received=="PULSE"){
        choix=3;
     }
  if (choix==0){
  
   
    
   }
  if (choix==1){
    /*____________________________ Volta______________________________________*/
    /********************************************************************/
    /*            SET parameters command                                */
    /********************************************************************/

    if ( received != "ACQ" && received != "BOARD" ) {

      for ( i = 0 ; i < NB_PARAM1 ; i++) { 
        received_length = received.length() ;
        received_pos_comma  = received.indexOf(COMMA) ;
        received_param = received.substring(0, received_pos_comma) ;
        param1[i] = received_param.toInt() ;
        received = received.substring(received_pos_comma + 1, received_length);
      } 
      
      resis_index     = param1[5] ;
      cap_index       = param1[6] ;
      rita(resis_index );
      cap(cap_index);
      delay(10);
      if ( param1[1] > param1[2]) { // We start with Oxydation
        code_step = CODE_STEP ;
        ox = true ;    
      }
      else {
        code_step = - CODE_STEP ;
        ox = false ;
      }
    }

      /********************************************************************/
      /*            BOARD command                                         */
      /********************************************************************/
    else if(received == "BOARD") {
      Serial.println(TEENSY_BOARD) ;     // send the board type to the Pyhon script  
    }   
     
      /********************************************************************/
      /*            ACQ command                                           */
      /********************************************************************/
    else if(received == "ACQ") {   
      //Timer1.initialize(period);
      //Timer1.attachInterrupt(ISR_State); // 
      digitalWrite(LED_BUILTIN, HIGH) ;
      //time_final = micros();
      delayMicroseconds(DELAY_1ms);
      
      code_DAC1_vstart = param1[1] ;
      code_DAC1_vstop  = param1[2]  ;
      code_DAC1_vstop1  = param1[3]  ;
      nb_cycle = param1[0] ;
      period = param1[4] ;
      analogWrite(DAC_OUT, code_DAC1_vstart) ;
      delay(DELAY_1s) ;
      //Serial.print("code_DAC1_vstart = ") ;Serial.println(code_DAC1_vstart) ;
      //Serial.print("code_DAC1_vstop  = ") ;Serial.println(code_DAC1_vstop) ;
      
      /********************************************************************/
      /*            Loop for firt part of the cycle                       */
      /********************************************************************/
     int values[] = {code_DAC1_vstart, code_DAC1_vstop, code_DAC1_vstop1};
     int numValues = sizeof(values) / sizeof(values[0]);
     index_acq1=0;
     // Loop through each value three times
     for (i_cycle = 0; i_cycle < nb_cycle; i_cycle++) {
      index_acq1=0;
      for (int i = 0; i < numValues; i++) {
        int current_value = values[i];
        int next_index = (i + 1) % numValues; // when the vaules goes to index 2 the next value will be  index 0
        int next_value = values[next_index];

        // Gradually increase DAC output from current_value to next_value
        if (current_value < next_value) {
          for (int output = current_value; output <= next_value; output++) {
            analogWrite(DAC_OUT, output);
            delayMicroseconds(period);
            val[i_cycle][index_acq1] = adc->adc0->analogRead(ADC_IN); 
           // Serial.print(output);Serial.print(",");Serial.println(val[i_cycle][index_acq1]);

            index_acq1++;
           // Print DAC and ADC values for debugging
        }
        } else { // Decrease DAC output if current_value > next_value
          for (int output = current_value; output >= next_value; output--) {
            analogWrite(DAC_OUT, output);
            delayMicroseconds(period);
            val[i_cycle][index_acq1] = adc->adc0->analogRead(ADC_IN);
            //Serial.print(output);Serial.print(",");Serial.println(val[i_cycle][index_acq1]);
            index_acq1++;
          }
        }
      }
    }

    // Serial.println("don dacing");
      //***************************************************************/
      /*           Loop for printing Data on Serial link                  */
      /********************************************************************/
      index_acq1=0;
        blk = true ; 
     for (i_cycle = 0; i_cycle < nb_cycle; i_cycle++) {
      index_acq1=0;
      for (int i = 0; i < numValues; i++) {
        int current_value = values[i];
        int next_index = (i + 1) % numValues; // when the vaules goes to index 2 the next value will be  index 0
        int next_value = values[next_index];

        // Gradually increase DAC output from current_value to next_value
        if (current_value < next_value) {
          for (int output = current_value; output <= next_value; output++) {
  
            delay(3);
            if(i_cycle<0 || i_cycle >3 || index_acq1 >12000||  index_acq1 <0  ){Serial.print("ERROR:trying to print i_cycle: " );Serial.print( i_cycle);Serial.print("+ index_acq1: ");Serial.println(index_acq1);}
            Serial.print(output);Serial.print(",");Serial.println(val[i_cycle][index_acq1]);
            Serial.send_now(); 
            Serial.flush(); 
            index_acq1++;
            i_blk = output % PER_BLK ;
            if (i_blk == 0) {
              digitalWrite(LED_BUILTIN, blk); // To show Serial link transfert
              blk = !blk ;
              //            Serial.flush();
            }


           // Print DAC and ADC values for debugging
        }
        } else { // Decrease DAC output if current_value > next_value
          for (int output = current_value; output >= next_value; output--) {
            delay(3);
            if(i_cycle<0 || i_cycle >3 || index_acq1 >12000||  index_acq1 <0  ){Serial.print("ERROR:trying to print i_cycle: " );Serial.print( i_cycle);Serial.print("+ index_acq1: ");Serial.println(index_acq1);}
            Serial.print(output);Serial.print(",");Serial.println(val[i_cycle][index_acq1]);
            Serial.send_now(); 
            Serial.flush(); 
            index_acq1++;

           i_blk = output % PER_BLK ;
            if (i_blk == 0) {
              digitalWrite(LED_BUILTIN, blk); // To show Serial link transfert
              blk = !blk ;
           //            Serial.flush();
            }

          }
        }
      }
    }
     // Serial.println("done");
      digitalWrite(LED_BUILTIN, LOW );
      analogWrite(DAC_OUT, code_DAC1_vstart); // DAC pin = A22
   
    }
   }
  if (choix==2){
   //  Serial.println("OCVED");
   if ( received != "ACQ" && received != "BOARD" ) {
     //    Serial.println("datasend");
      for ( i = 0 ; i < NB_PARAM2 ; i++) { 
        
        received_length = received.length() ;
        
       
        received_pos_comma  = received.indexOf(COMMA) ;
       // Serial.printf(" received_pos_comma: %i\n",received_pos_comma);
        received_param = received.substring(0, received_pos_comma) ;
       // Serial.printf(" received_param: %s\n",received_param.c_str());
        param2[i] = received_param.toInt() ;
       // Serial.printf( " param 2 :  %i\n", param2[i]);
        received = received.substring(received_pos_comma +1 , received_length);
       // Serial.printf(" received_line: %s\n",received.c_str());
        delay(50);
      //  Serial.flush();
      } 
       V1              = param2[0] ;
       V2              = param2[1] ;
       nb_cyc          = param2[2] ;
     //downtime        = param2[3] ;
       period          = param2[4] ;
     //nb_test         = param2[5] ;
       resis_index     = param2[6] ;
       cap_index       = param2[7] ;
      rita(resis_index );
      cap(cap_index);
      pinMode(DAC_OUT,INPUT) ; 
      delay(10);
     //Serial.println(V1);
    //Serial.println(V2);
    //Serial.println(nb_cyc);
    //Serial.println(period);
    //Serial.println(resis_index);
     //Serial.println(cap_index); 
   }
  
   else if(received == "BOARD") {
      Serial.println(TEENSY_BOARD) ;     // send the board type to the Pyhon script  
    }   

    else if(received == "ACQ") {
     //Serial.println("acq");
     digitalWrite(LED_BUILTIN, HIGH) ;
      //time_final = micros();
    delayMicroseconds(DELAY_1ms);
    datacount=0;
    for(int cycle=0; cycle < MAX_CYCLE1; cycle++ ){
     
      analogWrite(DAC_OUT, V1);

      for (int i = 0; i < nb_cyc; ++i) {
         // Read ADC value
        adcread[datacount] = adc->adc0->analogRead(ADC_IN);  // Store ADC reading in the array
        datacount++;  // Increment the index for the next reading
        delay(period);
      }

      analogWrite(DAC_OUT, V2);
      
      for (int i = 0; i < nb_cyc; ++i) {
         // Read ADC value
        adcread[datacount] = adc->adc0->analogRead(ADC_IN);  // Store ADC reading in the array
        datacount++;  // Increment the index for the next reading
        delay(period);
      }

    }
     pinMode(DAC_OUT,INPUT) ; 
     for (int i = 0; i < datacount; ++i) {
    

      Serial.println(adcread[i]);
      i_blk = i % PER_BLK ;
      if (i_blk == 0) {
      digitalWrite(LED_BUILTIN, blk); // To show Serial link transfert
      blk = !blk ;
      }
    }


    }
  
  
   }
  if (choix==3){

    //  Serial.println("pulse");
   if ( received != "ACQ" && received != "BOARD" ) {
     //    Serial.println("datasend");
      for ( i = 0 ; i < NB_PARAM2 ; i++) { 
        
        received_length = received.length() ;  
        received_pos_comma  = received.indexOf(COMMA) ;
       // Serial.printf(" received_pos_comma: %i\n",received_pos_comma);
        received_param = received.substring(0, received_pos_comma) ;
       // Serial.printf(" received_param: %s\n",received_param.c_str());
        param2[i] = received_param.toInt() ;
       // Serial.printf( " param 2 :  %i\n", param2[i]);
        received = received.substring(received_pos_comma +1 , received_length);
       // Serial.printf(" received_line: %s\n",received.c_str());
        delay(50);
      //  Serial.flush();
      } 
       V1              = param2[0] ;
       V2              = param2[1] ;
       nb_cyc          = param2[2] ;
     //downtime        = param2[3] ;
       period          = param2[4] ;
     //nb_test         = param2[5] ;
       resis_index     = param2[6] ;
       cap_index       = param2[7] ;
      rita(resis_index );
      cap(cap_index);
      pinMode(DAC_OUT,INPUT) ; 
      delay(10);
     //Serial.println(V1);
    //Serial.println(V2);
    //Serial.println(nb_cyc);
    //Serial.println(period);
    //Serial.println(resis_index);
     //Serial.println(cap_index); 
   }
  
   else if(received == "BOARD") {
      Serial.println(TEENSY_BOARD) ;     // send the board type to the Pyhon script  
    }   

    else if(received == "ACQ") {
     //Serial.println("acq");
     digitalWrite(LED_BUILTIN, HIGH) ;
      //time_final = micros();
     delayMicroseconds(DELAY_1ms);
     datacount=0;


     analogWrite(DAC_OUT, V1);
      for (int i = 0; i < nb_cyc; ++i) {
         // Read ADC value
        adcread[datacount] = adc->adc0->analogRead(ADC_IN);  // Store ADC reading in the array
        datacount++;  // Increment the index for the next reading
        delay(period);
      }

      analogWrite(DAC_OUT, V2);
      
      for (int i = 0; i < nb_cyc; ++i) {
         // Read ADC value
        adcread[datacount] = adc->adc0->analogRead(ADC_IN);  // Store ADC reading in the array
        datacount++;  // Increment the index for the next reading
        delay(period);
      }

    
     pinMode(DAC_OUT,INPUT) ; 
      for (int i = 0; i < datacount; ++i) {
       Serial.println(adcread[i]);
        i_blk = i % PER_BLK ;
        if (i_blk == 0) {
        digitalWrite(LED_BUILTIN, blk); // To show Serial link transfert
        blk = !blk ;
      }
    }
   }
  
  


   }
 }

}
/********************************************************************/
/*     The interrupt will start acquisition using DAC and ADC       */
/********************************************************************/     
void ISR_State1(void) {
  state = ACTIVE_STATE ;
  counter++ ;
}

void ISR_State(void) {
  state = ACTIVE_STATE ;
}
void cap(int index){

  switch (index) {

    // input array of what the user 0:2p  1:20p   2:50p   3:100p  4:200p  5:1n  6:50n  7:100n 
    // output array  2p:x3  20p:x0  50p:x1  100p:x2 200p:x5 1n:x7 50n:x6 100n:x4
    case 1: //x0
      digitalWrite(cap_port1, LOW);
      digitalWrite(cap_port2, LOW);
      digitalWrite(cap_port3, LOW);
      break;
    case 2://x1
      digitalWrite(cap_port1, HIGH);
      digitalWrite(cap_port2, LOW);
      digitalWrite(cap_port3, LOW);
      break;
    case 3://x2
      digitalWrite(cap_port1, LOW);
      digitalWrite(cap_port2, HIGH);
      digitalWrite(cap_port3, LOW);
      break;
    case 0://x3
      digitalWrite(cap_port1, HIGH);
      digitalWrite(cap_port2, HIGH);
      digitalWrite(cap_port3, LOW);
      break;
    case 7://x4
      digitalWrite(cap_port1, LOW);
      digitalWrite(cap_port2, LOW);
      digitalWrite(cap_port3, HIGH);
      break;
    case 4://x5
      digitalWrite(cap_port1, HIGH);
      digitalWrite(cap_port2, LOW);
      digitalWrite(cap_port3, HIGH);
      break;
    case 6://x6
      digitalWrite(cap_port1, LOW);
      digitalWrite(cap_port2, HIGH);
      digitalWrite(cap_port3, HIGH);
      break;
    case 5://x7
      digitalWrite(cap_port1, HIGH);
      digitalWrite(cap_port2, HIGH);
      digitalWrite(cap_port3, HIGH);
      break;
    default:
      // Handle cases beyond 7 (e.g., x0)
      digitalWrite(cap_port1, LOW);
      digitalWrite(cap_port2, LOW);
      digitalWrite(cap_port3, LOW);
      break;
  }
}
void rita(int index){

  // input array    0:1k  1:10k   2:100k   3:1M  4:10M  5:30M  6:100M  7:1G
  // output array  1k:x4  10k:x6  100k:x7  1m:x5 10m:x2 30m:x1 100M:x0 1G:x3
  switch (index) {
    case 6: // x0
      digitalWrite(resistor_portA, LOW);
      digitalWrite(resistor_portB, LOW);
      digitalWrite(resistor_portC, LOW);
      break;
    case 5: //x1
      digitalWrite(resistor_portA, HIGH);
      digitalWrite(resistor_portB, LOW);
      digitalWrite(resistor_portC, LOW);
      break;
    case 4: //x2
      digitalWrite(resistor_portA, LOW);
      digitalWrite(resistor_portB, HIGH);
      digitalWrite(resistor_portC, LOW);
      break;
    case 7: //x3
      digitalWrite(resistor_portA, HIGH);
      digitalWrite(resistor_portB, HIGH);
      digitalWrite(resistor_portC, LOW);
      break;
    case 0: //x4
      digitalWrite(resistor_portA, LOW);
      digitalWrite(resistor_portB, LOW);
      digitalWrite(resistor_portC, HIGH);
      break;
    case 3: //x5
      digitalWrite(resistor_portA, HIGH);
      digitalWrite(resistor_portB, LOW);
      digitalWrite(resistor_portC, HIGH);
      break;
    case 1: //x6
      digitalWrite(resistor_portA, LOW);
      digitalWrite(resistor_portB, HIGH);
      digitalWrite(resistor_portC, HIGH);
      break;
    case 2: //x7
      digitalWrite(resistor_portA, HIGH);
      digitalWrite(resistor_portB, HIGH);
      digitalWrite(resistor_portC, HIGH);
      break;
    default:
      // Handle cases beyond 7 (e.g., x0)
      digitalWrite(resistor_portA, LOW);
      digitalWrite(resistor_portB, LOW);
      digitalWrite(resistor_portC, LOW);
      break;
  }

}



