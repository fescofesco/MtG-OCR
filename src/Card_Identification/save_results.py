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
import csv
import re
  
import pandas as pd

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
        
   
        # path = os.path.join(destination_directory, filename)  # Combine location and name using os.path.join()
    
            
        
        # header = ','.join(["name", "CMC", "Type", "Color", "Set", "Collector Number", "Rarity", "Color Category", "status", "Finish", "maybeboard", "image URL", "tags", "Notes", "MTGO ID"])
        
        # # Open the CSV file and write the data
        # with open(path, 'w', newline='') as csv_file:
        #     # csv_writer = csv.writer(csv_file, quoting=csv.QUOTE_NONE, escapechar='')
        #     csv_file.write(header + '\n')
        #     for line in data:
        #         entry_str = ','.join([str(field) for field in line])
        #         fields = [field.strip() for field in entry_str.split(",")]
        #         csv_line = ','.join(fields)
        #         csv_file.write(csv_line + '\n')
                
def write_results_to_csv_multi(identified_cards_paths, filename=None, destination_directory= None):
    if filename is None:
        filename = "CubeCobraCSV"  # Use current date and time as default name
        
    if not filename.endswith(".csv"):
        filename = filename + "_"+  datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = filename + '.csv'
        
    if destination_directory is None:
        destination_directory = get_path(PathType.RESULTS)  # Use the default results path
    
        
    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)
        
    if type(identified_cards_paths)== list:
        # Initialize an empty list to hold DataFrames
        data_frames = []

    
        # Read and merge data from all specified paths
        for identified_cards_path in identified_cards_paths:
            with open(identified_cards_path, 'r') as json_file:
                data = pd.read_json(json_file)
                data_frames.append(data)
                
                # Merge all DataFrames into a single DataFrame
                merged_data = pd.concat(data_frames, ignore_index=True)
        data = merged_data
        
        merged_data.columns = ["name", "CMC", "Type", "Color", "Set", "Collector Number", "Rarity", "Color Category", "status", "Finish", "maybeboard", "image URL", "tags", "Notes", "MTGO ID"]
        
        # Assign the renamed DataFrame to the 'data' variable
        data = merged_data
        
        # Display summary statistics of the data
        print(data.describe())
        
        # Display the first few rows of the data
        print(data.head())

        data = data.drop(data.columns[0], axis=1)
        print(data.describe())
        print(data.head())
           
   
    else:
        with open(identified_cards_path, 'r') as json_file:
            data = pd.read(json_file)
            print(data["name"])
            
    
       
    # Filter out empty sublists and exclude the first element from each sublist
    data = [item[1] for item in data if item]
        

    path = os.path.join(destination_directory, filename)  # Combine location and name using os.path.join()

        
    
    header = ','.join(["name", "CMC", "Type", "Color", "Set", "Collector Number", "Rarity", "Color Category", "status", "Finish", "maybeboard", "image URL", "tags", "Notes", "MTGO ID"])
    
    # Open the CSV file and write the data
    with open(path, 'w', newline='') as csv_file:
        # csv_writer = csv.writer(csv_file, quoting=csv.QUOTE_NONE, escapechar='')
        csv_writer = csv.writer(csv_file)

        csv_file.write(header + '\n')
        for line in data:
            csv_writer.writerow(line)        


            
    # with open(path, 'w', newline='') as csv_file:
    #     csv_writer = csv.writer(csv_file)
    #     csv_writer.writerow(header)  # Write header
    #     for line in merged_data:
    #         # Check if the maybeboard field is empty and set it to "false" if so
    #         line = [str(field).strip() if i != 10 or field else "false" for i, field in enumerate(line)]
    #         csv_writer.writerow(line)        
            
    # Reopen the CSV file to replace triple quotes with single quotes
    with open(path, 'r') as csv_file:
        csv_content = csv_file.read()
    
  
    
        
    csv_content = csv_content.replace('"""', '"')

    # Reopen the CSV file to modify the "name" column and replace triple quotes with single quotes
    with open(path, 'r', newline='') as csv_file:
        csv_reader = csv.reader(csv_file)
      

    return path

  
# identified_cards_paths =     ['C:\\Users\\felix\\Documents\\MtG-OCR\\MtG-OCR\\data\\Card_Identification\\results\\identified_cards_20240521_213011.txt',
#      'C:\\Users\\felix\\Documents\\MtG-OCR\\MtG-OCR\\data\\Card_Identification\\results\\identified_cards_20240520_213844.txt',
#      'C:\\Users\\felix\\Documents\\MtG-OCR\\MtG-OCR\\data\\Card_Identification\\results\\identified_cards_20240519_231450.txt']     


# path = write_results_to_csv(identified_cards_paths)
# print(path)

# Example usage
# path = "your_csv_file.csv"  # Replace with your actual file path



# pandadata = pd.read_csv(path, encoding='ascii',errors='ignore')

# pandadata = pd.read_csv(path, encoding='utf-8',errors='ignore')
# pandadata = pd.read_csv(path, engine='python', encoding='utf-8')

# print(pandadata.header())
                     
def write_results_to_csv3(identified_cards_paths, filename=None, destination_directory=None):
    if filename is None:
        filename = "CubeCobraCSV2"
    
    if not filename.endswith(".csv"):
        filename = filename + "_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".csv"
    
    if destination_directory is None:
        destination_directory = get_path(PathType.RESULTS)
    
    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)
    
    merged_data = []

    # Read and merge data from all specified paths
    for identified_cards_path in identified_cards_paths:
        with open(identified_cards_path, 'r') as json_file:
            data = json.load(json_file)
            merged_data.extend([item[1] for item in data if item])
    
    path = os.path.join(destination_directory, filename)
    header = ["name", "CMC", "Type", "Color", "Set", "Collector Number", "Rarity", "Color Category", "status", "Finish", "maybeboard", "image URL", "image Back URL","tags", "Notes", "MTGO ID"]

    # Open the CSV file and write the data
    with open(path, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(header)  # Write header
        for line in merged_data:
            # Check if the maybeboard field is empty and set it to "false" if so
            line = [str(field).strip() if i != 10 or field else "false" for i, field in enumerate(line)]
            csv_writer.writerow(line)

    # Reopen the CSV file to modify the "name" column and replace triple quotes with single quotes
    with open(path, 'r', newline='') as csv_file:
        csv_reader = csv.reader(csv_file)
        rows = list(csv_reader)
    
    # Process rows to update the "name" column and remove triple quotes
    updated_rows = []
    for row in rows:
        if row[0] != "name":  # Skip the header
            row[0] = row[0].split("//")[0].strip()  # Remove "//" and following characters
        updated_rows.append([field.replace('"""', '"') for field in row])  # Replace triple quotes with single quotes

    
            
        # Reopen the CSV file to replace triple quotes with single quotes
    with open(path, 'r') as csv_file:
        csv_content = csv_file.read()
    
        

    csv_content = csv_content.replace('"""', '"')

    with open(path, 'w', newline='') as csv_file:
        csv_file.write(csv_content)


def write_results_to_csv1(identified_cards_paths, filename=None, destination_directory=None):
    if filename is None:
        filename = "CubeCobraCSV_1"  # Default filename
    
    if not filename.endswith(".csv"):
        filename = filename + "_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".csv"
    
    if destination_directory is None:
        destination_directory = get_path(PathType.RESULTS)  # Use the default results path
    
    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)
    
    merged_data = []

    # Read and merge data from all specified paths
    for identified_cards_path in identified_cards_paths:
        with open(identified_cards_path, 'r') as json_file:
            data = json.load(json_file)
            merged_data.extend([item[1] for item in data if item])  # Filter out empty sublists and exclude the first element from each sublist
    filename ="cube" + ".csv"
    path = os.path.join(destination_directory, filename)  # Combine location and name using os.path.join()

    header = ["name", "CMC", "Type", "Color", "Set", "Collector Number", "Rarity", "Color Category", "status", "Finish", "maybeboard", "image URL", "tags", "Notes", "MTGO ID"]

    merged_data.name
   

    # Open the CSV file and write the data
    with open(path, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(header)  # Write header
        for line in merged_data:
            line = [str(field).strip() if i != 10 or field else "false" for i, field in enumerate(line)]
            csv_writer.writerow([str(field).strip() for field in line])  # Write each line
            
            if line[0] != "name":  # Skip the header
               line[0] = line[0].split("//")[0].strip()  # Remove "//" and following characters
            
      # Reopen the CSV file to replace triple quotes with single quotes
    with open(path, 'r') as csv_file:
        csv_content = csv_file.read()
    
        

    csv_content = csv_content.replace('"""', '"')

    with open(path, 'w', newline='') as csv_file:
        csv_file.write(csv_content)
