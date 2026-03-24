import subprocess
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
    if depth == maxDepth and len(direction) > ProcessorsUsed and "result" not in direction:
        dir_name = dirname(direction)
        base_name = basename(direction)
        res_name = base_name+"-result"
        chdir(dir_name)
        print (dir_name, " cwd: ", getcwd(),"  ",res_name)
        #rmdir(res_name+'-result')
        #if not isdir(res_name):
        #    mkdir(res_name)
        log_file = base_name +".log"
        if (ProcessorsUsed > 1 and counter % ProcessorsUsed):
            cmd = f"pcaprepobsid indir={base_name} outdir={res_name} mode=h > {log_file}"+" 2>&1 &"
            #cmd = f"pcaprepobsid indir={base_name} outdir={res_name} > {log_file}"+" 2>&1 & "
        else:
            cmd = f"pcaprepobsid indir={base_name} outdir={res_name} mode=h > {log_file}"+" 2>&1"            
        print (cmd + f' {counter:d}')
        counter += 1
        system(f"{cmd}")
    #subprocess.run("pcaprepobsid", cwd=direction)
    

RecursionFolder(dirPath)
