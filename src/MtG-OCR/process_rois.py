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
from configuration_handler import MtGOCRData
from Levenshtein import distance as levenshtein_distance
import os
import re
from collections import Counter
import json
import filecmp
import numpy as np

def preprocess_roi(roi, verbose =2):
    """
    
    crops away the white part above the UI
    
    
    Parameters
    ----------
    roi : cv2 image
        DESCRIPTION.
    verbose : TYPE, optional
        DESCRIPTION. The default is 0.
    
    Returns
    -------
    TYPE
        DESCRIPTION.
    """
    
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (7,7), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    
    
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Find the largest contour
    largest_contour = max(contours, key=cv2.contourArea)
    
    # Create a mask for the largest contour
    mask_largest_contour = np.zeros_like(gray)
    cv2.drawContours(mask_largest_contour, [largest_contour], -1, 255, -1)
    
    # Bitwise AND operation to extract the area within the contour
    result = cv2.bitwise_and(roi, roi, mask=mask_largest_contour)
    
    # Find bounding rectangle of the largest contour
    x, y, w, h = cv2.boundingRect(largest_contour)
    
    # Crop the image excluding the black border
    cropped_image = result[y:y+h, x:x+w]
    
   
    if verbose >=2: 
        cv2.imshow('Cropped Image', cropped_image)
        cv2.imshow("Original Image", roi)
        cv2.imshow('Threshed Image', thresh)
    
        # Display the result
        cv2.waitKey(0)
        cv2.destroyWindow("Cropped Image")
    
        cv2.destroyAllWindows()
    
    return cropped_image



def extract_set_info(set_code_roi,verbose = 0):
    # Perform OCR to extract text from the set code ROI
    set_code_text1 = pytesseract.image_to_string(set_code_roi)
    set_code_text = re.sub(r'[^A-Za-z0-9\s]', '', set_code_text1)


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
        print("from: ", set_code_text1)
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
    blur = cv2.GaussianBlur(gray, (7,7), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    tresh_bw = cv2.bitwise_not(thresh)

    if verbose >=2: 
        cv2.imshow('Preprocessed Name Info', tresh_bw)
        cv2.waitKey(0)
        cv2.destroyWindow('Preprocessed Name Info')
       
    # Encode the pot_letters string as UTF-8 bytes
    utf8_pot_letters = pot_letters.encode('utf-8')

    # Prepare the custom configuration for Tesseract OCR using encoded bytes
    custom_config = r'--oem 3 --psm 5 -c tessedit_char_whitelist=' + \
        utf8_pot_letters.decode('utf-8')
    
    custom_config = r'-c tessedit_char_whitelist=' + \
        utf8_pot_letters.decode('utf-8')
        
    # Escape special characters in the config argument
    escaped_chars = ['"', "'", ',', '=', '_']
    for char in escaped_chars:
        custom_config = custom_config.replace(char, '\\' + char)

    # Perform OCR and extract text using the configured whitelist
    set_code_text = pytesseract.image_to_string(tresh_bw, config=custom_config)
    set_code_text_default = pytesseract.image_to_string(tresh_bw)
    if verbose >0:
            print("extract_name_info \n") 
            print("custom confing tesseract:", set_code_text)
            print("default confing tesseract (currently used):", set_code_text_default)

    # Find occurrences of pot_letters in the extracted text
    pot_name = re.findall(pot_letters, set_code_text_default)

    return pot_name


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

def mtg_letters(scryfall_data):
   
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
    print(pot_set)


def select_collectornumber(pot_collecturnumbers=[['15', '020'], ['015', '020']], verbose=1):
    # Flatten the list of lists to a single list of strings
    flat_numbers = [item.lstrip('0') for sublist in pot_collecturnumbers for item in sublist]

    # Count the occurrences of each number string
    counted_numbers = Counter(flat_numbers)

    # Get the most common numbers and their counts in descending order
    most_common = counted_numbers.most_common()

    # Calculate the threshold for frequency based on the most average number
    frequencies = [count for _, count in most_common]
    avg_frequency = sum(frequencies) / len(frequencies)
    frequency_threshold = avg_frequency / 2  # Ignoring numbers occurring 3 times less than the average

    # Initialize variables to keep track of the smallest number with the highest count
    smallest_number = float('inf')

    # Iterate through the most common numbers
    for number, count in most_common:
        if count >= frequency_threshold:
            number_int = int(number)
            if number_int < smallest_number:
                smallest_number = number_int

    if verbose > 1:
        print(f"The smallest number that occurs most frequently is probably the collectornumber: {smallest_number}")
    return str(smallest_number).zfill(len(str(smallest_number)))  # Ensure leading zeroes are added if necessary


def find_cardname_byname(pot_cardnameS, scryfall_all_data):
    """
   find the cardname by comparing with levenshtein to all of scryfall data
 

    Parameters
    ----------
    pot_cardnameS : list of strings
        potential cardnames
    scryfall_all_data : list of dicts
        scryfall data downloaded.

    Returns
    -------
    closest_matches : TYPE
        DESCRIPTION.

    """
    closest_matches = []

    for potential_name in pot_cardnameS:
        min_distance = float('inf')
        best_match = None

        for card_data in scryfall_all_data:
            name = card_data['name'].split('//')[0].strip()  # Get the first name before '//'
            distance = levenshtein_distance(name.lower(), potential_name[0].lower())  # Convert both to lowercase for case-insensitive comparison

            if distance < min_distance:
                min_distance = distance
                best_match = card_data

        closest_matches.append(best_match['name'])

    return closest_matches


def remove_duplicates(value=['ELD', 'ELD', 'ELD', 'ELD']):
    """
    remove_duplicates(value=['ELD', 'ELD', 'ELD', 'ELD'])
    this function removes all duplicates from the potential sets to check for the 
    easiest match if thats correcet

    Parameters
    ----------
    value : TYPE, optional
        DESCRIPTION. The default is ['ELD', 'ELD', 'ELD', 'ELD'].

    Returns
    -------
    unique_values : Set of strings
        Only one value per kind is returned. a set is returned.

    """
    # Remove duplicates by converting to a set
    try:
        unique_values = list(set(value))
    except TypeError:
        flattened_values = [item for sublist in value for item in sublist if item]

        # Remove duplicates by converting to a set
        unique_values = list(set(flattened_values))

    return unique_values


def find_cardname_byUI(collector_numbers, sets, rarities,scryfall_all_data, verbose = 0):
    """
    Identification of the cardname by the UI unique information provided by
    OCR data.
    

Input Parameters:

collector_numbers: List of potential collector numbers for the card.
sets: List of potential set names for the card.
rarities: List of potential rarities for the card.
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

Return a list of tuples, each containing the card's name and its associated Scryfall data that matches the specified collector number, set name, and rarity criteria.

Verbosity:

If verbose is set to a value greater than 0, it prints the collected card names with their associated data for debugging or logging purposes.

    Parameters
    ----------
    collector_numbers : TYPE
        DESCRIPTION.
    sets : TYPE
        DESCRIPTION.
    rarities : TYPE
        DESCRIPTION.
    scryfall_all_data : TYPE
        DESCRIPTION.
    verbose : TYPE, optional
        DESCRIPTION. The default is 0.

    Returns
    -------
    card_names : list of tuples [("name", scryfall_entry), ...]
        

    """

    
    # Remove preceding zeros from each element within inner lists
    collector_numbers = remove_duplicates(collector_numbers)
    sets = remove_duplicates(sets)
    # remove duplicates of found sets
    rarities = remove_duplicates(rarities)
    card_names = []
    if verbose >=1:
        print("rarities", rarities)
        print("sets", sets)
        print("ccnumbers",collector_numbers)
    
    # Check for token rarities and modify sets accordingly
    if all(rar == 'T' for rar in rarities):
        sets = ['t' + s for s in sets]
    elif any(rar == 'T' for rar in rarities):
        sets.extend(['t' + s for s in sets])
                            
    for i in range(len(collector_numbers)):
        for collector_number in collector_numbers:
            for set_name in sets:
                for card in scryfall_all_data:
                    if card.get('collector_number') == collector_number and card.get('set').lower() == set_name.lower():
            
                        
                        if 'M' in rarities and card.get('rarity').lower() == 'mythic':
                            card_names.append((card.get('name'), card))
                            break
                        elif 'C' in rarities and card.get('rarity').lower() == 'common':
                            card_names.append((card.get('name'), card))
                            break
                        elif 'R' in rarities and card.get('rarity').lower() == 'rare':
                            card_names.append((card.get('name'), card))
                            break
                        elif 'T' in rarities:
                            if card.get('rarity').lower() == 'special' or card.get('set').lower().startswith('t'):
                                card_names.append((card.get('name'), card))
                                break
                        else:
                            pass
    
    if len(card_names) > 0:
        if verbose >0:
            # print(card_names)
            print(card_names[0][0])
        if verbose >= 3:
            print(card_names)
        return card_names
    
    else:
        # No cardnames were found
        return None

def cardname_by_comp_UI_name(cardname_byname,cardname_byUI, verbose =0 ):
    # Get unique card names from cardname_byname
    unique_card_names = set(cardname_byname)
    
    # Filter and maintain original order
    unique_by_UI = []
    seen = set()
    try:
        
        for tup in cardname_byUI:
            if tup[0] in unique_card_names and tup[0] not in seen:
                unique_by_UI.append(tup)
                seen.add(tup[0])
    except TypeError:
        print(cardname_byname)
        
        print(cardname_byname)
    # if no comparision was succesful, most prabable the  UI was not readable, 
    # therefore only the cardname gets passed to this tuple 
    if unique_by_UI == []:
        unique_by_UI = (cardname_byname[0],"")
        if verbose >0:
            print("Ui was not identified, but the cardname was identified by",
                  "reading the cardname, set was not detected")
    return unique_by_UI
    

def return_cardname_from_ROI(filename, scryfall_all_data, verbose = 0, roi_directory = 'ROIs'):
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
       
    # Get the current working directory
    current_directory = os.getcwd()
    
    # Define the directory containing UI ROIs
    roi_directory = os.path.join(current_directory, roi_directory)
    
    # collect all potential (pot) collectornumbers, sets, rarities, cardnames
    pot_collectornumberS = []
    pot_setS = []
    pot_rarityS = []
    pot_cardnameS = []
    
    # List all roi files in the directory
    roi_files = os.listdir(roi_directory)
    if verbose >=3:
        print("roi file::", roi_files)
    
    # Loop through each file
    for roi_file in roi_files:
        # Assuming UI ROIs have this naming convention
        if roi_file.startswith(f"{filename}_ui"): 
            
            file_path = os.path.join(roi_directory, roi_file)
            if verbose > 0:
                print(file_path)
            # Read the image
            ui_roi = cv2.imread(file_path)
    
      
            roi_info = preprocess_roi(ui_roi,verbose=2)
            pot_collectornumber, pot_set, pot_rarity = extract_set_info(roi_info)
            # pot_collectornumber, pot_set, pot_rarity = extract_set_info(ui_roi)
            if verbose > 0:
                print("ccn",pot_collectornumber, "set:", pot_set, "pot_rarity:", pot_rarity)
       
            if pot_collectornumber != []:
                pot_collectornumberS.append(pot_collectornumber)
            if pot_set != []:
                pot_setS.append(pot_set)
            if pot_rarity != []:
                pot_rarityS.append(pot_rarity)
             
        if roi_file.startswith(f"{filename}_name"): 
            file_path = os.path.join(roi_directory, roi_file)
            if verbose > 0:
                print(file_path)
            
            # Read the image
            name_roi = cv2.imread(file_path)
            
            # Call preprocess_roi function to get relevant information
            # and Apply extract_set_code function
            # roi_info = preprocess_roi(name_roi,verbose)
            roi_info = name_roi
            pot_cardname = [''.join(extract_name_info(roi_info, potential_letters, verbose))]
            
            if pot_cardname != []:
                pot_cardnameS.append(pot_cardname)
               
    print(pot_cardnameS)
    cardname_by_name = find_cardname_byname(pot_cardnameS, scryfall_all_data)
    cardname_by_UI = find_cardname_byUI(pot_collectornumberS, pot_setS, 
                                       pot_rarityS, scryfall_all_data,verbose)
    # "compare cardname by name and cardname by UI to find the correct name"
    cardname = None
    cardname = cardname_by_comp_UI_name(cardname_by_name,cardname_by_UI)
    return cardname

def display_cardname(tuple_name_and_infos):
    if tuple_name_and_infos[0] !='' and tuple_name_and_infos[1] !='':
        print(tuple_name_and_infos[0], "from ",tuple_name_and_infos[1]['set'])
    elif tuple_name_and_infos[0] !='' and tuple_name_and_infos[1] =='':
        print(tuple_name_and_infos[0], "from a non defined set.")
    else:
        print("Ui was not read, only the cardname not the expansion was found")
        
    
def str_cardname(tuple_name_and_infos):
    if tuple_name_and_infos[0] !='' and tuple_name_and_infos[1] !='':
        a= str(tuple_name_and_infos[0], "from ",tuple_name_and_infos[1]['set'])
    elif tuple_name_and_infos[0] !='' and tuple_name_and_infos[1] =='':
        a=str(tuple_name_and_infos[0], "from a non defined set.")
    else:
        a=str("Ui was not read, only the cardname not the expansion was found")
    return a   
    

def rename_and_move_ROIs(filename, tuple_name_and_infos, save_directory='identified ROIS', roi_directory='ROIs', verbose=0):
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

def delete_duplicate_ROIs(filename, roi_directory='ROIs', verbose=0):
    
    if filename.endswith(".jpg"):
        filename = filename.strip(".jpg") 
        
    # Get the current working directory
    current_directory = os.getcwd()
    # Define the directory containing UI ROIs
    roi_directory = os.path.join(current_directory, roi_directory)
    # List all ROI files in the directory
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
                        
                                                      
"""
# Function to ask for user input
def ask_user_input():
    # cardname = display_cardname()  # Get the card name to display
    
    # Ask for user input
    user_input = input(f"The card was identified as {cardname}. Is that correct? [Y/N]: ").strip().lower()
    
    # Check user input
    if user_input == 'y':
        print("User confirmed the identification.")
        # Perform actions for correct identification
    elif user_input == 'n':
        print("User indicated incorrect identification.")
        # Perform actions for incorrect identification
    else:
        print("Invalid input. Please enter Y or N.")
        # Handle invalid input, possibly ask again or handle accordingly

# Call the function to ask for user input
ask_user_input()
"""

if __name__ == "__main__":
    verbose = 0
    # Define pytesseract location
    pytesseract.pytesseract.tesseract_cmd = \
    r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    # check if the ROIs need to be constructed with the function process_card
    
    # from card_identification import extract_card
    from process_card import create_rois_from_filename
    from card_extraction import extract_card
    
    #  Visage of Dread, LCI 
    filename = "IMG_20231222_111834.jpg" 
    
    # Food Token ELD
    # filename = "IMG_20231213_212201.jpg"
    
    # # This image is not resolved enough that the UI can be read
    # filename = '1'

    mtg_ocr_config = MtGOCRData()
    storage_directory = mtg_ocr_config.get_img_directory()

    
    

    # Directory path where the files are located
    path = storage_directory + "/" + filename        
    print(path)
        
   
    card, error = extract_card(path,verbose)
    if error != None:
        print(error)
     
    mtg_ocr_config.set_relative_coordinates(card)
    create_rois_from_filename(filename, mtg_ocr_config, card)

    # 1 open the mtg scryfall data
    # mtg_ocr_config  = MtGOCRData
    potential_letters = mtg_ocr_config.get_Mtg_letters()
    scryfall_all_data= mtg_ocr_config.open_scryfall_file()
    pot_letters = "WdE&Su0\u00e261fF(4O\u00fctkJ\u00f6nZz\u00f1y\u00c9YICNla\\'_ \u00edcjh\u00e19\u00fa\u00e3HX\u0160M\u00e0s7Pp\u00f3\u00fb8v+:\u00e9beq3L-TiVwm?Qx\u00e4\\\"goGDU\u00aeA!K2/rB.),R"

    delete_duplicate_ROIs(filename,verbose)
    cardname = return_cardname_from_ROI(filename, scryfall_all_data, verbose =1, roi_directory = 'ROIs')
    display_cardname(cardname[0])
    
    
    
    # #  testing select_collectornumber
    # pot_collecturnumbers = [['15', '020'],  ['020', '15', '020'], ['015', '002']]
    # a = select_collectornumber(pot_collecturnumbers, verbose=1)
    # print(a)
    
 

  
            
    