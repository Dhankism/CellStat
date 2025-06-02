#include <TimerOne.h>
#include <ADC.h>
#include <ADC_util.h>
#include <SPI.h>

ADC *adc = new ADC(); // ADC object

#define TEENSY_BOARD "Teensy"
#define BAUD_RATE  9600
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

unsigned short *adcread = nullptr; // Pointer for dynamic ADC storage
unsigned short *dacValues = nullptr; // Pointer for dynamic DAC storage
int datacount;

// Function Prototypes
void parseSerialToIntArray(int *array, int &size, int maxSize);
void runCV(int V1, int V2, int V3, int period, int cycles );
void cap(int index);
void rita(int index);
void setup();
void loop();

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
    if (!Serial.available()) return;

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
// MAIN LOOP - Handles CV Scanning
// =====================================
void loop() {
    int parameters[8];  
    int parameterSize = 0;
    parseSerialToIntArray(parameters, parameterSize, 8);

    if (parameterSize == 0) return;  // No valid data received

    if (parameters[0] == 0) {  
        // Case 0: Ping and set DAC value
        Serial.println("Pinged");
        analogWrite(DAC_OUT, parameters[1]);
        return;
    } 
    else if (parameters[0] == 1 && parameterSize == 8) {  
        // Extract parameters
        int V1 = parameters[1], V2 = parameters[2], V3 = parameters[3];
        int period = parameters[4], cycles = parameters[5];
        int rita_val = parameters[6];  // Resistor value (0-7)
        int cap_val = parameters[7];   // Capacitor value (0-7)

        // Set resistor and capacitor values
        rita(rita_val);
        cap(cap_val);

        // Optimized Serial Output (Now includes resistor and capacitor values)
        Serial.printf("Running CV with V1=%d, V2=%d, V3=%d, period=%d, cycles=%d, rita=%d, cap=%d\n",
                      V1, V2, V3, period, cycles, rita_val, cap_val);

        runCV(V1, V2, V3, period, cycles);
    }
}

// =====================================
//  CV FUNCTION - Handles CV Scanning
// =====================================
void runCV(int V1, int V2, int V3, int period, int cycles) {
    digitalWrite(LED_BUILTIN, HIGH);
    delay(DELAY_1ms);

    int values[] = {V1, V2, V3};  
    int numValues = sizeof(values) / sizeof(values[0]);

    // Estimate total samples for memory allocation
    int total_samples = cycles * (abs(V2 - V1) + abs(V3 - V2) + abs(V1 - V3));

    // Allocate memory dynamically for DAC and ADC storage
    if (adcread) delete[] adcread;
    if (dacValues) delete[] dacValues;
    adcread = new unsigned short[total_samples];
    dacValues = new unsigned short[total_samples];
    datacount = 0;

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
                    delayMicroseconds(period);
                    adcread[datacount] = adc->adc0->analogRead(ADC_IN);
                    dacValues[datacount] = output;
                    datacount++;
                }
            }
            // Gradually decrease DAC output if current_value > next_value
            else {
                for (int output = current_value; output >= next_value; output--) {
                    analogWrite(DAC_OUT, output);
                    delayMicroseconds(period);
                    adcread[datacount] = adc->adc0->analogRead(ADC_IN);
                    dacValues[datacount] = output;
                    datacount++;
                }
            }
        }
    }

    // Print all stored values at once after acquisition
    for (int i = 0; i < datacount; i++) {
        Serial.print(dacValues[i]);
        Serial.print(",");
        Serial.println(adcread[i]);
    }

    // Free memory after use
    delete[] adcread;
    delete[] dacValues;
    adcread = nullptr;
    dacValues = nullptr;
    digitalWrite(LED_BUILTIN, LOW);
}

void cap(int index){

  switch (index) {

    // input array of what the user 0:2p  1:20p   2:50p   3:100p  4:200p  5:1n  6:50n  7:100n 
    // output array  2p:x3  20p:x0  50p:x1  100p:x2 200p:x5 1n:x7 50n:x6 100n:x4
    case 1: //x0
      digitalWrite(cap_port1, LOW);
      digitalWrite(cap_port2, LOW);
      digitalWrite(cap_port3, LOW);
    
    case 2://x1
      digitalWrite(cap_port1, HIGH);
      digitalWrite(cap_port2, LOW);
      digitalWrite(cap_port3, LOW);
     
    case 3://x2
      digitalWrite(cap_port1, LOW);
      digitalWrite(cap_port2, HIGH);
      digitalWrite(cap_port3, LOW);
      
    case 0://x3
      digitalWrite(cap_port1, HIGH);
      digitalWrite(cap_port2, HIGH);
      digitalWrite(cap_port3, LOW);
      
    case 7://x4
      digitalWrite(cap_port1, LOW);
      digitalWrite(cap_port2, LOW);
      digitalWrite(cap_port3, HIGH);
   
    case 4://x5
      digitalWrite(cap_port1, HIGH);
      digitalWrite(cap_port2, LOW);
      digitalWrite(cap_port3, HIGH);

    case 6://x6
      digitalWrite(cap_port1, LOW);
      digitalWrite(cap_port2, HIGH);
      digitalWrite(cap_port3, HIGH);
    
    case 5://x7
      digitalWrite(cap_port1, HIGH);
      digitalWrite(cap_port2, HIGH);
      digitalWrite(cap_port3, HIGH);
   
    default:
      // Handle cases beyond 7 (e.g., x0)
      digitalWrite(cap_port1, LOW);
      digitalWrite(cap_port2, LOW);
      digitalWrite(cap_port3, LOW);
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
     
    case 5: //x1
      digitalWrite(resistor_portA, HIGH);
      digitalWrite(resistor_portB, LOW);
      digitalWrite(resistor_portC, LOW);
      
    case 4: //x2
      digitalWrite(resistor_portA, LOW);
      digitalWrite(resistor_portB, HIGH);
      digitalWrite(resistor_portC, LOW);
      
    case 7: //x3
      digitalWrite(resistor_portA, HIGH);
      digitalWrite(resistor_portB, HIGH);
      digitalWrite(resistor_portC, LOW);
     
    case 0: //x4
      digitalWrite(resistor_portA, LOW);
      digitalWrite(resistor_portB, LOW);
      digitalWrite(resistor_portC, HIGH);
      
    case 3: //x5
      digitalWrite(resistor_portA, HIGH);
      digitalWrite(resistor_portB, LOW);
      digitalWrite(resistor_portC, HIGH);
      
    case 1: //x6
      digitalWrite(resistor_portA, LOW);
      digitalWrite(resistor_portB, HIGH);
      digitalWrite(resistor_portC, HIGH);
     
    case 2: //x7
      digitalWrite(resistor_portA, HIGH);
      digitalWrite(resistor_portB, HIGH);
      digitalWrite(resistor_portC, HIGH);
      
    default:
      // Handle cases beyond 7 (e.g., x0)
      digitalWrite(resistor_portA, LOW);
      digitalWrite(resistor_portB, LOW);
      digitalWrite(resistor_portC, LOW);

  }

}



