# -*- coding: utf-8 -*-
"""
main_Card_Identification.py
Created on 08.01.2024

author: Felix Scope
"""


import cv2
import time
import os


from img_from_adb import transfer_images_from_device
from card_extraction import (extract_card)
from process_card import (create_rois_from_filename)
from process_rois import (return_cardname_from_ROI)
from configuration_handler import MtGOCRData
from path_manager import (get_path, PathType,return_folder_image_contents)
from save_results import (write_results_to_txt, write_results_to_csv)
from copy_img_to_data import (select_and_copy_images_to_data,move_content_to_subfolders)
from user_dialog_cardname import user_cardname_confirmation

# from src.card_identificationimg_from_adb import transfer_images_from_device
# from src.card_identificationcard_extraction import (extract_card)
# from src.card_identificationprocess_card import (create_rois_from_filename)
# from src.card_identificationprocess_rois import (return_cardname_from_ROI)
# from src.card_identificationconfiguration_handler import MtGOCRData
# from src.card_identificationpath_manager import (get_path, PathType,return_folder_image_contents)
# from src.card_identificationsave_results import (write_results_to_txt, write_results_to_csv)
# from src.card_identificationcopy_img_to_data import (select_and_copy_images_to_data,move_content_to_subfolders)
# from src.card_identificationuser_dialog_cardname import user_cardname_confirmation


def main_Card_Identification(mode:str = None, verbose =None):
    """

    Parameters
    ----------
    mode : str, The mode how to start the program. Default is "quickstart"
    
 `quickstart` Select the folder where the card images are present. The images
         are safed to `~/git/MtG-OCR/data/Card_Identification/raw_IMGs`.
         All already present images will be moved to subfolder with the
         current DATETIME. Only the selected cards will be processed.
 `all files`: The images must be safed to 
         `~/git/MtG-OCR/data/Card_Identification/raw_IMGs` beforehand. 
         Then the contents of the selected folder is processed within 
         the directory (`~/git/MtG-OCR/data/Card_Identification/raw_IMGs`).
         All these images are processed. 
  `adb`: At program start all images from the folder `MTG-OCR` on the connected
          android device  are downloaed and transfered _via_ adb to 
          ~/git/MtG-OCR/data/Card_Identification/raw_IMGs`. All images from the
          android device are processed. 
  `adb-live`: Like adb, but the image contents of the MtG-OCR folder are 
          downloaed continuously and only the newest image is processed. After 
          each processed card a new image needs to be taken. This mode is 
          suited for live analysis.
        
    Returns
    ----------
    None but writes 3 files. 

* `results_DATETIME.txt`: identified card as a list of 
        [scryfall data](https://scryfall.com/docs/api/cards) 
        `[["filename1.jpg",{dict of scryfall_data of filename1}]]`
* `identified_cards_DATETIME.txt`:  a list of filename the correspondig list  
        `[["filename1.jpg",[name,CMC,Type,Color,Set,Collector Number,Rarity,
        Color Category,status,Finish,maybeboard,image URL,image Back URL,tags,
        Notes,MTGO ID]]` 
* `unidentified_cards_DATETIME.txt`: a list of filenames which could not be 
        identified `[["filename1.jpg"]]`
* `CubeCobraCSV.csv`: Created from `identified_cards_DATETIME.txt`. This `.csv`
         file can be exported manually to [cubecobra](www.cubecobra.com) to 
         exchange ones cube.
    """
    cv2.destroyAllWindows()
    if verbose is None:
        verbose = 1

    if mode is None:
        mode = "quickstart"

    # Initialise working directory
    if mode != "all_images":
        for myPathType in [PathType.RAW_IMAGE, PathType.PROCESSED_ROI,PathType.FINAL_ROI, PathType.RESULTS]:
            path_to_directory = get_path(myPathType)
            move_content_to_subfolders(path_to_directory)
    else:
        for myPathType in [PathType.PROCESSED_ROI,PathType.FINAL_ROI, PathType.RESULTS]:
            path_to_directory = get_path(myPathType)
            move_content_to_subfolders(path_to_directory)
        
        
    if mode == "quickstart":
        select_and_copy_images_to_data()
        all_images = return_folder_image_contents(get_path(PathType.RAW_IMAGE))
        
    elif mode == "adb":
        transfer_images_from_device(source_folder="MTG-OCR")
        all_images = return_folder_image_contents(get_path(PathType.RAW_IMAGE))

    elif mode == "all_images":
        all_images = return_folder_image_contents(get_path(PathType.RAW_IMAGE))
        if all_images ==[]:
            return None
        
    elif mode == "adb-live":
        filename = get_newest_image(get_path(PathType.RAW_IMAGE))
        source_folder= "MTG-OCR"
        destination_folder = get_path(PathType.RAW_IMAGE)
        transfer_images_from_device(source_folder, destination_folder, verbose = 2)
  

    if verbose > 0: 
        print("Main Func Of main_MtG-Card_Identification")
        print("mode: ", mode)

    mtg_ocr_config = MtGOCRData()
    scryfall_file = mtg_ocr_config.open_scryfall_file(verbose )
  
    card_data = {"identified_cards": [], "unidentified_cards": [], "results": []}

    
    if mode == "adb-live":
        while True:
          # Transfer images from the device
          transfer_images_from_device(source_folder, destination_folder, verbose = 0)
          # Get the newest image
          while True:
               filename_new = get_newest_image(destination_folder)
               if filename_new is not None:
                   break
               time.sleep(1)
               # Process the image with card extraction
               if filename_new != filename:
                   card_data =  process_images(filename, card_data, mtg_ocr_config,scryfall_file, verbose)
                   filename_new = filename
               else:
                   print(f"File '{filename}' does not exist. Skipping card extraction.")
        
    else:
        
        while len(all_images) > 0:
            for filename in all_images:
                card_data =  process_images(filename, card_data, mtg_ocr_config,scryfall_file, verbose)
            card_data = update_image_list(card_data)
            if verbose >1:
                print("unid", card_data["unidentified_cards"])
                print(card_data)
            all_images = card_data["unidentified_cards"]
            if verbose >1:
                print(f"The list of unidentified cards contains {len(card_data['unidentified_cards'])} elements.")
           
            card_data["unidentified_cards"] = []
            if verbose > 2: print(all_images)
            if len(all_images) > 0: print("Now redo the unidentified cards again.")


    path_to_identified_cards = write_results_to_txt(card_data["identified_cards"],"identified_cards")
    write_results_to_txt(card_data["unidentified_cards"],"unidentified_cards")
    write_results_to_txt(card_data["results"],"results")
    write_results_to_csv(path_to_identified_cards)
    
    cv2.destroyAllWindows()
    
    

def process_images(filename, card_data, mtg_ocr_config,scryfall_file, verbose):
        path = get_path(PathType.RAW_IMAGE,filename)
        card, error = extract_card(path ,verbose=0)
        if error or card is None: 
            print(error)
            card_data["unidentified_cards"].append(filename)
        
        if error is None:
            if verbose >2 : print("path in process_images:", path)
            filename = os.path.basename(path)
            if verbose >1: print("filename: ", filename)
            
            create_rois_from_filename(filename, mtg_ocr_config, card, verbose)
            cardnames = return_cardname_from_ROI(filename, scryfall_file, verbose)
            # display_cardname(cardnames)

            if cardnames is not None:
               updated_card_data = user_cardname_confirmation(filename, cardnames[0], card_data, card, scryfall_file, mtg_ocr_config, verbose)
               card_data = updated_card_data
               if verbose > 3:
                   print(card_data)
     
        return card_data



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
    newest_image STR
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


def update_image_list(card_data):
    identified_names = [item[0] for item in card_data["identified_cards"]]
    card_data["unidentified_cards"] = [name for name in card_data["unidentified_cards"] if name not in identified_names]

    return card_data


if __name__ == "__main__":

    # cardnames = main_Card_Identification('adb')
    verbose = 3
    cardnames = main_Card_Identification('all_images', verbose)
    # cardnames = main_Card_Identification('adb')
    # main_Card_Identification('quickstart', verbose)
    # cardnames = main_Card_Identification('adb-live')



