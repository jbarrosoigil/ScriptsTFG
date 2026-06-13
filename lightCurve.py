import numpy as np
from astropy.io import fits
from astropy.time import Time
from os import listdir, getcwd, mkdir, chdir, rmdir, system, path, symlink
from os.path import isfile, join, isdir, dirname, basename
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from datetime import datetime
import copy
import shutil

dirPath = getcwd()
counter = 1
maxDepth = 3

class lcPoint:
    def __init__(self, light, errLight, HR, errHR, exposureSrc, date, lsrc, errLsrc, lbkg, errLbkg):
        self.light = light
        self.errLight = errLight
        self.HR = HR
        self.errHR = errHR
        self.exposureSrc = exposureSrc
        self.date = date
        self.lsrc = lsrc
        self.errLsrc = errLsrc
        self.lbkg = lbkg
        self.errLbkg = errLbkg
    
    def addFile(self, fileName):
        self.file = fileName
dots = []
        

def GetFolders(dire):
    return [
        f for f in listdir(dire) if isdir(join(dire, f))
    ]   

def GetFiles(dire):
    return [
        f for f in listdir(dire) if isfile(join(dire, f))
    ]  

      
def RecursionFolder(direction, depth=1):
    global counter
    folders = GetFolders(direction)

    if len(folders) > 0 and depth < maxDepth:
        for folder in folders:
            if folder == "abstracts" or folder == "test": 
                continue

            path = direction + "/" + folder
            RecursionFolder(path, depth=depth+1)

    if True:
        dir_name = dirname(direction)
        base_name = basename(direction)

        res_name = base_name+"-result"
        basic_name = base_name + "-all-basic"

        filtfile_path = f"{res_name}/FP_xtefilt.lis"

        chdir(dir_name)

        print(dir_name, " cwd: ", getcwd(),"  ",res_name)

        log_file = base_name + "_maketime.log"
        
        #Gets all the filenames and lists them without the extension.
        fileList = GetFiles(direction)
        fileList = [s for s in fileList if s.endswith(".txt")]


        #dated_files = sorted(dated_files, key=lambda x: x[1])
        
        for file in fileList:
            try:
                with open(direction + "/" + file) as f:
                    numbers = [(line.strip()) for line in f]
                    light, errLight, HR, errHR, exposureSrc, date, lsrc, errLsrc, lbkg, errLbkg = numbers
                    if not light == "nan":
                        dot = lcPoint(float(light), float(errLight), float(HR), float(errHR), float(exposureSrc), date, float(lsrc), float(errLsrc), float(lbkg), float(errLbkg))
                        dot.addFile(file)
                        dots.append(copy.copy(dot))
                    else:
                        a = 0
            except Exception as e:
                print(f"Skipping {file} (missing or invalid): {e}")
                continue
        
RecursionFolder(dirPath)

figures_dir = path.join(dirPath, "figures")
if not path.exists(figures_dir):
    mkdir(figures_dir)

dots.sort(key=lambda obj: obj.date)

############# Remove invalid points ####################


errs = np.array([obj.errLight for obj in dots])
mean_err = np.mean(errs)
std_err = np.std(errs)
threshold = mean_err + 3 * std_err
dots = [
    obj for obj in dots
    if obj.errLight <= threshold
]
errHRs = np.array([obj.errHR for obj in dots])
median = np.median(errHRs)
mad = np.median(np.abs(errHRs - median))
robust_sigma = 1.4826 * mad
dots = [
    obj for obj in dots
    if obj.errHR <= median + 3 * robust_sigma
]


#########################################################

dotsOutburst = []
dotsOutburst.append([obj for obj in dots if Time(obj.date).mjd < 53000 ])
dotsOutburst.append([obj for obj in dots if 53100 <= Time(obj.date).mjd < 53500 ])
dotsOutburst.append([obj for obj in dots if 53500 <= Time(obj.date).mjd < 54000 ])
dotsOutburst.append([obj for obj in dots if 54300 <= Time(obj.date).mjd < 54600 ])
dotsOutburst.append([obj for obj in dots if 54600 <= Time(obj.date).mjd < 54900 ])
dotsOutburst.append([obj for obj in dots if 54900 <= Time(obj.date).mjd < 55100 ])
dotsOutburst.append([obj for obj in dots if 55100 <= Time(obj.date).mjd < 55300 ])
dotsOutburst.append([obj for obj in dots if 55300 <= Time(obj.date).mjd < 55500 ])

maxExposure = 900

for i in range(len(dotsOutburst)):
    dotsOutburst[i] = [obj for obj in dotsOutburst[i] if obj.exposureSrc > maxExposure ]

#for dotsOut in dotsOutburst:

# d = ([obj.file for obj in dotsOutburst[0] if  ( 
#     (obj.exposureSrc > maxExposure) and 
#     (Time(obj.date).mjd < 52963) and 
#     (obj.HR <= 0.75) and 
#     (obj.light > 80) 
#     )]) 
# for s in d:
#     path = "P" + s[0:5] 
#     s = path + "/" + s
#     print(s)
#     symlink(s, "selec_data/")

# print(d)
# print(len(d))
    
colours = ["red", "gold", "darkorange", "green", "cyan", "blue", "blueviolet", "violet"]


########### light curve

from matplotlib.lines import Line2D

plt.figure(figsize=(8,6))

for i in range(len(dotsOutburst)):

    # Filter once
    filtered = [
        obj for obj in dotsOutburst[i]
        if obj.exposureSrc > maxExposure
    ]

    x = [Time(obj.date).mjd for obj in filtered]
    y = [obj.light for obj in filtered]
    errY = [obj.errLight for obj in filtered]
    errX = [obj.errHR for obj in filtered]

    label = f"outburst no. {i + 1}"

    # -------------------------
    # Global plot (unchanged)
    # -------------------------
    plt.errorbar(
        x,
        y,
        yerr=errY,
        fmt='.',
        color=colours[i],
        label=label
    )

    # -------------------------
    # Individual plot
    # -------------------------
    fig, ax = plt.subplots(figsize=(8,6))

    n = len(x)
    n_colours = len(colours)

    if n > 0:

        point_colours = [
            colours[min(j * n_colours // n, n_colours - 1)]
            for j in range(n)
        ]

        # Plot points
        for xx, yy, ex, ey, c in zip(x, y, errX, errY, point_colours):
            ax.errorbar(
                xx,
                yy,
                xerr=ex,
                yerr=ey,
                fmt='.',
                color=c
            )

        # Legend
        legend_handles = []

        for k, colour in enumerate(colours):

            start = k * n // n_colours
            end = (k + 1) * n // n_colours

            if start >= end:
                continue

            min_date = x[start]
            max_date = x[end - 1]

            legend_handles.append(
                Line2D(
                    [0], [0],
                    marker='.',
                    linestyle='',
                    color=colour,
                    label=f"{min_date:.0f} MJD - {max_date:.0f} MJD"
                )
            )

        ax.legend(
            handles=legend_handles,
            fontsize="small",
            loc="upper right"
        )

    ax.set_xlabel("Date (MJD)")
    ax.set_ylabel("Rate (c/s)")
    ax.grid(True)

    ax.set_title(label)

    fig.savefig(
        figures_dir + f"/lc_outburst_{i}.png",
        bbox_inches="tight"
    )

    plt.close(fig)

plt.xlabel("Date (MJD)")
plt.ylabel("Rate (c/s)")

plt.grid(True)
plt.legend()

plt.savefig(
    figures_dir + "/lc.png",
    bbox_inches="tight"
)

plt.clf()














##################################### individual HR 
d = []

for i in range(len(dotsOutburst)):

    x = [obj.HR for obj in dotsOutburst[i]]
    y = [obj.light for obj in dotsOutburst[i]]
    errY = [obj.errLight for obj in dotsOutburst[i]]
    errX = [obj.errHR for obj in dotsOutburst[i]]

    label = (
        f"{min(Time(obj.date) for obj in dotsOutburst[i]).mjd:.0f}"
        f" MJD - "
        f"{max(Time(obj.date) for obj in dotsOutburst[i]).mjd:.0f}"
        f" MJD"
    )

    plt.errorbar(
        x,
        y,
        xerr=errX,
        yerr=errY,
        fmt='.',
        color=colours[i],
        label=label
    )

    fig, ax = plt.subplots(figsize=(8, 6))

    n = len(x)
    n_colours = len(colours)

    point_colours = [
        colours[min(j * n_colours // n, n_colours - 1)]
        for j in range(n)
    ]

    for xx, yy, ex, ey, c in zip(x, y, errX, errY, point_colours):
        ax.errorbar(
            xx,
            yy,
            xerr=ex,
            yerr=ey,
            fmt='.',
            color=c
        )

    legend_handles = []

    for k, colour in enumerate(colours):

        start = k * n // n_colours
        end = (k + 1) * n // n_colours

        if start >= end:
            continue

        min_date = Time(dotsOutburst[i][start].date).mjd
        max_date = Time(dotsOutburst[i][end - 1].date).mjd

        legend_handles.append(
            Line2D(
                [0], [0],
                marker='.',
                linestyle='',
                color=colour,
                label=f"{min_date:.0f} MJD - {max_date:.0f} MJD"
            )
        )

    ax.set_xlabel("HR")
    ax.set_ylabel("Log Rate (c/s)")
    ax.set_yscale("log")
    ax.grid(True)

    ax.set_title(label)

    ax.legend(
        handles=legend_handles,
        fontsize="small",
        loc="upper right"
    )

    fig.savefig(
        figures_dir + f"/Rate_VS_HR_outburst_{i}.png",
        bbox_inches="tight"
    )

    plt.close(fig)

plt.xlabel("HR")
plt.ylabel("Log Rate (c/s)")
plt.yscale("log")

plt.legend(
    fontsize="small",
    loc="upper right"
)

plt.grid(True)

plt.savefig(
    figures_dir + "/Rate_VS_HR.png",
    bbox_inches="tight"
)

plt.clf()













#Red
odds = [obj for obj in dots if obj.HR < 1 and (obj.light) < 40]
normals = [obj for obj in dots if not (obj.HR < 1 and (obj.light) < 40)]
oddsExp = ([obj.exposureSrc for obj in odds])
oddsBkg = ([obj.lbkg for obj in odds])
normalsExp = ([obj.exposureSrc for obj in normals])
normalsBkg = ([obj.lbkg for obj in normals])


x = normalsExp
y = normalsBkg
plt.plot(
    x,
    y,
    marker='.', 
    linestyle='None',
    color="blue",
    label="normal",
    #capsize=5 
)
x = oddsExp
y = oddsBkg
plt.plot(
    x,
    y,
    marker='.',
    linestyle='None',
    color="orange",
    label="odd"
    #capsize=5 
)
plt.xlabel("exposure (s)")
plt.ylabel("bkg (keV)")
#plt.title("Values over time")
plt.grid(True)
plt.legend(loc="lower right")
plt.savefig(figures_dir + "/exposure.png")
plt.clf()

###################################

x = [obj.HR for obj in odds]
y = [obj.light for obj in odds]
errY = [obj.errLight for obj in odds]
errX = [obj.errHR for obj in odds]
plt.errorbar(
    x,
    y,
    xerr=errX,
    yerr=errY,
    fmt='.',
    color="orange",
    label = "odd"
    #capsize=5 
)
x = [obj.HR for obj in normals]
y = [obj.light for obj in normals]
errY = [obj.errLight for obj in normals]
errX = [obj.errHR for obj in normals]
plt.errorbar(
    x,
    y,
    xerr=errX,
    yerr=errY,
    fmt='.',
    color="blue",
    label = "normals"
    #capsize=5 
)
plt.xlabel("HR")
plt.ylabel("Rate (c/s, log scale)")
plt.yscale("log")
#plt.axhline(y=50, color='r', linestyle='-')
# plt.axhline(y=50, color='r', linestyle='-')
plt.legend(
    fontsize="small",
    bbox_to_anchor=(1.05, 1),
    loc="upper left")
plt.grid(True)
plt.savefig(figures_dir + "/fa_odds.png", bbox_inches="tight")
plt.clf()


#output_dir = dirPath + "/Scripts TFG/collected_files"
#output_dir.mkdir(exist_ok=True)
# def RecursionFolder2(direction, depth=1):
#     global counter
#     folders = GetFolders(direction)
#     if len(folders) > 0 and depth < maxDepth:
#         for folder in folders:
#             if folder == "abstracts" or folder == "test" or folder == "collected_files": 
#                 continue
#             path = direction + "/" + folder
#             RecursionFolder2(path, depth=depth+1)
#     if True:
#         dir_name = dirname(direction)
#         base_name = basename(direction)
#         res_name = base_name+"-result"
#         basic_name = base_name + "-all-basic"
#         filtfile_path = f"{res_name}/FP_xtefilt.lis"
#         chdir(dir_name)
#         print (dir_name, " cwd: ", getcwd(),"  ",res_name)
#         #rmdir(res_name+'-result')
#         #if not isdir(res_name):
#         #    mkdir(res_name)
#         log_file = base_name + "_maketime.log"
        
#         #Gets all the filenames and lists them without the extension.
#         fL = GetFiles(direction)
#         fL = [s for s in fL if s.endswith(".txt")]
#         fileList = fL
#         #fileList = [f.replace("_bck.pha", "") for f in fL]
#         fileList = list(set(fileList)) #removes duplicates
        
#         for file in fileList:
#             if file in d:
#                 f = direction + "/" + file
#                 shutil.copy2(f, output_dir)
        
# RecursionFolder2(dirPath)
