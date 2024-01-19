# -*- coding: utf-8 -*-
"""
main_Card_Identification.py
Created on 17.01.2024

author: Felix Scope

writes the results to a file

"""


from src.Card_Identification.path_manager import (get_path, PathType)
import os 
import datetime
import json

def write_results_to_file(card_names, name=None, nodatetime=None, location=None):
    if name is None:
        name = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")  # Use current date and time as default name
    elif nodatetime is None:
        name = name + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
    if not name.endswith(".txt"):
        name = name + '.txt'
    if location is None:
        location = get_path(PathType.RESULTS)  # Use the default results path
    
    path = os.path.join(location, name)  # Combine location and name using os.path.join()

    # Check if the directory exists and create it if it doesn't
    if not os.path.exists(location):
        os.makedirs(location)
        
    with open(path, "w") as f:
        json.dump(card_names, f, indent=2)