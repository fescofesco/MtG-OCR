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
import re
import colorama

colorama.init()

from src.Card_Identification.img_from_adb import transfer_images_from_device
from src.Card_Identification.card_extraction import (extract_card, display_image)
from src.Card_Identification.process_card import (create_rois_from_filename)
from src.Card_Identification.process_rois import (return_cardname_from_ROI, display_cardname, delete_duplicate_ROIs)
from src.Card_Identification.configuration_handler import MtGOCRData
from src.Card_Identification.path_manager import (get_path, PathType,return_folder_image_contents)
from src.Card_Identification.save_results import (write_results_to_file)
from src.Card_Identification.copy_img_to_data import (select_and_copy_images_to_data)
from src.Card_Identification.save_results import write_results_to_file




def save_card_infos(card_infos, card, filename, finish=None, status=None, maybeboard=None, image_url=None, image_back_url=None, tags=None, notes=None):
# the scryfall.csv logic is: name,CMC,Type,Color,Set,Collector Number,Rarity,Color Category,status,Finish,maybeboard,image URL,image Back URL,tags,Notes,MTGO ID

    print("card_infos = ", card_infos)
    if finish is None:
        finish = "non-foil"
    if status is None:
        status = "owned"
    if maybeboard is None:
        maybeboard = "false"
    if image_url is None:
        image_url = ""
    if image_back_url is None:
        image_back_url = ""
    if tags is None:
        tags = ""
    if notes is None:
        notes = ""
        
    try:
        card_infos['mtgo_id']
    except KeyError:
        card_infos['mtgo_id'] = ""
    
    entry = [card_infos["name"], card_infos["cmc"], card_infos["type_line"], card_infos["color_identity"], card_infos["collector_number"], card_infos["rarity"],     [color.lower() for color in card_infos["color_identity"]],  status, finish, maybeboard, image_url, image_back_url, tags, notes, card_infos["mtgo_id"]] # Lowercase each element
    title = filename + "_" + card_infos["name"] + "_" + card_infos["collector_number"] + "_" + card_infos["set"] + "_finish: " + finish + "_status: " + status + ".jpg"
    path = get_path(PathType.RESULTS, title)
    cv2.imwrite(path, card)
    return entry

def save_infos(filename, card_infos, card_data, card, scryfall_file, mtg_ocr_config, default_action=None):
    print(f"Save infos for {filename} in identified_DATETIME.txt")
    finish = "non-foil"
    status = "owned"
    print(card_data)
    card_data["identified_cards"].append((filename, save_card_infos(card_infos, card, filename, finish=finish, status=status)))
    return card_data
    
def save_infos_foil(filename, card_infos, card_data, card, scryfall_file, mtg_ocr_config, default_action=None):
    print(f"Save infos for {filename} with finish foil in identified_DATETIME.txt")
    finish = "foil"
    status = "owned"
    card_data["identified_cards"].append((filename, save_card_infos(card_infos, card, filename, finish=finish, status=status)))
    return card_data
    
def save_proxied(filename, card_infos, card_data, card, scryfall_file, mtg_ocr_config, default_action=None):
    print(f"Save infos for {filename} with status Proxied")
    finish = "non-foil"
    status = "proxied"
    card_data["identified_cards"].append((filename, save_card_infos(card_infos, card, filename, finish=finish, status=status)))
    return card_data
    
def move_to_unidentified(filename, card_infos, card_data, card, scryfall_file, mtg_ocr_config, default_action=None):
    print(f"Move {filename} to undidentified_DATETIME.txt")
    card_data["unidentified_cards"].append(filename)
    return card_data
    
def scrap_image(filename, card_infos, card_data, card, scryfall_file, mtg_ocr_config, default_action=None):
    print(f"Scrap image for {filename}. {filename} will NOT be moved to undidentified_DATETIME.txt")
    return card_data
    
def define_rois(filename, card_infos, card_data, card, scryfall_file, mtg_ocr_config, default_action=None):
    print(f"Define ROIs for {filename} and start anew")
    mtg_ocr_config.set_relative_coordinates(card)
    move_to_unidentified(filename, card_infos, card_data, card, scryfall_file, mtg_ocr_config, default_action)
    return card_data


def checkif_scryfall_file_contains_card(scryfall_file, pot_sets, pot_collector_numbers):
    #  Check if the scryfall file contains 
    # Return True if the card is found, otherwise return False
    
        # Convert collector numbers to integers to remove leading zeros
    collector_numbers = [int(collector_number) for collector_number in pot_collector_numbers]
    
    # Find the smallest collector number
    smallest_collector_number = min(collector_numbers)
    
    # Convert it back to a string if needed
    smallest_collector_number_str = str(smallest_collector_number)

    print(pot_sets)
    print(pot_collector_numbers)
    for card in scryfall_file:
        for pot_set in pot_sets:
                if card["set"] == pot_set.lower() and card["collector_number"] == smallest_collector_number_str:
                    return card
    return False

# def enter_UI(filename, card_infos, card_data, card, scryfall_file, mtg_ocr_config, default_action=None):
#     print("Enter UI chosen")
#     print("Enter set abbreviation and collector number e.g. MH2 020 ")

#     # Wait for user input
    
#     user_input = input("Enter set abbreviation and collector number: \n If rarity is token add t in front of the set, eg. TGRN ")

#     # Use regular expressions to extract potential set and collector number
#     pot_sets = re.findall(r'\b[A-Za-z]{3,4}\b', user_input)
#     pot_collector_numbers = re.findall(r'\b\d+\b', user_input)
#     # pot_collectornumbers = int(pot_collectornumber[0])

#     # Check if cards exist
#     card_infos = checkif_scryfall_file_contains_card(scryfall_file, pot_sets, pot_collector_numbers)
#     if card_infos:
#         print(f"Card identified as {card_infos['name']} from set {card_infos['set']}")
#         card_data = user_cardname_confirmation(filename, card_infos, card_data, card, scryfall_file, mtg_ocr_config, default_action)
#         return card_data
#     else:
#         print("No valid input, try again? [Y]es, [N]o?")
#         response = input().lower()
#         if response == 'n':
#             move_to_unidentified(filename, card_infos, card_data, card, scryfall_file, mtg_ocr_config, default_action)
#         elif response == 'y':
#                 enter_UI(filename, card_infos, card_data, card, scryfall_file, mtg_ocr_config, default_action)
#                 return card_data
#         else:
#             pass
             

           

def write_results_files(filename, card_infos, card_data, card, scryfall_file, mtg_ocr_config, default_action=None):
    print("Write files chosen.")
    write_results_to_file(card_data["unidentified_cards"],"redo_cards")
    write_results_to_file(card_data["identified_cards"],"identified_cards")
    user_cardname_confirmation(filename, card_infos, card_data, card, scryfall_file, mtg_ocr_config, default_action=None)
    return card_data




def exit_program(filename, card_infos, card_data, card, scryfall_file, mtg_ocr_config, default_action=None):
    print("Exiting the program.")
    write_results_files(filename, card_infos, card_data, card, scryfall_file, mtg_ocr_config, default_action)
    sys.exit()

# def user_cardname_confirmation(filename, card_infos, card_data, card, scryfall_file, mtg_ocr_config, default_action=None):
#     """
#     Displays a user confirmation dialog and returns the selected action.
#     """
    
#     display_image(card_infos["name"],card)
#     valid_choices = ['Y','F', 'P', 'U', 'UI', 'N', 'R', 'X', 'W']


#     if default_action:
#         # If a default action is provided, execute it and return
#         default_action(filename, card_infos)
#         return
    
#     while True:
#         print(f"The file {filename} was identified as {card_infos['name']} ccn {card_infos['collector_number']} from {card_infos['set']}. Is this correct?")
#         print("[Y]es - save infos in identified_DATETIME.txt")
#         print("[F] yes and save it with finish foil identified_DATETIME.txt")
#         print("[P] yes and save it with status:Proxied")
#         print("[U]  move filename to undidentified images to to analyse it again")
#         print("[N] No and scrap image, filename will NOT be moved to undidentified_DATETIME.txt")
#         print("[UI] No and enter UI")
#         print("[R]ois - define the rois again and move image to unitdentied to analyse it again")
#         print("[W]rite current results to identified_DATETIME.txt and unidentified_DATETIME.txt in", get_path(PathType.RESULTS))
#         print("[X] exit program")

#         # Get user input
#         choice = input("Enter your choice: ").upper()

#         if choice in valid_choices:
#             break
#         else:
#             print("Invalid choice. Please enter a valid option.")

#     # Define actions based on user choices
#     actions = {
#         'Y': save_infos,
#         'F': save_infos_foil,
#         'P': save_proxied,
#         'U': move_to_unidentified,
#         'N': scrap_image,
#         'UI': enter_UI, 
#         'R': define_rois,
#         'X': exit_program,
#         'W': write_files
#     }

#     # Perform the selected action
#     updated_card_data = actions[choice](filename, card_infos, card_data, card, scryfall_file, mtg_ocr_config, default_action=None)
    
    
#     return updated_card_data

def checkif_scryfall_file_contains_UI(user_input, filename, card_infos, card_data, card, scryfall_file, mtg_ocr_config, default_action):
    #  Check if the scryfall file contains 
    # Return True if the card is found, otherwise return False
    try:
        user_input = str(user_input)
    
        pot_sets = re.findall(r'\b[A-Za-z0-9]{3,4}\b', user_input)
        pot_collector_number = re.findall(r'\b\d+\b', user_input)
    
            # Convert collector numbers to integers to remove leading zeros
        print(pot_collector_number)
        # print(type(pot_collector_numbers[0]))
        print(pot_sets)
        
        # int_collector_numbers = [int(collector_number) for collector_number in pot_collector_numbers]
        # print(int_collector_numbers)
        
        # # Find the smallest collector number
        # smallest_collector_number = min(int_collector_numbers)
        # Convert it back to a string if needed
        # smallest_collector_number_str = str(int_collector_numbers)
    
        for card in scryfall_file:
            for pot_set in pot_sets:
                    if card["set"] == pot_set.lower() and card["collector_number"] == pot_collector_number:
                        mycard = card
                        print(mycard["name"])
                        return card
        return None
    
    except ValueError:
        return None
    except IndexError:
        return None

def user_cardname_confirmation(filename, card_infos, card_data, card, scryfall_file, mtg_ocr_config, default_action=None):
    """
    Displays a user confirmation dialog and returns the selected action.
    """
    
    display_image(card_infos["name"],card)
    valid_choices = ['Y','F', 'P', 'U', 'N', 'R', 'X', 'W']


    if default_action:
        # If a default action is provided, execute it and return
        default_action(filename, card_infos)
        return
   


    while True:
        
        colorama.init()
        
        red_title = f"The file {filename} was identified as " #  colorama.Fore.RED + "{card_infos['name']} ccn {card_infos['collector_number']} " + colorama.Fore.RESET + " from {card_infos['set']}. Is this correct?"
        # red_title = colorama.Fore.RED + title + colorama.Fore.RESET
        # # 
       
        
        print(red_title)        
        print("[Y]es - save infos in identified_DATETIME.txt")
        print("[F] yes and save it with finish foil identified_DATETIME.txt")
        print("[P] yes and save it with status:Proxied")
        print("[U]  move filename to undidentified images to to analyse it again")
        print("[N] No and scrap image, filename will NOT be moved to undidentified_DATETIME.txt")
        print("[R]ois - define the rois again and move image to unitdentied to analyse it again")
        print("[W]rite current results to identified_DATETIME.txt and unidentified_DATETIME.txt in", get_path(PathType.RESULTS))
        print("[X] exit program")
        print("No, type UI to identify card")

        # Get user input
        choice = input("Enter your choice: ").upper()

        #
        if len(choice) > 5:
            new_card =  checkif_scryfall_file_contains_UI(choice, filename, card_infos, card_data, card, scryfall_file, mtg_ocr_config, default_action)
            if new_card != None:
                card_data = user_cardname_confirmation(filename, card_infos, card_data, card, scryfall_file, mtg_ocr_config, default_action)
                return card_data
        
        if choice in valid_choices:
            break
        else:
            print("Invalid choice. Please enter a valid option.")

    # Define actions based on user choices
    actions = {
        'Y': save_infos,
        'F': save_infos_foil,
        'P': save_proxied,
        'U': move_to_unidentified,
        'N': scrap_image,
        'R': define_rois,
        'X': exit_program,
        'W': write_results_files
    }

    # Perform the selected action
    updated_card_data = actions[choice](filename, card_infos, card_data, card, scryfall_file, mtg_ocr_config, default_action=None)
    

    return updated_card_data



def process_images(all_images, card_data, mtg_ocr_config,scryfall_file, verbose):
    for filename in all_images:
    

        path = get_path(PathType.RAW_IMAGE,filename)
   
        card, error = extract_card(path ,verbose)
        if error: 
            print(error)
            card_data["unidentified_cards"].append(filename)
        
        
        if error is None:
            print(path)
            filename = os.path.basename(path)
            print(filename)
            create_rois_from_filename(filename, mtg_ocr_config, card, verbose)
            cardnames = return_cardname_from_ROI(filename, scryfall_file, verbose)
            # display_cardname(cardnames)

        
            if cardnames is not None:
               updated_card_data = user_cardname_confirmation(filename, cardnames[0], card_data, card, scryfall_file, mtg_ocr_config)
               card_data = updated_card_data
               print(card_data)
        else:
            continue
    
    return card_data

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
    cv2.destroyAllWindows()
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
    scryfall_file = mtg_ocr_config.open_scryfall_file(verbose )
  
    
    card_data = {"identified_cards": [], "unidentified_cards": []}

        
        
    while len(all_images) > 0:
        card_data = process_images(all_images, card_data, mtg_ocr_config,scryfall_file, verbose)
        card_data["identified_cards"].append(card_data["unidentified_cards"])
        all_images = card_data["unidentified_cards"]
        card_data["unidentified_cards"] = []
        print(f"The list of unidentified cards contains {len(card_data['unidentified_cards'])} elements.")
        print("Now redo the unidentified cards again.")

        
    write_results_to_file(card_data["identified_cards"],"identified_cards")
    write_results_files(filename, card_infos, card_data, card, scryfall_file, mtg_ocr_config, default_action=None)
       


if __name__ == "__main__":

    cardnames = main_Card_Identification()
  


