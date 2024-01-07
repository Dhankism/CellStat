

#include <ADC.h>
#include <ADC_util.h>

void rita(int index);
void cap(int index);

ADC *adc = new ADC(); // adc object;

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

#define resistor_portA  27
#define resistor_portB  28
#define resistor_portC  29
#define cap_port1       24
#define cap_port2       25
#define cap_port3       26
String received ;
int RITA_value;
int DAC_value=0;
int DAC_step=100;
bool flag= FALSE;
int DAC_values[3][4100]

void setup() {
  // put your setup code here, to run once:
  pinMode(resistor_portA, OUTPUT); // for resistor mux
  pinMode(resistor_portB, OUTPUT); // for resistor mux
  pinMode(resistor_portC, OUTPUT); // for resistor mux
  pinMode(cap_port1, OUTPUT); // for capcitor mux
  pinMode(cap_port2, OUTPUT); // for  capcitor mux
  pinMode(cap_port3, OUTPUT); // for  capcitor mux


  /****************************************************************************/
  /*              Setup ADC parameters                                        */
  /****************************************************************************/
  analogWriteResolution(12);
  analogReadResolution(12) ;
  adc->adc0->setReference(ADC_REFERENCE::REF_3V3);
  adc->adc0->setAveraging(8); // set number of averages ;
  adc->adc0->setConversionSpeed(ADC_CONVERSION_SPEED::HIGH_SPEED); // change the conversion speed
  adc->adc0->setSamplingSpeed(ADC_SAMPLING_SPEED::HIGH_SPEED); // change the sampling speed
  
  Serial.begin(BAUD_RATE);
  delay(3*DELAY_1s);    
  Serial.println("*  *  set resistor . input a value of 0 to 7  *  *") ;
  Serial.println("*  *  0:1k  1:10k   2:100k   3:1M  4:10M  5:30M  6:100M  7:1G*  *") ;

}

void loop() {

  if (Serial.available() > 0) {
  
  received = Serial.readString() ;
  if(received=)
  
  
  
  }    
  // put your main code here, to run repeatedly:

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




