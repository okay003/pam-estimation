import os
import numpy as np
from numpy.lib.shape_base import column_stack
import pandas as pd
import scipy.optimize as sciopt
import matplotlib.pyplot as plt

def getCsvAsList(rawFileName):
  # get raw csv as 2d array
  raw=[]
  for row in open(rawFileName):
    raw.append(row.split(","))
  for i in range(len(raw)):
    for j in range(len(raw[i])):
      raw[i][j] = raw[i][j].replace("\n","")

  # get para
  freeLength = int(raw[0][1])
  stepNum = int(raw[1][1])
  halfPoint = 0
  initPoint = 0
  for i in range(len(raw)):
    for j in range(len(raw[i])):
      if raw[i][1] == "4095":
        halfPoint = i
        initPoint = halfPoint-stepNum

  # extruct load, pressure, en/unpress, cast str to float
  load = []
  pressure = []
  enpress = []
  unpress = []
  for i in range(initPoint,halfPoint+1):
    load.append(int(raw[i][0]))
    pressure.append(int(raw[i][1]))
    enpress.append(float(raw[i][2]))
    unpress.append(float(raw[len(raw)-i+3][2]))

  # calc contraction ratio
  relativeZero = enpress[0]
  for i in range(len(enpress)):
    enpress[i] = (enpress[i]-relativeZero)/freeLength*100
    unpress[i] = (unpress[i]-relativeZero)/freeLength*100

  # return floated list
  enpressList = [list(map(float,load)),list(map(float,pressure)),list(map(float,enpress))]
  unpressList = [list(map(float,load)),list(map(float,pressure)),list(map(float,unpress))]
  return enpressList,unpressList

# ---- ---- ---- ---- ---- ---- ---- ----

def moddedSigmoid(x,a,b,c):
    return a/(1+np.exp(-b*(x+c)))

# ---- ---- ---- ---- ---- ---- ---- ----
# main
# ---- ---- ---- ---- ---- ---- ---- ----

# initialize message
print("\033[36mStart \"" + os.path.basename(__file__) + "\"\033[0m")

# get all raw .csv files in pwd
allFiles = os.listdir(os.getcwd())
rawFiles = []
for i in allFiles:
  if os.path.isfile(i) and not i.startswith("_") and i.endswith(".csv"):
    rawFiles.append(i)

if rawFiles == []:
  print("There is no .csv files, Exit program")
  exit()

# get 3-nested list, 1st: each file, 2nd: load-pressure-contraction, 3rd: each float value
enpresss = []
unpresss = []
for fileName in rawFiles:
  en,un = getCsvAsList(fileName)
  enpresss.append(en)
  unpresss.append(un)

# make pandas.DataFrame, see : https://note.nkmk.me/python-pandas-dataframe-values-columns-index/
load = []
pressure = list(map(lambda x: x*0.7/4095, enpresss[0][1])) # old was : pressure = enpress[0][1]
encon = []
uncon = []
for i in range(len(enpresss)):
  load.append((lambda x: x*0.001*9.798406)(enpresss[i][0][0]))
  encon.append(enpresss[i][2])
  uncon.append(unpresss[i][2])

endf = pd.DataFrame(encon,columns=pressure,index=load)
undf = pd.DataFrame(uncon,columns=pressure,index=load)
endf = endf.sort_index()
undf = undf.sort_index()

# approximate raw data to sigmoid
# see : https://qiita.com/Hiko630/items/7d9f683276f63270a052
# see : https://qiita.com/kon2/items/6498e66af55949b41a99
# see : https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html
enx = endf.columns.values # input x : pressure
enys =endf.values # input y : raw contraction
enconsFitted = [] # output y : Fitted contraction
enopts = [] # opt : paras of moddedSigmoid-fitting
ensds = [] # sd : standard deviation from covariance of input-output (maybe)
unx = undf.columns.values
unys =undf.values
unconsFitted = []
unopts = [] # opt : paras of moddedSigmoid-fitting
unsds = [] # sd : standard deviation from covariance of input-output (maybe)
for i in range(len(enys)):
    enopt,encov = sciopt.curve_fit(moddedSigmoid,enx,enys[i],p0=(30,20,-0.2))
    enopts.append(enopt.tolist())
    ensds.append(np.sqrt(np.diag(encov)).tolist())
    unopt,uncov = sciopt.curve_fit(moddedSigmoid,unx,unys[i],p0=(30,20,-0.2))
    unopts.append(unopt.tolist())
    unsds.append(np.sqrt(np.diag(uncov)).tolist())
    encon,uncon = [],[]
    for x in enx:
        encon.append(moddedSigmoid(x,enopt[0],enopt[1],enopt[2]))
        uncon.append(moddedSigmoid(x,unopt[0],unopt[1],unopt[2]))
    enconsFitted.append(encon)
    unconsFitted.append(uncon)

# save data as pandas.DataFrame
endfFitted = pd.DataFrame(enconsFitted,columns=enx,index=endf.index.values)
undfFitted = pd.DataFrame(unconsFitted,columns=unx,index=undf.index.values)
endfopt = pd.DataFrame(enopts,columns=["opt-a","opt-b","opt-c"],index=endf.index.values)
endfsd = pd.DataFrame(ensds,columns=["sd-a","sd-b","sd-c"],index=endf.index.values)
undfopt = pd.DataFrame(unopts,columns=endfopt.columns.values,index=endf.index.values)
undfsd = pd.DataFrame(unsds,columns=endfsd.columns.values,index=endf.index.values)
endfopt = endfopt.join(endfsd)
undfopt = undfopt.join(undfsd)
endfFitted = endfFitted.join(endfopt)
undfFitted = undfFitted.join(undfopt)

serialNumber = rawFiles[0].split("= (")[1].split(",")[0]
endf.to_csv("_" + serialNumber + "_en_raw.csv")
undf.to_csv("_" + serialNumber + "_un_raw.csv")
endfFitted.to_csv("_" + serialNumber + "_en_fit.csv")
undfFitted.to_csv("_" + serialNumber + "_un_fit.csv")

# finalize message
print("\033[36mCompleted successfully, Exit \"" + os.path.basename(__file__) + "\"\033[0m")