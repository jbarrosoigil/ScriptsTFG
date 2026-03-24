import numpy as np
from astropy.io import fits
from os import listdir, getcwd, mkdir, chdir, rmdir, system
from os.path import isfile, join, isdir, dirname, basename

dirPath = getcwd()
counter = 1
maxDepth = 3
ProcessorsUsed = 45

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
        print (dir_name, " cwd: ", getcwd(),"  ",res_name)
        #rmdir(res_name+'-result')
        #if not isdir(res_name):
        #    mkdir(res_name)
        log_file = base_name + "_maketime.log"
        
        #Gets all the filenames and lists them without the extension.
        fL = GetFiles(direction)
        fL = [s for s in fL if s.endswith("_src.pha")]
        fileList = [f.replace("_src.pha", "") for f in fL]
        #fileList = [f.replace("_bck.pha", "") for f in fL]
        fileList = list(set(fileList)) #removes duplicates
        
        for file in fileList:
            light = 0
            err = 0
            src = direction + "/" + file + "_src.pha"
            bkg = direction + "/" + file + "_bkg.pha"

            try:
                with fits.open(src) as hdul:
                    data = hdul[1].data
                    col = data.columns.names
                    val_col = "COUNTS" if "COUNTS" in col else "RATE"
                    err_col = "STAT_ERR" if "STAT_ERR" in col else None
                    light += data[val_col][6:46].sum()
                    if err_col:
                        err += (data[err_col][6:46]**2).sum()

                with fits.open(bkg) as hdul:
                    data = hdul[1].data
                    col = data.columns.names
                    val_col = "COUNTS" if "COUNTS" in col else "RATE"
                    err_col = "STAT_ERR" if "STAT_ERR" in col else None
                    light -= data[val_col][6:46].sum()
                    if err_col:
                        err += (data[err_col][6:46]**2).sum()
                err = np.sqrt(err)
                cmd = f'echo -e "{light}\n{err}" > "{direction}/{file}.txt"'
                system(cmd)

            except Exception as e:
                print(f"Skipping {file} (missing or invalid): {e}")
                continue
        
RecursionFolder(dirPath)
