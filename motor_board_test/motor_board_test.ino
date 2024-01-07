const int pwmPins[] = {2,  3,  4,  5,  6,  7,  8,  9,  10, 11, 12, 13, 44, 45, 46}; // PWM pin numbers
const int LEDPins[] = {22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36};
const int numPins = sizeof(pwmPins) / sizeof(pwmPins[0]); // Number of PWM pins

bool pwmEnabled = true; // Flag to indicate whether PWM is enabled or not

void setup() {
  Serial.begin(9600); // Initialize serial communication

  // Set the prescaler for Timer0, Timer2, and Timer3 to achieve a PWM frequency of 980 Hz
  TCCR0B = (TCCR0B & 0xF8) | 0x02;
  TCCR2B = (TCCR2B & 0xF8) | 0x02;
  TCCR3B = (TCCR3B & 0xF8) | 0x02;
 
  for (int i = 0; i < numPins; i++) {
    pinMode(pwmPins[i], OUTPUT); // Set PWM pins as outputs
    pinMode(LEDPins[i], OUTPUT);
  }
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n'); // Read the serial command
   
        // Parse the command for pin index and PWM value
        int pinIndex = command.substring(0, command.indexOf(',')).toInt();
        int pwmValue = command.substring(command.indexOf(',') + 1).toInt();
       
        // Check if valid pin index and PWM value are received
        if (pinIndex >= 0 && pinIndex < numPins && pwmValue >= 0 && pwmValue <= 255) {
          analogWrite(pwmPins[pinIndex], pwmValue); // Set the PWM output
          Serial.print("PWM value set for pin ");
          Serial.print(pwmPins[pinIndex]);
          Serial.print(": ");
          Serial.println(pwmValue);
          if(pinIndex == 0) {
            digitalWrite(LEDPins[pinIndex],LOW ); // Set the LED output
          }
           else{
            digitalWrite(LEDPins[pinIndex],HIGH );            
            }
        } else {
          Serial.println("Invalid pin index or PWM value. Please enter valid values.");
        }
      }
}
  
