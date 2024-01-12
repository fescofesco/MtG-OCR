# -*- coding: utf-8 -*-
"""
pathmanagment.py

Created on 08.01.2024

author: Felix Scope

Provides functions to manage the paths from

MtG-OCR
├── data
│   ├─── scryfall_data
│   │    ├──────────── all_sets.json
│   │    └──────────── default-cards-DATESTRTIME.json
│   └─── Card_Identification
│        ├────────────────── raw_IMGs
│        │                   └─DATE
│        ├────────────────── processed_ROIs
│        └────────────────── final_identified_ROIs
├── docs
│   ├── make.bat
│   ├── Makefile
│   └── source
│       ├── conf.py
│       └── index.rst
├── examples
│   └─────── example.py
├── src
│   └── Card_Identification
│       ├────────────────── __init__.py
│       ├────────────────── main_Card_Identification.py
│       ├────────────────── configuration_handler.py
│       ├────────────────── card_extraction.py
│       ├────────────────── process_card.py
│       ├────────────────── process_rois.py
│       ├────────────────── img_from_adb.py
│       └────────────────── path_manager.py
├── tests
│   ├── Card_Identification
│   │   ├────────────────── __init__.py
│   │   └──────────────────test_path_manager.py
│   └── data
│       └── Card_Identification
│           ├────────────────── raw_IMGs
│           │                   └─ 2023-12-24
│           ├────────────────── processed_ROIs
│           ├────────────────── final_identified_ROIs
│           ├────────────────── scryfall_data
│           │                   ├── all_sets.json
│           │                   └── default-cards-DATESTRTIME.json
            └────────────────── results
├── .gitignore
├── LICENSE.txt
├── MANIFEST.in
├── README.rst
├── requirements.txt
├── setup.cfg
├── setup.py
└── tox.ini
"""
import os
from pathlib import Path

# Get the base directory where the project is located
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # Adjust the parent calls as needed

IMG_STORAGE_PATH = str(BASE_DIR / 'data' / 'Card_Identification' / 'raw_IMGs')
ROI_PROCESSED_STORAGE_PATH = str(BASE_DIR / 'data' / 'Card_Identification' / 'processed_ROIs')
SCRYFALL_STORAGE_PATH = str(BASE_DIR / 'data' / 'Card_Identification' / 'config')
ROI_FINAL_STORAGE_PATH = str(BASE_DIR / 'data' / 'Card_Identification' / 'final_ROIs')
RESULTS_SORAGE_PATH = str(BASE_DIR / 'data' / 'Card_Identification' / 'results')

def create_directory_if_not_exists(directory_path: str):
    """
    create a directory on the path if it does not already exist

    Parameters
    ----------
    directory_path : STR
        path to directory

    Returns
    -------
    None.

    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        


def get_path(path_type: str, file_name:str =None, verbose=0, create_folder=False):
    """
    
    returns the path to the image folders form the data folder 

    Parameters
    ----------
    path_type : str
        DESCRIPTION.
    file_name : str, optional
        filename . The default is None.
    verbose : TYPE, optional
        DESCRIPTION. If >1 the contents of the directory are printed
    create_folder : TYPE, optional
        the folder is created if not present by calling create_folder(). The default is False.

    Returns
    -------
    TYPE
        path to the folder.
        if filename is  given, the returned path includes the filename, 
        if not, the returned filename 
    """
    path_dict = {
        # 
        'results' : (RESULTS_SORAGE_PATH),
        #used by card_identification.py from card_extraction
        'raw_image': (IMG_STORAGE_PATH),
        # get the path to the produced ROI 
        # from process_card.py for process_roi.py
        'processed_roi': (ROI_PROCESSED_STORAGE_PATH),
        # get the path to the final, identified ROI 
        # from process_rois.py
        'final_roi': (ROI_FINAL_STORAGE_PATH),
        # get the path to the scryfall_data
        'config': (SCRYFALL_STORAGE_PATH)
    }

    directory_path = path_dict[path_type]
    


    if not os.path.exists(directory_path) and create_folder:
        create_directory_if_not_exists(directory_path)

    if file_name:
        path = os.path.join(directory_path, file_name)
        if verbose > 0:
            print(f"Contents of directory '{directory_path}':")
            directory_contents = os.listdir(directory_path)
            for item in directory_contents:
                print(item)
        return path
    else:
        if verbose > 0:
            print(f"Contents of directory '{directory_path}':")
            directory_contents = os.listdir(directory_path)
            for item in directory_contents:
                print(item)
        return directory_path

def return_folder_contents(path_to_folder = IMG_STORAGE_PATH):
    # Get the list of all items in the folder
    all_items = os.listdir(path_to_folder)

    # Filter out only files and folders
    contents = [item for item in all_items if os.path.isfile(os.path.join(path_to_folder, item)) or os.path.isdir(os.path.join(path_to_folder, item))]

    return contents


def display_folder_contents():
    """
    func to test if the paths are correct by displaying the folders contents

    Returns
    -------
    None. But displays the folders contents.

    """
    print("Raw Image Path Contents:")
    raw_image_contents = get_path("raw_image",verbose=1)
    print("-------------------------")
    print("Processed ROI Path Contents:")
    processed_roi_contents = get_path("processed_roi",verbose=1)
    print("-------------------------")
    print("Final ROI Path Contents:")
    processed_roi_contents = get_path("final_roi",verbose=1)
    print("-------------------------")
    print("Scryfall Path Contents:")
    processed_roi_contents = get_path("config",verbose=1)
    print("-------------------------")

if __name__ == "__main__":
    display_folder_contents()


