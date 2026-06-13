import numpy as np
from astropy.io import fits
from astropy.time import Time
from os import listdir, getcwd, mkdir, chdir, rmdir, system, path, symlink
from os.path import isfile, join, isdir, dirname, basename
import matplotlib.pyplot as plt
from datetime import datetime
import copy
import shutil
import pandas as pd

dirPath = getcwd()

def GetFiles(dire):
    return [
        f for f in listdir(dire) if isfile(join(dire, f))
    ] 


nameBBDD = "results.csv"


fn = "/selec_data"

fL = GetFiles(dirPath + fn)
fL = [s for s in fL if s.endswith(".fitresults")]
IDs = [f.replace("_src.fitresults", "") for f in fL]
IDs = list(set(IDs)) #removes duplicates

cols = ["ID", "MJD", "rate", "hr", "exposure", "BGrate", "N_H", "Gamma", "Frac_SC", "T_disk", "Norm" ]


df = pd.DataFrame(columns=cols)

for ID in IDs:
    
    rate = errRate = HR = errHR = exposure = date = lsrc = lbkg = 0
    a1 = a2 = a3 = a4 = a5 = a6 = 0
    fitResults =  [None] * 5
    folderName = "P" + ID[0:5]
    
    try:
        with open(dirPath + "/" + folderName + "/" + ID + ".txt") as f:
            numbers = [(line.strip()) for line in f]
            rate, errRate, HR, errHR, exposure, date, rateSrc, errRateSrc, rateBkg, errRateBkg = numbers
        rate = str(rate) + "^{+" + str(errRate) + "}_{-" + str(errRate) + "}"
        HR = str(HR) + "^{+" + str(errHR) + "}_{-" + str(errHR) + "}"
        rateBkg = str(rateBkg) + "^{+" + str(errRateBkg) + "}_{-" + str(errRateBkg) + "}"
        with open(dirPath + fn + "/" + ID + "_src.fitresults") as f:
            numbers = [(line.strip()) for line in f]
            fitResults[0], fitResults[1], fitResults[2], _, fitResults[3], fitResults[4] = numbers
        fitResults = [fr.replace("$", "") for fr in fitResults ]
        df.loc[len(df)] = [ID.replace("-all", ""), Time(date).mjd, rate, HR, exposure, rateBkg, fitResults[0], fitResults[1], fitResults[2], fitResults[3], fitResults[4]]
    except Exception as e:
        print(e)
   
df = df.sort_values(by="MJD", ascending=True)
df.to_csv(dirPath + "/" + nameBBDD, index=False)