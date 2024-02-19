# -*- coding: utf-8 -*-
"""
%(filename)
${file}
Created on %(date)s

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


finsihed =[]


mode = "adb-live"
i = 1
if mode == "adb-live":
     source_folder= "MTG-OCR"
     destination_folder = get_path(PathType.RAW_IMAGE)
     transfer_images_from_device(source_folder, destination_folder, verbose = 2)
     filename = None
        
        
if mode == "adb-live":
    last_processed_filename = "None"  # Initialize variable to keep track of the last processed filename
    while True:
        transfer_images_from_device(source_folder, destination_folder, verbose=2)
        time.sleep(1)

        # Get the newest image
        while True:
            print("last_processed_filename:", last_processed_filename)
            filename_new = get_newest_image(destination_folder)
            print("filename_new:", filename_new)
    
            if filename_new is None:
                break
            elif filename_new != last_processed_filename:
                print("card_data =  process_images(filename, card_data, mtg_ocr_config,scryfall_file, verbose)")
                i +=1
                last_processed_filename = filename_new
                transfer_images_from_device(source_folder, destination_folder, verbose=2)
                finsihed.append(filename_new)
            elif filename_new == last_processed_filename:
                print("sames")
                transfer_images_from_device(source_folder, destination_folder, verbose=2)

            else:
                time.sleep(1)  # Sleep if the same image is still the newest
            