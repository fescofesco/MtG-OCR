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
import sys


from src.Card_Identification.img_from_adb import transfer_images_from_device
from src.Card_Identification.card_extraction import extract_card
from src.Card_Identification.process_card import (create_rois_from_filename)
from src.Card_Identification.process_rois import (return_cardname_from_ROI, display_cardname, delete_duplicate_ROIs)
from src.Card_Identification.configuration_handler import MtGOCRData
from src.Card_Identification.path_manager import (get_path, PathType)
from src.Card_Identification.save_results import (write_results_to_file)
from src.Card_Identification.copy_img_to_data import (select_and_copy_images_to_data)




def save_infos(filename, cardname):
    print(f"Save infos for {filename} in identified_DATETIME.txt")
    cardnames.append([filename,cardname[0],])

def save_infos_foil(filename, cardname):
    print(f"Save infos for {filename} with finish foil in identified_DATETIME.txt")

def save_proxied(filename, cardname):
    print(f"Save infos for {filename} with status Proxied")

def move_to_unidentified(filename, cardname):
    print(f"Move {filename} to undidentified_DATETIME.txt")

def scrap_image(filename, cardname):
    print(f"Scrap image for {filename}. {filename} will NOT be moved to undidentified_DATETIME.txt")

def define_rois(filename, cardname):
    print(f"Define ROIs for {filename} and start anew")

def exit_program(filename, cardname):
    print("Exiting the program.")
    sys.exit()

def user_cardname_confirmation(filename, cardname, default_action=None):
    """
    Displays a user confirmation dialog and returns the selected action.
    """
    valid_choices = ['Y','F', 'P', 'N', 'S', 'R', 'X']


    if default_action:
        # If a default action is provided, execute it and return
        default_action(filename, cardname)
        return
    
    while True:
        print(f"The file {filename} was identified as {cardname[0]['name']} ccn {cardname[0]['collector_number']} from {cardname[0]['set']}. Is this correct?")
        print("[Y]es - save infos in identified_DATETIME.txt")
        print("[F] yes and save it with finish foil identified_DATETIME.txt")
        print("[P] yes and save it with status:Proxied")
        print("[N]o - move filename to undidentified_DATETIME.txt")
        print("[S] No and scrap image, filename will NOT be moved to undidentified_DATETIME.txt")
        print("[R]ois - define the rois again and start anew")
        print("[X] exit program")

        # Get user input
        choice = input("Enter your choice: ").upper()

        if choice in valid_choices:
            break
        else:
            print("Invalid choice. Please enter a valid option.")

    # Define actions based on user choices
    actions = {
        'Y': save_infos,
        'F': save_infos_foil,
        'P': save_proxied,
        'N': move_to_unidentified,
        'S': scrap_image,
        'R': define_rois,
        'X': exit_program
    }

    # Perform the selected action
    actions[choice](filename, cardname)
    

def main_Card_Identification(mode:str = None):
    """

    Parameters
    ----------
    mode : str, optional
    
        quickstart: A file dialog asks the user to select a folder 
        adb:
        all_files:
        
        DESCRIPTION. The default is None.

    Returns
    -------
    cardnames : TYPE
        DESCRIPTION.

    """
    
    if mode is None:
        mode = "quickstart"

    if mode == "quickstart":
        select_and_copy_images_to_data()
        all_images = return_folder_image_contents(get_path(PathType.RAW_IMAGE))
    elif mode == "adb":
        pass
    elif mode == "all_files":
        pass
        
    # main_Card_Identification()
    print("Main Func Of main_MtG-Card_Identification")
   
    verbose = 0
    # Create a generator for processing unprocessed files
   
    mtg_ocr_config = MtGOCRData()
    scryfall_all_data = mtg_ocr_config.open_scryfall_file()
    cardnames = []
    cardsnotidentified = []
    # Define the mode of file aquisition

    for filename in all_images:
    

        path = get_path(PathType.RAW_IMAGE,filename)
   
        card, error = extract_card(path ,verbose)
        if error: 
            print(error)
            cardsnotidentified.append(filename)
        
        
        if error is None:
            print(path)
            filename = os.path.basename(path)
            print(filename)
            create_rois_from_filename(filename, mtg_ocr_config, card, verbose)
            cardname = return_cardname_from_ROI(filename, scryfall_all_data, verbose)
            display_cardname(cardname)

        
            if cardname is not None:
                user_cardname_confirmation(filename,cardname)
        else:
            continue
       


# def main_Card_Identification(mode:str = None):
#     """

#     Parameters
#     ----------
#     mode : str, optional
    
#         quickstart: A file dialog asks the user to select a folder 
#         adb:
#         all_files:
        
#         DESCRIPTION. The default is None.

#     Returns
#     -------
#     cardnames : TYPE
#         DESCRIPTION.

#     """
    
#     if mode is None:
#         mode = "quickstart"

#     if mode == "quickstart":
#         select_and_copy_images_to_data()
#     elif mode == "adb":
#         pass
#     elif mode == "all_files":
        
#    # main_Card_Identification()
#    print("Main Func Of main_MtG-Card_Identification")
   
#    verbose = 0
#    # Create a generator for processing unprocessed files
#    file_generator = process_files(get_path(PathType.RAW_IMAGE))
#    timeout = 10
#    start_time = time.time()
#    mtg_ocr_config = MtGOCRData()
#    scryfall_all_data = mtg_ocr_config.open_scryfall_file()
#    cardnames = []
#    # Define the mode of file aquisition
#    while True:
#        try:
#            unprocessed_file = next(file_generator)
#            path = get_path(PathType.RAW_IMAGE,unprocessed_file)
   
#            card, error = extract_card(path ,verbose)
#            if error: print(error)
           
#            if error is None:
#                print(path)
#                filename = os.path.basename(path)
#                print(filename)
#                create_rois_from_filename(filename, mtg_ocr_config, card, verbose)
#                delete_duplicate_ROIs(filename,verbose)
#                cardname = return_cardname_from_ROI(filename, scryfall_all_data, verbose)
#                display_cardname(cardname)

#                if cardname is not None:
#                     cardnames.append([filename,cardname[0],])
#            else:
#                continue
           
            
#        except RuntimeError:
#            print("No new files found, exiting program")
#            return cardnames
#            break
       
#        except StopIteration:
#            print("StopIteration new files found, exiting program")
#            return cardnames
#            break
#        except KeyboardInterrupt:
#            print("User Termination")
#            return cardnames
#            break

if __name__ == "__main__":

    cardnames = main_Card_Identification()
    for card in cardnames:
        print(card[0], "was identified as", card[1]["name"], "from ", card[1]["set"])
    write_results_to_file(cardnames)



