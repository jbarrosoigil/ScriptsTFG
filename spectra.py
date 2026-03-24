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
        basic_name = base_name + "-all-basic"
        filtfile_path = f"{res_name}/FP_xtefilt.lis"
        chdir(dir_name)
        print (dir_name, " cwd: ", getcwd(),"  ",res_name)
        #rmdir(res_name+'-result')
        #if not isdir(res_name):
        #    mkdir(res_name)
        log_file = base_name + "_maketime.log"
        cmd = (
            #f"pcaprepobsid indir={base_name} outdir={res_name} mode=h ; "

            f"pcaextspect2 "
            f"src_infile=@{base_name}-all-result/FP_dtstd2.lis "
            f"bkg_infile=@{base_name}-all-result/FP_dtbkg2.lis "
            f"src_phafile={base_name}-all_src.pha bkg_phafile={base_name}-all_bkg.pha "
            f"gtiandfile={base_name}-all-basic.gti "
            f"filtfile=@{base_name}-all-result/FP_xtefilt.lis "
            f"respfile={base_name}-all.rsp "
            f"pculist=ALL layerlist=ALL"
        )

        # if ProcessorsUsed > 1 and counter % ProcessorsUsed:
        #     cmd += " &"

        print (cmd + f' {counter:d}')
        counter += 1
        subprocess.run(cmd, shell=True)
        #system(f"{cmd}")
    

RecursionFolder(dirPath)
