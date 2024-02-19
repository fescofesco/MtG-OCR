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
import sys
# from card_identification.card_extraction import extract_card # does not work
# card_identification is currently not recognised as an module
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'card_identification'))
sys.path.append(root_path)



from configuration_handler import (MtGOCRData, CubeCobraData)
from path_manager import (get_path)
from card_extraction import extract_card
from test_path_manager import PathType



@patch('path_manager.PathType', PathType)
@patch('configuration_handler.PathType', PathType)
class TestConfigurationHandler(unittest.TestCase):
    
 
    # @patch('path_manager.PathType', 'test_path_manager.PathType')
    # @patch('configuration_handler.PathType', 'test_path_manager.PathType')
    def setUp(self):
        # """Remove parameters.txt before each test and initialize it anew"""
        parameters_file_path = get_path(PathType.CONFIG, "cubecobralogin.txt")
        print(parameters_file_path)
        print("pfile path", parameters_file_path)
        # Check if parameters.txt exists and delete it if it does
        if Path(parameters_file_path).is_file():
            try:
                Path(parameters_file_path).unlink()
                print("Reinisialised Parameters.txt")
            except Exception as e:
                print(f"Error deleting parameters.txt: {e}")
        self.CubeData= CubeCobraData()
  

    # @patch('path_manager.PathType', 'test_path_manager.PathType')
    # @patch('configuration_handler.PathType', 'test_path_manager.PathType')
  
    def test_start_CubeCobraData(self):

        CubeData = CubeCobraData()
        CubeData.set_cube_username("chrilix")
        self.assertEqual(CubeData.get_cube_username(),"chrilix")
        
        CubeData.set_cube_password("123456")
        self.assertEqual(CubeData.get_cube_password(),"123456")

    # @patch('path_manager.PathType', PathType)
    # @patch('configuration_handler.PathType', PathType)
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
              if the roi looks fine. close the window with q or Q or ESC. \
              Otherwise this test fails.")
        mtg_ocr_config.set_relative_coordinates(card)
    
        for mode in modes:
            new_coordinates.append(mode)
            new_coordinates.extend(mtg_ocr_config.get_coordinates_from_file(mode))
    
     
        self.assertGreater(len(new_coordinates), len(old_coordinates))
        if len(new_coordinates) == len(old_coordinates):
            print("Test failed, but did you added new coordinates after \
                  pressing enter after the roi selection?")
        
        
if __name__ == '__main__':
    unittest.main()