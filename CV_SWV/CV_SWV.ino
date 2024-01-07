#include <TimerOne.h>
#include <ADC.h>
#include <ADC_util.h>
#include <SPI.h> 

ADC *adc = new ADC(); // adc object;

#define TEENSY_BOARD "Teensy"
#define BAUD_RATE  115200
#define NB_PARAM   6
#define NB_PARAM1 5
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
#define DAC_OUT      A22
#define PERIOD        10  // Period of 10 µs
#define PIN_MARK       6  // To synchronise an Oscilloscope
#define PIN_CTRL       5

#define DELAY_1s     1000
#define DELAY_1ms    1000
#define DELAY_BLK     200
#define PER_BLK       512

#define MIN_CYCLE       1
#define MAX_CYCLE       1
#define MAX_CYCLE1       3

#define ERROR_INDEX     -1   // Indicateur d'erreur si l'entrée de la chaîne de caractères n'est pas une de celles qui est attendue
#define OK              true // Simple transposition du booléen true
#define ERROR_INPUT     false// Idem pour false

unsigned long time_init, time_final ;
int cur[11*1024] ;
int val[MAX_CYCLE1][10153] ;
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

volatile boolean State = IDDLE_STATE; // for the ISR subroutine
volatile byte  counter = 0;

int received_length, received_pos_comma, received_pos_equal ;
unsigned long param[NB_PARAM] ;
unsigned long period ;
String received, received_param ;
boolean status_input ; 
boolean status_input_param ;
boolean status_input_acq ;
boolean blk, ox ;

boolean choix;

/****************************************************************************/
/*              Setup pins                                                  */
/****************************************************************************/
void setup(void) {
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(DAC_OUT,OUTPUT) ;   // for DAC
  pinMode(ADC_IN, INPUT);     // for ADC
  pinMode(PIN_MARK, OUTPUT) ; // To synchronise an Oscilloscope
  pinMode(PIN_CTRL, OUTPUT) ; // To switch on/off the cell
 
  /****************************************************************************/
  /*              Setup ADC parameters                                        */
  /****************************************************************************/
  digitalWrite(PIN_CTRL, LOW) ;
  State = IDDLE_STATE ;
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

  status_input        = ERROR_INPUT ;
  status_input_param  = ERROR_INPUT ;
  status_input_acq    = ERROR_INPUT ;
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
 
    if (received=="SquareWave"){
        choix=false;
      }
    if (received=="VoltaCyclique"){
          choix=true;
      }
      
    
    if (choix==false){
    /********************************************************************/
    /*            SET parameters command                                */
    /********************************************************************/
   
    if ( received != "ACQ" && received != "BOARD" ) {
      for ( i = 0 ; i < NB_PARAM ; i++) {     
        received_length = received.length() ;
        received_pos_comma  = received.indexOf(COMMA) ;
        received_param = received.substring(0, received_pos_comma) ;
        param[i] = received_param.toInt() ;
        received = received.substring(received_pos_comma + 1, received_length);
      } 
      code_DAC_Estart = param[0] ;
      code_DAC_Estop  = param[1]  ;
      code_DAC_dE     = param[2] ;
      code_DAC_Esw    = param[3] ;
      period          = param[4] ;
      nb_ech          = param[5] ;
      nb_ph = abs(round((float)((float)param[1] - (float)param[0])/((float)code_DAC_dE))) ;
      //Serial.println(nb_ph);
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
      Timer1.initialize(period);
      Timer1.attachInterrupt(ISR_State1); // 
      digitalWrite(LED_BUILTIN, HIGH) ;
      digitalWrite(PIN_CTRL, HIGH) ; // Switch on the cell
      //time_final = micros();
      delayMicroseconds(DELAY_1ms);
      
      analogWrite(DAC_OUT, code_DAC_Estart) ;
      delay(2*DELAY_1s) ;
      //Serial.print("code_DAC_Estart = ") ;Serial.println(code_DAC_Estart) ;
      //Serial.print("code_DAC_Estop  = ") ;Serial.println(code_DAC_Estop) ;
      
      /********************************************************************/
      /*            Loop for the acquisition                              */
      /********************************************************************/
      nb_cycle = 1 ;

/********************************************************************/
/*           Acquisition starts                                     */
/********************************************************************/ 
      index_acq = 0 ;
      
      State = IDDLE_STATE ;  
      for ( i_ph = 0 ; i_ph < nb_ph ; i_ph++ ) {
        counter = 0 ;
        code_high = code_DAC_Estart + i_ph * code_DAC_dE + code_DAC_Esw ;
        code_low  = code_high - 2 * code_DAC_Esw ;
        analogWrite(DAC_OUT, code_high); // DAC pin = A22
        digitalWrite(PIN_MARK, !digitalRead(PIN_MARK));
        while ( counter < nb_ech ) {
          while (State == IDDLE_STATE) ;
          State = IDDLE_STATE ;
          cur[index_acq] = adc->adc0->analogRead(ADC_IN) ;
          index_acq++ ;
        }
        counter = 0 ;
        analogWrite(DAC_OUT, code_low); // DAC pin = A22
        while ( counter < nb_ech ) {
          while (State == IDDLE_STATE) ;
          State = IDDLE_STATE ;
          cur[index_acq] = adc->adc0->analogRead(ADC_IN) ;
          index_acq++ ;
        }
        index_acq_cycle = index_acq - 1;
        //Serial.println(index_acq_cycle) ;
      }
      
      /********************************************************************/
      /*           Loop for printing Data on Serial link                  */
      /********************************************************************/
        blk = true ;                 
        for ( i = 0 ; i <= index_acq_cycle ; i++ ) {
          i_blk = i % PER_BLK ;
          if (i_blk == 0) {
            digitalWrite(LED_BUILTIN, blk); // To show Serial link transfert
            blk = !blk ;
          }
            delay(3);
            Serial.println(cur[i]);
        }
        digitalWrite(PIN_CTRL, LOW) ;  // Switch off the cell
        digitalWrite(LED_BUILTIN, LOW) ;
        
    }
    
  }
  if(choix==true){
/*********************************** volta****************************************************/
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
      period = param1[4] ;
      Timer1.initialize(period);
      Timer1.attachInterrupt(ISR_State); // 
      digitalWrite(LED_BUILTIN, HIGH) ;
      //time_final = micros();
      delayMicroseconds(DELAY_1ms);
      
      code_DAC1_vstart = param1[1] ;
      code_DAC1_vstop  = param1[2]  ;
      code_DAC1_vstop1  = param1[3]  ;
      analogWrite(DAC_OUT, code_DAC1_vstart) ;
      delay(2*DELAY_1s) ;
      //Serial.print("code_DAC1_vstart = ") ;Serial.println(code_DAC1_vstart) ;
      //Serial.print("code_DAC1_vstop  = ") ;Serial.println(code_DAC1_vstop) ;
      
      /********************************************************************/
      /*            Loop for firt part of the cycle                       */
      /********************************************************************/
      nb_cycle = param1[0] ;
      if( nb_cycle > 3) nb_cycle = 3 ;
      switch (nb_cycle) {
        case 1:
          code_DAC1_end[0] = code_DAC1_vstart ;
          break;
        case 2:
          code_DAC1_end[0] = code_DAC1_vstart - code_step ;
          code_DAC1_end[1] = code_DAC1_vstart ;
          break;
        case 3:
          code_DAC1_end[0] = code_DAC1_vstart - code_step ;
          code_DAC1_end[1] = code_DAC1_vstart - code_step ;
          code_DAC1_end[2] = code_DAC1_vstart ;
          break;
      }

/********************************************************************/
/*           Cycle starts in Oxydation                              */
/********************************************************************/ 
      if (ox == true) {
        for (i_cycle = 0 ; i_cycle < nb_cycle ; i_cycle++) {
          index_acq1 = 0 ;   
          
          for ( code_DAC1 = code_DAC1_vstart; code_DAC1 >= code_DAC1_vstop ; code_DAC1 -= CODE_STEP ) {
            while (State == IDDLE_STATE) ;
            State = IDDLE_STATE ;
            analogWrite(DAC_OUT, code_DAC1); // DAC pin = A22
            val[i_cycle][index_acq1] = adc->adc0->analogRead(ADC_IN); // read a new value, will return ADC_ERROR_VALUE if the comparison is false.
            index_acq1 +=1 ;
          }
          index_acq1_down[i_cycle] = index_acq1 - 1;
      
      /********************************************************************/
      /*            Loop for second part of the cycle                     */
      /********************************************************************/     
          for ( code_DAC1 = code_DAC1_vstop ; code_DAC1 <= code_DAC1_vstop1 ; code_DAC1 += CODE_STEP ){
            while (State == IDDLE_STATE) ;
            State = IDDLE_STATE ;
            analogWrite(DAC_OUT, code_DAC1);
            val[i_cycle][index_acq1] = adc->adc0->analogRead(ADC_IN); // read a new value, will return ADC_ERROR_VALUE if the comparison is false.
            index_acq1 +=1 ;
          }
          index_acq1_up[i_cycle] = index_acq1 - 1 ;
        
        /************************************************************/
        for ( code_DAC1 = code_DAC1_vstop1; code_DAC1 >= code_DAC1_end[0] ; code_DAC1 -= CODE_STEP ) {
            while (State == IDDLE_STATE) ;
            State = IDDLE_STATE ;
            analogWrite(DAC_OUT, code_DAC1); // DAC pin = A22
            val[i_cycle][index_acq1] = adc->adc0->analogRead(ADC_IN); // read a new value, will return ADC_ERROR_VALUE if the comparison is false.
            index_acq1 +=1 ;
          }
          index_acq1_down1[i_cycle] = index_acq1 - 1;
        }
    
      /********************************************************************/
      /*           Loop for printing Data on Serial link                  */
      /********************************************************************/

        blk = true ; 
        for ( i_cycle = 0 ; i_cycle < nb_cycle ; i_cycle++ ) {                 
          for ( i = 0 ; i <= index_acq1_down1[i_cycle] ; i += CODE_STEP ) {
            if ( i <= index_acq1_down[i_cycle] ) {
              code_DAC1 = code_DAC1_vstart - i ;
            }
            else if(i>index_acq1_down[i_cycle] and i<=index_acq1_up[i_cycle]){
              code_DAC1 = code_DAC1_vstop + (i - index_acq1_down[i_cycle] - 1) ;
            }
            else{
              code_DAC1 = code_DAC1_vstop1 - (i - index_acq1_up[i_cycle] - 1) ;
            }
            i_blk = i % PER_BLK ;
            if (i_blk == 0) {
              digitalWrite(LED_BUILTIN, blk); // To show Serial link transfert
              blk = !blk ;
            }
            delay(3);
            Serial.print(code_DAC1);Serial.print(",");Serial.println(val[i_cycle][i]);

          }
        }
      }

/********************************************************************/
/*           Cycle starts in Reduction                              */
/********************************************************************/      
      else {
        for (i_cycle = 0 ; i_cycle < nb_cycle ; i_cycle++) {
          index_acq1 = 0 ; 
            
          for ( code_DAC1 = code_DAC1_vstart; code_DAC1 < code_DAC1_vstop ; code_DAC1 += CODE_STEP ) {
            while (State == IDDLE_STATE) ;
            State = IDDLE_STATE ;
            analogWrite(DAC_OUT, code_DAC1); // DAC pin = A22
            val[i_cycle][index_acq1] = adc->adc0->analogRead(ADC_IN); // read a new value, will return ADC_ERROR_VALUE if the comparison is false.
            index_acq1 +=1 ;
          }
          index_acq1_up[i_cycle] = index_acq1  - 1;
      
      /********************************************************************/
      /*            Loop for second part of the cycle                     */
      /********************************************************************/     
          for ( code_DAC1 = code_DAC1_vstop ; code_DAC1 > code_DAC1_vstop1; code_DAC1 -= CODE_STEP ){
            while (State == IDDLE_STATE) ;
            State = IDDLE_STATE ;
            analogWrite(DAC_OUT, code_DAC1);
            val[i_cycle][index_acq1] = adc->adc0->analogRead(ADC_IN); // read a new value, will return ADC_ERROR_VALUE if the comparison is false.
            index_acq1 +=1 ;
          }
          index_acq1_down[i_cycle] = index_acq1 - 1 ;

/***********************************************************************/
           for ( code_DAC1 = code_DAC1_vstop1; code_DAC1 <= code_DAC1_end[0]  ; code_DAC1 += CODE_STEP ) {
            while (State == IDDLE_STATE) ;
            State = IDDLE_STATE ;
            analogWrite(DAC_OUT, code_DAC1); // DAC pin = A22
            val[i_cycle][index_acq1] = adc->adc0->analogRead(ADC_IN); // read a new value, will return ADC_ERROR_VALUE if the comparison is false.
            index_acq1 +=1 ;
          }
          index_acq1_up1[i_cycle] = index_acq1  - 1;


          
        }
      /********************************************************************/
      /*           Loop for printing Data on Serial link                  */
      /********************************************************************/
        blk = true ; 

        for ( i_cycle = 0 ; i_cycle < nb_cycle ; i_cycle++ ) {                 
          for ( i = 0 ; i <= index_acq1_up1[i_cycle] ; i += CODE_STEP ) {
            if ( i <= index_acq1_up[i_cycle] ) {
              code_DAC1 = code_DAC1_vstart + i*CODE_STEP ;
            }
            else if(i>index_acq1_up[i_cycle] and i<=index_acq1_down[i_cycle]) {
              code_DAC1 = code_DAC1_vstop - (i*CODE_STEP - index_acq1_up[i_cycle] - 1) ;
            }
             else {
              code_DAC1 = code_DAC1_vstop1 +(i*CODE_STEP - index_acq1_down[i_cycle] - 1) ;
            }

            
            i_blk = i % PER_BLK ;
            if (i_blk == 0) {
              digitalWrite(LED_BUILTIN, blk); // To show Serial link transfert
              blk = !blk ;
            }
                        delay(3);
            Serial.print(code_DAC1);Serial.print(",");Serial.println(val[i_cycle][i]);
          }

          
         }
      }  
      digitalWrite(LED_BUILTIN, LOW );
      analogWrite(DAC_OUT, code_DAC1_vstart); // DAC pin = A22
    }
    
    //


  }
  }

}
/********************************************************************/
/*     The interrupt will start acquisition using DAC and ADC       */
/********************************************************************/     
void ISR_State1(void) {
  State = ACTIVE_STATE ;
  counter++ ;
}

void ISR_State(void) {
  State = ACTIVE_STATE ;
}
