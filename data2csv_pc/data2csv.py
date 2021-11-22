import serial
import pandas as pd

ser = serial.Serial("/dev/ttyACM0",9600,timeout=1)
isFirst = True
zeroCounter = 0
file = []
progress = 0

if __name__ == "__main__":
  while True:
    if ser.inWaiting() > 0:
      data = str(ser.readline().strip())[2:-2].split(":")[1].split(",")
      if isFirst == True:
        print("start measurements ...")
        isFirst = False
        file = [["freeLength",data[1]],["stepNum",data[2]],["mass","eprVin","distance"]]
      elif isFirst != True:
        file.append([data[3],data[4],data[5]])
        print(data)
        print("progress[%]","{:.1f}".format(progress/(2*int(data[2]))*100))
        progress += 1
        if data[4] == "0" and data[5] != "0.0":
          zeroCounter += 1
    elif zeroCounter == 2:
      df = pd.DataFrame(file)
      df.to_csv(data[0]+","+data[3]+".csv",index=False,header=False)
      ser.close()
      print("finish measurements ...")
    else:
      _=0