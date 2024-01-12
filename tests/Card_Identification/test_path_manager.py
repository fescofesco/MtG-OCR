# -*- coding: utf-8 -*-
"""
test_path_manager.py

tests MtG_OCR_Card_Identification/path_manager.py
display the contents of the paths of the working tree

Created on 08.01.2024

author: Felix Scope
"""
import unittest
from unittest.mock import patch
import os
from pathlib import Path
from src.Card_Identification.path_manager import (
get_path, return_folder_contents
)




class TestPathManager(unittest.TestCase):
    BASE_DIR = Path(__file__).resolve().parent.parent.parent  # Adjust the parent calls as needed
    TEST_IMG_STORAGE_PATH = str(BASE_DIR /'tests'/ 'data' / 'Card_Identification' / 'raw_IMGs')
    TEST_ROI_PROCESSED_STORAGE_PATH = str(BASE_DIR /'tests' / 'data' / 'Card_Identification' / 'processed_ROIs')
    TEST_SCRYFALL_STORAGE_PATH = str(BASE_DIR /'tests'/ 'data' / 'Card_Identification' / 'config')
    TEST_ROI_FINAL_STORAGE_PATH = str(BASE_DIR/'tests'/  'data' / 'Card_Identification' / 'final_ROIs')
    
    
    
    @patch('src.Card_Identification.path_manager.IMG_STORAGE_PATH', TEST_IMG_STORAGE_PATH)
    def test__raw_image_coontents(self):
        path_to_test_folder =get_path("raw_image")
        contents_test_folder = return_folder_contents(path_to_test_folder)
        expected_contents = ['1.jpg', '2.jpg', '2023-12-24', '3.jpg', '4.jpg']              
        self.assertEqual(contents_test_folder, expected_contents)           
                  
    def test_get_scryfall_path(self):
        get_path("config",verbose=1)
        
        
if __name__ == '__main__':
    # print(TestPathManager.print_folder_contents())
    unittest.main()



