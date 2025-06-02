#include <ADC.h>
#include <ADC_util.h>

ADC *adc = new ADC(); // adc object;

// This example uses the timer interrupt to blink an LED
// and also demonstrates how to share a variable between
// the interrupt and the main program.
#define BAUD_RATE  115200


#define ADC_STEP        0.000805664/1.51
#define CODE_STEP       1
#define MAX_ADC      4095         // Maximum code for DAC
#define DAC_VZERO       0
#define DAC_V1V65    2048

#define DELAY_1s       1000

#define EQUAL             "="
#define INPUT_DAC         "DAC"
#define INPUT_DAC_MAX_LENGHT  9
#define INPUT_DAC_LENGTH      3
#define MIN_DAC      0
#define MAX_DAC   4095

#define INPUT_ADC         "ADC"
#define INPUT_ADC_MAX_LENGHT  4
#define INPUT_ADC_LENGTH      3
#define MIN_ADC      0
#define MAX_ADC   4095




#define GO     "GO"
#define ERROR_INDEX     -1   // Indicateur d'erreur si l'entrée de la chaîne de caractères n'est pas une de celles qui est attendue
#define OK              true // Simple transposition du booléen true
#define ERROR_INPUT     false// Idem pour false
#define Delay_1ms 1000

int i, code_ADC, code_DAC ;
const int led = LED_BUILTIN;  // the pin with a LED
const int readPin = A0; // ADC0

String received ;
String received_input ;
String received_DAC_code ;

boolean status_input ; 
boolean status_input_ADC, status_input_DAC ;
boolean status_Go ;


byte  received_length ;     // Longeur de la chaîne de cracatètre reçue de l'interface série 
int   DAC_selected ;

/****************************************************************************/
/*              Setup pins                                                  */
/****************************************************************************/
void setup(void) {
  pinMode(led, OUTPUT);
  pinMode(readPin, INPUT) ;   // for ADC
  
  /****************************************************************************/
  /*              Setup ADC parameters                                        */
  /****************************************************************************/
  analogWriteResolution(12);
  analogReadResolution(12) ;
  adc->adc0->setReference(ADC_REFERENCE::REF_3V3);
  adc->adc0->setAveraging(8); // set number of averages ;
  adc->adc0->setConversionSpeed(ADC_CONVERSION_SPEED::HIGH_SPEED); // change the conversion speed
  adc->adc0->setSamplingSpeed(ADC_SAMPLING_SPEED::HIGH_SPEED); // change the sampling speed
  
  /****************************************************************************/
  /*              Print message and wait 1 s                                  */
  /****************************************************************************/
  Serial.begin(BAUD_RATE);
  delay(3*DELAY_1s);              // wait for 3 seconds
  Serial.println("\t*************************************************************");
  Serial.println("\t*        Enter DAC=code, from DAC=0 to DAC=4095             *");
  Serial.println("\t*                                                           *");
  Serial.println("\t*           Then enter ADC to read ADC code                 *");
  Serial.println("\t*************************************************************");
  status_input_DAC = ERROR_INPUT ;
  status_input_ADC = ERROR_INPUT ;
  delay(DELAY_1s);              // Wait for 1 second
}

/****************************************************************************/
/*    The main program will print the data to the Arduino Serial Monitor    */
/****************************************************************************/

void loop(void) {

  /****************************************************************************/
  /*              Test input character                                        */
  /****************************************************************************/
  //Serial.begin(BAUD_RATE);
  if (Serial.available() > 0) { // If serial data available
    received = Serial.readString() ;       // Get serial string
    received_input = received.substring(0, 3) ;
    if (received_input == INPUT_DAC) {
      status_input_DAC = get_DAC(received) ;
    }
    if (received_input == INPUT_ADC) status_input_ADC = OK ;
    
    if (status_input_DAC == OK && status_input_ADC == OK ) {
      Serial.println("\t") ;
      Serial.println("********************************************************") ;
      Serial.println("*  **************************************************  *") ;
      Serial.println("*  *     DAC voltage set and ADC voltage readed     *  *") ;
      Serial.println("*  **************************************************  *") ;
      Serial.println("********************************************************") ;
      status_input_DAC = ERROR_INPUT ;
      status_input_ADC = ERROR_INPUT ;
      
      /********************************************************************/
      /*            Setup Timer                                           */
      /********************************************************************/
      code_DAC = DAC_selected ;
      analogWrite(A22, code_DAC) ;
      delay(2*DELAY_1s) ;
      code_ADC = adc->adc0->analogRead(readPin);
      Serial.print("code_DAC = ") ;Serial.println(code_DAC) ;
      Serial.print("code_ADC = ") ;Serial.println(code_ADC) ;
    }
  }
}


/********************************************************************/
/*          Function for extracting DAC code                        */
/********************************************************************/
boolean get_DAC(String string_received) {
    String received_DAC  ; // 
    byte received_length ; // 
    byte received_pos_equal  ;
    status_input = OK ;
    received_length     = string_received.length() ;
    received_pos_equal  = string_received.indexOf('=') ;    
    //Serial.println(received_length) ;
    //Serial.println(received_pos_equal) ;
    if (received_length > INPUT_DAC_MAX_LENGHT || received_pos_equal == ERROR_INDEX || received_pos_equal != INPUT_DAC_LENGTH ) {
        status_input = ERROR_INPUT ; 
        output_wrong_DAC() ;
        return status_input ; // Return status of the input
    }
    if (status_input != ERROR_INPUT) { // 
        received_DAC = string_received.substring(0,received_pos_equal) ; // 
        //Serial.println(received_vstep) ;   
        if (received_DAC != INPUT_DAC) {
          status_input = ERROR_INPUT ;
          output_wrong_DAC() ;
          return status_input ; // Return status of the input
        }
        received_DAC_code = string_received.substring(received_pos_equal + 1 ,received_length) ;
        DAC_selected = received_DAC_code.toInt() ;
        //Serial.println(vstep_selected) ;   
        if (DAC_selected < MIN_ADC || DAC_selected > MAX_ADC) {
          status_input = ERROR_INPUT ;
          output_wrong_DAC();
          return status_input ; // Return status of the input
        }

      if (status_input == OK) {
         Serial.println("\n") ;
         Serial.println("    ************************************") ;
         Serial.print  ("    *      Selected DAC code = ");
         Serial.print(DAC_selected) ;
         Serial.println ("    *");
         Serial.println("    ************************************") ;
      }       
    }
    return status_input ; // Return status of the input
}

/********************************************************************/
/*          Function for DAC voltage error message                  */
/********************************************************************/
void output_wrong_DAC(void) {
  Serial.println("    ***********************************") ;
  Serial.println("    *     Wrong DAC code  detected    *") ;
  Serial.println("    ***********************************") ;
}
