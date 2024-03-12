# -*- coding: utf-8 -*-
"""
%(filename)
${file}
Created on %(date)s

author: Felix Scope
"""

import tkinter as tk
from tkinter import filedialog
import os
from collections import defaultdict
import csv
import colorama
from colorama import Fore, Style
import json
from path_manager import (get_path, PathType)
from card_extraction import (display_image, extract_card)


def load_files(file_paths=None):
    if file_paths is None:
        root = tk.Tk()
        root.withdraw()
        file_paths = filedialog.askopenfilenames(title="Select files", filetypes=[("CSV files", "*.csv")])
    
    data = []
    for file_path in file_paths:
        with open(file_path, 'r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)
    return data




def load_txt_files(file_paths=None):
    if file_paths is None:
        root = tk.Tk()
        root.withdraw()
        file_paths = filedialog.askopenfilenames(title="Select files", filetypes=[("TXT files", "*.txt")])
    
    data = []
    
    for file_path in file_paths:
        with open(file_path, 'r', newline='') as file:
            content = json.load(file)
       
            for entry in content:
                image_name = entry[0]
                card_info = entry[1]

                keys = ["name", "CMC", "Type", "Color", "Set", "Collector Number", "Rarity", "Color Category", 
                        "status", "Finish", "maybeboard", "image URL", "tags", "Notes", "MTGO ID"]
                
                card_dict = dict(zip(keys, card_info))
                card_dict["imagename"] = image_name
                
                data.append(card_dict)
    return data




def get_duplicates_path(directory=None):
    if directory==None:
        duplicates_files = [filename for filename in os.listdir("C:/Users/unisp/Documents/Infoprojekte/MtG_OCR/tests/data/card_identification/results") if filename.startswith("duplicates") and filename.endswith(".txt")]
    
    if not duplicates_files:
        print("No duplicates files found.")
        return None
    
    if len(duplicates_files) == 1:
        selected_file = duplicates_files[0]
    else:
        print("Multiple duplicates files found:")
        for i, file in enumerate(duplicates_files):
            print(f"{i + 1}. {file}")
        choice = int(input("Enter the number of the file you want to select: "))
        selected_file = duplicates_files[choice - 1]
    

    return selected_file

def get_default_duplicates(duplicates_file_path):
    default_duplicates = []
    if duplicates_file_path and os.path.exists(duplicates_file_path):
        with open(duplicates_file_path, "r") as f:
            duplicates_data = [eval(line.strip()) for line in f.readlines()]
    else:
        print("No duplicates file found")
        return [""]

    
    for entry in duplicates_data:
        default_duplicates.append(entry)
    return default_duplicates


    
def find_duplicates(data, default_duplicates):
    duplicates = defaultdict(list)
    for entry in data:
        if entry["name"] not in default_duplicates:
            key = (entry["name"], entry["Set"], entry["Collector Number"], entry["Finish"], entry["status"])
            duplicates[key].append(entry)
    return duplicates


def handle_duplicates(data,duplicates, default_duplicates,mode=None):
    for key, entries in duplicates.items():
        if len(entries) > 1:
                if mode =="NoDuplicates":
                    choice = "n"
                else:
                    print("Functional Duplicate:")
                    for entry in entries:
                        print_entry(entry)
                    choice = input("Do you want to keep these entries? (Y/N): ")
                if choice.lower() not in ('y', 'yes'):
                    # Remove all but the first entry from the list
                    for entry in entries[1:]:
                        data.remove(entry)
                else:
                  default_duplicates.append(entry["name"])
    return data, default_duplicates



def print_entry(entry, differing_keys=None):
    for key, value in entry.items():
        if key in ["name", "Set", "Collector Number", "Finish", "status"]:
            if differing_keys and key in differing_keys:
                print(f"{key}: {Fore.RED}{value}{Style.RESET_ALL}", end=" ")  # Print differing value in red
            else:
                print(f"{key}: {value}", end=" ")
    print()

import os

def find_image_by_name(image_name, folder):
    for root, dirs, files in os.walk(folder):
        if image_name in files:
            return os.path.join(root, image_name)
    return None

def find_and_display_differing_duplicates(data, default_duplicates, images_folder):
    name_map = defaultdict(list)
    
    # Step 1: Group entries by name
    for entry in data:
        key = (entry["name"], entry["Set"], entry["Collector Number"], entry["Finish"], entry["status"], entry["imagename"])
        name_map[entry["name"]].append(key)

    # Step 2: Iterate through grouped entries
    for name, keys in name_map.items():
        if len(keys) > 1:
            if name not in default_duplicates:
                differing_entries = defaultdict(list)
                
                # Step 3: Identify differing keys
                for key in keys:
                    for k, v in zip(["Set", "Collector Number", "Finish", "status"], key[1:]):
                        differing_entries[k].append(v)
                
                # Step 4: Print entries with differing keys
                print(f"Differing Duplicates for {Fore.CYAN}{name}{Style.RESET_ALL}:")
                print(keys)
                for index, key in enumerate(keys):
                    entry_info = key[:1] + key[1:5]  # Remove the name and image name from the key
                    print(f"{index+1}:", " ".join(map(str, entry_info)))
                
                    # Show the option to view the image
                    choice = input("Do you want to view the image associated with this entry? (Y/N): ")
                    if choice.lower() == 'y':
                        image_path = find_image_by_name(key[-1], images_folder)
                        if image_path:
                            card, error = extract_card(image_path)
                            display_image(name,card)
                        else:
                            print("Image not found.")
            
            choice = input("Which is the correct entry? (Enter index or N to skip): ")
            if choice.lower() != 'n':
                try:
                    choice = int(choice)
                    if 1 <= choice <= len(keys):
                        correct_entry = keys[choice - 1]
                        correct_index = data.index({"name": name, "Set": correct_entry[1], "Collector Number": correct_entry[2], "Finish": correct_entry[3], "status": correct_entry[4], "imagename": correct_entry[5]})
                        for key, value in zip(["Set", "Collector Number", "Finish", "status"], correct_entry[1:]):
                            data[correct_index][key] = value
                    else:
                        print("Invalid index. Entry not found.")
                except ValueError:
                    print("Invalid input. Please enter a valid index.")
            elif choice.lower() == 'n':
                choice = input("Do you want to add this duplicate to default duplicates? (Y/N)")
                if choice.lower() in ("y", "yes"): 
                    default_duplicates.append(name)
                elif choice.lower() in ("n", "no"):
                    pass
                else:
                    print("Invalid choice.")
        
    return data, default_duplicates

# def find_and_display_differing_duplicates(data, default_duplicates):
#     name_map = defaultdict(list)
    
#     # Step 1: Group entries by name
#     for entry in data:
#         key = (entry["name"], entry["Set"], entry["Collector Number"], entry["Finish"], entry["status"])
#         name_map[entry["name"]].append(key)

#     # Step 2: Iterate through grouped entries
#     for name, keys in name_map.items():
#         if len(keys) > 1:
#             if name not in default_duplicates:
#                 differing_entries = defaultdict(list)
                
#                 # Step 3: Identify differing keys
#                 for key in keys:
#                     for k, v in zip(["Set", "Collector Number", "Finish", "status"], key[1:]):
#                         differing_entries[k].append(v)
                
#                 # Step 4: Print entries with differing keys
#                 print(f"Differing Duplicates for {Fore.CYAN}{name}{Style.RESET_ALL}:")
#                 for index, key in enumerate(keys):
#                     entry_info = key[:1] + key[1:]  # Remove the name from the key
#                     print(f"{index+1}:", " ".join(map(str, entry_info)))

#             choice = input("Which is the correct entry? (Enter index or N to skip): ")
#             if choice.lower() != 'n':
#                 try:
#                     choice = int(choice)
#                     if 1 <= choice <= len(keys):
#                         correct_entry = keys[choice - 1]
#                         correct_index = data.index({"name": name, "Set": correct_entry[1], "Collector Number": correct_entry[2], "Finish": correct_entry[3], "status": correct_entry[4]})
#                         for key, value in zip(["Set", "Collector Number", "Finish", "status"], correct_entry[1:]):
#                             data[correct_index][key] = value
#                     else:
#                         print("Invalid index. Entry not found.")
#                 except ValueError:
#                     print("Invalid input. Please enter a valid index.")
#             elif choice.lower() == 'n':
#                 choice = input("Do you want to add this duplicate to default duplicates? (Y/N)")
#                 if choice.lower() in ("y", "yes"): 
#                     default_duplicates.append(name)
#                 elif choice.lower() in ("n", "no"):
#                     pass
#                 else:
#                     print("Invalid choice.")
        
#     return data, default_duplicates


    

# def find_and_display_differing_duplicates(data, default_duplicates):
#     colorama.init()  # Initialize colorama for cross-platform color support
#     name_map = defaultdict(list)
    
#     # Step 1: Group entries by name
#     for entry in data:
#         key = (entry["name"], entry["Set"], entry["Collector Number"], entry["Finish"], entry["status"])
#         name_map[entry["name"]].append(key)

#     # Step 2: Iterate through grouped entries
#     for name, keys in name_map.items():
#         if len(keys) > 1:
#             if name not in default_duplicates:
#                 differing_entries = defaultdict(list)
                
#                 # Step 3: Identify differing keys
#                 for key in keys:
#                     for k, v in zip(["Set", "Collector Number", "Finish", "status"], key[1:]):
#                         differing_entries[k].append(v)
                
#                 # Step 4: Print entries with differing keys highlighted
#                 print(f"Differing Duplicates for {Fore.CYAN}{name}{Style.RESET_ALL}:")
#                 options = []  # Initialize options list
#                 for i, (key, values) in enumerate(differing_entries.items(), 1):
#                     print("values",values)
#                     print("keys",keys)
#                     if len(set(values)) > 1:
#                         options.append((i, values))
#                         print(f"{i}: ", end="")
#                         for value in values:
#                             if values.count(value) == 1:
#                                 print(f"{Fore.RED}{key}: {value}{Style.RESET_ALL}", end=" ")  # Print differing key-value pair in red
#                             else:
#                                 print(f"{key}: {value}", end=" ")  # Print non-differing key-value pair
#                         print()

#             choice = input("Which is the correct entry? (Enter index or N to skip): ")
#             if choice.lower() != 'n':
#                 try:
#                     choice = int(choice)
#                     if 1 <= choice <= len(options):
#                         correct_entry = keys[choice - 1]
#                         correct_index = data.index({"name": name, "Set": correct_entry[1], "Collector Number": correct_entry[2], "Finish": correct_entry[3], "status": correct_entry[4]})
#                         for key, value in zip(["Set", "Collector Number", "Finish", "status"], correct_entry[1:]):
#                             data[correct_index][key] = value
#                     else:
#                         print("Invalid index. Entry not found.")
#                 except ValueError:
#                     print("Invalid input. Please enter a valid index.")
#             elif choice.lower() == 'n':
#                 choice = input("Do you want to add this duplicate to default duplicates? (Y/N)")
#                 if choice.lower() == ("y" or "yes"): 
#                     default_duplicates.append(name)
#                 elif choice.lower() == "n":
#                     pass
#                 else:
#                     print("Invalid choice.")
        
#     return data, default_duplicates

# def save_data(data, out_path=None):
#     if out_path is None:
#         root = tk.Tk()
#         root.withdraw()
#         out_path = filedialog.asksaveasfilename(title="Save file", defaultextension=".csv", filetypes=[("CSV files", "*.csv")])

#     header = ["name", "CMC", "Type", "Color", "Set", "Collector Number", "Rarity", "Color Category", "status", "Finish", "maybeboard", "image URL", "tags", "Notes", "MTGO ID"]
    
#     out_path = "C:/Users/unisp/Documents/Infoprojekte/MtG_OCR/data/card_identification/results/MainCube_copy.csv"

#     with open(out_path, 'w', newline='') as csv_file:
#         csv_file.write(",".join(header) + '\n')
#         for entry in data:
#             line = f'"{entry["name"]}"'
#             # line = '"' + entry["name"] + '",' + entry["CMC"]
#             # for field in header.split(","):
#             for field in header[1:]:
#                 if field not in ["CMC","Rarity","Color","Color Category","status","Finish","maybeboard", "image URL"]:
#                     line += f',"{entry[field]}"'  # Add double quotes for specified fields
#                 else:
#                     line += ',' + entry[field]  # Don't add double quotes for "Rarity"
#             csv_file.write(line + '\n')


#     print("CSV file updated successfully.")
def save_data(data, out_path=None):
    if out_path is None:
        root = tk.Tk()
        root.withdraw()
        out_path = filedialog.asksaveasfilename(title="Save file", defaultextension=".csv", filetypes=[("CSV files", "*.csv")])

    header = ["name", "CMC", "Type", "Color", "Set", "Collector Number", "Rarity", "Color Category", "status", "Finish", "maybeboard", "image URL", "tags", "Notes", "MTGO ID"]
    
    # out_path = "C:/Users/unisp/Documents/Infoprojekte/MtG_OCR/data/card_identification/results/MainCube_copy.csv"

    with open(out_path, 'w', newline='') as csv_file:
        csv_file.write(",".join(header) + '\n')
        for entry in data:
            line = f'"{entry["name"]}"'
            for field in header[1:]:
                if field in ["CMC", "Collector Number", "MTGO ID"]:  # Convert integer fields to strings
                    line += ',' + str(entry[field])
                else:
                    line += f',"{entry[field]}"'  # Add double quotes for specified fields
            csv_file.write(line + '\n')

    print("CSV file updated successfully.")

def save_duplicates(duplicates, out_path=None):
    if out_path is None:
        root = tk.Tk()
        root.withdraw()
        out_path = filedialog.asksaveasfilename(title="Save duplicates file", defaultextension=".txt", filetypes=[("CSV files", "*.csv")])


    with open(out_path, 'w', newline='') as file:
        for entry in duplicates:
            print(entry)
            file.write(entry + '\n')


def find_and_prompt_short_names(data, default_duplicates,mode=None):
    short_name_entries = [entry for entry in data if len(entry["name"]) < 5]
    if not short_name_entries:
        print("No entries with names shorter than 5 characters found.")
        return

    print("Entries with names shorter than 5 characters:")
    for entry in short_name_entries:
        if entry["name"] not in default_duplicates:
            if mode == "No_short_names":
                choice = "n"
            else:
                print_entry(entry)
                
                choice = input(f"Do you want to keep {entry['name']} ? (Y/N): ")
            if choice.lower() == 'y':
                # data = [entry for entry in data if entry not in short_name_entries]
                choice2 = input(f"Add {entry['name']} to default_duplicates? (Y/N): ")
                if choice2 == 'n':
                    default_duplicates.append(entry["name"])
            elif choice.lower() == ("n" or "no"):
                data.remove(entry)
    
    return data, default_duplicates




# Main function
def main():
    # Step 0
    txt_path =[
        r"C:/Users/unisp/Documents/Infoprojekte/MtG_OCR/data/card_identification/results/identified_cards_20240209_162117.txt",
        r"C:/Users/unisp/Documents/Infoprojekte/MtG_OCR/data/card_identification/results/identified_cards_20240209_182745.txt"]
    
    # txt_path =[
    #     r"C:/Users/unisp/Documents/Infoprojekte/MtG_OCR/data/card_identification/results/identified_cards_20240209_150946.txt"]
    # txt_path =[r"C:/Users/unisp/Documents/Infoprojekte/MtG_OCR/identified_cards_20240209_1.txt"]
    print(txt_path)
    txt_data = load_txt_files(txt_path)
    print(txt_data)

    path = "C:/Users/unisp/Documents/Infoprojekte/MtG_OCR/data/card_identification/results/CubeCobraCSV_20240209_182745.csv"
    path = txt_path
    # data1 = load_files(path)
    data = txt_data
    # print(data)
    duplicate_mode = "NoDuplicates"
    #Step 0
    path_default_duplicates = get_duplicates_path()
    default_duplicates = get_default_duplicates(path_default_duplicates)

    # Step 1
    duplicates = find_duplicates(data, default_duplicates)
    
    data, default_duplicates = handle_duplicates(data,duplicates, default_duplicates,duplicate_mode)
    mode_short_names = "No_short_names"
    data, default_duplicates = find_and_prompt_short_names(data,default_duplicates,mode_short_names)
    # Step 2
    image_folder = get_path(PathType.RAW_IMAGE)
    data,default_duplicates = find_and_display_differing_duplicates(data,default_duplicates,image_folder)
    # print(data)
    # Step 3
    # data = exclude_land_duplicates(data)
    out_path = "C:/Users/unisp/Documents/Infoprojekte/MtG_OCR/data/card_identification/results/MainCube.csv"
    save_data(data,out_path)
    print("duplicates",default_duplicates)
    out_path_duplicates = r"C:/Users/unisp/Documents/Infoprojekte/MtG_OCR/data/card_identification/config/duplicates.txt"
    if len(duplicates)>0: save_duplicates(default_duplicates,out_path_duplicates)
    
if __name__ == "__main__":
    main()
