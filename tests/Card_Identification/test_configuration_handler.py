# -*- coding: utf-8 -*-
"""
# card_identification.py
V 1.0
Created on Thu Nov 20 

@author: Felix Scope


Test Not working currently

"""

import unittest
from unittest.mock import patch
import os
from pathlib import Path
# import cv2
from enum import Enum


# Add the project root directory to sys.path
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.Card_Identification.configuration_handler import (MtGOCRData, CubeCobraData)
from src.Card_Identification.path_manager import (get_path, return_folder_contents, PathType)
from src.Card_Identification.card_extraction import extract_card



class PathType(Enum):
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    RESULTS = str(BASE_DIR /'tests' / 'data' / 'Card_Identification' / 'results')
    RAW_IMAGE = str(BASE_DIR /'tests' / 'data' / 'Card_Identification' / 'raw_IMGs')
    PROCESSED_ROI = str(BASE_DIR / 'tests' /'data' / 'Card_Identification' / 'processed_ROIs')
    FINAL_ROI = str(BASE_DIR /'tests' / 'data' / 'Card_Identification' / 'final_ROIs')
    CONFIG = str(BASE_DIR /'tests' /  'data' /'Card_Identification' / 'config')
    

@patch('src.Card_Identification.path_manager.PathType', PathType)
@patch('src.Card_Identification.configuration_handler.PathType', PathType)
class TestConfigurationHandler(unittest.TestCase):
    
    @patch('src.Card_Identification.path_manager.PathType', PathType)
    @patch('src.Card_Identification.configuration_handler.PathType', PathType)
    def setUp(self):
        # """Remove parameters.txt before each test and initialize it anew"""
        parameters_file_path = get_path(PathType.CONFIG, "cubecobralogin.txt")
        print("pfile path", parameters_file_path)
        # Check if parameters.txt exists and delete it if it does
        if Path(parameters_file_path).is_file():
            try:
                Path(parameters_file_path).unlink()
                print("Reinisialised Parameters.txt")
            except Exception as e:
                print(f"Error deleting parameters.txt: {e}")
        CubeData= CubeCobraData()
  
    # def start_MtGOCRData(self):
    #     # Set the path to the image you want to test
        
    #     # Create an instance of ConfigurationHandler
    #     mtg_ocr_data  = MtGOCRData()
        
    #     print(mtg_ocr_data.get_img_storage_directory())
        
    #     mtg_ocr_data.set_phone_directory(None)
                
    #     print(mtg_ocr_data.get_img_storage_directory())
    #     mtg_ocr_data.set_phone_directory()

        
    #     # Perform assertions to validate the result
    #     self.assertIsNotNone(mtg_ocr_data.get_phone_directory())  # Ensure the function returns a result
    #     # Add more specific assertions based on the expected result
    # @patch('src.Card_Identification.path_manager.PathType', PathType)
    # @patch('src.Card_Identification.path_manager.PathType', PathType)
    # @patch('src.Card_Identification.configuration_handler.PathType', PathType)
    # def test_start_CubeCobraData(self):

    #     CubeData = CubeCobraData()
    #     CubeData.set_cube_username("chrilix")
    #     self.assertEqual(CubeData.get_cube_username(),"chrilix")
        
    #     CubeData.set_cube_password("123456")
    #     self.assertEqual(CubeData.get_cube_password(),"123456")
    
    # @patch('src.Card_Identification.path_manager.PathType', PathType)
    # @patch('src.Card_Identification.configuration_handler.PathType', PathType)
    # def test_start_MtgOCRData(self):
    #     mtg_ocr_config = MtGOCRData()
    #     filename = "1.jpg"   
      
    #     pathtoimage = get_path(PathType.RAW_IMAGE, filename)
    #     print("pathtoimage", pathtoimage)
    #     image = cv2.imread(pathtoimage)
    #     # image =cv2.imread(get_path(PathType.RAW_IMAGE, filename))
      
    #     old_coordinates = []
    #     new_coordinates =[]
    #     modes = ["ui","name","exp"]
    #     for mode in modes:
    #         old_coordinatesparameters.append( mtg_ocr_config.get_coordinates_from_file(mode))
        
    #     mtg_ocr_config.set_relative_coordinates(image)
        
    #     for mode in modes:
    #         new_coordinates.append(mtg_ocr_config.get_coordinates_from_file(mode)))
    
    #     self.assert more entries in new_coordinates than in old_coordinates


    @patch('src.Card_Identification.path_manager.PathType', PathType)
    @patch('src.Card_Identification.configuration_handler.PathType', PathType)
    def test_start_MtgOCRData(self):
        mtg_ocr_config = MtGOCRData()
        filename = "1.jpg"  # Change filename to the actual image file path
    
        card,error  = extract_card(get_path(PathType.RAW_IMAGE,filename, verbose =0),0)
        # print("pathtoimage", pathtoimage)
        # image =cv2.imread(get_path(PathType.RAW_IMAGE, filename))
    
        old_coordinates = []
        new_coordinates = []
        modes = ["ui", "name", "exp"]
        for mode in modes:
            old_coordinates.append(mode)
            old_coordinates.extend(mtg_ocr_config.get_coordinates_from_file(mode))
    
        print("enter a new ROi by clicking in the image, and pressing enter \
              if the roi looks fine. close the window with q or Q or ESC.  \
              Otherwise this test fails.")
        mtg_ocr_config.set_relative_coordinates(card)
    
        for mode in modes:
            new_coordinates.append(mode)
            new_coordinates.extend(mtg_ocr_config.get_coordinates_from_file(mode))
    
     
        self.assertGreater(len(new_coordinates), len(old_coordinates))
        if len(new_coordinates) == len(old_coordinates):
            print("Test failed, but did you added new coordinates after \
                  pressing enter after the roi selection?")
        
    @patch('src.Card_Identification.path_manager.PathType', PathType)
    @patch('src.Card_Identification.configuration_handler.PathType', PathType)
    def test_start_MtgOCRData(self):
        mtg_ocr_config = MtGOCRData()
        print(mtg_ocr_config.get_coordinates_from_file("ui"))
        print(mtg_ocr_config.get_coordinates_from_file("exp"))
        print(mtg_ocr_config.get_coordinates_from_file("name"))
        self.assertEqual(1,1)
        
if __name__ == '__main__':
    # print("MAIN", get_path(PathType.CONFIG))
    # print(return_folder_contents(get_path(PathType.CONFIG)))

    unittest.main()