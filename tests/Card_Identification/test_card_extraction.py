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

import unittest
from unittest.mock import patch
import os
from pathlib import Path

from src.Card_Identification.path_manager import get_path
from src.Card_Identification.card_extraction import extract_card
from src.Card_Identification.path_manager import (PathType,
get_path, return_folder_contents
)



class PathType():
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    RESULTS = str(BASE_DIR /'tests' / 'data' / 'Card_Identification' / 'results')
    RAW_IMAGE = str(BASE_DIR /'tests' / 'data' / 'Card_Identification' / 'raw_IMGs')
    PROCESSED_ROI = str(BASE_DIR / 'tests' /'data' / 'Card_Identification' / 'processed_ROIs')
    FINAL_ROI = str(BASE_DIR /'tests' / 'data' / 'Card_Identification' / 'final_ROIs')
    CONFIG = str(BASE_DIR /'tests' /  'data' /'Card_Identification' / 'config')



@patch('src.Card_Identification.path_manager.PathType', PathType)    
class TestIdentifyCard(unittest.TestCase):
    

    def test_raw_image_contents(self):
        # check if folder contains the right images
        path_to_test_folder = get_path(PathType.RAW_IMAGE,verbose =0)
        contents_test_folder = return_folder_contents(path_to_test_folder)
        expected_contents = ['1.jpg', '2.jpg', '2023-12-24', '3.jpg', '4.jpg']
        self.assertEqual(contents_test_folder, expected_contents)
        
    def test_identify_card_with_image_1(self):
        # test with full filename
        filename = "1.jpg"
        # verbose 2
        card,error  = extract_card(get_path(PathType.RAW_IMAGE,filename, verbose =0), 1)
        if error != None:
            print(error)
        self.assertEqual(error, None)
   
    def test_identify_card_with_image_2(self):
        # test without .jpg
        filename = "2"
        # verbose 2
        card,error  = extract_card(get_path(PathType.RAW_IMAGE,filename, verbose =0), 2)
        if error != None:
            print(error)
        self.assertEqual(error, None)
        
    def test_identify_card_without_imagepath(self):
        # test if correct error when image is not found
        filename = "Non found.jpg"
        card,error  = extract_card(get_path(PathType.RAW_IMAGE,filename, verbose =0),2)
        self.assertEqual(error, "Image not loaded. Check the image path")
        
        

if __name__ == '__main__':
    unittest.main()

         