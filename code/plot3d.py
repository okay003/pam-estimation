import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# get all DataFramed .csv files in pwd
allFiles = os.listdir(os.getcwd())
enRawName = ""
enFitName = ""
unRawName = ""
unFitName = ""
for f in allFiles:
  if os.path.isfile(f) and f.startswith("_") and f.endswith(".csv"):
    if f.endswith("_en_raw.csv"):
      enRawName = f
    if f.endswith("_en_fit.csv"):
      enFitName = f
    if f.endswith("_un_raw.csv"):
      unRawName = f
    if f.endswith("_un_fit.csv"):
      unFitName = f
if enRawName == "" or enFitName == "" or unRawName == "" or unFitName == "":
  print("There is no DataFramed .csv files, Exit program")
  exit()
endfRaw = pd.read_csv(enRawName,index_col=0)
undfRaw = pd.read_csv(unRawName,index_col=0)
endfFit = pd.read_csv(enFitName,index_col=0)
undfFit = pd.read_csv(unFitName,index_col=0)
endfFitVal = endfFit.loc[:,"0.0":"0.7"] # https://www.self-study-blog.com/dokugaku/pandas-dataframe-loc-iloc-at-iat/
endfFitOSD = endfFit[["opt-a","opt-b","opt-c","sd-a","sd-b","sd-c"]]
undfFitVal = undfFit.loc[:,"0.0":"0.7"] # https://www.self-study-blog.com/dokugaku/pandas-dataframe-loc-iloc-at-iat/
undfFitOSD = undfFit[["opt-a","opt-b","opt-c","sd-a","sd-b","sd-c"]]

# preparation for plot
fig = plt.figure()
plt.rcParams["font.family"] = "Times New Roman"
euax = fig.add_subplot(1,3,1,projection="3d",proj_type="ortho") # https://stackoverflow.com/questions/23840756/
euax.set_xlabel("Pressure [MPa]")
euax.set_ylabel("Load [N]")
euax.set_zlabel("Contraction rate [%]")
enax = fig.add_subplot(1,3,2,projection="3d",proj_type="ortho") # https://stackoverflow.com/questions/23840756/
enax.set_xlabel("Pressure [MPa]")
enax.set_ylabel("Load [N]")
enax.set_zlabel("Contraction rate [%]")
unax = fig.add_subplot(1,3,3,projection="3d",proj_type="ortho") # https://stackoverflow.com/questions/23840756/
unax.set_xlabel("Pressure [MPa]")
unax.set_ylabel("Load [N]")
unax.set_zlabel("Contraction rate [%]")
euax.view_init(elev=30,azim=-135)
enax.view_init(elev=30,azim=-135)
unax.view_init(elev=30,azim=-135)

# enun in same plot
plotx,ploty = np.meshgrid(endfFitVal.columns.values.astype(float),endfFitVal.index.values.astype(float))
enz = endfFitVal.values.astype(float)
unz = undfFitVal.values.astype(float)
euax.plot_surface(plotx,ploty,enz,color=(1,0,0,0.16))
euax.plot_wireframe(plotx,ploty,enz,color=(1,0,0,0.36),label="apprx. to sigmoid (enpressurise)")
euax.plot_surface(plotx,ploty,unz,color=(0,0,1,0.16))
euax.plot_wireframe(plotx,ploty,unz,color=(0,0,1,0.36),label="apprx. to sigmoid (depressurise)")
plotx,ploty = plotx.flatten(),ploty.flatten()
enz = endfRaw.values.astype(float).flatten()
unz = undfRaw.values.astype(float).flatten()
euax.scatter(plotx,ploty,enz,color="indianred",label="raw data (enpressurise)")
euax.scatter(plotx,ploty,unz,color="steelblue",label="raw data (depressurise)")

# plot fit data, see : https://ja.stackoverflow.com/q/38367
plotx,ploty = np.meshgrid(endfFitVal.columns.values.astype(float),endfFitVal.index.values.astype(float))
enz = endfFitVal.values.astype(float)
unz = undfFitVal.values.astype(float)
enax.plot_surface(plotx,ploty,enz,color=(1,0,0,0.16))
enax.plot_wireframe(plotx,ploty,enz,color=(1,0,0,0.36))
unax.plot_surface(plotx,ploty,unz,color=(0,0,1,0.16))
unax.plot_wireframe(plotx,ploty,unz,color=(0,0,1,0.36))

# plot raw data as bar-scatter, see : https://ja.stackoverflow.com/q/38367
plotx,ploty = plotx.flatten(),ploty.flatten()
enz = endfRaw.values.astype(float).flatten()
unz = undfRaw.values.astype(float).flatten()
# bottom = np.zeros(len(plotx))
# width = depth = 0.001
# enax.bar3d(plotx,ploty,bottom,width,depth,enz,color="indianred")
enax.scatter(plotx,ploty,enz,color="indianred")
# unax.bar3d(plotx,ploty,bottom,width,depth,unz,color="steelblue")
unax.scatter(plotx,ploty,unz,color="steelblue")

euax.legend(ncol=2,loc=(0.5,1))
plt.show()
  