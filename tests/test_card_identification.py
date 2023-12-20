# -*- coding: utf-8 -*-
"""
# card_identification.py
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
import sys
import os
# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from card_identification import identify_card


class TestIdentifyCard(unittest.TestCase):
    def test_identify_card_with_image1(self):
        # Set the path to the image you want to test
        image_path = "1.jpg"  # Replace with the actual path
        
        # Call the identify_card function with the image path
        result = identify_card(image_path,2)
        
        # Perform assertions to validate the result
        self.assertIsNotNone(result)  # Ensure the function returns a result
        # Add more specific assertions based on the expected result
        
    def test_identify_card_with_image_2(self):
       # Test case for image 2.jpg
       image_path = "2.jpg"  # Replace with the actual path to image 2.jpg
       
       result = identify_card(image_path)
       
       self.assertIsNotNone(result)  # Ensure the function returns a result
       # Add more specific assertions based on the expected result for image 2.jpg
        
if __name__ == '__main__':
    unittest.main()