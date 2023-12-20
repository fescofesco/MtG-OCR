# -*- coding: utf-8 -*-
"""
Created on Sat Nov 11 18:36:52 2023

@author: unisp
"""

import os
import json
from tkinter import filedialog, simpledialog
import tkinter as tk
from urllib.parse import urlparse, urljoin
import re
import requests
from datetime import datetime, timedelta


#  ConfigHandler is the parent of MtGOCRData and CubeCObraData 
# MtGOCR contains the parameters img_storage_directory, phone_storate_directory
#   and scryfall date
#   MTGOCRData manages the parameters necessary for the OCR
# Cubecobra data contains the Cube URL and login Data 
#   CubeCobra manages the parameters necessary for interacting with CubeCobra
class ConfigHandler:
    def __init__(self, parameters_file="parameters.txt", cubecobra_file="cubecobralogin.txt"):
        self.parameters_file = parameters_file
        self.cubecobra_file = cubecobra_file
       
        
    def prompt_for_parameter_value(self, parameter):
        root = tk.Tk()
        root.withdraw()
        value = simpledialog.askstring("Input", f"Add value for {parameter}")
        root.destroy()
        return value
    
    def check_file_existence(self, filename):
        return os.path.isfile(filename)
    
#  MtGOCRData file contains the 
# img storage directory (Default called Img Storage) folder
# phone image directory needed if the img get automatically imported from the phone
# scryfall file date (now set to upadate 30 days) so the new expansions get 
#   downloaed or can be downloaed automatically by calling 
# If a set function of a working directory is called without providing a 
#  input, a tkinter window asks for the specific directory
class MtGOCRData(ConfigHandler):
    def __init__(self, parameters_file="parameters.txt"):
        super().__init__(parameters_file)
        if not os.path.exists(self.parameters_file):
            self.create_default_config()

        # self.setup_parameters_file()
        self.load_parameters_config()
        self.check_scryfall_date()

    def create_default_config(self):
        
        default_config = {
            "img_storage_directory": os.path.join(os.getcwd(), "Img Storage"),
            "phone_IMG_directory": None,
            "scryfall_file_date": None,
            "ui":[ 
                [[0.12149532, 0.928333], [0.2453, 0.973]]],
            "exp": [
              [[0.8137, 0.5616], [0.925, 0.6366]]
            ],
            "name": [
              [[0.10983, 0.085], [0.9088, 0.135]]
            ],
            "Mtg_letters": ["WdE&Su0\u00e261fF(4O\u00fctkJ\u00f6nZz\u00f1y\u00c9YICNla\\'_ \u00edcjh\u00e19\u00fa\u00e3HX\u0160M\u00e0s7Pp\u00f3\u00fb8v+:\u00e9beq3L-TiVwm?Qx\u00e4\\\"goGDU\u00aeA!K2/rB.),R"]
            }

        with open(self.parameters_file, "w") as f:
            json.dump(default_config, f, indent=2)
            
        print(default_config)
        img_storage_dir = default_config["img_storage_directory"]
        if not os.path.exists(img_storage_dir):
            os.makedirs(img_storage_dir)
        
        self.parameters_config = default_config      
        self.save_config()
        
        
    def load_parameters_config(self):
        if os.path.exists(self.parameters_file):
            with open(self.parameters_file, "r") as f:
                file_content = f.read()
                # Add this line for debugging
                # print("File content:", repr(file_content))  
                try:
                    self.parameters_config = json.loads(file_content)
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")
                    self.parameters_config = {}
        else:
            self.create_default_config()
             
    def update_Mtg_letters(self,verbose = 0):         
        
        scryfall_data = self.open_scryfall_file()
        # Assuming 'scryfall_data' contains the list of dicts with 'name' key for card names
        card_names = [card['name'] for card in scryfall_data]
        
        # Joining all card names into a single string
        all_card_names = ' '.join(card_names)
        
        # Finding unique letters used in card names
        unique_letters = set(all_card_names)
        unique_letters_str = ''.join(unique_letters)
      
        # Constructing the regular expression pattern to match these unique letters
        letters_pattern = f"[{''.join(unique_letters)}]"
      
        
        unique_letters_str = letters_pattern.replace("'", "\\'").replace('"', '\\"')
        if verbose >0:
            print("updated unique letters: ", unique_letters_str)

        # Now you can use this pattern in re.findall to match these letters in text
        # text = "Sample text containing MTG card letters"
        # pot_set = re.findall(letters_pattern, text)
        # print(pot_set)
        
        self.parameters_config["Mtg_letters"] = unique_letters_str
        self.save_config()
    
    
    # When displayed in this format, it helps to represent characters 
    # that might not be readily visible or easily typable.
    # To work with these special characters represented as Unicode escape 
    # sequences (\uXXXX), 
    # Python treats them the same way as the actual characters. For instance, 
    # \u00e9is the Unicode escape sequence for the character "é".
    def get_Mtg_letters(self):
        value = self.parameters_config["Mtg_letters"].encode('utf-8').decode('unicode-escape')

        if value is None or value == "":
            self.update_Mtg_letters()
            value = self.parameters_config["Mtg_letters"].encode('utf-8').decode('unicode-escape')

        return value
        
    def check_scryfall_date(self):       
        # Get the latest scryfall file
        latest_scryfall_file = self.get_latest_scryfall_file()
       
        if latest_scryfall_file is not None:
             timestamp = re.search(r'\d{14}', latest_scryfall_file).group()
             scryfall_date = datetime.strptime(timestamp, "%Y%m%d%H%M%S")
             # Update scryfall_file_date in the configuration
             self.parameters_config["scryfall_file_date"] = scryfall_date.strftime("%Y-%m-%d %H:%M:%S")
                   
             # Check if the scryfall file is older than 30 days
             if datetime.now() - scryfall_date > timedelta(days=30):
                 self.update_scryfall_file()
          
             # Save the updated configuration
             self.save_config()
         
        else:
             self.update_scryfall_file()
  
    def save_config(self):
        with open(self.parameters_file, "w") as f:
            json.dump(self.parameters_config, f, indent=2)
            

    def get_img_directory(self):
        value = self.parameters_config["img_storage_directory"]
        if value is None or value == "":
            self.set_img_storage_directory(os.path.join(os.getcwd(), "Img Storage"))
        return value

    def set_img_directory(self, value=None):
        if value is None:
            root = tk.Tk()
            root.withdraw()
            
            # Prompt for directory selection
            value = filedialog.askdirectory(title="Select Image Storage Directory")
        if value == "default":
            value = os.path.join(os.getcwd(), "Img Storage")
        
        # Create a temporary Tk instance to use filedialog
       
        print(value)
        # Destroy the temporary Tk instance
        root.destroy()
        
        # Update the img_storage_directory parameter
        self.parameters_config["img_storage_directory"] = value
        self.save_config()
        
 
    def get_phone_directory(self):
        value = self.parameters_config["phone_IMG_directory"]
        if value is None or value == "":
            self.set_phone_directory(None)
            return self.get_phone_directory()
        return value

    def set_phone_directory(self, value=None):
        if value is None:
            # value = self.prompt_for_parameter_value("phone_IMG_directory")
            root = tk.Tk()
            root.withdraw()
            value = filedialog.askdirectory(title="Select Phone Img")
            root.destroy()
        self.parameters_config["phone_IMG_directory"] = value
        self.save_config()



    def get_latest_scryfall_file(self):
        files = [f for f in os.listdir() if f.endswith('.json') and 
                 re.match(r'default-cards-\d{14}', f)]
        if not files:
            return None

        latest_file = max(files, key=lambda x: 
            datetime.strptime(re.search(r'\d{14}', x).group(), "%Y%m%d%H%M%S"))
        return latest_file

    # the set list is the sum of all mtg set names with their maximum collector
    # number
    def get_set_list(self, verbose = 0):
        filename = "all_sets.json"
        if not os.path.exists(filename):
            self.update_set_list(self.open_scryfall_file())
                  
        with open(filename, 'r', encoding='utf-8') as file:
            all_sets = json.load(file)
            
        if verbose >0:
            print("Loaded all_sets file")
            
        return all_sets
       
    def update_set_list(self,scryfall_file):
        # Initialize dictionaries to store set names and maximum collector numbers
        all_set_names = {}
        max_collector_numbers = {}

        for card_data in scryfall_file:
            if card_data.get('booster') is True:
                set_name = card_data['set']
                collector_number_str = card_data['collector_number']

                # Extract the numeric portion of the collector number  to '★'
                numeric_collector_number_str = collector_number_str.split('★')[0].strip()

                # Try to convert the numeric portion to an integer
                try:
                    collector_number = int(numeric_collector_number_str)
                except ValueError:
                    # Skip card entries with non-numeric collector numbers
                    continue

                if set_name not in all_set_names:
                    all_set_names[set_name] = []

                all_set_names[set_name].append(collector_number)

        # Find the maximum collector number for each set
        for set_name, collector_numbers in all_set_names.items():
            max_collector_numbers[set_name] = max(collector_numbers)

        # Filter sets containing only 3 letters
        three_letter_sets = {set_name: max_num for set_name, max_num in max_collector_numbers.items() if len(set_name) == 3}

        # Create a list of sets with their maximum collector numbers
        result_list = [{'set': set_name, 'max_collector_number': max_num} for set_name, max_num in three_letter_sets.items()]

        # Write the result list to a JSON file
        with open('all_sets.json', 'w') as f:
            json.dump(result_list, f, indent=0)

    def open_scryfall_file(self, verbose=0):
        files_in_directory = os.listdir()

        # Search for a file with a filename that starts with "default-cards" and ends with ".json"
        for filename in files_in_directory:
            if filename.startswith("default-cards") and filename.endswith(".json"):
                # Open and read the JSON file
                with open(filename, 'r', encoding='utf-8') as file:
                    if verbose >0:
                        print(filename)
                    scryfall_file = json.load(file)
          
        return scryfall_file
    
    def delete_old_scryfall_files(verbose=0):
        # Get all files in the directory
        files_in_directory = os.listdir()
    
        # Filter files that start with "default-cards" and end with ".json"
        relevant_files = [filename for filename in files_in_directory if filename.startswith("default-cards") and filename.endswith(".json")]
    
        # Extract and convert datetime from filenames
        file_date_times = []
        for filename in relevant_files:
            # Extract date and time information from the filename
            datetime_string = filename.split("default-cards-")[1].split(".json")[0]
    
            # Convert the extracted string into a datetime object
            try:
                file_datetime = datetime.strptime(datetime_string, "%Y%m%d%H%M%S")
                file_date_times.append((filename, file_datetime))
            except ValueError:
                pass  # Skip files with invalid datetime formats
    
        # Sort files based on datetime information in the filename
        file_date_times.sort(key=lambda x: x[1], reverse=True)
    
        # Keep the most recent file and delete the older ones
        for idx, (filename, _) in enumerate(file_date_times):
            if idx > 0:
                # Delete older files
                os.remove(filename)
                if verbose > 0:
                    print(f"Deleted: {filename}")
    
   

    def update_scryfall_file(self):
       # Implement your logic for updating the scryfall file here
       # Delete all but the latest scryfall file
    
       # Define the URL to download Scryfall bulk data files
       bulk_data_url = "https://api.scryfall.com/bulk-data"
    
       # Send a GET request to the Scryfall API to get the bulk data information
       response = requests.get(bulk_data_url)
    
       # Check if the request was successful
       download_successful = False
       if response.status_code == 200:
           data = response.json()
           print("Dowloading new scryfall data. \n Connection to scryfall successful")
           # Loop through the data to find the relevant download link
           for entry in data['data']:
               if entry['object'] == 'bulk_data' and entry['name'] == 'Default Cards':
                   download_link = entry['download_uri']
                   download_successful = True
                   break
    
       if download_successful:
           # Check if the file already exists in your working directory
           filename = os.path.basename(download_link)
           if not os.path.exists(filename):
               # Download the file
               response = requests.get(download_link)
    
               if response.status_code == 200:
                   with open(filename, 'wb') as file:
                       file.write(response.content)
    
                   print(f"Downloaded {filename}")
    
                   # Get the current datetime
                   scryfall_date = datetime.now()
    
                   # Load the existing configuration
               
    
                   # Update scryfall_file_date in the configuration
                   self.parameters_config["scryfall_file_date"] = scryfall_date.strftime("%Y-%m-%d %H:%M:%S")
    
                   # Save the updated configuration
                   # self.save_config(self.parameters_file, parameters_config)
                   self.save_config()

                   # print(self.parameters_config)
    
                   # Close the file before reloading
                   file.close()
    
                   # List files in the current directory
                   files_in_directory = os.listdir()
                   print("files_in_directory: ", files_in_directory)
                   # Delete files with a specific extension or criteria
                   for file in files_in_directory:
                       # Delete all files except my all_sets.json as this file
                       if file != filename and file != "all_sets.json":
                           if file.endswith(".json") or file.endswith(".JSON"):
                               print(file)
                               os.remove(file)
    
                   # Updating set list when no bulk data file is available
                   scryfall_file = self.open_scryfall_file()
                   self.update_set_list(scryfall_file)
                   self.update_Mtg_letters()
    
               else:
                   print(f"Failed to download {filename}")
    
           else:
               print(f"File {filename} already exists.")
    
       else:
           print("Failed to fetch bulk data from Scryfall API.")
         


#  CubeCObraData file contains the Cube URL and login Data 
class CubeCobraData(ConfigHandler):
    def __init__(self, cubecobra_file="cubecobralogin.txt"):
        super().__init__()
        self.cubecobra_file = cubecobra_file
        if not os.path.exists(self.cubecobra_file):
            self.create_default_cubecobra_config()
        self.load_cubecobra_config()

    def create_default_cubecobra_config(self):
        default_cubecobra_config = {
            "cube_url": None,
            "cube_username": None,
            "cube_password": None
        }

        with open(self.cubecobra_file, "w") as f:
            json.dump(default_cubecobra_config, f, indent=2)
           
    def load_cubecobra_config(self):
        if os.path.exists(self.cubecobra_file):
            with open(self.cubecobra_file, "r") as f:
                file_content = f.read()
                print("File content:", repr(file_content))  # Add this line for debugging
                try:
                    self.cubecobra_config_data = json.loads(file_content)
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")
                    self.cubecobra_config_data = {}
        else:
            self.cubecobra_config_data = {}

    def save_cubecobra_config(self):
        with open(self.cubecobra_file, "w") as f:
            json.dump(self.cubecobra_config_data, f, indent=2)

    def get_cube_url(self):
        value = self.cubecobra_config_data["cube_url"]
        if value is None:
            value = self.set_cube_url(None)
        return value

    def set_cube_url(self, value=None):
        if value is None:
            value = self.prompt_for_parameter_value("Cube URL or ID")
        # Check if the input is a valid URL
        parsed_url = urlparse(value)
        if not (parsed_url.scheme and parsed_url.netloc):
            # If not a valid URL, construct a URL using the base and input ID
            base_url = "https://cubecobra.com/cube/list/"
            constructed_url = urljoin(base_url, value)
            value = constructed_url
        self.cubecobra_config_data["cube_url"] = value
        self.save_cubecobra_config()

    def get_cube_username(self):
        value = self.cubecobra_config_data["cube_username"]
        if value is None:
            value = self.set_cube_username(None)
        return value

    def set_cube_username(self, value=None):
        if value == None:
            value = self.prompt_for_parameter_value("Cube Username")
        self.cubecobra_config_data["cube_username"] = value
        self.save_cubecobra_config()

    def get_cube_password(self):
        value = self.cubecobra_config_data["cube_password"]
        if value is None:
            value = self.set_cube_password(None)
        return value
    
    def set_cube_password(self, value=None):
        if value == None:
            value = self.prompt_for_parameter_value("Cube Password")
        self.cubecobra_config_data["cube_password"] = value
        self.save_cubecobra_config()
        


# Example usage
if __name__ == "__main__":
    # Create an instance of ConfigurationHandler
    mtg_ocr_data  = MtGOCRData()
    CubeData = CubeCobraData()
    # print(mtg_ocr_data.get_img_storage_directory())
    
    # mtg_ocr_data.set_phone_directory(None)
    # CubeData.get_cube_url()
    CubeData.set_cube_url("chrilix")
    # print(CubeData.get_cube_url())
    CubeData.set_cube_username("chrilix")
    CubeData.set_cube_password("meinpin6")
    # print(mtg_ocr_data.get_img_storage_directory())
    # mtg_ocr_data.set_phone_directory()

    print(CubeData.get_cube_url())
    
