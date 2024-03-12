# -*- coding: utf-8 -*-
"""
Created on Fri Dec 15 18:39:31 2023

@author: Felix Scope

I want to identify the name of mtg card names with a python fucntion. 
Step 1: Name Comparison
Load Scryfall Data:

Load the Scryfall file containing card names into a Python list of dictionaries.
Name Comparison:

Implement a function that takes the card name ROI and compares it against the list of card names using Levenshtein distance or another suitable similarity metric.
Return the matched card name.
Step 2: UI Information Extraction
Extract Set Code:

Implement a function to extract the three-letter set code from the UI ROI.
Extract Collector Number and Set Size:

Create a function to extract the collector number and maximum set size (if available) from the UI ROI.
Set Code and Collector Number Comparison:

Use the extracted set code and collector number to identify the card by cross-referencing with the Scryfall dataset.
Step 3: Combine Information
Combine the results obtained from the name comparison and UI extraction to verify the card's identity.
Step 4: Expansion Symbol Identification


Not yet implemented:
Load Expansion Symbols:

Load the expansion symbols stored as .svg images in the /setsymbols directory.
Symbol Comparison:

Compare the expansion symbol of filename_exp_version.jpg with the symbols in the /setsymbols directory.
Find the closest matching symbols.

Use appropriate image processing libraries in Python (like OpenCV or PIL) to extract ROIs.
Levenshtein distance was implemented for name comparison.
"""

import pytesseract
import cv2
from Levenshtein import distance as levenshtein_distance
import os
import re
import json
import filecmp
from card_extraction import display_image
from process_card import create_rois_from_filename
from card_extraction import extract_card
from configuration_handler import MtGOCRData
from path_manager import (get_path, return_folder_contents, PathType)


def return_cardname_from_ROI(filename, scryfall_all_data, verbose = 0):
    """
    main function of this file
    this function accepts the roi location and the rois provided by process_rois.py

    calls find_cardname_byname()
    tries to get the cardname by analysing the name of the card
    
    
    calls find_cardname_byUI()
    tries to get the cardname and expansion by analysing UI
    Parameters
    ----------
    filename : STR
        DESCRIPTION.
    scryfall_all_data : list (.json opened datafile of scryfall bulk data
                              https://scryfall.com/docs/api/bulk-data)
                        STR   name of bulk data file.json file
        DESCRIPTION.
    verbose : INT, optional
        if 1 file paths of the rois are openend. The default is 0.
    roi_directory : STR, optional
        the relative directory the roi_directory is located at
        DESCRIPTION. The default is 'ROIs'.

    Returns
    -------
    cardname : tuple ('cardname','{scryfall data}')
    
        important scryfall_ddata keys:
        'colours' list
        'foil' BOOL 
        'name'
        'set' 
        
        
    name,CMC,Type,Color,Set,Collector Number,Rarity,Color Category,status,Finish,maybeboard,image URL,image Back URL,tags,Notes,MTGO ID

    """
     # Check if scryfall_all_data is a list or a string
    if isinstance(scryfall_all_data, list):
       pass
    elif isinstance(scryfall_all_data, str):
        # Open the JSON file
        with open(scryfall_all_data, 'r', encoding='utf-8') as file:
            scryfall_all_data = json.load(file)
    else:
        print("scryfall_all_data must be a list or a string (file path).")
        
    # check if filename is with .jpg or without
    
    if filename.endswith(".jpg"): filename = filename.strip(".jpg")
       
  
    
    # collect all potential (pot) collectornumbers, sets, rarities, cardnames
    pot_collectornumbers = []
    pot_sets = []
    pot_rarities = []
    pot_cardnames = []


    # List all roi files in the directory
    roi_files = return_folder_contents(get_path(PathType.PROCESSED_ROI))
    if verbose >=3:
        print(get_path(PathType.PROCESSED_ROI,verbose = 1))

    
    # Loop through each file
    for roi_file in roi_files:
        # Assuming UI ROIs have this naming convention
        if roi_file.startswith(f"{filename}_ui"): 
            
            file_path = get_path(PathType.PROCESSED_ROI,roi_file)
            if verbose > 2:
                print(file_path)
            # Read the image
            ui_roi = cv2.imread(file_path)
    
      
            # roi_info = preprocess_roi(ui_roi,verbose=0)
            roi_info = ui_roi

            pot_collectornumber, pot_set, pot_rarity = extract_set_info(roi_info)
            # pot_collectornumber, pot_set, pot_rarity = extract_set_info(ui_roi)
            if verbose > 2:
                print("ccn",pot_collectornumber, "set:", pot_set, "pot_rarity:", pot_rarity)
       
            if pot_collectornumber != []:
                pot_collectornumbers.extend(pot_collectornumber)
            if pot_set != []:
                pot_sets.extend(pot_set)
            if pot_rarity != []:
                pot_rarities.extend(pot_rarity)
                
        if roi_file.startswith(f"{filename}_name"): 
            file_path = get_path(PathType.PROCESSED_ROI, roi_file)
            if verbose > 2:
                print("filepath path", file_path)
           
            # Read the image
            name_roi = cv2.imread(file_path)
            # Call preprocess_roi function to get relevant information
            # and Apply extract_set_code function
            # roi_info = preprocess_roi(name_roi,verbose)
            roi_info = name_roi
            potential_letters = MtGOCRData().get_Mtg_letters()
            roi_info = name_roi
            pot_cardname = [''.join(extract_name_info(roi_info, potential_letters, verbose))]
            if verbose > 2: print(pot_cardname)
           
            # pot_cardname = [''.join(extract_name_info(roi_info, verbose))]

            if pot_cardname != []:
                pot_cardnames.extend(pot_cardname)
    if verbose > 1: print("pot:cardnames: ",pot_cardnames)               
    # print("return_cardname_from_ROI \n find_cardname_byname:", pot_cardnameS)
    
    pot_cardnames = [name.lower() for name in pot_cardnames]

    lists_to_update = [pot_sets, pot_cardnames, pot_collectornumbers, pot_rarities]
    
    # Remove specific characters
    updated_lists_to_update = remove_specific_characters(lists_to_update)

    # Ensure each sublist contains only unique elements
    for i in range(len(updated_lists_to_update)):
        if isinstance(updated_lists_to_update[i], list):
            updated_lists_to_update[i] = list(set(updated_lists_to_update[i]))


    pot_sets, pot_cardnames, pot_collectornumbers, pot_rarities = updated_lists_to_update
      
    cardname_by_name = find_cardname_byname(pot_cardnames, scryfall_all_data)

    if verbose >0 :
        print("cardname_by_name", cardname_by_name, "pot_sets", pot_sets, "pot_rarities", pot_rarities, "pot_collectornumbers", pot_collectornumbers)


    cardname = find_card_by_infos(pot_collectornumbers, pot_sets, pot_rarities, cardname_by_name, scryfall_all_data, verbose=0)
    
    return cardname

def remove_specific_characters(list_to_update):
    updated_list = []
    for item in list_to_update:
        if isinstance(item, list):
            # Recursively call remove_specific_characters() for sub-lists
            updated_list.append(remove_specific_characters(item))
        else:
            # Apply remove_specific_characters() to individual strings
            updated_list.append(re.sub(r"['\\/\~\n'>}]", '', str(item)))
    return updated_list


def find_card_by_infos(pot_collectornumbers, pot_sets, pot_rarities, pot_cardnames, scryfall_all_data, verbose=0):
    """
        Identification of the cardname by the UI unique information provided by
        OCR data.
        
    
    Input Parameters:
    
    pot_collector_numbers: List of potential collector numbers for the card.
    pot_sets: List of potential set names for the card.
    pot_rarities: List of potential rarities for the card.
    pot_cardnames: list of potential cardnames
    scryfall_all_data: Scryfall dataset containing card information.
    verbose: Parameter controlling the verbosity of print statements for debugging purposes.
    Process Overview:
    
    It iterates through the provided collector numbers, sets, and rarities.
    For each combination of collector number, set, and rarity:
    It checks against each card in the Scryfall dataset.
    If the collector number and set name match a card in the dataset, it checks the rarity.
    If the rarity matches with the specified conditions (e.g., 'M' for mythic, 'C' for common, 'R' for rare, 'T' for token), it appends the card's name and card data (Scryfall information) to the card_names list.
    If the rarity is 'T' (token), it includes cards with a rarity of 'special' or a set name starting with 't'.
    Output:
    """
    if verbose > 3:
        print("pot_sets= ",pot_sets)
        print("pot_collectornumbers= ", pot_collectornumbers)
        print("pot_rariteis= ",pot_rarities)
        print("pot_cardnames= ",pot_cardnames)
        
    updated_pot_sets=pot_sets.copy()
    updated_pot_rarities = []
    for rarity in pot_rarities:
        if rarity == "C":
            updated_pot_rarities.append("common")
        elif rarity == "T":
            updated_pot_rarities.append("token")
            for pot_set in pot_sets:
                if len(pot_set)==3:
                    pot_set = 't' + pot_set.lower()
                    if verbose > 2: print(pot_set)
                    
                    updated_pot_sets.append(pot_set)
        elif rarity == "U":
            updated_pot_rarities.append("uncommon")
        elif rarity == "M":
            updated_pot_rarities.append("mythic")

        # Regular expression pattern to check if a string contains any letters
        # this kicks out any promo or foreign language cards
        contains_letters_pattern = re.compile('[a-zA-Z]')
        
        # Assuming 'name' and 'cards' are defined somewhere
        possible_cards = []
        for name in pot_cardnames:
            for card in scryfall_all_data:
                if card["name"] == name and not contains_letters_pattern.search(card["collector_number"]):
                    possible_cards.append(card)
               

        pot_collectornumbers = [str(num).lstrip('0') for num in pot_collectornumbers]
        print("modified ccn",pot_collectornumbers)
        pot_collectornumbers = list(set(pot_collectornumbers))
        
        
        unique_combinations = set()
        unique_cards = []

        for card in possible_cards:
            # Create a tuple containing the values of "name", "set", and "collector_number"
            card_tuple = (card["name"], card["set"], card["collector_number"])
            
            # Check if the combination is not already in unique_combinations
            if card_tuple not in unique_combinations:
                # Add the combination to unique_combinations set
                unique_combinations.add(card_tuple)
                # Add the card to unique_cards
                unique_cards.append(card)
                
      
        
        for card in unique_cards:
            best_name_dist = float("inf")
            best_set_dist = float("inf")
            best_collector_number_dist = float("inf")
      
            for pot_cardname in pot_cardnames:
                name_dist = levenshtein_distance(card["name"].lower(), pot_cardname.lower())
                if name_dist < best_name_dist:
                    best_name_dist = name_dist
                    # best_name = pot_cardname
            for pot_set in pot_sets:
                set_dist = levenshtein_distance(card["set"].lower(), pot_set.lower())
                if set_dist < best_set_dist:
                    best_set_dist = set_dist
                    # best_set = pot_set
      
            if pot_collectornumbers:
                for pot_collector_number in pot_collectornumbers:
                    collector_number_dist = levenshtein_distance(card["collector_number"].lower(), pot_collector_number.lower())
                    if collector_number_dist < best_collector_number_dist:
                        best_collector_number_dist = collector_number_dist
                                               # Update the score for the card
                        
            card["score"] = (best_name_dist + best_set_dist) + best_collector_number_dist
                        # Sort the possible cards by their score
        sorted_cards = sorted(unique_cards, key=lambda card: card["score"])
        best_match = sorted_cards[0]
        # Return the best matching card
        return best_match, sorted_cards




def extract_set_info(set_code_roi,verbose = 0):
    gray = cv2.cvtColor(set_code_roi, cv2.COLOR_BGR2GRAY)
    gray = cv2.bitwise_not(gray)
    if verbose >2: 
        display_image("gray",gray)
        cv2.waitKey(1)

    # Perform OCR to extract text from the set code ROI
    custom_config = r'--oem 3 --psm 6'  # Adjust as needed

    set_code_text = pytesseract.image_to_string(gray, config=custom_config)
    # set_code_text = re.sub(r'[^A-Za-z0-9\s]', '', set_code_text1)

    # Extracting numbers using regular expression
    pot_collecturnumber = re.findall(r'\b\d{1,4}\b', set_code_text)

    # Extracting 3-letter words using regular expression
    # pot_set = re.findall(r'\b[a-zA-Z123465789]{3}\b', set_code_text)
    pot_set = re.findall(r'[a-zA-Z0-9]{3}', re.sub(r'[^A-Za-z0-9]', '', set_code_text))

    # Identifying rarity (assuming rarity is denoted by single letters)
    pot_rarity = re.findall(r'[MCTRU]', set_code_text)
    
    if verbose >0:
        print("extract_set_info: /n","ccn" ,pot_collecturnumber, "set:", pot_set, "pot_rarity:", 
              pot_rarity)
        

    if verbose >= 2:
        print("found text:", set_code_text) 
    return pot_collecturnumber, pot_set, pot_rarity


def extract_name_info(contour_name_roi, pot_letters, verbose = 0):
    """
    
    extracts the name info via OCR tesseract from a contour name with pre
    processing

    Parameters
    ----------
    contour_name_roi : cv2 image
        cv2 iamge snippet of card name to be analysed
    pot_letters : list of strings, utf8 encoded characters
        potential letters to be found
    verbose : int, optional
        DESCRIPTION. The default is 0.

    Returns
    -------
    pot_name : list of strings
        list of cardnames found.

    """
    
    image = contour_name_roi
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # blur = cv2.GaussianBlur(gray, (7,7), 0)
    # thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    # tresh_bw = cv2.bitwise_not(gray)

    if verbose >4: 
        cv2.imshow('Preprocessed Name Info', gray)
        cv2.waitKey(0)
        cv2.destroyWindow('Preprocessed Name Info')
       
    # Encode the pot_letters string as UTF-8 bytes
    utf8_pot_letters = pot_letters.encode('utf-8')

    # Prepare the custom configuration for Tesseract OCR using encoded bytes
    custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=' + \
        utf8_pot_letters.decode('utf-8')
    
    # custom_config = r'-c tessedit_char_whitelist=' + \
    #     utf8_pot_letters.decode('utf-8')
        
    # Escape special characters in the config argument
    escaped_chars = ['"', "'", ',', '=', '_']
    for char in escaped_chars:
        custom_config = custom_config.replace(char, '\\' + char)

    # Perform OCR and extract text using the configured whitelist
    # set_code_text = pytesseract.image_to_string(gray, config=custom_config)
    set_code_text_default = pytesseract.image_to_string(gray, lang='eng', config='--psm 6 --oem 3')
    # set_code_text_default2 = pytesseract.image_to_string(thresh)

    if verbose >2:
            print("extract_name_info") 
            # print("custom confing tesseract tresh:", set_code_text_default2)
            print("default confing tesseract (currently used):", set_code_text_default)


    set_code_text_default  = ''.join(char for char in set_code_text_default if char != ' ')
    if verbose >2: print(set_code_text_default)
    # Use a character class [] to find any character from pot_letters in set_code_text_default
    # pot_name_list = re.findall('[' + re.escape(utf8_pot_letters) + ']', set_code_text_default)

    # pot_name = ''.join(pot_name_list)
    if verbose >2: print(set_code_text_default)
    # Join the list of characters into a single string
    # pot_name = ''.join(set_code_text_default)
    if verbose >2: print("potential name", set_code_text_default)

    return set_code_text_default


def compare_name(card_name_roi, scryfall_data):
    best_match = None
    min_distance = float('inf')
    
    for card_data in scryfall_data:
        name = card_data['name']
        distance = levenshtein_distance(card_name_roi, name)
        
        if distance < min_distance:
            min_distance = distance
            best_match = card_data
    
    return best_match

def mtg_letters(scryfall_data, verbose =0 ):
   
    # Assuming 'scryfall_data' contains the list of dicts with 'name' key for card names
    card_names = [card['name'] for card in scryfall_data]
    
    # Joining all card names into a single string
    all_card_names = ' '.join(card_names)
    
    # Finding unique letters used in card names
    unique_letters = set(all_card_names)
    
    # Constructing the regular expression pattern to match these unique letters
    letters_pattern = f"[{''.join(unique_letters)}]"
    
    # Now you can use this pattern in re.findall to match these letters in text
    text = "Sample text containing MTG card letters"
    pot_set = re.findall(letters_pattern, text)
    if verbose >0:
        print(pot_set)



def find_cardname_byname(pot_cardnameS, scryfall_all_data, verbose = 1):
    """
   find the cardname by comparing with levenshtein to all of scryfall data
 

    Parameters
    ----------
    pot_cardnameS : list of strings ['Fury sliiver', 'FooD']
        potential cardnames
    scryfall_all_data : list of dicts
        scryfall data downloaded.

    Returns
    -------
    closest_matches : list of strings ['Fury Sliver', 'Food']
        the closest match for each given pot_cardname

    """
    closest_matches = []
    
    if verbose >2: print("potential cardnames:", pot_cardnameS)
    
    for potential_name in pot_cardnameS:
        if verbose >1: print(potential_name)
        min_distance = float('inf')
        best_match = None

        for card_data in scryfall_all_data:
            # Get the first name before '//'
            name = card_data['name'].split('//')[0].strip() 
            # Convert both to lowercase for case-insensitive comparison
            distance = levenshtein_distance(name.lower(), potential_name.lower())

            if distance < min_distance:
                min_distance = distance
                best_match = card_data

        closest_matches.append(best_match['name'])
        
    if verbose >1: print("closest_matches:", closest_matches)
       
    return closest_matches



def display_cardname(cardname):
    if cardname is not None:
        print(cardname[0]["name"], "from ",cardname[0]['set'].upper())
    else:
        print("Cardname was not identified.")

    
def str_cardname(tuple_name_and_infos):
    if tuple_name_and_infos[0] !='' and tuple_name_and_infos[1] !='':
        a= str(tuple_name_and_infos[0], "from ",tuple_name_and_infos[1]['set'])
    elif tuple_name_and_infos[0] !='' and tuple_name_and_infos[1] =='':
        a=str(tuple_name_and_infos[0], "from a non defined set.")
    else:
        a=str("Ui was not read, only the cardname not the expansion was found")
    return a   
    

def rename_and_move_ROIs(filename, tuple_name_and_infos, save_directory='Identified_ROIS', roi_directory='ROIs', verbose=0):
    # Check if the filename ends with ".jpg" and remove it if present
    if filename.endswith('.jpg'):
        filename = filename[:-4]  # Remove the last 4 characters (i.e., '.jpg')
        
     # Get the current working directory
    current_directory = os.getcwd()
    # Define the directory containing UI ROIs
    roi_directory = os.path.join(current_directory, roi_directory)
    # Define the save directory for renamed files
    save_directory = os.path.join(roi_directory, save_directory)
    
    # Create the save_directory if it doesn't exist
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)
    
    # cardname
    name = tuple_name_and_infos[1]['name']
    # expansion
    expansion = tuple_name_and_infos[1]['set']
    collectornumber = tuple_name_and_infos[1]['collector_number']
    # List all ROI files in the directory
    roi_files = os.listdir(roi_directory)
    
    if verbose > 0:
        print("ROI files:", roi_files)
    
    # Loop through each file
    for roi_file in roi_files:
        # Check if the ROI file matches the specified filename pattern
        if roi_file.startswith(f"{filename}_"):
            # Split the filename into the cardname and the rest of the filename
            _, rest_of_filename = roi_file.split(f"{filename}_", 1)
                            
            # Construct the new filename
            new_filename = f"{name}_{expansion}_{collectornumber}_{rest_of_filename}"
            
            # Move the file to the save_directory with the new filename
            os.rename(os.path.join(roi_directory, roi_file), os.path.join(save_directory, new_filename))
            print(f"Renamed and moved {roi_file} to {os.path.join(save_directory, new_filename)}")

def delete_duplicate_ROIs(filename, verbose=0):
    
    if filename.endswith(".jpg"):
        filename = filename.strip(".jpg") 
    
    roi_directory = get_path(PathType.PROCESSED_ROI)

    roi_files = os.listdir(roi_directory)
    
    if verbose > 0:
        print("ROI files:", roi_files)
    
    # Group files by filename_mode
    grouped_files = {}
    for roi_file in roi_files:
        if roi_file.startswith(f"{filename}_"):
            filename_mode = roi_file.split('_')[1]
            if filename_mode not in grouped_files:
                grouped_files[filename_mode] = []
            grouped_files[filename_mode].append(roi_file)

    # Check for duplicates within each group based on file size
    for mode, files in grouped_files.items():
        file_sizes = {}
        for file in files:
            file_path = os.path.join(roi_directory, file)
            size = os.path.getsize(file_path)
            if size not in file_sizes:
                file_sizes[size] = []
            file_sizes[size].append(file_path)
        
        # Check for duplicates based on file size
        for same_size_files in file_sizes.values():
            if len(same_size_files) > 1:
                if verbose >0: print("Deleted duplicate file: ")
                for idx, file1 in enumerate(same_size_files):
                    for file2 in same_size_files[idx + 1:]:
                        # Check if files exist before comparing
                        if os.path.exists(file1) and os.path.exists(file2):
                            # Check if files have identical content
                            if filecmp.cmp(file1, file2):
                                # Delete the duplicate file
                                os.remove(file2)
                                if verbose > 0:
                                    print(f"{file2}")
                        


if __name__ == "__main__":
    

    mtg_ocr_config = MtGOCRData()
    potential_letters = mtg_ocr_config.get_Mtg_letters()
    scryfall_all_data= mtg_ocr_config.open_scryfall_file()
    
    verbose = 0
    # Define pytesseract location
    pytesseract.pytesseract.tesseract_cmd = \
    r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    #  Visage of Dread, LCI 
    filename = "1.jpg" 
  
    #goblin from TRGN 
    # filename = "2.jpg"
    # Food Token ELD
    filename = "3.jpg"
    path = get_path(PathType.TEST_RAW_IMAGE, filename)
    
    card, error = extract_card(path,verbose)
    
    if error != None:
        print("error:", error)
     
    mtg_ocr_config.set_relative_coordinates(card)
    create_rois_from_filename(filename, mtg_ocr_config, card, verbose = 2)


    delete_duplicate_ROIs(filename,verbose)
    cardname = return_cardname_from_ROI(filename, scryfall_all_data, verbose =2)
    display_cardname(cardname)
 

  
    # name = extract_name_info(img, potential_letters, verbose = 6)
    # print(name)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    
    # cardname_by_name ['Voldaren Epicure // Voldaren Epicure', 'Mirozel'] pot_sets ['teM', '3GV', 'cle', 'TIN', 'INA', 'CKO', 'AFA', 'NPe', 'Ca1', 'MAR', 'WEN', 'OWE', 'ART', '827', '182', '277', 'FAC', 'CVO', 'sie', 'KOV'] pot_rarities ['R', 'T', 'M', 'C'] pot_collectornumbers ['277', '182', '1827']
    # modified ccn ['277', '182', '1827']
            
    