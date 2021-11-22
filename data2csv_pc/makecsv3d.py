import os
import numpy as np
import pandas as pd
import scipy.optimize as sciopt
import matplotlib.pyplot as plt

# ---- ---- ---- ---- ---- ---- ---- ----

def moddedSigmoidSurface(xy,a,b,c,d,e):
  x,y = xy
  return a*(1+np.exp(-b*(y+c)))/(1+np.exp(-d*(x+e)))

def plot3dScatter(ax,elev,azim,df,ende,condis,color):
  if ende == "en":
    ax.set_title("Enpressure Data")
  if ende == "de":
    ax.set_title("Depressure Data")
  if condis == "con":
    ax.set_xlabel("Voltage [12bit]")
    ax.set_xticks([0,1023,2047,3071,4095])
    ax.set_ylabel("Load [N]")
    ax.set_zlabel("Displacement [mm]")
  if condis == "dis":
    ax.set_xlabel("Pressure [MPa]")
    ax.set_ylabel("Load [N]")
    ax.set_zlabel("Construction rate [%]")
  ax.view_init(elev=elev,azim=azim)
  ax.w_xaxis.set_pane_color((0,0,0))
  ax.w_yaxis.set_pane_color((0,0,0))
  ax.w_zaxis.set_pane_color((0,0,0))

  x,y = np.meshgrid(df.columns.values,df.index.values)
  x,y = x.flatten(),y.flatten()
  z = df.values.flatten()
  ax.scatter(x,y,z,color=color,label="Raw Data").set_rasterized(True)

def check3dScatter(sn,dfs):
  fig = plt.figure()
  fig.suptitle(sn)
  elev = 30
  azim = 150
  axConEn = fig.add_subplot(2,2,1,projection="3d",proj_type="ortho")
  axConDe = fig.add_subplot(2,2,2,projection="3d",proj_type="ortho")
  axDisEn = fig.add_subplot(2,2,3,projection="3d",proj_type="ortho")
  axDisDe = fig.add_subplot(2,2,4,projection="3d",proj_type="ortho")
  encon,decon,endis,dedis = dfs
  plot3dScatter(axConEn,elev,azim,encon,"en","con","indianred")
  plot3dScatter(axConDe,elev,azim,decon,"de","con","steelblue")
  plot3dScatter(axDisEn,elev,azim,endis,"en","dis","indianred")
  plot3dScatter(axDisDe,elev,azim,dedis,"de","dis","steelblue")
  axConEn.legend()
  axConDe.legend()
  axDisEn.legend()
  axDisDe.legend()
  mng = plt.get_current_fig_manager()
  mng.full_screen_toggle()
  plt.show()

# ---- ---- ---- ---- ---- ---- ---- ----
# main
# ---- ---- ---- ---- ---- ---- ---- ----

if __name__ == "__main__":
  # initialize message
  print("\033[36mStart \"" + os.path.basename(__file__) + "\"\033[0m")

  # get all serial numbers
  allFiles = os.listdir(os.getcwd())
  serialNumbers = []
  for f in allFiles:
    if os.path.isfile(f) and f.endswith(".csv"):
      serialNumbers.append(f.split(",")[0])
  serialNumbers = list(set(serialNumbers))

  # make file group each serial number
  fileGroup = []
  for sn in serialNumbers:
    element = []
    for f in allFiles:
      if os.path.isfile(f) and f.endswith(".csv") and f.startswith(sn):
        element.append(f)
    fileGroup.append(sorted(element))

  # make DataFrame each group
  for group in fileGroup:
    freeLength = int(pd.read_csv(group[0],header=None)[1][0])
    stepNum = int(pd.read_csv(group[0],header=None)[1][1])
    turningPoint = 0
    mass = []
    eprVin = []
    distance = []
    load = []
    pressure = []
    contraction = []
    for file in group:
      rawCsv = pd.read_csv(file,header=2)
      turningPoint = rawCsv[rawCsv["eprVin"]==4095].index.tolist()[0]

      mass.append(rawCsv["mass"][0])
      eprVin = rawCsv["eprVin"][:2*turningPoint+1].tolist()
      dist = rawCsv["distance"][:2*turningPoint+1].tolist()
      for i in range(len(dist)):
        dist[i] -= rawCsv["distance"][0]
      distance.append(dist)

      load = list(map(lambda x:x*0.001*9.798406,mass))
      pressure = list(map(lambda x:x*0.7/4095,eprVin))
      cont = rawCsv["distance"][:2*turningPoint+1].tolist()
      for i in range(len(cont)):
        cont[i] -= rawCsv["distance"][0]
        cont[i] /= freeLength
        cont[i] *= 100
      contraction.append(cont)
    eddf_control = pd.DataFrame(distance,columns=eprVin,index=load).sort_index().T
    endf_control = eddf_control.iloc[:turningPoint+1,:].T
    dedf_control = eddf_control.iloc[turningPoint:,:].sort_index().T
    eddf_display = pd.DataFrame(contraction,columns=pressure,index=load).sort_index().T
    endf_display = eddf_display.iloc[:turningPoint+1,:].T
    dedf_display = eddf_display.iloc[turningPoint:,:].sort_index().T

    # get approximation para
    enConInitPara = (26,0.15,15,20,-0.2)
    deConInitPara = (26,0.1,15,20,-0.2)

    enDisInitPara = (26,0.15,15,20,-0.2)
    deDisInitPara = (26,0.1,15,20,-0.2)

    # enConOpt,enConCov = sciopt.curve_fit(moddedSigmoidSurface,(enConX,enConY),enConZ,p0=enConInitPara)
    # deConOpt,deConCov = sciopt.curve_fit(moddedSigmoidSurface,(deConX,deConY),deConZ,p0=deConInitPara)
    # enConSd = np.sqrt(np.diag(enConCov))
    # deConSd = np.sqrt(np.diag(deConCov))
    # edConOptSd = [np.append(enConOpt,enConSd).tolist(),np.append(deConOpt,deConSd).tolist()]
    # eddfConOptSd = pd.DataFrame(edConOptSd,columns=["opt-a","opt-b","opt-c","opt-d","opt-e","sd-a","sd-b","sd-c","sd-d","sd-e"],index=["en","de"])

    # enDisOpt,enDisCov = sciopt.curve_fit(moddedSigmoidSurface,(enDisX,enDisY),enDisZ,p0=enDisInitPara)
    # deDisOpt,deDisCov = sciopt.curve_fit(moddedSigmoidSurface,(deDisX,deDisY),deDisZ,p0=deDisInitPara)
    # enDisSd = np.sqrt(np.diag(enDisCov))
    # deDisSd = np.sqrt(np.diag(deDisCov))
    # edDisOptSd = [np.append(enDisOpt,enDisSd).tolist(),np.append(deDisOpt,deDisSd).tolist()]
    # eddfDisOptSd = pd.DataFrame(edDisOptSd,columns=["opt-a","opt-b","opt-c","opt-d","opt-e","sd-a","sd-b","sd-c","sd-d","sd-e"],index=["en","de"])

    # print(eddfDisOptSd)

    # save as .csv
    sn = group[0].split(",")[0]
    # endf_control.to_csv(sn+",control,en.csv")
    # dedf_control.to_csv(sn+",control,de.csv")
    # endf_display.to_csv(sn+",display,en.csv")
    # dedf_display.to_csv(sn+",display,de.csv")

    # check 3d scatter
    dfs = (endf_control,dedf_control,endf_display,dedf_display)
    # print(dfs)
    check3dScatter(sn,dfs)
    
  # finalize message
  print("\033[36mCompleted successfully, Exit \"" + os.path.basename(__file__) + "\"\033[0m")