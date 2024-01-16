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
from src.Card_Identification.process_rois import return_cardname_from_ROI

  

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
    @patch('src.Card_Identification.card_extraction.PathType', PathType)
    @patch('src.Card_Identification.process_rois.PathType', PathType)
    def test_create_rois_from_filename_visageofDrad_doubleside(self):
        
        mtg_ocr_config = MtGOCRData()
        potential_letters = mtg_ocr_config.get_Mtg_letters()
        scryfall_all_data= mtg_ocr_config.open_scryfall_file()
        
        verbose = 0
      
      
        #  Visage of Dread, LCI 
        filename = "4.jpg" 
    
    
           
        path = get_path(PathType.RAW_IMAGE, filename,2)
        
    
       
        card, error = extract_card(path,verbose)
        if error != None:
            print("error:", error)
         
        mtg_ocr_config.set_relative_coordinates(card, verbose =1)
        create_rois_from_filename(filename, mtg_ocr_config, card, verbose = 2)
    
        # 1 open the mtg scryfall data
        # mtg_ocr_config  = MtGOCRData
      
        pot_letters = "WdE&Su0\u00e261fF(4O\u00fctkJ\u00f6nZz\u00f1y\u00c9YICNla\\'_ \u00edcjh\u00e19\u00fa\u00e3HX\u0160M\u00e0s7Pp\u00f3\u00fb8v+:\u00e9beq3L-TiVwm?Qx\u00e4\\\"goGDU\u00aeA!K2/rB.),R"
    
        # delete_duplicate_ROIs(filename,verbose)
        cardname = return_cardname_from_ROI(filename, scryfall_all_data, verbose =0)
        # display_cardname(cardname)
        self.assertEqual(cardname[0]["name"],"Visage of Dread // Dread Osseosaur")
        
        self.assertEqual(cardname[0]["set"],"lci")

    def test_create_rois_from_filename_foodtoken(self):
        
        mtg_ocr_config = MtGOCRData()
        potential_letters = mtg_ocr_config.get_Mtg_letters()
        scryfall_all_data= mtg_ocr_config.open_scryfall_file()
        
        verbose = 0
      
      
        #  Visage of Dread, LCI 
        filename = "IMG_20231222_111834.jpg" 
        # Food Token ELD
        filename = "3.jpg"
    
           
        path = get_path(PathType.RAW_IMAGE, filename,2)
        
    
       
        card, error = extract_card(path,verbose)
        if error != None:
            print("error:", error)
         
        mtg_ocr_config.set_relative_coordinates(card, verbose =1)
        create_rois_from_filename(filename, mtg_ocr_config, card, verbose = 2)
    
        # 1 open the mtg scryfall data
        # mtg_ocr_config  = MtGOCRData
      
        pot_letters = "WdE&Su0\u00e261fF(4O\u00fctkJ\u00f6nZz\u00f1y\u00c9YICNla\\'_ \u00edcjh\u00e19\u00fa\u00e3HX\u0160M\u00e0s7Pp\u00f3\u00fb8v+:\u00e9beq3L-TiVwm?Qx\u00e4\\\"goGDU\u00aeA!K2/rB.),R"
    
        # delete_duplicate_ROIs(filename,verbose)
        cardname = return_cardname_from_ROI(filename, scryfall_all_data, verbose =0)
        # display_cardname(cardname)
        self.assertEqual(cardname[0]["name"],"Food")
        
        self.assertEqual(cardname[0]["set"],"teld")

if __name__ == '__main__':
    unittest.main()

