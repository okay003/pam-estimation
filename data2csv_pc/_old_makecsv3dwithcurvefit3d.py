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

  # extruct load, pressure, en/depress, cast str to float
  load = []
  pressure = []
  enpress = []
  depress = []
  for i in range(initPoint,halfPoint+1):
    load.append(int(raw[i][0]))
    pressure.append(int(raw[i][1]))
    enpress.append(float(raw[i][2]))
    depress.append(float(raw[len(raw)-i+3][2]))

  # calc contraction ratio
  relativeZero = enpress[0]
  for i in range(len(enpress)):
    enpress[i] = (enpress[i]-relativeZero)/freeLength*100
    depress[i] = (depress[i]-relativeZero)/freeLength*100

  # return floated list
  enpressList = [list(map(float,load)),list(map(float,pressure)),list(map(float,enpress))]
  depressList = [list(map(float,load)),list(map(float,pressure)),list(map(float,depress))]
  return enpressList,depressList

# ---- ---- ---- ---- ---- ---- ---- ----

def moddedSigmoidSurface(xy,a,b,c,d,e):
  x,y = xy
  return a*(1+np.exp(-b*(y+c)))/(1+np.exp(-d*(x+e)))

# ---- ---- ---- ---- ---- ---- ---- ----
# main
# ---- ---- ---- ---- ---- ---- ---- ----

# initialize message
print("\033[36mStart \"" + os.path.basename(__file__) + "\"\033[0m")

# get all DataFramed .csv files in pwd
allFiles = os.listdir(os.getcwd())
enRawName = ""
en2dFitName = ""
deRawName = ""
de2dFitName = ""
for f in allFiles:
  if os.path.isfile(f) and f.startswith("_") and f.endswith(".csv"):
    if f.endswith("_en_raw.csv"):
      enRawName = f
    if f.endswith("_en_2dfit.csv"):
      en2dFitName = f
    if f.endswith("_de_raw.csv"):
      deRawName = f
    if f.endswith("_de_2dfit.csv"):
      de2dFitName = f
if enRawName == "" or en2dFitName == "" or deRawName == "" or de2dFitName == "":
  print("There is no DataFramed .csv files, Exit program")
  exit()
endfRaw = pd.read_csv(enRawName,index_col=0)
dedfRaw = pd.read_csv(deRawName,index_col=0)
endf2dFit = pd.read_csv(en2dFitName,index_col=0)
dedf2dFit = pd.read_csv(de2dFitName,index_col=0)
endf2dFitVal = endf2dFit.loc[:,"0.0":"0.7"] # https://www.self-study-blog.com/dokugaku/pandas-dataframe-loc-iloc-at-iat/
endf2dFitOSD = endf2dFit[["opt-a","opt-b","opt-c","sd-a","sd-b","sd-c"]]
dedf2dFitVal = dedf2dFit.loc[:,"0.0":"0.7"] # https://www.self-study-blog.com/dokugaku/pandas-dataframe-loc-iloc-at-iat/
dedf2dFitOSD = dedf2dFit[["opt-a","opt-b","opt-c","sd-a","sd-b","sd-c"]]

# preparation for approximate
enx = endfRaw.columns.values
eny = endfRaw.index.values
enx,eny = np.meshgrid(enx,eny)
enx = enx.flatten()
eny = eny.flatten()
enz = endfRaw.values.flatten()
dex = dedfRaw.columns.values
dey = dedfRaw.index.values
dex,dey = np.meshgrid(dex,dey)
dex = dex.flatten()
dey = dey.flatten()
dez = dedfRaw.values.flatten()

# get approximation para
enInitPara = (26,0.15,15,20,-0.2)
deInitPara = (26,0.1,15,20,-0.2)
enopt,encov = sciopt.curve_fit(moddedSigmoidSurface,(enx,eny),enz,p0=enInitPara)
deopt,decov = sciopt.curve_fit(moddedSigmoidSurface,(dex,dey),dez,p0=deInitPara)
ensd = np.sqrt(np.diag(encov))
desd = np.sqrt(np.diag(decov))
optsd = [np.append(enopt,ensd).tolist(),np.append(deopt,desd).tolist()]
dfoptsd = pd.DataFrame(optsd,columns=["opt-a","opt-b","opt-c","opt-d","opt-e","sd-a","sd-b","sd-c","sd-d","sd-e"],index=["en","de"])
print(dfoptsd)

# save data as pandas.DataFrame
serialNumber = enRawName.split("_")[1]
dfoptsd.to_csv("_" + serialNumber + "_ende_surfacefit.csv")

# finalize message
print("\033[36mCompleted successfully, Exit \"" + os.path.basename(__file__) + "\"\033[0m")