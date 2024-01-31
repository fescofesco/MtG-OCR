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
from enum import Enum
import sys
# from card_identification.card_extraction import extract_card # does not work
# card_identification is currently not recognised as an module
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'card_identification'))
sys.path.append(root_path)
from  path_manager import (get_path, return_folder_contents)


class PathType(Enum):
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    RESULTS = str(BASE_DIR /'tests' / 'data' / 'card_identification' / 'results')
    RAW_IMAGE = str(BASE_DIR /'tests' / 'data' / 'card_identification' / 'raw_IMGs')
    PROCESSED_ROI = str(BASE_DIR / 'tests' /'data' / 'card_identification' / 'processed_ROIs')
    FINAL_ROI = str(BASE_DIR /'tests' / 'data' / 'card_identification' / 'final_ROIs')
    CONFIG = str(BASE_DIR /'tests' /  'data' /'card_identification' / 'config')


class TestIdentifyCard(unittest.TestCase):
        @patch('path_manager.PathType', PathType)
        def test_raw_image_contents(self):
            """" Checks if the contents of the raw_image are correct"""
            path_to_test_folder = get_path(PathType.RAW_IMAGE,verbose =0)
            contents_test_folder = return_folder_contents(path_to_test_folder)
            expected_contents = ['1.jpg', '2.jpg', '2023-12-24', '3.jpg', '4.jpg']
            self.assertEqual(contents_test_folder, expected_contents)
        
    
    
if __name__ == '__main__':
    unittest.main()