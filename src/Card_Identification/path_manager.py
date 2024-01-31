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
│   └── 
│       ├────────────────── __init__.py
│       ├────────────────── main_Card_Identification.py
│       ├────────────────── configuration_handler.py
│       ├────────────────── card_extraction.py
│       ├────────────────── process_card.py
│       ├────────────────── process_rois.py
│       ├────────────────── img_from_adb.py
│       └────────────────── path_manager.py
├── tests
│   ├── tests_card_identification
│   │   ├────────────────── __init__.py
│   │   ├──────────────────test_card_extraction.py
│   │   └──────────────────test_path_manager.py
│   └── data
│       └── card_identification
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
from enum import Enum
import cv2


class PathType(Enum):
    BASE_DIR = Path(__file__).resolve().parent.parent.parent

    RESULTS = str(BASE_DIR / 'data' / 'card_identification' / 'results')
    RAW_IMAGE = str(BASE_DIR / 'data' / 'card_identification' / 'raw_IMGs')
    PROCESSED_ROI = str(BASE_DIR / 'data' / 'card_identification' / 'processed_ROIs')
    FINAL_ROI = str(BASE_DIR / 'data' / 'card_identification' / 'final_ROIs')
    CONFIG = str(BASE_DIR / 'data' / 'card_identification' / 'config')

    TEST_RESULTS = str(BASE_DIR / 'tests'/ 'data' / 'card_identification' / 'results')
    TEST_RAW_IMAGE = str(BASE_DIR / 'tests'/ 'data' / 'card_identification' / 'raw_IMGs')
    TEST_PROCESSED_ROI = str(BASE_DIR /'tests'/  'data' / 'card_identification' / 'processed_ROIs')
    TEST_FINAL_ROI = str(BASE_DIR / 'data' /'tests'/  'card_identification' / 'final_ROIs')
    TEST_CONFIG = str(BASE_DIR / 'data' / 'tests'/ 'card_identification' / 'config')

def get_path(path_type: PathType = None, file_name: str = None, verbose: int = 0):
    """
    Returns the path to the image folders from the data folder. 

    Parameters:
        path_type (PathType, str, optional): Enum or a custom path. Default is None.
        
        supported path_types are:
            
        RESULTS
        RAW_IMAGE
        PROCESSED_ROI
        FINAL_ROI
        CONFIG
        
        and custum paths by
        
        file_name (str, optional): Filename. Default is None.
        verbose (int, optional): If > 0, the contents of the directory are printed.

    Returns:
        str: Path to the folder. If filename is given, the returned path includes the filename.
             If the filename is not given, the fodlder contents are returned.
    """

    if path_type is None:
        print("Provide a valid path_type or a custom path.")
        return None

    # elif isinstance(path_type, PathType):
    try:
        directory_path = path_type.value
    except TypeError:
        
        if isinstance(path_type, str):
            if os.path.isabs(path_type):
                    directory_path = path_type
            else:
                # print(absolute_path)
                absolute_path = str(PathType.BASE_DIR / path_type)
                directory_path = absolute_path

    # Create directory if it does not exist
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

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

def return_folder_contents(path_to_folder : str):
    """
    returns all folder contents as a list
    """

    # Get the list of all items in the folder
    all_items = os.listdir(path_to_folder)

    # Filter out only files and folders
    contents = [item for item in all_items \
                if os.path.isfile(os.path.join(path_to_folder, item)) \
                    or os.path.isdir(os.path.join(path_to_folder, item))]

    return contents

def return_folder_image_contents(path_to_folder: str):
    """
    Returns a list of all image files that OpenCV can read in the folder.
    """
    # Get the list of all items in the folder
    all_items = os.listdir(path_to_folder)

    # Filter out only image files that OpenCV can read
    image_files = [
        item for item in all_items
        if (
            any(item.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff'])
            and os.path.isfile(os.path.join(path_to_folder, item))
            and cv2.imread(os.path.join(path_to_folder, item)) is not None
        )
    ]

    return image_files


if __name__ == "__main__":
    
    print(return_folder_contents(get_path(PathType.RESULTS)))
    print(return_folder_contents(get_path(PathType.RAW_IMAGE)))
    print(return_folder_contents(get_path(PathType.CONFIG)))
    print(return_folder_contents(get_path(PathType.PROCESSED_ROI)))
    print(return_folder_contents(get_path(PathType.FINAL_ROI)))
    print(return_folder_image_contents(get_path(PathType.RAW_IMAGE)))
    print(return_folder_image_contents(get_path(PathType.TEST_RAW_IMAGE)))

