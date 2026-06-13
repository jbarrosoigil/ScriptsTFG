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
import re
from itertools import combinations

class AsymmetricValue:
    def __init__(self, value, errMax, errMin):
        self.value = value
        self.errMax = errMax
        self.errMin = errMin
        self.sigma = (errMax + errMin) * 0.5
        
        self._weight = None
        
        
    @property
    def weight(self):
        if self._weight is None:
            # sigma = (errMax + errMin)/2
            # weight = 1/sigma**2
            self._weight = 4 / (self.errMax + self.errMin)**2
        return self._weight

def WeightedMean(values):
    weighted_sum = 0
    weight_total = 0

    for v in values:
        w = v.weight

        weighted_sum += v.value * w
        weight_total += w

    mean = weighted_sum / weight_total
    uncertainty = np.sqrt(1 / weight_total)

    return mean, uncertainty

def GetValues(columnName):
    pattern = r'([-+]?\d*\.?\d+)\^\{\+([-+]?\d*\.?\d+)\}_\{[-+]*(\d*\.?\d+)\}'
    d = []
    for s in df[columnName]:

        match = re.match(pattern, s)
        if match:
            value  = float(match.group(1))
            errMax = float(match.group(2))
            errMin = float(match.group(3))

            d.append(
                AsymmetricValue(value, errMax, errMin)
            )
    return np.array(d, dtype=object)

import numpy as np


def filterByUncertainty(
    values,
    mask,
    sigmaLevel=3,
    robust=False
):
    mask = np.array(mask, dtype=bool)
    
    errs = [[obj.errMin for obj in values], [obj.errMax for obj in values]]
    
    for err in errs:
        mean_err = np.mean(err)
        std_err = np.std(err)
        threshold = mean_err + sigmaLevel * std_err
        for i, obj in enumerate(values):
            if mask[i]:
                if obj.errMin > threshold or obj.value < err[i]:
                    mask[i] = False
    
    return mask
    

def FilterByUncertainty_(
    primary_list,
    secondary_list,
    sigma_level=3,
    robust=False
):
    """
    Filter two aligned lists using the uncertainty
    distribution of the first list only.

    Parameters
    ----------
    primary_list : list[AsymmetricValue]
        List used to compute the filtering criterion.

    secondary_list : list[AsymmetricValue]
        List filtered using the same mask.

    sigma_level : float
        Sigma clipping threshold.

    robust : bool
        If True, use MAD-based robust sigma.
        If False, use mean/std.

    Returns
    -------
    filtered_primary, filtered_secondary
    """


    uncertainties = np.array([
        obj.sigma for obj in primary_list
    ])

    # Classical sigma clipping
    if not robust:

        mean_unc = np.mean(uncertainties)
        std_unc = np.std(uncertainties)

        threshold = (
            mean_unc
            + sigma_level * std_unc
        )

    # Robust sigma clipping
    else:

        median_unc = np.median(uncertainties)

        mad = np.median(
            np.abs(uncertainties - median_unc)
        )

        robust_sigma = 1.4826 * mad

        threshold = (
            median_unc
            + sigma_level * robust_sigma
        )

    filtered_primary = []
    filtered_secondary = []

    for obj1, obj2 in zip(
        primary_list,
        secondary_list
    ):
        if obj1.value > 50000:
            aaa=0
        
        if obj1.sigma <= threshold:

            filtered_primary.append(obj1)
            filtered_secondary.append(obj2)

    return (
        filtered_primary,
        filtered_secondary
    )
        
dirPath = getcwd()
figures_dir = path.join(dirPath, "figures")
if not path.exists(figures_dir):
    mkdir(figures_dir)

ddbbName = "results.csv"

#["ID", "MJD", "rate", "hr", "exposure", "BGrate", "N_H", "Gamma", "Frac_SC", "T_disk", "Norm" ]
df = pd.read_csv(dirPath + "/" + ddbbName)
df = df.sort_values(by="MJD", ascending=True)
dates = df["MJD"]
rate = GetValues("rate")
N_H = GetValues("N_H")
T_disk = GetValues("T_disk")
gamma = GetValues("Gamma")
hr = GetValues("hr")
normDisk = GetValues("Norm")

maxDate = 52925
mask = [d < maxDate for d in dates]

dates = dates[mask]
rate = rate[mask]
N_H = N_H[mask]
T_disk = T_disk[mask]
gamma = gamma[mask]
hr = hr[mask]
normDisk = normDisk[mask]

mask = [True] * len(dates)
# mask = filterByUncertainty(rate, mask)
# mask = filterByUncertainty(N_H, mask)
# mask = filterByUncertainty(T_disk, mask,)
mask = filterByUncertainty(gamma, mask)
# mask = filterByUncertainty(hr, mask)
mask = filterByUncertainty(normDisk, mask, sigmaLevel = 20)

values = [v.value for v in N_H]
errMax = [v.errMax for v in N_H]
errMin = [v.errMin for v in N_H]
wMean, errWMean = WeightedMean(N_H)
print(wMean, errWMean)
plt.errorbar(
    x = dates,
    y = values,
    yerr=[errMin, errMax],
    fmt='.',
    color = "orange",
    label="mesurement"
)
plt.xlabel("Date (MJD)")
plt.ylabel("H column")
plt.grid(True)
plt.axhline(y=wMean, color='blue', linestyle='-', label="weighted mean value")
plt.axhline(y=wMean+errWMean, color='blue', linestyle='--', label="uncertanty of the weighted mean value")
plt.axhline(y=wMean-errWMean, color='blue', linestyle='--')
plt.legend(loc='upper left')
plt.savefig(figures_dir + "/H_Column.png")
plt.clf()

dates = dates[mask]
rate = rate[mask]
N_H = N_H[mask]
T_disk = T_disk[mask]
gamma = gamma[mask]
hr = hr[mask]
normDisk = normDisk[mask]
# if False:
#     plt.errorbar(
#         x = dates,
#         y = values,
#         yerr=[errMin, errMax],
#         fmt='.',
#         color = "orange",
#         label="mesurement"
#     )
#     plt.xlabel("Date (MJD)")
#     plt.ylabel("H column")
#     plt.grid(True)
#     plt.axhline(y=wMean, color='blue', linestyle='-', label="weighted mean value")
#     plt.axhline(y=wMean+errWMean, color='blue', linestyle='--', label="uncertanty of the weighted mean value")
#     plt.axhline(y=wMean-errWMean, color='blue', linestyle='--')
#     plt.legend(loc='upper left')
#     plt.show()
# else:   

#     N_H_2 = [v for v, m in zip(N_H, dates) if m < 52925]

#     values = [v.value for v in N_H_2]
#     sigmas = [v.sigma for v in N_H_2]
#     errMax = [v.errMax for v in N_H_2]
#     errMin = [v.errMin for v in N_H_2]
#     wMean, errWMean = weightedMean(N_H_2)

#     print(len(values), len(dates))
            
#     plt.errorbar(
#         x = sigmas,
#         y = values,
#         yerr=[errMin, errMax],
#         fmt='.',
#         color = "orange",
#         label="mesurement"
#     )
#     plt.xlabel("Delta")
#     plt.ylabel("H column")
#     plt.grid(True)
#     plt.axhline(y=wMean, color='blue', linestyle='-', label="weighted mean value (wmv)")
#     plt.axhline(y=wMean+errWMean, color='blue', linestyle='--', label="uncertanty of wmv")
#     plt.axhline(y=wMean-errWMean, color='blue', linestyle='--')
#     plt.legend(loc='lower left')
#     plt.show()
    
#Norm = (R_in/D_10)^(1/2) cos theta
    
fig, axs = plt.subplots(nrows=6, ncols=1, sharex=False, figsize=(10, 12))
plt.subplots_adjust(hspace=0)
labelsize = 12
# Plot on each subplot
axs[0].errorbar(dates, [v.value for v in rate], yerr=[v.errMax for v in rate], fmt='.b', label='Light Curve')
axs[0].plot(dates, [v.value for v in rate], linestyle=':', color='gray')
axs[0].set_ylabel('Rate (c/s)')
#axs[0].set_yscale('log')
axs[0].set_xlabel('Time (MJD)')
axs[0].legend(loc='upper right', fontsize=labelsize)

axs[1].errorbar(dates, [v.value for v in hr], yerr=[v.errMax for v in hr], fmt='.r', label='Hardness Ratio')
axs[1].plot(dates, [v.value for v in hr], linestyle=':', color='gray')
axs[1].set_ylabel('HR (5-11/2-5) keV')
axs[1].set_xlabel('Time (MJD)')
axs[1].legend(loc='upper right', fontsize=labelsize)

axs[2].errorbar(dates, [v.value for v in T_disk], yerr=([v.errMin for v in T_disk], [v.errMax for v in T_disk]), fmt='.g', label='Disk Temperature')
axs[2].plot(dates, [v.value for v in T_disk], linestyle=':', color='gray')
axs[2].set_ylabel('Temperature (keV)')
axs[2].set_xlabel('Time (MJD)')
axs[2].legend(loc='best', fontsize=labelsize)

axs[3].errorbar(dates, [v.value for v in normDisk], yerr=([v.errMin for v in normDisk], [v.errMax for v in normDisk]), fmt='.', color='black', label='Disk Normalization')
axs[3].plot(dates, [v.value for v in normDisk], linestyle=':', color='gray')
#axs[3].axhline(y=0., color='gray', linestyle='--')
axs[3].set_ylabel('Norm')
axs[3].set_yscale("log")
axs[3].set_xlabel('Time (MJD)')
axs[3].legend(loc='lower right', fontsize=labelsize)

axs[4].errorbar(dates, [v.value for v in gamma], yerr=([v.errMin for v in gamma], [v.errMax for v in gamma]), fmt='.', color='purple', label='Compton Spectral Index')
axs[4].plot(dates, [v.value for v in gamma], linestyle=':', color='gray')
#axs[4].axhline(y=0., color='gray', linestyle='--')
axs[4].set_ylabel(r'$\Gamma$')
axs[4].set_xlabel('Time (MJD)')
axs[4].legend(loc='upper right', fontsize=labelsize)

degreesToRad = np.pi / 180
RadToDegrees = 180 / np.pi

distance = 8.5 #kpc
errDistance = 0.8 #kpc
inclination = 75 * degreesToRad
errInclination = 3 * degreesToRad
D_10 = distance * 0.1
errD_10 = errDistance * 0.1

r = []

cosi = np.cos(inclination)
sqrtcos = np.sqrt(cosi)
for n in normDisk:
    sqrtn = np.sqrt(n.value)
    R = (sqrtn / sqrtcos )*D_10
    dR_dn2 =  (D_10/  (2 * sqrtcos * sqrtn))**2
    dR_di2 = (D_10 * sqrtn * sqrtcos * np.sin(n.value)) / (2 * cosi * cosi)**2
    dR_dD2 = (sqrtn / sqrtcos)**2
    
    inclinationVarianceTerm =dR_di2*errInclination**2
    distanceVarianceTerm =dR_dD2*errD_10**2
    
    errRMax = np.sqrt(dR_dn2*n.errMax+inclinationVarianceTerm+distanceVarianceTerm)
    errRMin = np.sqrt(dR_dn2*n.errMin+inclinationVarianceTerm+distanceVarianceTerm)
    r.append(AsymmetricValue(R, errRMax, errRMin))

axs[5].errorbar(dates, [v.value for v in r], yerr=([v.errMin for v in r], [v.errMax for v in r]), fmt='.', color='darkorange', label='Inner Disk Radius')
axs[5].plot(dates, [v.value for v in r], linestyle=':', color='gray')
#axs[4].axhline(y=0., color='gray', linestyle='--')
axs[5].set_ylabel('R (km)')
axs[5].set_xlabel('Time (MJD)')
axs[5].legend(loc='upper right', fontsize=labelsize)

#Add vertical shaded regions
for ax in axs:
    ax.axvspan(52730, 52790, alpha=0.05, color='blue', label='SIMS')
    ax.axvspan(52764, 52783, alpha=0.05, color='blue', label='SIMS')
    ax.axvspan(52790, 52925, alpha=0.05, color='green', label='SS')
    ax.axvspan(52775, 52776.5, alpha=0.20, color='orange', label='Weird dot')
    
    # ax.axvspan(52750, 52790, alpha=0.05, color='blue', label='SIMS')


# Set common x-axis label and display the plot
plt.xlabel('Time (MJD)')
#plt.tight_layout()
plt.savefig(figures_dir + "/multiplot.png")
plt.clf()

degreesToRad = np.pi / 180
RadToDegrees = 180 / np.pi

distance = 8.5 #kpc
errDistance = 0.8 #kpc
inclination = 75 * degreesToRad
errInclination = 3 * degreesToRad
D_10 = distance * 0.1
errD_10 = errDistance * 0.1

r = []

cosi = np.cos(inclination)
sqrtcos = np.sqrt(cosi)

for n in normDisk:
    sqrtn = np.sqrt(n.value)
    R = (sqrtn / sqrtcos )*D_10
    dR_dn2 =  (D_10/  (2 * sqrtcos * sqrtn))**2
    dR_di2 = (D_10 * sqrtn * sqrtcos * np.sin(n.value)) / (2 * cosi * cosi)**2
    dR_dD2 = (sqrtn / sqrtcos)**2
    
    inclinationVarianceTerm =dR_di2*errInclination**2
    distanceVarianceTerm =dR_dD2*errD_10**2
    
    errRMax = np.sqrt(dR_dn2*n.errMax+inclinationVarianceTerm+distanceVarianceTerm)
    errRMin = np.sqrt(dR_dn2*n.errMin+inclinationVarianceTerm+distanceVarianceTerm)
    r.append(AsymmetricValue(R, errRMax, errRMin))
    
filtered_dates = []
filtered_r = []

for date, radius in zip(dates, r):

    if radius.value < 200:
        filtered_dates.append(date)
        filtered_r.append(radius)  


plt.errorbar(
        x = filtered_dates,
        y = [v.value for v in filtered_r], 
        yerr=([v.errMin for v in filtered_r], [v.errMax for v in filtered_r]),
        fmt='.',
        color = "blue"
    )
#plt.rcParams.update({'font.size': 40})
plt.xlabel("Date (MJD)")
plt.ylabel("Radius (km)")
#plt.xticks(fontsize=20)
plt.yticks(fontsize=20)
plt.xticks(
    np.linspace(min(filtered_dates), max(filtered_dates), 6),
    fontsize=20
)
plt.grid(True)
# plt.axhline(y=wMean, color='blue', linestyle='-', label="weighted mean value")
# plt.axhline(y=wMean+errWMean, color='blue', linestyle='--', label="uncertanty of the weighted mean value")
# plt.axhline(y=wMean-errWMean, color='blue', linestyle='--')
# plt.legend(loc='upper right')
plt.savefig(figures_dir + "/R_vs_date.png")
plt.clf()

normDisk_f, T_disk_f = normDisk, T_disk#FilterByUncertainty_(normDisk, T_disk, 3, False)

# plt.errorbar(
#         x = [v.value for v in T_disk_f],
#         y = [v.value for v in normDisk_f], 
#         xerr=([v.errMin for v in T_disk_f], [v.errMax for v in T_disk_f]),
#         yerr=([v.errMin for v in normDisk_f], [v.errMax for v in normDisk_f]),
#         fmt='.',
#         color = "blue"
#     )
# plt.xlabel("Temperature")
# plt.ylabel("Norm")
# plt.grid(True)
# #plt.show()
# plt.savefig(figures_dir + "/Norm_vs_Temp.png")
# plt.clf()

setName = ["norm", "Temp (keV)", "rate (c/s)", 'gamma', 'HR']
sets = [normDisk, T_disk, rate, gamma, hr]

for j in range(len(sets)):

    for i in range(j + 1, len(sets)):

        x = sets[i]
        y = sets[j]

        plt.errorbar(
            x = [v.value for v in x],
            y = [v.value for v in y], 
            #xerr=([v.errMin for v in x], [v.errMax for v in x]),
            #yerr=([v.errMin for v in y], [v.errMax for v in y]),
            fmt='--',
            color = "gray",
        )
        plt.errorbar(
            x = [v.value for v in x],
            y = [v.value for v in y], 
            #xerr=([v.errMin for v in x], [v.errMax for v in x]),
            #yerr=([v.errMin for v in y], [v.errMax for v in y]),
            fmt='o',
            color = "blue",
        )
        plt.xlabel(setName[i])
        plt.ylabel(setName[j])
        
        if setName[i] == "log norm":
            plt.xscale("log")
        if setName[j] == "log norm":
            plt.yscale("log")
        plt.xlabel(setName[i], fontsize=20)
        plt.ylabel(setName[j], fontsize=20)

        plt.xticks(fontsize=18)
        plt.yticks(fontsize=18)
        plt.grid(True)
        #plt.axhline(y=0, color='blue', linestyle='-', label="")
        #plt.show()
        namey = setName[j].replace("/","_")
        namex = setName[i].replace("/","_")
        plt.ylim(700,4000)
        plt.savefig(figures_dir + "/" + namey + "_vs_"+ namex + ".png")
        plt.clf()

# for i in range(len(sets) - 1):

#     xset = sets[i]
#     xname = setName[i]

#     remaining_sets = sets[i + 1:]
#     remaining_names = setName[i + 1:]

#     nrows = len(remaining_sets)

#     fig, axs = plt.subplots(
#         nrows=nrows,
#         ncols=1,
#         sharex=True,
#         figsize=(8, 3 * nrows)
#     )

#     # Needed if only one subplot
#     if nrows == 1:
#         axs = [axs]

#     plt.subplots_adjust(hspace=0)

#     x = [v.value for v in xset]

#     xerr = [
#         [v.errMin for v in xset],
#         [v.errMax for v in xset]
#     ]

#     for ax, yset, yname in zip(
#         axs,
#         remaining_sets,
#         remaining_names
#     ):

#         y = [v.value for v in yset]

#         yerr = [
#             [v.errMin for v in yset],
#             [v.errMax for v in yset]
#         ]

#         ax.errorbar(
#             x,
#             y,
#             xerr=xerr,
#             yerr=yerr,
#             fmt='.'
#         )

#         ax.set_ylabel(yname)

#     axs[-1].set_xlabel(xname)

#     plt.show()


