#include <VL53L0X.h>
#include <Wire.h>

VL53L0X sensor;
uint8_t MCP4725_ADDRESS = 0x60;  // mcp4725 address

// get milli order dt data of Arduiono
int getMilliDt();
// get distance data from VL53L0X
int getDistance();
// set DAC-out voltage
void setDac(uint16_t target);
// for PAM input
void setVinTrapezium(int minimum, int maximum, float slope, int holdTime);
// serial communication, send to processing
void scA2P();

const int mass = 459;  // default mass is 99 [g]
const int eprSpeed = 500;  // default eprSpeed is 500 [mV/s]
int eprVin = 0;  // default eprVin is 0

bool isMeasuring = false; // measure and send: true, finish measuring: false

int wavePhase = 0;  // flag for PAM input
int waveHoldTimer = 0;  // timer for PAM input

void setup() {
  Serial.begin(115200);
  
  Wire.begin();
  sensor.setTimeout(500);
  if(!sensor.init()){
    Serial.println("Failed to detect and initialize VL53L0X");
    while(1){}
  }
  sensor.startContinuous();
  
  delay(1000);
  getMilliDt(); // initial dt is long, call in setup() to avoid bringing long initial dt to loop()
}

void loop() {
  setDac(eprVin);
  scA2P();
  
  int dV = eprSpeed * getMilliDt() * 0.0008192;
  setVinTrapezium(0, 4095, dV, 100);
}

// get milli order dt data of Arduino
int getMilliDt(){
  static int pre = 0;
  int dt = (float)(millis() - pre);
  pre = millis();
  return dt;
}

// get distance data from VL53L0X
int getDistance(){
  int dist = sensor.readRangeContinuousMillimeters();
  if (sensor.timeoutOccurred()) {
    Serial.print("VL53L0X is timeouted"); 
  }
  return dist;
}

// set DAC-out voltage
void setDac(uint16_t target){
  uint8_t low = target & 0xff;
  uint8_t high = (target >> 8) & 0x0f;
  
  Wire.beginTransmission(MCP4725_ADDRESS);
  Wire.write(high);
  Wire.write(low);
  Wire.endTransmission();
}

// for PAM input
void setVinTrapezium(int minimum, int maximum, float slope, int holdTime){
    switch(wavePhase){
    case 0: // lamp up
      if(eprVin < maximum){
        eprVin += slope;
        if(eprVin >= maximum){
          eprVin = maximum;
        }
      }else{
        wavePhase++;
      }
      break;
    case 1: // hold max
      if(waveHoldTimer < holdTime){
        eprVin = maximum;
        waveHoldTimer++;
      }else{
        waveHoldTimer = 0;
        wavePhase++;
      }
      break;
    case 2: // lamp down
      if(eprVin > minimum){
        eprVin -= slope;
        if(eprVin <= minimum){
          eprVin = minimum;
        }
      }else{
        wavePhase++;
      }
      break;
    case 3: // hold min
      if(waveHoldTimer < holdTime){
        eprVin = minimum;
        waveHoldTimer++;
      }else{
        waveHoldTimer = 0;
        wavePhase = 0;
      }
      break;
    default:
      Serial.print("error");
      break;
  }
}

// serial communication, send to processing
void scA2P(){
  Serial.print("measurements:");  // watchword for communication
  Serial.print(mass);
  Serial.print(',');
  Serial.print(eprSpeed);
  Serial.print(',');
  Serial.print(getMilliDt());
  Serial.print(',');
  Serial.print(eprVin);
  Serial.print(',');
  Serial.print(getDistance());
  Serial.print('\n');
}
