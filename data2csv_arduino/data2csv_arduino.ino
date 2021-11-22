#include <VL53L0X.h>
#include <Wire.h>

VL53L0X sensor;
uint8_t MCP4725_ADDRESS = 0x60;  // mcp4725 address

// get distance data from VL53L0X
int getDistance();
// set DAC-out voltage
void setDac(uint16_t target);
// serial communication, send to processing
void scA2P(int index);
// wave initialize routine
void waveInitialize();
// wave finalize routine
void waveFinalize();

const String serialNumber = "MonoPlaE";  // default serialNumber is A
const int mass = 2500;  // default mass is 99 [g]
int eprVin = 0;  // default eprVin is 0
const int freeLength = 234;

float distanceAverage = 0;
int averageCounter = 0;

#define RISE_HOLD 0
#define RISE 1
#define FALL 2
#define FALL_HOLD 3
#define END 999
int waveState = RISE_HOLD;  // sequencer for PAM input
int waveCounter = 0;  // counter for PAM input

bool isFirst = true;

int stepNum = 1 << 5; // resolution of PAM input
int stepHeight = 4096 / stepNum; // PAM input value per step
unsigned long holdTimer = 0;  // timer of hold section
int holdTime = 8000; // length of hold section
int slope = 1; // speed of PAM input

void setup() {
  delay(4000);
  
  Serial.begin(9600);

  Wire.begin();
  sensor.setTimeout(500);
  if (!sensor.init()) {
    Serial.println("Failed to detect and initialize VL53L0X");
    while (1) {}
  }
  sensor.startContinuous();

  holdTimer = millis();
}

void loop() {
  setDac(eprVin);

  int cut = stepHeight * waveCounter - 1;
  if (waveCounter > stepNum) {
    cut = stepHeight * (2 * stepNum - waveCounter) - 1;
  }
  if (cut < 0) {
    cut = 0;
  }

  if (isFirst) {
    waveInitialize();
    isFirst = false;
  }

  switch (waveState) {
    case RISE_HOLD: // hold section (rise)
      if (millis() - holdTimer < holdTime) {
        if (waveCounter == 0) {
          eprVin = 0;
        } else {
          eprVin = cut;
        }
        distanceAverage += getDistance();
        averageCounter++;
      } else if (waveCounter == stepNum) {  // waveCounter gets turning point
        waveFinalize();
        waveState = FALL;
      } else {
        waveFinalize();
        waveState = RISE;
      }
      break;
    case RISE: // rise section
      if (eprVin < cut) {
        eprVin += slope;
        delay(10);
        if (eprVin > cut) {
          eprVin = cut;
        }
      } else {
        waveState = RISE_HOLD;
        holdTimer = millis();
      }
      break;
    case FALL_HOLD: // hold section (fall)
      if (millis() - holdTimer < holdTime) {
        eprVin = cut;
        distanceAverage += getDistance();
        averageCounter++;
      } else if (waveCounter == 2 * stepNum) {
        waveFinalize();
        waveState = END;
      } else {
        waveFinalize();
        waveState = FALL;
      }
      break;
    case FALL: // fall section
      if (eprVin > cut + 1) {
        eprVin -= slope;
        delay(10);
        if (eprVin < cut) {
          eprVin = cut;
        }
      } else {
        waveState = FALL_HOLD;
        holdTimer = millis();
      }
      break;
    case END: // end section
      scA2P();
      Serial.end();
      break;
    default:
      while (1) {
        Serial.println("error");
        delay(100);
      }
      break;
  }
  if (eprVin < 0) {
    eprVin = 0;
  }
}

// get distance data from VL53L0X
int getDistance() {
  int dist = sensor.readRangeContinuousMillimeters();
  if (sensor.timeoutOccurred()) {
    Serial.print("VL53L0X is timeouted");
  }
  return dist;
}

// set DAC-out voltage
void setDac(uint16_t target) {
  uint8_t low = target & 0xff;
  uint8_t high = (target >> 8) & 0x0f;

  Wire.beginTransmission(MCP4725_ADDRESS);
  Wire.write(high);
  Wire.write(low);
  Wire.endTransmission();
}

// serial communication, send to processing
void scA2P() {
  Serial.print("measurements:");  // watchword for communication
  Serial.print(serialNumber);
  Serial.print(',');
  Serial.print(freeLength);
  Serial.print(',');
  Serial.print(stepNum);
  Serial.print(',');
  Serial.print(mass);
  Serial.print(',');
  Serial.print(eprVin);
  Serial.print(',');
  Serial.print(distanceAverage);
  Serial.print('\n');
}

// wave initialize routine
void waveInitialize() {
  eprVin = 0;
  distanceAverage = 0;
  averageCounter = 0;
  scA2P();
  holdTimer = millis();
}

// wave finalize routine
void waveFinalize() {
  distanceAverage /= averageCounter;
  scA2P();
  distanceAverage = 0;
  averageCounter = 0;
  waveCounter++;
}
