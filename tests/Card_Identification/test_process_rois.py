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
from src.Card_Identification.process_rois import (
    return_cardname_from_ROI, display_cardname)

  

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
    @patch('src.Card_Identification.card_extraction.PathType', PathType)
    @patch('src.Card_Identification.process_rois.PathType', PathType)
    def setUp(self):
        
        self.mtg_ocr_config = MtGOCRData()
        self.potential_letters = self.mtg_ocr_config.get_Mtg_letters()
        self.scryfall_all_data= self.mtg_ocr_config.open_scryfall_file()
        
        
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
            # print("path of parameters.txt", file_path)
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
        
        #  Visage of Dread, LCI 
        filename = "4.jpg"
        path = get_path(PathType.RAW_IMAGE, filename)
        card, error = extract_card(path,verbose = 1)
        if error != None:
            print("error:", error)
         
        self.mtg_ocr_config.set_relative_coordinates(card, verbose =1)
        create_rois_from_filename(filename, self.mtg_ocr_config, card, verbose = 2)
    
        cardname = return_cardname_from_ROI(filename, self.scryfall_all_data, verbose =0)
        display_cardname(cardname)
        self.assertEqual(cardname[0]["name"],"Visage of Dread // Dread Osseosaur")
        print("name", cardname[0]['name'])
        print("set", cardname[0]['set'])
        self.assertEqual(cardname[0]["set"],"lci")

    @patch('src.Card_Identification.process_card.PathType', PathType)    
    @patch('src.Card_Identification.path_manager.PathType', PathType)
    @patch('src.Card_Identification.configuration_handler.PathType', PathType)
    @patch('src.Card_Identification.card_extraction.PathType', PathType)
    @patch('src.Card_Identification.process_rois.PathType', PathType)
    def test_create_rois_from_filename_foodtoken(self):
          # Food Token ELD
        filename = "3.jpg"
        path = get_path(PathType.RAW_IMAGE, filename)
        card, error = extract_card(path,verbose = 1)
        if error != None:
            print("error:", error)
         
        self.mtg_ocr_config.set_relative_coordinates(card, verbose =1)
        create_rois_from_filename(filename, self.mtg_ocr_config, card, verbose = 2)
    
        cardname = return_cardname_from_ROI(filename, self.scryfall_all_data, verbose =0)
        display_cardname(cardname)
        # display_cardname(cardname)
        self.assertEqual(cardname[0]["name"],"Food")
        self.assertEqual(cardname[0]["set"],"teld")

    @patch('src.Card_Identification.process_card.PathType', PathType)    
    @patch('src.Card_Identification.path_manager.PathType', PathType)
    @patch('src.Card_Identification.configuration_handler.PathType', PathType)
    @patch('src.Card_Identification.card_extraction.PathType', PathType)
    @patch('src.Card_Identification.process_rois.PathType', PathType)
    def test_create_rois_from_filename_goblin(self):
        # Goblin Token GRN
        filename = "2.jpg"
        path = get_path(PathType.RAW_IMAGE, filename)
        card, error = extract_card(path,verbose = 1)
        if error != None:
            print("error:", error)
        self.mtg_ocr_config.set_relative_coordinates(card, verbose =1)
        create_rois_from_filename(filename, self.mtg_ocr_config, card, verbose = 0)
        cardname = return_cardname_from_ROI(filename, self.scryfall_all_data, verbose =0)
        display_cardname(cardname)
        # display_cardname(cardname)
        self.assertEqual(cardname[0]["name"],"Goblin")
        # cant check for set because resolution  is to low
        # self.assertEqual(cardname[0]["set"],"grn")
    
    @patch('src.Card_Identification.process_card.PathType', PathType)    
    @patch('src.Card_Identification.path_manager.PathType', PathType)
    @patch('src.Card_Identification.configuration_handler.PathType', PathType)
    @patch('src.Card_Identification.card_extraction.PathType', PathType)
    @patch('src.Card_Identification.process_rois.PathType', PathType)
    def test_create_rois_from_filename_asmo(self):
        # Asmoranomardicadaistinaculdacar from mh2
        filename = "1.jpg"
        path = get_path(PathType.RAW_IMAGE, filename)
        card, error = extract_card(path,verbose = 0)
        if error != None:
            print("error:", error)
        self.mtg_ocr_config.set_relative_coordinates(card, verbose =1)
        create_rois_from_filename(filename, self.mtg_ocr_config, card, verbose = 0)
        cardname = return_cardname_from_ROI(filename, self.scryfall_all_data, verbose =1)
        display_cardname(cardname)
        # display_cardname(cardname)
        self.assertEqual(cardname[0]["name"],"Asmoranomardicadaistinaculdacar")
        # cant check for set because resolution is to bad
        # self.assertEqual(cardname[0]["set"],"mh2")
            
if __name__ == '__main__':
    unittest.main()

