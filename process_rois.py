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
Load Expansion Symbols:

Load the expansion symbols stored as .svg images in the /setsymbols directory.
Symbol Comparison:

Compare the expansion symbol of filename_exp_version.jpg with the symbols in the /setsymbols directory.
Find the closest matching symbols.
Implementation Notes:
Use appropriate image processing libraries in Python (like OpenCV or PIL) to extract ROIs.
Implement Levenshtein distance or similar string similarity metrics for name comparison.
Ensure proper error handling for cases where data might be missing or inconsistent.
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



def extract_info(roi, verbose =0):
 # Convert the UI ROI to grayscale
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    
    # Apply adaptive thresholding to get a binary image
    threshold = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    
    # Find contours in the thresholded image
    contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    threshold_value = 10
    
    # Filter contours based on size (assuming the set code region has a specific size)
    filtered_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > threshold_value]
    
    # Sort contours from left to right
    filtered_contours = sorted(filtered_contours, key=lambda x: cv2.boundingRect(x)[0])
    if verbose > 0:
        cv2.imshow("Contours",roi)
        cv2.waitKey(0)
        cv2.destroyWindow("Contours")
        
    
    # Extract the bounding box for the first contour (assuming it's the set code)
    if filtered_contours:
        x, y, w, h = cv2.boundingRect(filtered_contours[0])
    
        # Crop the region of interest (set code)
        roi_info = gray[y:y+h, x:x+w]
        
        return roi_info
             
    return []


def extract_set_info(set_code_roi,verbose = 0):
    # Perform OCR to extract text from the set code ROI
    set_code_text = pytesseract.image_to_string(set_code_roi)
    
    # Extracting numbers using regular expression
    pot_collecturnumber = re.findall(r'\b\d{1,4}\b', set_code_text)

    # Extracting 3-letter words using regular expression
    pot_set = re.findall(r'\b[A-Z123465789]{3}\b', set_code_text)
    
    # Identifying rarity (assuming rarity is denoted by single letters)
    pot_rarity = re.findall(r'[MCTRU]', set_code_text)
    
    if verbose >0:
        print("ccn",pot_collecturnumber, "set:", pot_set, "pot_rarity:", 
              pot_rarity)
    return pot_collecturnumber, pot_set, pot_rarity


def extract_name_info(contour_name_roi, pot_letters, verbose = 0):
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
    set_code_text = pytesseract.image_to_string(contour_name_roi, config=custom_config)
    set_code_text_default = pytesseract.image_to_string(contour_name_roi)
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



'''
find_cardname_byname(pot_cardnameS, scryfall_all_data):
    
 
find the cardname by comparing with levenshtein to all of scryfall data
'''
def find_cardname_byname(pot_cardnameS, scryfall_all_data):
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




"""
remove_duplicates(value=['ELD', 'ELD', 'ELD', 'ELD'])
this function removes all duplicates from the potential sets to check for the 
easiest match if thats correcet

"""
def remove_duplicates(value=['ELD', 'ELD', 'ELD', 'ELD']):
    # Remove duplicates by converting to a set
    try:
        unique_values = list(set(value))
    except TypeError:
        flattened_values = [item for sublist in value for item in sublist if item]

        # Remove duplicates by converting to a set
        unique_values = list(set(flattened_values))

    return unique_values

"""
find the cardname by using the information obtained by UI
rarity
set
collector_number
"""
def find_cardname_byUI(collector_numbers, sets, rarities,data, verbose = 0):
       
    # Remove preceding zeros from each element within inner lists
    collector_numbers = remove_duplicates(collector_numbers)
    sets = remove_duplicates(sets)
    rarities = remove_duplicates(rarities)
    card_names = []
    
    # Check for token rarities and modify sets accordingly
    if all(rar == 'T' for rar in rarities):
        sets = ['t' + s for s in sets]
    elif any(rar == 'T' for rar in rarities):
        sets.extend(['t' + s for s in sets])
          
    for i in range(len(collector_numbers)):
        for collector_number in collector_numbers:
            for set_name in sets:
                for card in data:
                    if card.get('collector_number') == collector_number and card.get('set').lower() == set_name.lower():
                        rarity_index = sets.index(set_name)
                        rarity = rarities[rarity_index]
                        
                        if rarity == 'M' and card.get('rarity').lower() == 'mythic':
                            card_names.append((card.get('name'), card))
                            break
                        elif rarity == 'C' and card.get('rarity').lower() == 'common':
                            card_names.append((card.get('name'), card))
                            break
                        elif rarity == 'R' and card.get('rarity').lower() == 'rare':
                            card_names.append((card.get('name'), card))
                            break
                        elif rarity == 'T':
                            if card.get('rarity').lower() == 'special' or card.get('set').lower().startswith('t'):
                                card_names.append((card.get('name'), card))
                                break
                        else:
                            pass
        
    if verbose > 0:
        print(card_names)
    return card_names

def cardname_by_comp_UI_name(cardname_byname,cardname_byUI, verbose =0 ):
    # Get unique card names from cardname_byname
    unique_card_names = set(cardname_byname)
    
    # Filter and maintain original order
    unique_by_UI = []
    seen = set()
    for tup in cardname_byUI:
        if tup[0] in unique_card_names and tup[0] not in seen:
            unique_by_UI.append(tup)
            seen.add(tup[0])
            
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
    if verbose >1:
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
    
      
            roi_info = extract_info(ui_roi,verbose)
            pot_collectornumber, pot_set, pot_rarity = extract_set_info(roi_info)
    
            if verbose > 0:
                print("return ccn",pot_collectornumber, "set:", pot_set, "pot_rarity:", pot_rarity)
       
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
            
            # Call extract_info function to get relevant information
            # and Apply extract_set_code function
            roi_info = extract_info(name_roi,verbose)
            pot_cardname = [''.join(extract_name_info(roi_info, potential_letters, verbose))]
            
            if pot_cardname != []:
                pot_cardnameS.append(pot_cardname)
               
    cardname_by_name = find_cardname_byname(pot_cardnameS, scryfall_all_data)
    cardname_by_UI = find_cardname_byUI(pot_collectornumberS, pot_setS, 
                                       pot_rarityS, scryfall_all_data)
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
                for idx, file1 in enumerate(same_size_files):
                    for file2 in same_size_files[idx + 1:]:
                        # Check if files exist before comparing
                        if os.path.exists(file1) and os.path.exists(file2):
                            # Check if files have identical content
                            if filecmp.cmp(file1, file2):
                                # Delete the duplicate file
                                os.remove(file2)
                                if verbose > 0:
                                    print(f"Deleted duplicate file: {file2}")
                        else:
                            if verbose > 0:
                                print(f"One or both files not found: {file1}, {file2}")
                                
                                

# Function to ask for user input
def ask_user_input():
    cardname = display_cardname()  # Get the card name to display
    
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

if __name__ == "__main__":
    
    pot_letters = "WdE&Su0\u00e261fF(4O\u00fctkJ\u00f6nZz\u00f1y\u00c9YICNla\\'_ \u00edcjh\u00e19\u00fa\u00e3HX\u0160M\u00e0s7Pp\u00f3\u00fb8v+:\u00e9beq3L-TiVwm?Qx\u00e4\\\"goGDU\u00aeA!K2/rB.),R"
    

    # 1 open the mtg scryfall data
    mtg_ocr_data  = MtGOCRData()
    potential_letters = mtg_ocr_data.get_Mtg_letters()
    scryfall_all_data= mtg_ocr_data.open_scryfall_file()

    # from card_identification import identify_card
    from process_card import create_rois_from_filename
    filename = "IMG_20231213_212201.jpg"

    create_rois_from_filename(filename)

    cardname_food = return_cardname_from_ROI(filename, scryfall_all_data, verbose = 0, roi_directory = 'ROIs')
    display_cardname(cardname_food[0])
   
    rename_and_move_ROIs(filename, cardname_food[0], roi_directory='ROIs', verbose=0)
   
    # This image is not resolved enough that the UI can be read
    filename = '1'
    cardname_asmo = return_cardname_from_ROI(filename, scryfall_all_data, verbose = 0, roi_directory = 'ROIs')
    display_cardname(cardname_asmo)
    delete_duplicate_ROIs(filename)
  
    
    #  testing select_collectornumber
    pot_collecturnumbers = [['15', '020'],  ['020', '15', '020'], ['015', '002']]
    a = select_collectornumber(pot_collecturnumbers, verbose=1)
    print(a)
    
    # Define pytesseract location
    pytesseract.pytesseract.tesseract_cmd = \
    r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    

  
            
    