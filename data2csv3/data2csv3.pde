import processing.serial.*; // for serial communication

Serial serial;
PrintWriter fs;

boolean isFirst = true;  // to detect first serial communication, for making .csv

int timerHolder = 0;

// to store measurements data from arduino
class Measurements {
  int mass = 0;
  int eprSpeed = 0;
  int dt = 0;
  int eprVin = 0;
  int distance = 0;

  Measurements() {
    mass = eprSpeed = dt = eprVin = distance = 0;
  }

  void setter(int[] data) {
    if (data.length < 5) {
      return;
    }
    mass = data[0];
    eprSpeed = data[1];
    dt = data[2];
    eprVin = data[3];
    distance = data[4];
  }
};

Measurements measurements;

void setup() {
  serial = new Serial(this, "COM8", 115200);
  serial.bufferUntil(10);

  measurements = new Measurements();
  measurements = null;

  size(320, 180);
  background(0);

  delay(10);
}

void draw() {
  if ((measurements != null) && (!isFirst)) {
    timerHolder += measurements.dt;
    fs.println(timerHolder + "," + measurements.eprVin + "," + measurements.distance);
    fs.flush();
    measurements = null;  // reflesh measurements
  }
}

void serialEvent(Serial serial) {
  String receives = serial.readStringUntil('\n');
  receives = trim(receives);

  //println(receives);

  if ((receives != null) && (measurements == null)) {
    String[] data = split(receives, ":");
    if (data[0].equals("measurements")) {  // check the watchword
      Measurements temp = new Measurements();
      temp.setter(int(split(data[1], ",")));
      measurements = temp;

      if (isFirst) {  // make .csv
        fs = createWriter("([g], [mVps]) = (" + measurements.mass + ", " + measurements.eprSpeed + ").csv");
        fs.print("mass [g]," + measurements.mass + ",eprSpeed [mVps]," + measurements.eprSpeed + "\n");
        fs.print("time,eprVin,distance\n");
        fs.flush();
        isFirst = false;
      }
    }
  }
}
