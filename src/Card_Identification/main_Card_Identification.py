# -*- coding: utf-8 -*-
"""
main_Card_Identification.py
Created on 08.01.2024

author: Felix Scope
"""


import pytesseract
import cv2
import datetime
import time
import os
from pathlib import Path
import json

from src.Card_Identification.img_from_adb import transfer_images_from_device
from src.Card_Identification.card_extraction import extract_card
from src.Card_Identification.process_card import (create_rois_from_filename)
from src.Card_Identification.process_rois import (return_cardname_from_ROI, display_cardname, delete_duplicate_ROIs)
from src.Card_Identification.configuration_handler import MtGOCRData
from src.Card_Identification.path_manager import (get_path, PathType)


def process_files(directory, timeout=2):
    if not os.path.isabs(directory):
        full_path = os.path.join("ImgStorage", directory)
    else:
        full_path = directory
        
    processed_files = set()
    start_time = time.time()

    while True:
        files = os.listdir(full_path)
        jpg_files = [file for file in files if file.endswith('.jpg')]

        for jpg_file in jpg_files:
            if jpg_file not in processed_files:
                processed_files.add(jpg_file)
                yield os.path.join(directory, jpg_file)

        elapsed_time = time.time() - start_time
        if elapsed_time > timeout:
            raise StopIteration


def get_newest_image(directory):
    """
    returns the name of the newest image by file name change date of the specified
    directory

    Parameters
    ----------
    directory : STR
        relative or absolute directory where the function searches.

    Returns
    -------
    cv2 image
        returns the latest card from the folder

    """
    if not os.path.isabs(directory):
        directory = os.path.join(os.getcwd(), directory)  # Join with current working directory if not absolute

    image_files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

    if not image_files:
        return None  # No image files found

    # Sort files by name to get the one with the highest timestamp
    image_files.sort(reverse=True)

    newest_image = os.path.join(directory, image_files[0])  # Return absolute path to the newest image
    return newest_image

def write_results_to_file(card_names, name=None, location=None):
    if name is None:
        name = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")  # Use current date and time as default name
    
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


def main_Card_Identification():
   # main_Card_Identification()
   print("Main Func Of main_MtG-Card_Identification")
   
   verbose = 0
   # Create a generator for processing unprocessed files
   file_generator = process_files(get_path(PathType.RAW_IMAGE))
   timeout = 10
   start_time = time.time()
   mtg_ocr_config = MtGOCRData()
   scryfall_all_data = mtg_ocr_config.open_scryfall_file()
   cardnames = []
   # Define the mode of file aquisition
   while True:
       try:
           unprocessed_file = next(file_generator)
           path = get_path(PathType.RAW_IMAGE,unprocessed_file)
   
           card, error = extract_card(path ,verbose)
           if error: print(error)
           
           if error is None:
               print(path)
               filename = os.path.basename(path)
               print(filename)
               create_rois_from_filename(filename, mtg_ocr_config, card, verbose)
               delete_duplicate_ROIs(filename,verbose)
               cardname = return_cardname_from_ROI(filename, scryfall_all_data, verbose)
               display_cardname(cardname)

               if cardname is not None:
                    cardnames.append([filename,cardname[0],])
           else:
               continue
           
            
       except RuntimeError:
           print("No new files found, exiting program")
           return cardnames
           break
       
       except StopIteration:
           print("StopIteration new files found, exiting program")
           return cardnames
           break
       except KeyboardInterrupt:
           print("User Termination")
           return cardnames
           break

if __name__ == "__main__":

    cardnames = main_Card_Identification()
    for card in cardnames:
        print(card[0], "was identified as", card[1]["name"], "from ", card[1]["set"])
    write_results_to_file(cardnames)



