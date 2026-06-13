import numpy as np
from astropy.io import fits
from astropy.time import Time
from os import listdir, getcwd, mkdir, chdir, rmdir, system
from os.path import isfile, join, isdir, dirname, basename

dirPath = getcwd()
counter = 1
maxDepth = 3

firstIndex = 0
highestIndexSoftState = 7
smallestIndexHardState = highestIndexSoftState + 1
lastIndex = 24

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
        fL = GetFiles(direction)
        fL = [s for s in fL if s.endswith("_src.pha")]
        fileList = [f.replace("_src.pha", "") for f in fL]
        fileList = list(set(fileList)) #removes duplicates
        dated_files = []

        for file in fileList:
            src = direction + "/" + file + "_src.pha"
            try:
                with fits.open(src) as hdul:

                    if "MJD-OBS" in hdul[1].header:
                        obs_time = hdul[1].header["MJD-OBS"]

                    else:
                        date_obs = hdul[1].header["DATE-OBS"]

                        obs_time = Time(
                            date_obs,
                            format='isot',
                            scale='utc'
                        ).mjd
                    dated_files.append((file, obs_time))
            except Exception as e:
                print(f"Could not read date for {file}: {e}")
                continue

        dated_files = sorted(dated_files, key=lambda x: x[1])
        fileList = [f[0] for f in dated_files]
        
        for file in fileList:

            light = 0
            err = 0

            soft = 0
            errSoft = 0
            hard = 0
            errHard = 0
            
            errHR = 0

            src = direction + "/" + file + "_src.pha"
            bkg = direction + "/" + file + "_bkg.pha"
            
            lsrc = 0
            errLsrc = 0
            lbkg = 0
            errLbkg = 0

            # headerSrc
            # headerBkg
            try:
                with fits.open(src) as hdul:
                    data = hdul[1].data
                    headerSrc = hdul[1].header
                    dateObs = hdul[1].header["DATE-OBS"]

                    exposureSrc = headerSrc["EXPOSURE"]
                    col = data.columns.names
                    val_col = "COUNTS" if "COUNTS" in col else "RATE"
                    err_col = "STAT_ERR" if "STAT_ERR" in col else None

                    expo = 1
                    if val_col == "COUNTS":
                        expo = exposureSrc
                    
                    lsrc = data[val_col][firstIndex:lastIndex + 1].sum()/expo
                    light += lsrc
                    
                    soft += data[val_col][firstIndex:highestIndexSoftState + 1].sum()/expo
                    hard += data[val_col][smallestIndexHardState:lastIndex + 1].sum()/expo

                    if err_col:
                        err += (data[err_col][firstIndex:lastIndex + 1]**2).sum()/expo**2
                        errLsrc += (data[err_col][firstIndex:lastIndex + 1]**2).sum()/expo**2
                        errSoft += (data[err_col][firstIndex:highestIndexSoftState + 1]**2).sum()/expo**2
                        errHard += (data[err_col][smallestIndexHardState:lastIndex + 1]**2).sum()/expo**2
                    else:
                        err += data[val_col][firstIndex:lastIndex + 1].sum()/expo**2
                        errLsrc += data[val_col][firstIndex:lastIndex + 1].sum()/expo**2
                        errSoft += data[val_col][firstIndex:highestIndexSoftState + 1].sum()/expo**2
                        errHard += data[val_col][smallestIndexHardState:lastIndex + 1 ].sum()/expo**2

                with fits.open(bkg) as hdul:
                    data = hdul[1].data
                    exposure = hdul[1].header["EXPOSURE"]

                    col = data.columns.names

                    val_col = "COUNTS" if "COUNTS" in col else "RATE"
                    err_col = "STAT_ERR" if "STAT_ERR" in col else None

                    expo = 1
                    if val_col == "COUNTS":
                        expo = exposure
                    
                    lbkg = data[val_col][firstIndex:lastIndex + 1].sum()/expo
                    light -= lbkg
                    
                    soft -= data[val_col][firstIndex:highestIndexSoftState + 1].sum()/expo
                    hard -= data[val_col][smallestIndexHardState:lastIndex + 1].sum()/expo
                    
                    if err_col:
                        err += (data[err_col][firstIndex:lastIndex + 1]**2).sum()/expo**2
                        errLbkg += (data[err_col][firstIndex:lastIndex + 1]**2).sum()/expo**2
                        errSoft += (data[err_col][firstIndex:highestIndexSoftState + 1]**2).sum()/expo**2
                        errHard += (data[err_col][smallestIndexHardState:lastIndex + 1]**2).sum()/expo**2
                    else:
                        err += data[val_col][firstIndex:lastIndex].sum()/expo**2
                        errLbkg += data[val_col][firstIndex:lastIndex].sum()/expo**2
                        errSoft += data[val_col][firstIndex:highestIndexSoftState + 1].sum()/expo**2
                        errHard += data[val_col][smallestIndexHardState:lastIndex + 1].sum()/expo**2

                err = np.sqrt(err)
                errLsrc = np.sqrt(errLsrc)
                errLbkg = np.sqrt(errLbkg)
                errSoft = np.sqrt(errSoft)
                errHard = np.sqrt(errHard)
                errHR = np.sqrt((errHard/soft)**2 + ((hard*errSoft)/soft**2)**2)

                HR = hard / soft if soft != 0 else 0
                
                if np.isfinite(light) and np.isfinite(HR) and np.isfinite(errHR) and np.isfinite(err):
                    cmd = f'echo "{light}\n{err}\n{HR}\n{errHR}\n{exposureSrc}\n{dateObs}\n{lsrc}\n{errLsrc}\n{lbkg}\n{errLbkg}" > "{direction}/{file}.txt"'
                    system(cmd) 
                
                
                
                #print(file, light, err, HR)

            except Exception as e:
                print(f"Skipping {file} (missing or invalid): {e}")
                continue
        
RecursionFolder(dirPath)