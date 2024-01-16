# -*- coding: utf-8 -*-
"""
%(filename)
${file}
Created on %(date)s

author: Felix Scope
"""

import unittest
from unittest.mock import patch
import os
from pathlib import Path
from enum import Enum

from src.Card_Identification.configuration_handler import MtGOCRData
from src.Card_Identification.card_extraction import extract_card
from src.Card_Identification.path_manager import (PathType,
get_path, return_folder_contents)
from src.Card_Identification.process_card import create_rois_from_filename


class PathType(Enum):
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    RESULTS = str(BASE_DIR /'tests' / 'data' / 'Card_Identification' / 'results')
    RAW_IMAGE = str(BASE_DIR /'tests' / 'data' / 'Card_Identification' / 'raw_IMGs')
    PROCESSED_ROI = str(BASE_DIR / 'tests' /'data' / 'Card_Identification' / 'processed_ROIs')
    FINAL_ROI = str(BASE_DIR /'tests' / 'data' / 'Card_Identification' / 'final_ROIs')
    CONFIG = str(BASE_DIR /'tests' /  'data' /'Card_Identification' / 'config')

@patch('src.Card_Identification.process_card.PathType', PathType)    
@patch('src.Card_Identification.path_manager.PathType', PathType)
@patch('src.Card_Identification.configuration_handler.PathType', PathType)
class TestProcessCard(unittest.TestCase):


    @patch('src.Card_Identification.process_card.PathType', PathType)    
    @patch('src.Card_Identification.path_manager.PathType', PathType)
    @patch('src.Card_Identification.configuration_handler.PathType', PathType)
    def setUp(self):
        # This method will be called before each test method is executed
        # Delete all files in the test folder before running the test
        test_folder_path = get_path(PathType.PROCESSED_ROI)
        for file_name in os.listdir(test_folder_path):
            file_path = os.path.join(test_folder_path, file_name)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Error: {e}")
        try:
            file_path = get_path(PathType.CONFIG, "parameters.txt")
            os.unlink(file_path)
            print("path of parameters.txt", file_path)
            mtg_ocr_config = MtGOCRData()
        except Exception as e:
            print(f"Failed to delete {file_path}. Error: {e}")
          #  get the necessary parameters from confiog parameters.txt handler

    @patch('src.Card_Identification.process_card.PathType', PathType)    
    @patch('src.Card_Identification.path_manager.PathType', PathType)
    @patch('src.Card_Identification.configuration_handler.PathType', PathType)
    def test_raw_image_contents(self): #test is okay
        # check if folder contains the right images
        path_to_test_folder = get_path(PathType.PROCESSED_ROI)
        contents_test_folder = return_folder_contents(path_to_test_folder)
        expected_contents = []
        self.assertEqual(contents_test_folder, expected_contents)
        

    @patch('src.Card_Identification.path_manager.PathType', PathType)
    @patch('src.Card_Identification.configuration_handler.PathType', PathType)
    @patch('src.Card_Identification.process_card.PathType', PathType)    
    @patch('src.Card_Identification.card_extraction.PathType', PathType)
    def test_create_rois_from_filename(self):
        filename = "1.jpg"

        path = get_path(PathType.RAW_IMAGE, filename)

        card, error = extract_card(path,verbose = 1)
        if error != None:
            print(error)
        mtg_ocr_config = MtGOCRData()
        print("contents in processed roi")

        create_rois_from_filename(filename, mtg_ocr_config, card,verbose =3)
        
    #     # create_rois_from_filename(filename, mtg_ocr_config, card,verbose =2)

        # self.assertEqual(None, None)
        print("contents in processed roi")
        get_path(PathType.PROCESSED_ROI, verbose =3)
        contents_test_folder = return_folder_contents(get_path(PathType.PROCESSED_ROI))
        expected_contents = ['1_exp_1.jpg','1_exp_2.jpg', '1_name_1.jpg','1_name_2.jpg', '1_ui_1.jpg','1_ui_2.jpg']
        self.assertEqual(contents_test_folder, expected_contents)

if __name__ == '__main__':
    unittest.main()

