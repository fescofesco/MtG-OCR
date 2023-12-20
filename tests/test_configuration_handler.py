# -*- coding: utf-8 -*-
"""
# card_identification.py
V 1.0
Created on Thu Nov 20 

@author: Felix Scope


Test Not working currently

"""


import unittest
import sys
import os
# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from configuration_handler import MtGOCRData, CubeCobraData


class TestIdentifyCard(unittest.TestCase):
    def start_MtGOCRData(self):
        # Set the path to the image you want to test
        
        # Create an instance of ConfigurationHandler
        mtg_ocr_data  = MtGOCRData()
        
        print(mtg_ocr_data.get_img_storage_directory())
        
        mtg_ocr_data.set_phone_directory(None)
        
        
        print(mtg_ocr_data.get_img_storage_directory())
        mtg_ocr_data.set_phone_directory()

        
        # Perform assertions to validate the result
        self.assertIsNotNone(mtg_ocr_data.get_phone_directory())  # Ensure the function returns a result
        # Add more specific assertions based on the expected result
        
    def start_CubeCobraData(self):
        CubeData = CubeCobraData()
        CubeData.set_cube_username("chrilix")
        CubeData.set_cube_password("meinpin6")
        print(CubeData.get_cube_url())
        CubeData.get_cube_url()
        CubeData.set_cube_url("chrilix")
        print(CubeData.get_cube_url())

    
        
if __name__ == '__main__':
    unittest.main()