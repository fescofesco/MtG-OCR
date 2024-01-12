# -*- coding: utf-8 -*-
"""
# test_card_extraction.py
V 1.0
Created on Thu Nov 16 08:39:30 2023

@author: Felix Scope


# This scirpt allows card identification of images. Only one card per
# image, but easy implementable to allow more. Currently the whole card must be 
visisble.

Main function is 
    identify_card(path_to_img_folder, verbose=1):


"""


# import unittest
# import sys
# import os
# # Add the project root directory to sys.path
# # sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# from pathlib import Path
# from src.Card_Identification.card_extraction import identify_card
# from src.Card_Identification.path_manager import get_path


import unittest
from unittest.mock import patch
import os
from pathlib import Path
from src.Card_Identification.path_manager import get_path
# import src.Card_Identification.card_extraction.extract_card

from src.Card_Identification.card_extraction import extract_card

# # Add the project root directory to sys.path
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.Card_Identification.path_manager import (
get_path, return_folder_contents
)


class TestIdentifyCard(unittest.TestCase):
    
    BASE_DIR = Path(__file__).resolve().parent.parent.parent  # Adjust the parent calls as needed
    TEST_IMG_STORAGE_PATH = str(BASE_DIR /'tests'/ 'data' / 'Card_Identification' / 'raw_IMGs')
   
    
    @patch('src.Card_Identification.path_manager.IMG_STORAGE_PATH', TEST_IMG_STORAGE_PATH)
    def return_files_to_test(self):
        folder_content = return_folder_contents(get_path("raw_image"))
        return folder_content
        
    @patch('src.Card_Identification.path_manager.IMG_STORAGE_PATH', TEST_IMG_STORAGE_PATH)
    def test_identify_card_with_image1(self):
      
        
        files_to_test = self.return_files_to_test()
        print(files_to_test)
        for file in files_to_test:
            
            image_path = get_path("raw_image",file)
            # Call the identify_card function with the image path
            result = extract_card(image_path,2)
            
            # Perform assertions to validate the result
            self.assertIsNotNone(result)  # Ensure the function returns a result
   
        
if __name__ == '__main__':
    unittest.main()