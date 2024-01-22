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


from src.Card_Identification.img_from_adb import transfer_images_from_device
from src.Card_Identification.card_extraction import (extract_card, display_image)
from src.Card_Identification.process_card import (create_rois_from_filename)
from src.Card_Identification.process_rois import (return_cardname_from_ROI, display_cardname, delete_duplicate_ROIs)
from src.Card_Identification.configuration_handler import MtGOCRData
from src.Card_Identification.path_manager import (get_path, PathType,return_folder_image_contents)
from src.Card_Identification.save_results import (write_results_to_file)
from src.Card_Identification.copy_img_to_data import (select_and_copy_images_to_data,move_content_to_subfolders)
from src.Card_Identification.save_results import write_results_to_file
from src.Card_Identification.user_dialog_cardname import (user_cardname_confirmation)



def process_images(all_images, card_data, mtg_ocr_config,scryfall_file, verbose):
    for filename in all_images:
    
        path = get_path(PathType.RAW_IMAGE,filename)
   
        card, error = extract_card(path ,verbose)
        if error or card is None: 
            print(error)
            card_data["unidentified_cards"].append(filename)
        
        
        if error is None:
            if verbose >2 : print("path in process_images:", path)
            filename = os.path.basename(path)
            print("filename: ", filename)
            
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

def main_Card_Identification(mode:str = None, verbose = 2):
    """

    Parameters
    ----------
    mode : str, optional
    
        quickstart: A file dialog asks the user to select a folder 
        adb:The files are imported automatically from MtG-OCR directory of phone
            enable 'adb' debugging 
        all_images: all images are checked wihtin working directory
        
        DESCRIPTION. The default is None.

    Returns
    -------
    cardnames : TYPE
        DESCRIPTION.

    """
    cv2.destroyAllWindows()
    
    # initizalise directoreis
    for myPathType in [PathType.RAW_IMAGE, PathType.PROCESSED_ROI,PathType.FINAL_ROI, PathType.RESULTS]:
        path_to_directory = get_path(myPathType)
        move_content_to_subfolders(path_to_directory)
        
        
    if mode is None:
        mode = "quickstart"

    if mode == "quickstart":
        select_and_copy_images_to_data()
        all_images = return_folder_image_contents(get_path(PathType.RAW_IMAGE))
        
    elif mode == "adb":
        transfer_images_from_device(source_folder="MTG-OCR")
        all_images = return_folder_image_contents(get_path(PathType.RAW_IMAGE))

    elif mode == "all_images":
        all_images = return_folder_image_contents(get_path(PathType.RAW_IMAGE))

        
    # main_Card_Identification()
    print("Main Func Of main_MtG-Card_Identification")
   


    mtg_ocr_config = MtGOCRData()
    scryfall_file = mtg_ocr_config.open_scryfall_file(verbose )
  
    card_data = {"identified_cards": [], "unidentified_cards": []}
        
    while len(all_images) > 0:
        card_data = process_images(all_images, card_data, mtg_ocr_config,scryfall_file, verbose)
        card_data["identified_cards"].append(card_data["unidentified_cards"])
        all_images = card_data["unidentified_cards"]
        print(f"The list of unidentified cards contains {len(card_data['unidentified_cards'])} elements.")
       
        card_data["unidentified_cards"] = []
        if len(all_images) > 0: print("Now redo the unidentified cards again.")

    write_results_to_file(card_data["identified_cards"],"identified_cards")
    cv2.destroyAllWindows()
       


if __name__ == "__main__":

    # cardnames = main_Card_Identification('adb')
    verbose = 0
    cardnames = main_Card_Identification('all_images', verbose)
    # cardnames = main_Card_Identification('adb')

