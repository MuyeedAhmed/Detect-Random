import sys
import os
import pandas as pd

from pathlib import Path

from ModifyLibraryFile import ModifyLibraryFile


def EditLib(libPath):
    root_path = Path(libPath)
    for libFile in root_path.rglob("*.py"):
        # print(libFile, type(libFile))
        mlf = ModifyLibraryFile(FilePath=str(libFile))
        mlf.fit()

if __name__ == "__main__":
    libFile = ""
    args = sys.argv
    if os.path.exists(args[1]):
        libPath = args[1]
    else:
        print("Path does not exist")
        exit()
    EditLib(libPath)
    
        
    
    
    




