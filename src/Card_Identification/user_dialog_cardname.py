# -*- coding: utf-8 -*-
"""
%(filename)
${file}
Created on %(date)s

author: Felix Scope
"""


import cv2
import datetime
import time
import os
from pathlib import Path
import json
import sys
import re
import colorama


from card_extraction import (extract_card, display_image)
from process_card import (create_rois_from_filename)
from configuration_handler import MtGOCRData
from path_manager import (get_path, PathType,return_folder_image_contents)
from save_results import (write_results_to_txt, write_results_to_csv)
from copy_img_to_data import (select_and_copy_images_to_data)


def user_cardname_confirmation(filename, card_infos, card_data, card, scryfall_file, mtg_ocr_config, verbose=1, default_action=None):
    """
    Displays a user confirmation dialog and returns the selected action.
    """
    if verbose > 0:
        display_image(card_infos["name"],card)
        cv2.waitKey(0)
    valid_choices = ['Y','F', 'P', 'U', 'N', 'R', 'X', 'W'] # and UI 


    if default_action:
        # If a default action is provided, execute it and return
        default_action(filename, card_infos)
        return

    while True:
        
        colorama.init()
        
        red_title = f"The file {filename} was identified as " + colorama.Fore.RED + f"{card_infos['name']} ccn {card_infos['collector_number']} " + colorama.Fore.RESET + f" from {card_infos['set'].upper()}. Is this correct?"
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
        print(red_title)
        # Get user input
        choice = input("Enter your choice: ").upper()
        
        if len(choice) > 4:
            new_card =  checkif_scryfall_file_contains_UI(choice, filename, card_infos, card_data, card, scryfall_file, mtg_ocr_config, default_action)
            if new_card != None:
                card_data = user_cardname_confirmation(filename, new_card, card_data, card, scryfall_file, mtg_ocr_config, verbose, default_action)
                return card_data
        
        if choice in valid_choices:
            break
        # else:
        #     print("Invalid choice. Please enter a valid option.")

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
    updated_card_data = actions[choice](filename, card_infos, card_data, card, scryfall_file, mtg_ocr_config, verbose, default_action=None)
    
    cv2.destroyAllWindows()
    return updated_card_data

def save_card_infos(card_infos, card, filename, finish=None, status=None, maybeboard=None, image_url=None, image_back_url=None, tags=None, notes=None):
# the scryfall.csv logic is: name,CMC,Type,Color,Set,Collector Number,Rarity,Color Category,status,Finish,maybeboard,image URL,image Back URL,tags,Notes,MTGO ID

    # print("card_infos = ", card_infos)
    if finish is None:
        finish = ""
    if status is None:
        status = "Owned"
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
    
 
 

    cmc = int(card_infos["cmc"])
    name = '"' + card_infos["name"] +'"'
    type_line = '"' + card_infos["type_line"].replace('—', '-')  + '"'
    card_set = '"' + card_infos["set"] + '"'
    ccn = '"' + card_infos["collector_number"] + '"'

    color_id = "".join(card_infos["color_identity"])


    rarity =  card_infos["rarity"]
    
    if len(card_infos["color_identity"]) ==1:
        color_category = [color.lower() for color in card_infos["color_identity"]][0]
    else:
        color_category = "m"
  
    status = status
    finish = finish 
    maybeboard = ""
    image_url = ""
    image_Back_URL = ""
    tags = '"''"'
    Notes = '"''"'
    MTGO_ID =  card_infos["mtgo_id"]
    entry = (name, cmc, type_line, color_id, card_set, ccn, rarity, color_category, status, finish, maybeboard, image_url, tags, Notes, MTGO_ID)
    # entry =['"' + card_infos["name"]+'"', card_infos["cmc"], '"'+card_infos["type_line"]+'"', card_infos["color_identity"], '"'+card_infos["set"]+'"', card_infos["collector_number"], card_infos["rarity"],   [color.lower() for color in card_infos["color_identity"]],  status, finish, maybeboard, image_url, image_back_url, tags, notes, card_infos["mtgo_id"]] # Lowercase each element
    title = filename + "_" + card_infos["name"] + "_" + card_infos["collector_number"] + "_" + card_infos["set"] + "_finish: " + finish + "_status: " + status + ".jpg"
    path = get_path(PathType.RESULTS, title)
    cv2.imwrite(path, card)
    return entry

def save_infos(filename, card_infos, card_data, card, scryfall_file, mtg_ocr_config, verbose=1, default_action=None):
    if verbose >0: print(f"Save infos for {filename} in identified_DATETIME.txt")
    finish = ""
    status = "Owned"
    card_data["identified_cards"].append((filename, save_card_infos(card_infos, card, filename, finish=finish, status=status)))
    card_data["results"].append((filename, finish, status, card_infos))

    return card_data
    
def save_infos_foil(filename, card_infos, card_data, card, scryfall_file, mtg_ocr_config, verbose=1, default_action=None):
    if verbose >0: print(f"Save infos for {filename} with finish foil in identified_DATETIME.txt")
    finish = "Foil"
    status = "Owned"
    card_data["identified_cards"].append((filename, save_card_infos(card_infos, card, filename, finish=finish, status=status)))
    card_data["results"].append((filename, finish, status, card_infos))
    return card_data
def save_proxied(filename, card_infos, card_data, card, scryfall_file, mtg_ocr_config, verbose=1, default_action=None):
    if verbose >0: print(f"Save infos for {filename} with status Proxied")
    finish = ""
    status = "Proxied"
    card_data["identified_cards"].append((filename, save_card_infos(card_infos, card, filename, finish=finish, status=status)))
    card_data["results"].append((filename, finish, status, card_infos))
    return card_data
    
def move_to_unidentified(filename, card_infos, card_data, card, scryfall_file, mtg_ocr_config, verbose=1, default_action=None):
    if verbose >0: print(f"Move {filename} to undidentified_DATETIME.txt")
    card_data["unidentified_cards"].append(filename)
    return card_data
    
def scrap_image(filename, card_infos, card_data, card, scryfall_file, mtg_ocr_config, verbose=1, default_action=None):
    if verbose >0: print(f"Scrap image for {filename}. {filename} will NOT be moved to undidentified_DATETIME.txt")
    return card_data
    
def define_rois(filename, card_infos, card_data, card, scryfall_file, mtg_ocr_config, verbose=1, default_action=None):
    if verbose >0: print(f"Define ROIs for {filename} and start anew")
    mtg_ocr_config.set_relative_coordinates(card)
    move_to_unidentified(filename, card_infos, card_data, card, scryfall_file, mtg_ocr_config, verbose, default_action)
    return card_data

def write_results_files(filename, card_infos, card_data, card, scryfall_file, mtg_ocr_config, verbose=1, default_action=None):
    print("Write files chosen.")
    path_to_identified_cards = write_results_to_txt(card_data["identified_cards"],"identified_cards")
    write_results_to_txt(card_data["unidentified_cards"],"unidentified_cards")
    write_results_to_txt(card_data["results"],"results")
    write_results_to_csv(path_to_identified_cards)
    user_cardname_confirmation(filename, card_infos, card_data, card, scryfall_file, mtg_ocr_config, verbose, default_action)
    return card_data

def exit_program(filename, card_infos, card_data, card, scryfall_file, mtg_ocr_config, verbose=1, default_action=None):
    if verbose >0: print("Exiting the program.")
    cv2.destroyAllWindows()
    sys.exit()

def checkif_scryfall_file_contains_UI(user_input, filename, card_infos, card_data, card, scryfall_file, mtg_ocr_config, verbose = 0, default_action = None):
    """
    #  Check if the scryfall file contains 
    # Return True if the card is found, otherwise return False
    """
    try:
        user_input = str(user_input)
    
        pot_sets = re.findall(r'\b[A-Za-z0-9]{3,4}\b', user_input)
        pot_collector_number = re.findall(r'\b\d+\b', user_input)

        # Add two zeros to the left
        added_zeros = [number.rjust(len(number) + 2, '0') for number in pot_collector_number]
        
        # Remove two zeros from the left, and include variations without leading zeros
        removed_zeros = [number[1:] if number.startswith('0') else number for number in pot_collector_number]
        variations = [number for number in pot_collector_number if not number.startswith('0')]
        
        # Extend the original list with the results
        extended_pot_collector_number = pot_collector_number + added_zeros + removed_zeros + variations
        for card in scryfall_file:
            for pot_set in pot_sets:
                for pot_collector_number in extended_pot_collector_number:
                   if card["set"] == pot_set.lower() and card["collector_number"] == pot_collector_number:
                        return card
        return None
    
    except ValueError:
        return None
    except IndexError:
        return None
