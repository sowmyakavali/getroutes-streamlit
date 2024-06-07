# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 13:30:14 2024

@author: ManojSingh
"""
import os
import json
import platform

def save_file(file_data, file_name, file_type):    
    if platform.system() not in ['Windows', 'Darwin']:
        print(f"\n### Running on cloud, so NOT saving to {file_type} file {file_name} ###")
        return False
    
    #save file to local folder
    file_name = os.path.join('./output/', file_name)
    
    #save file to work folder
    if file_type == "txt":
        with open(file_name, "w") as f:
            f.writelines(file_data)
    elif file_type == "json":
        with open(file_name, "w") as f:
            f.writelines(json.dumps(file_data, indent=4))
    elif file_type == "html":
        file_data.save(file_name)    
    elif file_type == "csv":
        file_data.to_csv(file_name, index=False)    
    
    print(f"\n### saving to {file_type} file {file_name} ###")
    return True