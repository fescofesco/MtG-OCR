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
import cv2
import sys
# from card_identification.card_extraction import extract_card # does not work
# card_identification is currently not recognised as an module
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'card_identification'))
sys.path.append(root_path)


# Now you can import your modules
from card_extraction import extract_card
from path_manager import (get_path, return_folder_contents)
from configuration_handler import MtGOCRData
from process_card import create_rois_from_filename
from test_path_manager import PathType

@patch('process_card.PathType', PathType)    
@patch('path_manager.PathType', PathType)
@patch('configuration_handler.PathType', PathType)
@patch('card_extraction.PathType', PathType)
@patch('process_rois.PathType', PathType)
class TestProcessCard(unittest.TestCase):

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
        
        MtGOCRData()

          #  get the necessary parameters from confiog parameters.txt handler

    # def test_raw_image_contents(self): #test is okay
    #     """ check if the folder contains the right images"""
    #     path_to_test_folder = get_path(PathType.PROCESSED_ROI)
    #     contents_test_folder = return_folder_contents(path_to_test_folder)
    #     expected_contents = []
    #     self.assertEqual(contents_test_folder, expected_contents)
        

    def test_create_rois_from_filename(self):
        filename = "1.jpg"
        path = get_path(PathType.RAW_IMAGE, filename)
        card, error = extract_card(path,verbose = 1)
        if error != None:
            print(error)
        mtg_ocr_config = MtGOCRData()
  
        create_rois_from_filename(filename, mtg_ocr_config, card,verbose =4)

        contents_test_folder = return_folder_contents(get_path(PathType.PROCESSED_ROI))
        expected_contents = ['1_exp_1.jpg','1_exp_2.jpg', '1_name_1.jpg','1_name_2.jpg', '1_ui_1.jpg','1_ui_2.jpg']
        expected_contents = ['1_exp_1.jpg','1_exp_2.jpg','1_exp_3.jpg', '1_name_1.jpg','1_name_2.jpg','1_name_3.jpg', '1_ui_1.jpg']

        self.assertEqual(contents_test_folder, expected_contents)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
if __name__ == '__main__':
    unittest.main()

