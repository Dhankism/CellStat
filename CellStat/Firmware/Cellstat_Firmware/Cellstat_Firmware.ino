#include <TimerOne.h>
#include <ADC.h>
#include <ADC_util.h>
#include <SPI.h>

ADC *adc = new ADC(); // ADC object

#define TEENSY_BOARD "Teensy"
#define BAUD_RATE  115200
#define COMMA ','
#define DELAY_1ms    1000

#define DAC_12BITS    12
#define ADC_12BITS    12
#define ADC_AVG        8
#define ADC_IN        A0
#define DAC_OUT      A21

#define PIN_MARK       6  
#define PIN_CTRL       5  

#define resistor_portA  27
#define resistor_portB  28
#define resistor_portC  29
#define cap_port1       24
#define cap_port2       25
#define cap_port3       26

volatile boolean State = false;
volatile byte counter = 0;

int adcread[50000];
int datacount;
int DACidle=2045;

// Function Prototypes
void parseSerialToIntArray(int *array, int &size, int maxSize);
void runCV(int V1, int V2, int V3, int period, int cycles, int rita_val, int cap_val);
void setCapacitor(int index);
void setResistor(int index);
void setup();
void loop();
bool smartDelayMicro(unsigned long period);

// =====================================
// SETUP FUNCTION
// =====================================
void setup() {
    pinMode(DAC_OUT, OUTPUT);
    pinMode(ADC_IN, INPUT);
    pinMode(PIN_MARK, OUTPUT);
    pinMode(PIN_CTRL, OUTPUT);
    pinMode(LED_BUILTIN, OUTPUT);

    pinMode(resistor_portA, OUTPUT); // for resistor mux
    pinMode(resistor_portB, OUTPUT); // for resistor mux
    pinMode(resistor_portC, OUTPUT); // for resistor mux
    pinMode(cap_port1, OUTPUT); // for capacitor mux
    pinMode(cap_port2, OUTPUT); // for capacitor mux
    pinMode(cap_port3, OUTPUT); // for capacitor mux

    analogWriteResolution(DAC_12BITS);
    analogReadResolution(ADC_12BITS);
    adc->adc0->setReference(ADC_REFERENCE::REF_3V3);
    adc->adc0->setAveraging(ADC_AVG);
    adc->adc0->setConversionSpeed(ADC_CONVERSION_SPEED::HIGH_SPEED);
    adc->adc0->setSamplingSpeed(ADC_SAMPLING_SPEED::HIGH_SPEED);

    Serial.begin(BAUD_RATE);
    delay(DELAY_1ms);
}

// =====================================
// SERIAL INPUT PARSING FUNCTION
// =====================================
void parseSerialToIntArray(int *array, int &size, int maxSize) {
    if (!Serial.available()) 
      return;
    String receivedData = Serial.readString();
    receivedData.trim();
    size = 0;

    while (receivedData.length() > 0 && size < maxSize) {
        int commaIndex = receivedData.indexOf(COMMA);
        if (commaIndex == -1) {
            array[size++] = receivedData.toInt();
            break;
        }
        array[size++] = receivedData.substring(0, commaIndex).toInt();
        receivedData = receivedData.substring(commaIndex + 1);
    }
}

// =====================================
// MAIN LOOP - H
// =====================================
void loop() {
    int parameters[9];
    int parameterSize = 0;

    parseSerialToIntArray(parameters, parameterSize, 9);

  if (parameterSize == 0) return;// No valid data received
  else{ 

    int commandID = parameters[0];

   // Serial.println(parameterSize);

    if (commandID == 0) {  
        // Case 0: Ping and set DAC ideal value value
        Serial.println("PONG");
        DACidle = parameters[1];
        
    } 
    else if (commandID == 1 && parameterSize == 8) {  
        // Extract parameters
        int V1 = parameters[1], V2 = parameters[2], V3 = parameters[3], period = parameters[4], cycles = parameters[5];
        int rita_val = parameters[6] ,cap_val = parameters[7];   // Capacitor value (0-7)

        // Set resistor and capacitor values
        setResistor(rita_val);
        setCapacitor(cap_val);

        // Serial Output 
       // Serial.printf("Running CV with V1=%d, V2=%d, V3=%d, period=%d, cycles=%d, setResistor=%d, setCapacitor=%d\n",
          //            V1, V2, V3, period, cycles, rita_val, cap_val);

        runCV(V1, V2, V3, period, cycles);

    }
    else if (commandID == 2 && parameterSize == 9) {  
        int V1 = parameters[1], V2 = parameters[2], T1 = parameters[3], T2 = parameters[4], scanRate = parameters[5], cycles = parameters[6];
        int rita_val = parameters[7], cap_val = parameters[8];
        // Set resistor and capacitor values
        setResistor(rita_val);
        setCapacitor(cap_val);


       // Serial.printf("Running Pulse with V1=%d, V2=%d, T1=%d, T2=%d, scanRate=%d, cycles=%d, rita=%d, cap=%d\n",
                    //  V1, V2, T1, T2, scanRate, cycles, rita_val, cap_val);

        runPulse(V1, V2, T1, T2, scanRate, cycles);

    }
    analogWrite(DAC_OUT,DACidle);
    digitalWrite(LED_BUILTIN, LOW);
  }  
}

// =====================================
// CV FUNCTION - Handles CV Scanning
// =====================================
void runCV(int V1, int V2, int V3, int period, int cycles) {
    digitalWrite(LED_BUILTIN, HIGH);
    delay(DELAY_1ms);

    int values[] = {V1, V2, V3};  
    int numValues = sizeof(values) / sizeof(values[0]);
    datacount=0;
    // Loop through the given number of cycles
    for (int i_cycle = 0; i_cycle < cycles; i_cycle++) {
        for (int i = 0; i < numValues; i++) {
            int current_value = values[i];
            int next_index = (i + 1) % numValues;  // Wrap to first value after last
            int next_value = values[next_index];

            // Gradually increase DAC output from current_value to next_value
            if (current_value < next_value) {
                for (int output = current_value; output <= next_value; output++) {
                    analogWrite(DAC_OUT, output);
                    if(smartDelayMicro(period) == false) return;
                    adcread[datacount++] = adc->adc0->analogRead(ADC_IN); 
                }
            }
            // Gradually decrease DAC output if current_value > next_value
            else {
                for (int output = current_value; output >= next_value; output--) {
                    analogWrite(DAC_OUT, output);
                    if(smartDelayMicro(period) == false) return; 
                    adcread[datacount++] = adc->adc0->analogRead(ADC_IN);
                }
            }
        }
    }
    // again loop for serial output this is done not int the first loop to ensure less time lose in the first loop
    datacount=0;
    for (int i_cycle = 0; i_cycle < cycles; i_cycle++) {

      Serial.println("CYCLE_" + String(i_cycle));
      
      for (int i = 0; i < numValues; i++) {
          int current_value = values[i];
          int next_index = (i + 1) % numValues;  // Wrap to first value after last
          int next_value = values[next_index];

          // Gradually increase DAC output from current_value to next_value
          if (current_value < next_value) {
              for (int output = current_value; output <= next_value; output++) {
                   
                   Serial.print(output);
                   Serial.print(",");
                   Serial.println(adcread[datacount++]);
                   Serial.flush();
                    
              }
          }
          // Gradually decrease DAC output if current_value > next_value
          else {
              for (int output = current_value; output >= next_value; output--) {
                   Serial.print(output);
                   Serial.print(",");
                   Serial.println(adcread[datacount++]);
                   Serial.flush();
                    
              }
          }
      }
       
    }
    Serial.println("END");
    digitalWrite(LED_BUILTIN, LOW);
    
}
void runPulse(int V1, int V2, int T1, int T2, int scanRate, int cycles) {
    digitalWrite(LED_BUILTIN, HIGH);
    delay(DELAY_1ms);
    
    datacount = 0;

    for (int i_cycle = 0; i_cycle < cycles; i_cycle++) {
        analogWrite(DAC_OUT, V1);
        for (int step = 0; step < T1; step += scanRate) {
            if(smartDelayMicro(scanRate) == false) return;
            adcread[datacount++] = adc->adc0->analogRead(ADC_IN);
            //Serial.println(adcread[datacount]);
        }
        analogWrite(DAC_OUT, V2);
        for (int step = 0; step < T2; step += scanRate) { 
            if(smartDelayMicro(scanRate) == false) return ;
            adcread[datacount++] = adc->adc0->analogRead(ADC_IN);
            //Serial.println(adcread[datacount]);
        }
    }
    // end the wiht he starting voltage 
    for (int step = 0; step < T1; step += scanRate) {
        analogWrite(DAC_OUT, V1);
        if(smartDelayMicro(scanRate) == false) return;
        adcread[datacount++] = adc->adc0->analogRead(ADC_IN);
    }

    Serial.println("Time(ms), ADC Output");
    for (int i = 0; i < datacount; i++) {
        Serial.print(i * scanRate);
        Serial.print(",");
        Serial.println(adcread[i]);
        Serial.flush();
    }

    Serial.println("END");
    
}

bool smartDelayMicro(unsigned long period) {
    unsigned long startMicro = micros();  // Record current time
    while (micros() - startMicro < period) {  // Loop until time has passed
        if (Serial.available()) {  // Check for Serial input
            String command = Serial.readStringUntil('\n');
            command.trim();
            if (command == "RESET") {
             //   Serial.println("Restarting Teensy...");
                Serial.flush();  // Ensure Serial output is complete
                return false;
            }
        }
    }
   return true;
}



void setCapacitor(int index){

  switch (index) {

    // input array of what the user 0:2p  1:20p   2:50p   3:100p  4:200p  5:1n  6:50n  7:100n 
    // output array                2p:x3  20p:x0  50p:x1  100p:x2 200p:x5 1n:x7 50n:x6 100n:x4
     case 0://2p is x3
      digitalWrite(cap_port1, HIGH);
      digitalWrite(cap_port2, HIGH);
      digitalWrite(cap_port3, LOW);
      break;
    case 1: //20p is x0
      digitalWrite(cap_port1, LOW);
      digitalWrite(cap_port2, LOW);
      digitalWrite(cap_port3, LOW);
      break;
    case 2://50p is x1
      digitalWrite(cap_port1, HIGH);
      digitalWrite(cap_port2, LOW);
      digitalWrite(cap_port3, LOW);
      break;
    case 3://100p is x2
      digitalWrite(cap_port1, LOW);
      digitalWrite(cap_port2, HIGH);
      digitalWrite(cap_port3, LOW);
      break;
    case 4://200p is x5 
      digitalWrite(cap_port1, HIGH);
      digitalWrite(cap_port2, LOW);
      digitalWrite(cap_port3, HIGH);
      break;
    case 5://x7
      digitalWrite(cap_port1, HIGH);
      digitalWrite(cap_port2, HIGH);
      digitalWrite(cap_port3, HIGH);
      break;
     case 6://x6
      digitalWrite(cap_port1, LOW);
      digitalWrite(cap_port2, HIGH);
      digitalWrite(cap_port3, HIGH); 
      break;
    case 7://x4
      digitalWrite(cap_port1, LOW);
      digitalWrite(cap_port2, LOW);
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
void setResistor(int index){

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



