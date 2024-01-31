# -*- coding: utf-8 -*-
"""
main_Card_Identification.py
Created on 17.01.2024

author: Felix Scope

writes the results to a file

"""


import os 
import datetime
import json
from path_manager import (get_path, PathType)


def write_results_to_txt(card_names,filename=None, destination_directory=None):
    if filename is None:
        filename = "identified_cards"  # Use current date and time as default name
        
    if not filename.endswith(".txt"):
        filename = filename + "_"+  datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = filename + '.txt'
    if destination_directory is None:
        destination_directory = get_path(PathType.RESULTS)  # Use the default results path
    
    path = os.path.join(destination_directory, filename)  # Combine location and name using os.path.join()

    # Check if the directory exists and create it if it doesn't
    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)
        
    with open(path, "w") as f:
        json.dump(card_names, f, indent=2)
    
    return path
        
        
def write_results_to_csv(identified_cards_path, filename=None, destination_directory= None):
    if filename is None:
        filename = "CubeCobraCSV"  # Use current date and time as default name
        
    if not filename.endswith(".csv"):
        filename = filename + "_"+  datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = filename + '.csv'
    if destination_directory is None:
        destination_directory = get_path(PathType.RESULTS)  # Use the default results path
    
        
    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)
        
    with open(identified_cards_path, 'r') as json_file:
        data = json.load(json_file)
    
       
    # Filter out empty sublists and exclude the first element from each sublist
    data = [item[1] for item in data if item]
        

    path = os.path.join(destination_directory, filename)  # Combine location and name using os.path.join()

        
    
    header = ','.join(["name", "CMC", "Type", "Color", "Set", "Collector Number", "Rarity", "Color Category", "status", "Finish", "maybeboard", "image URL", "tags", "Notes", "MTGO ID"])
    
    # Open the CSV file and write the data
    with open(path, 'w', newline='') as csv_file:
        # csv_writer = csv.writer(csv_file, quoting=csv.QUOTE_NONE, escapechar='')
        csv_file.write(header + '\n')
        for line in data:
            entry_str = ','.join([str(field) for field in line])
            fields = [field.strip() for field in entry_str.split(",")]
            csv_line = ','.join(fields)
            csv_file.write(csv_line + '\n')
