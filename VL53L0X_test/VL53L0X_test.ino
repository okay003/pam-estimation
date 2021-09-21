#include <VL53L0X.h>

VL53L0X sensor;

void setup() {
  Serial.begin(9600);
  Wire.begin();
  sensor.setTimeout(500);
  if (!sensor.init()){
    Serial.println("Failed to detect and initialize VL53L0X");
    while(1){}
  }

  // Start continuous back-to-back mode (take readings as
  // fast as possible).  To use continuous timed mode
  // instead, provide a desired inter-measurement period in
  // ms (e.g. sensor.startContinuous(100)).
  sensor.startContinuous();
}

void loop() {
  Serial.print(sensor.readRangeContinuousMillimeters());
  if (sensor.timeoutOccurred()) {
    Serial.print("TIMEOUT"); 
  }
  Serial.println();

  delay(500);
}
