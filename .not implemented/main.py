import pytesseract
import cv2
from configuration_handler import MtGOCRData, CubeCobraData
# import datetime
import time
import os
from img_from_adb import transfer_images_from_device
from card_extraction import extract_card
from process_card import create_rois_from_filename
from process_rois import (return_cardname_from_ROI, display_cardname)

from path_manager import get_path


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



        
"""
multiple modes are possible:
    
    mode: 
        mode == "adb" ... the iamges are loaded constantly from the android device
            to the working directory. adb must be isntalled. see img_from_adb.py
            
            == "all" ... all images from the specified folder are anlalysed. 
                and as long the program is running new images can be transferred
                to the folder to be analysed
            
    currently only all mode is implemented
"""
if __name__ == "__main__":
    
    # Check if tesseract is installed
    try:
        tesseract_cmd = pytesseract.pytesseract.get_tesseract_cmd()
        if tesseract_cmd is None:
            raise Exception("Tesseract executable not found")
        print("Tesseract executable found:", tesseract_cmd)
    except Exception as e:
        print("Error:", e)
        
    #  This does not work
    # # Get the Tesseract executable location
    # tesseract_cmd = pytesseract.pytesseract.get_tesseract_cmd()
    
    # # Update the Tesseract executable path
    # pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


    # load the parameters with MTGOCRData file handler
    mtg_ocr_data = MtGOCRData()
    # Directory within the working directory to process the files
    directory_path = mtg_ocr_data.get_img_directory()  
    directory_path = get_path("raw_image")

    # Define the mode of file aquisition
    # mode = "adb"
    mode = "all"
    cardnames = ""
    cardnames_foil = ""
    debug = False
    show = 0
    Running = True
    verbose = 0
    roi_text = None

    
    # Create a generator for processing unprocessed files
    file_generator = process_files(directory_path)
    timeout = 10
    start_time = time.time()

    # Define the mode of file aquisition
    while True:
        if mode == "adb":
            #  Get the newest image files from the android device
            transfer_images_from_device()
            img_name = get_newest_image() 
            card = extract_card(img_name,verbose)
        elif mode == "all":
            try:
                unprocessed_file = next(file_generator)
                card = extract_card(unprocessed_file,verbose)
            except StopIteration:
               print('No more files to process. Exiting program...')
               break
        
        try:
          
            if verbose >1:
                print(f"Processing file: {img_name}")
          
            
            try:
                if card is None:
                    print("Card is None")
                    continue
            except NameError:
                
                print("Card is not defined")
                continue

            create_rois_from_filename(card, mtg_ocr_data)
            cardname = return_cardname_from_ROI(img_name, mtg_ocr_data, verbose = 0)
            
            try:
                diplay_cardname(cadname[0])
            except NameError:
                pass
            
            start_time = time.time()  # Reset the timer on file processing
 
            
        except RuntimeError:
            print("No new files found, exiting program")
            break
        
        except StopIteration:
            print("StopIteration new files found, exiting program")
            break

        
                