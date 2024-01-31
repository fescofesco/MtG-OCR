# -*- coding: utf-8 -*-
"""
Created on Sat Nov 11 18:36:52 2023

@author: Felix

configuration_handler.py

parent class that handles the paramters  / configuration of the MTG-OCR files
"""

import os
import json
from tkinter import filedialog, simpledialog
import tkinter as tk
from urllib.parse import urlparse, urljoin
import re
import requests
from datetime import datetime, timedelta
import cv2
from path_manager import (get_path, return_folder_contents, PathType)

# from src.card_identification.path_manager import (
#     get_path, return_folder_contents, PathType)


class ConfigHandler:
    """
      ConfigHandler is the parent of MtGOCRData and CubeCObraData 
  MtGOCR contains the parameters img_storage_directory, phone_storate_directory
      and scryfall date
      MTGOCRData manages the parameters necessary for the OCR
    Cubecobra data contains the Cube URL and login Data 
      CubeCobra manages the parameters necessary for interacting with CubeCobra
      
      
      
parent of 
    MTGOCRData          paramters are saved in parameters.txt
    CubeCobraData       logindata is saved in  cubecobralogin.txt
    
    If a set function of a working directory is called without providing a 
      input, a tkinter window asks for the specific directory
 
    
    """
    def __init__(self, parameters_file="parameters.txt",
                 cubecobra_file="cubecobralogin.txt"):
        self.parameters_file = parameters_file
        self.cubecobra_file = cubecobra_file
       
        
    def prompt_for_parameter_value(self, parameter):
        root = tk.Tk()
        root.withdraw()
        value = simpledialog.askstring("Input", f"Add value for {parameter}")
        root.destroy()
        return value
    
    


class MtGOCRData(ConfigHandler):
    """
        MtGOCRData file contains the 
      img_storage directory (Default called img_storage) folder
      phone image directory needed if the img get automatically imported from 
      the phone
      scryfall file date (now set to upadate 30 days) so the new expansions get 
        downloaed or can be downloaed automatically by calling 
  
           
    
##############################################################################

MTGOCRData 

contains and manages parameters used in the program and saved in parameter.txt

    If a set function of a working directory is called without providing a 
      input, a tkinter window asks for the specific directory
      

General parameters

  "img_storage_directory": where the card images are saved to, 
                          default "working directory / data / img_storage"
  "phone_IMG_directory": where the card images come from phone
                          default None, but save it in a folder "MTG-OCR",
                          the script will then autolocate the folder and 
                          save it 
  "scryfall_file_date":   date of the latest download of the scryfall files.
                          scryfall files are the online data bank of all the 
                          MtG card infomrations. It needs to be downloaded 
                          periodically (30 days e.g.) to provide support for 
                          latest Mtg Sets
                          
Specific paramters for the ROIs (region of interst). 
The ROIs are the card snippets that are analysed via OCR. by using card pre-
processing the OCR only finds more often the correct information and is not 
distracted.

Three categoreis of ROIs are defined:
    
    "ui" 
    "exp" 
    "name"
    
The default values are defining two edges of a rectanlge of the card snippet
  coordinates [[x0, y0], [x1, y1]] that are extracted from the card. 
  Coordinate system is centered on the top left corner. 
    
                          
  "ui": uniqueidentifier, contains 3 letter set code, card number and 
      rarity symbol. located on the bottom left of the card.
      default value:
          [ 
      [[0.12149532, 0.928333], [0.2453, 0.973]]],
  "exp": expansion symbol. contains the expansion symbol of the card. can be 
      used for machine learing to recogise the set just from the image. 
      the expansion symbol is located on the middle of the card on the right
      edge between artwork and text.
      
      default value:
      None but then set to 
          [
    [[0.8137, 0.5616], [0.925, 0.6366]]
    ],
      
  "name": the card name to be identied. The cardname is located on the top of 
      the card. Mostly starting from the top left to middle, but the tokens 
      name is locatd in the center of the card.
      
      default value:     
      [
    [[0.10983, 0.085], [0.9088, 0.135]]
  ],
      
      
  "Mtg_letters": all letters used in MTG card names, to limit OCR to these.
      default values, ecnoded in utf-8
      ["WdE&Su0\u00e261fF(4O\u00fctkJ\u00f6nZz\u00f1y\u00c9YICNla\\'_ 
       \u00edcjh\u00e19\u00fa\u00e3HX\u0160M\u00e0s7Pp\u00f3\u00fb8v+:
           \u00e9beq3L-TiVwm?Qx\u00e4\\\"goGDU\u00aeA!K2/rB.),R"]
  }
    
    
"""
    def __init__(self, parameters_file=None, verbose=0):
        """
        MtGOCRData file contains the 
        img_storage directory (Default called img_storage) folder
        phone image directory needed if the img get automatically imported from 
        the phone
        scryfall file date (now set to update 30 days) so the new expansions get 
        downloaded or can be downloaded automatically by calling
        rest of the init method
        """
        super().__init__(parameters_file or "parameters.txt")
        if not os.path.exists(get_path(PathType.CONFIG, self.parameters_file)):
            self.create_default_config()
        # self.setup_parameters_file()
        self.load_parameters_config()
        self.check_scryfall_date(verbose)

     
    def create_default_config(self): 
        default_config = {
        "phone_IMG_directory": None,
        "scryfall_file_date": "2024-01-11 22:05:17",
        "ui":[
            [[0.067, 0.906],[0.4509, 0.97]]
            ],
        "exp": [
            [[0.8224, 0.6733],[0.9135, 0.723]],
            [[0.7943, 0.5633],[0.9275, 0.62833]],
            [[0.7757, 0.7916],[0.9204, 0.86166]]
           ],
        "name": [
            [[0.20093, 0.095],[0.58411, 0.1467]],
            [[0.3434, 0.06], [0.621, 0.1333]],
            [[0.0983, 0.086], [0.9156, 0.13666]]
            ],
          "Mtg_letters": "[\u00ae\u00e0\u00e3c\u0160\u00faezO_C\\\")0bI(+ri:?!aLHXkSGdxtN\u00e19\u00f1lwAqgM\u00e2PUno\u00fcjJs\u00e9WpZ&\u00e4Vh\u00f3v3-\u00f6Ey\u00ed.B4K\u00fb,8FRm1f6/Q\\'\u00c9DT2u Y7]"
        }  
        self.parameters_config = default_config      
        self.save_config()
              
        
    def load_parameters_config(self):
        if os.path.exists(get_path(PathType.CONFIG,self.parameters_file)):
            with open(get_path(PathType.CONFIG, self.parameters_file), "r") as f:
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
        """ updates all used letters from MtG cards from scryfall file"""
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


        
        self.parameters_config["Mtg_letters"] = unique_letters_str
        self.save_config()
    
    
  
    def get_Mtg_letters(self):
        """ returns all letters used my MtG cards"""
        # When displayed in utf-8 encoded format, it  represent characters 
        # that might not be readily visible or easily typable.
        # To work with these special characters represented as Unicode escape 
        # sequences (\uXXXX), 
        # Python treats them the same way as the actual characters. For instance, 
        # \u00e9is the Unicode escape sequence for the character "é".
        value = self.parameters_config["Mtg_letters"]
     
        value = value[0].encode('utf-8').decode('unicode-escape')
        
        if value is None or value == "":
            self.update_Mtg_letters()
            value = self.parameters_config["Mtg_letters"].encode('utf-8').decode('unicode-escape')
        
        return value

    def check_scryfall_date(self,verbose =0):       
        """ returns the scryfall date, if too old, new file is donwloaded"""
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
            print("lates file is none")
            self.update_scryfall_file()
          
                 
  
    def save_config(self):
        with open(get_path(PathType.CONFIG,self.parameters_file), "w") as f:
            json.dump(self.parameters_config, f, indent=2)
            

 
    def get_phone_directory(self):
        value = self.parameters_config["phone_IMG_directory"]
        if value is None or value == "":
            self.set_phone_directory(None)
            return self.get_phone_directory()
        return value

    def set_phone_directory(self, value=None, tkinterDialog = True):
        if value is None:
            if tkinterDialog == True:
                root = tk.Tk()
                root.withdraw()
                value = filedialog.askdirectory(title="Select Phone Img")
                root.destroy()
            else:
                value = self.prompt_for_parameter_value("phone_IMG_directory")
        self.parameters_config["phone_IMG_directory"] = value
        self.save_config()

    def save_coordinates(self, mode, coordinates):
        with open(get_path(PathType.CONFIG, 'parameters.txt'), 'r') as file:
            data = json.load(file)

        if mode not in data:
            data[mode] = []  # Create an empty list for the mode if it doesn't exist

        data[mode].append(coordinates)  # Append the new coordinates to the list

        with open(get_path(PathType.CONFIG, 'parameters.txt'), 'w') as file:
            json.dump(data, file, indent=2)  # Save the updated data back to the file

        
    def click_event(self,event, x, y, flags, param):
        """
        Remembers the last 2 clicks on an image to define rectangles as future ROIS for 
        subsequent OCR recognition. Saves the coordinates.
    
        Parameters
        ----------
        event : TYPE
            you can click 2 times.
        x : TYPE
            x coordinates of clicked point
        y : TYPE
            y coordinates of clicked point
        flags : TYPE
            DESCRIPTION.
        param : TYPE
            DESCRIPTION.
    
        Returns
        -------
        None.
    
        """
        if event == cv2.EVENT_LBUTTONDOWN:
            param['clicked_points'].append((x, y))
            if len(param['clicked_points']) > 1:
                param['clicked_points'] = param['clicked_points'][-2:]  # Keep only the last 2 points
                self.draw_rectangle(param['image'], param['clicked_points'], param)
    
    def draw_rectangle(self, image, points, param):
        """
        draws a rectanlge of the last 2 clicked points to define the coordinates
        for a ROI thats saved if enter is pressed.
    
        Parameters
        ----------
        image : cv2 image
            DESCRIPTION.
        points : TYPE
            DESCRIPTION.
        param : TYPE
            DESCRIPTION.
    
        Returns
        -------
        None.
    
        """
        if len(points) == 2:
            img_copy = image.copy()  # Create a copy of the image to draw the rectangle on
            cv2.rectangle(img_copy, points[0], points[1], (0, 255, 0), thickness=2)
            cv2.imshow(param['window_name'], img_copy)
    
    
    def set_relative_coordinates(self, image, window_name= None,
                                 verbose =0, max_width=800, max_height=600):
        """
        this function help setting the coordinates for ui (unique identifier), name
        and expansion symbol. by clicking on both corner points of a rectangle that
        comprises the UI you want to safe the coordinates are written into
        paramters.txt file and can later be retrieved by 
        get_coordiantes_from_file("mode"), and be used to extract roi with 
        get_roi(card, coordinantes)
        
        clicking ... selects points that define the encompassing rectanlge 
        enter ... saves the rectangles coordinates depending on y- the position
            in "name",  "ui", "exp"
        'q' ... quits the function
    
        Parameters
        ----------
        image : cv2 image
            the card these identifiers shall be extracted from.
        mtg_ocr_config: class
            parameter handler for this program
        window_name : STR, optional
            how to call the window.
            The default is 'UI identifier, q to quit. Click coner points of UI, 
            exp symbol or name and press enter after each selsection'.
        verbose : TYPE, optional
            DESCRIPTION. The default is 0.
        max_width : TYPE, optional
            DESCRIPTION. The default is 800.
        max_height : TYPE, optional
            DESCRIPTION. The default is 600.
    
        Returns
        -------
        None.
    
        """
        if window_name is None:
            window_name = 'UI identifier, q to quit. Click coner points of UI,\
                exp symbol or name and press enter after each selsection to \
                    save coordinates'
        
        height, width, _ = image.shape
        scale = min(max_width / width, max_height / height)
        new_width = int(width * scale)
        new_height = int(height * scale)
        resized_image = cv2.resize(image, (new_width, new_height))
    
        param = {
            'width': new_width,
            'height': new_height,
            'image': resized_image,
            'clicked_points': [],
            'window_name': window_name
        }
    
        cv2.imshow(window_name, resized_image)
        cv2.setMouseCallback(window_name, self.click_event, param)
    
        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == ord('Q') or key == 27: #key 27 = ESC#:
                cv2.destroyWindow(window_name)
                break
            elif cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                break
            elif key == 13 :  # Check for 'Enter' key press or window closure
                points = tuple(param['clicked_points'])
                if len(points) == 2:
                    relative_coordinates = [
                        (p[0] / param['width'], p[1] / param['height']) for p in points
                    ]  # Calculate relative coordinates
                    
                    top_left = (min(relative_coordinates[0][0], relative_coordinates[1][0]), min(relative_coordinates[0][1], relative_coordinates[1][1]))
                    bottom_right = (max(relative_coordinates[0][0], relative_coordinates[1][0]), max(relative_coordinates[0][1], relative_coordinates[1][1]))
                    
                    coordinates = [top_left, bottom_right]
                    if verbose >2: print("coordinates", coordinates)
                    
                    # coordinates = tuple(relative_coordinates)
                    mode = self.determine_mode(top_left)  # Determine mode based on y position
                    if verbose > 0: print(mode, "added with rel. coordinates: ", coordinates)
                    self.save_coordinates(mode, coordinates)  # Save coordinates to file based on mode
                    cv2.imshow(window_name, resized_image)
                    cv2.setMouseCallback(window_name, self.click_event, param)
                    

    
    def determine_mode(self,top_left):
        """
        depends the relative height of the roi measured from the top of the card 
        to save it accordingly to either 
        
        'name' if roi is located on the top (0-0.35) of the card
        'exp'                    in the middle (0.36 - 0.7)
        'ui'                     at the bottom (0.71-1) of the card
        
        Parameters
        ----------
        y_coordinate : Float
           relative height of image
    
        Returns
        -------
        str
            mode 
            'name' name of the card
            'exp'  expansion smybol of the card
            'ui' unique identifier
                  
        """
        y_coordinate = top_left[0]
        x_coordinate = top_left[1]
        
        if x_coordinate >= 0.7:
            return "exp"
        
        if 0 <= y_coordinate <= 0.35:
            return 'name'
        elif 0.36 <= y_coordinate <= 0.7:
            return 'exp'
        elif 0.71 <= y_coordinate <= 1:
            return 'ui'
        else:
            print("determine_mode in process_card.py: wrong mode submitted \
                  to determine_mode")
            return 'unknown'    
        
    def get_coordinates_from_file(self, mode, verbose:int=0):
        """
        gets the coordinates of the fie from the paramters.txt file 

        Parameters
        ----------
        mode : STR
            'ui', 'name' or 'exp'

        Returns
        -------
        list of  lists of coordinates where the ROIS are extracted from
            [[[x_a1,y_a1],[x_a2,y_a2]],[[x_b1,y_b1],[x_b2,y_b2]],...]
            

        """
        filename = 'parameters.txt'
    
        with open(get_path(PathType.CONFIG, filename), 'r') as file:
            data = json.load(file)
       
        if verbose > 2: print("data:", data)
        if mode in data:
            return data[mode]
        else:
            print("Error, parameters.txt not found or mode not found.")
            print(" mode: ", mode)
            
            print("Define extractino area:")
            
            return None
            
        


    def get_latest_scryfall_file(self):
        files = [f for f in return_folder_contents(get_path(PathType.CONFIG)) if f.endswith('.json') and 
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
        if not os.path.exists(get_path(PathType.CONFIG ,filename)):
            self.update_set_list(self.open_scryfall_file(verbose))
                  
        with open(get_path(PathType.CONFIG, filename), 'r', encoding='utf-8') as file:
            all_sets = json.load(file)
            
        if verbose > 0:
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
        with open(get_path(PathType.CONFIG, 'all_sets.json'), 'w') as f:
            json.dump(result_list, f, indent=0)

    def open_scryfall_file(self, verbose=0):
        self.check_scryfall_date(verbose)
        if verbose >0: print("opening scryfall file")
        files_in_directory = return_folder_contents(get_path(PathType.CONFIG))
        self.delete_old_scryfall_files()
        if verbose > 0: print(files_in_directory)
        # Search for a file with a filename that starts with "default-cards" and ends with ".json"
        for filename in files_in_directory:
            if filename.startswith("default-cards") and filename.endswith(".json"):
                if verbose >0:
                    print("opening:", filename)
                # Open and read the JSON file
                with open(get_path(PathType.CONFIG, filename), 'r', encoding='utf-8') as file:
                
                    scryfall_file = json.load(file)
          
        return scryfall_file
    
    def delete_old_scryfall_files(self,verbose=0):
        # Get the directory path
        directory_path = get_path(PathType.CONFIG)
        
        # Filter files that start with "default-cards" and end with ".json"
        relevant_files = [filename for filename in os.listdir(directory_path) if filename.startswith("default-cards") and filename.endswith(".json")]
        
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
                # Create the full file path
                file_path = os.path.join(directory_path, filename)
                
                # Delete older files
                os.remove(file_path)
                if verbose > 0:
                    print(f"Deleted: {file_path}")
                print(f"Deleted: {file_path}")
    
   

    def update_scryfall_file(self, verbose =0):
       # Implement your logic for updating the scryfall file here
       # Delete all but the latest scryfall file
    
       # Define the URL to download Scryfall bulk data files
       bulk_data_url = "https://api.scryfall.com/bulk-data"
    
       # Send a GET request to the Scryfall API to get the bulk data information
       try:
           response = requests.get(bulk_data_url)
       except ConnectionError:
           print("Could not update scryfall file, check internet connection.")  
       else:
            
        
           # Check if the request was successful
           download_successful = False
           if response.status_code == 200:
               data = response.json()
               if verbose >0: 
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
               if not os.path.exists(get_path(PathType.CONFIG,filename)):
                   # Download the file
                   response = requests.get(download_link)
        
                   if response.status_code == 200:
                       with open(get_path(PathType.CONFIG,filename), 'wb') as file:
                           file.write(response.content)
        
                       print(f"Downloaded {filename}")
        
                       # Get the current datetime
                       scryfall_date = datetime.now()
        
                       # Update scryfall_file_date in the configuration
                       self.parameters_config["scryfall_file_date"] = scryfall_date.strftime("%Y-%m-%d %H:%M:%S")
        
                       # Save the updated configuration
                       self.save_config()
    
                                    # Close the file before reloading
                       file.close()
        
                       # List files in the current directory
                       files_in_directory = return_folder_contents(get_path(PathType.CONFIG))

                       if verbose >2:
                           print("files_in_directory: ", files_in_directory)
                       # Delete files with a specific extension or criteria
                       for file in files_in_directory:
                           # Delete all files except my all_sets.json as this file
                           if file != filename and file != "all_sets.json":
                               if file.endswith(".json") or file.endswith(".JSON"):
                                   print("removing old scryfall file", file)
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
        
        if not os.path.exists(get_path(PathType.CONFIG,self.cubecobra_file)):
            
            self.create_default_cubecobra_config()
        self.load_cubecobra_config()

    def create_default_cubecobra_config(self):
        default_cubecobra_config = {
            "cube_url": 123,
            "cube_username": "username",
            "cube_password": "password"
        }

        with open(get_path(PathType.CONFIG, self.cubecobra_file), "w") as f:
            json.dump(default_cubecobra_config, f, indent=2)
           
    def load_cubecobra_config(self):
        if os.path.exists(get_path(PathType.CONFIG,self.cubecobra_file)):
            with open(get_path(PathType.CONFIG,self.cubecobra_file), "r") as f:
                file_content = f.read()
                # print("File content:", repr(file_content))  # Add this line for debugging
                try:
                    self.cubecobra_config_data = json.loads(file_content)
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")
                    self.cubecobra_config_data = {}
        else:
            self.cubecobra_config_data = {}

    def save_cubecobra_config(self):
        with open(get_path(PathType.CONFIG,self.cubecobra_file), "w") as f:
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
    mtg_ocr_config  = MtGOCRData(verbose = 3)
    print(mtg_ocr_config.get_Mtg_letters())
    # storage_directory = mtg_ocr_config.get_img_directory()

    filename = "1.jpg"   
  
    
    image =cv2.imread(get_path(PathType.RAW_IMAGE_TEST, filename))   
    mtg_ocr_config.set_relative_coordinates(image)
    

    CubeData = CubeCobraData()
    # print(mtg_ocr_data.get_img_storage_directory())
    
    # mtg_ocr_data.set_phone_directory(None)
    # CubeData.get_cube_url()
    CubeData.set_cube_url()
    # print(CubeData.get_cube_url())
    CubeData.set_cube_username("chrilix")
    print(CubeData.get_cube_username())

    CubeData.set_cube_password()
    print(CubeData.get_cube_password())

    # print(mtg_ocr_data.get_img_storage_directory())
    # mtg_ocr_data.set_phone_directory()

    print(CubeData.get_cube_url())
    print("ui")
    print(mtg_ocr_config.get_coordinates_from_file("ui"))
    print(mtg_ocr_config.get_coordinates_from_file("exp"))
    print("name")
    print(mtg_ocr_config.get_coordinates_from_file("name"))
