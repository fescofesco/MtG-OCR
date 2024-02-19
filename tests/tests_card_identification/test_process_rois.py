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
from path_manager import get_path
from configuration_handler import MtGOCRData
from process_card import (create_rois_from_filename)
from process_rois import (return_cardname_from_ROI, display_cardname, find_card_by_infos)
from test_path_manager import PathType




@patch('process_card.PathType', PathType)    
@patch('path_manager.PathType', PathType)
@patch('configuration_handler.PathType', PathType)
@patch('card_extraction.PathType', PathType)
@patch('process_rois.PathType', PathType)
class TestProcessCard(unittest.TestCase):
    mtg_ocr_config = None
    scryfall_all_data = None
    
    @classmethod
    def setUpClass(cls):
      if cls.mtg_ocr_config is None:
          cls.mtg_ocr_config = MtGOCRData()
          cls.scryfall_all_data = cls.mtg_ocr_config.open_scryfall_file()
          print("Initialization done")
          test_folder_path = get_path(PathType.PROCESSED_ROI)
          for file_name in os.listdir(test_folder_path):
              file_path = os.path.join(test_folder_path, file_name)
              try:
                  if os.path.isfile(file_path):
                      os.unlink(file_path)
              except Exception as e:
                  print(f"Failed to delete {file_path}. Error: {e}")

          #  get the necessary parameters from confiog parameters.txt handler
          

    def tearDown(self):
    # This method will be called after each test method is executed
        cv2.waitKey(1)
           
    
    # def test_create_rois_from_filename_visageofDrad_doubleside(self):
        
    #     #  Visage of Dread, LCI 
    #     filename = "4.jpg"
    #     path = get_path(PathType.RAW_IMAGE, filename)
    #     card, error = extract_card(path,verbose = 1)
    #     if error != None:
    #         print("error:", error)
         
    #     # self.mtg_ocr_config.set_relative_coordinates(card, verbose =1)
    #     create_rois_from_filename(filename, self.mtg_ocr_config, card, verbose = 0)
    
    #     cardname = return_cardname_from_ROI(filename, self.scryfall_all_data, verbose =3)
    #     display_cardname(cardname)
    #     self.assertEqual(cardname[0]["name"],"Visage of Dread // Dread Osseosaur")
    #     print("name", cardname[0]['name'])
    #     print("set", cardname[0]['set'])
    #     self.assertEqual(cardname[0]["set"],"lci")
       
    def test_best_match(self):
        
        cardname_by_name = ['X', 'Murderous Cut', 'Cut // Ribbons', 'Murderous Cut', 'Murderous Cut'] 
        cardname_by_name = set(list(cardname_by_name))
        

        pot_sets = ['Ser', 'IOR', 'OAN', '812', 'NNS', 'VUT', 'ale', 'CHE', 'KTK', 'ACZ', 'SEG', '69U', 'NSC', '081', 'HEP', 'NAN', 'ENt', 'KEN', 's09', 'JOI', 'PAC', 'OHA', 'HAN', 'sOM', '269', 'eYO', 'ae0', 'UKT', 'teY']
        pot_rarities = ['U', 'R', 'T', 'C', 'M']

        # pot_sets = ['eld']
        
        pot_collectornumbers = ['269', '081', '09']

        best_match, possible_cards = find_card_by_infos(pot_collectornumbers, pot_sets, pot_rarities, cardname_by_name, self.scryfall_all_data, verbose=0)


        self.assertEqual(best_match["name"], "Murderous Cut")
        self.assertEqual(best_match["set"], "ktk")
        self.assertEqual(best_match["collector_number"], "81")
        
    def test_create_rois_from_filename_foodtoken(self):
          # Food Token ELD
        filename = "3.jpg"
        path = get_path(PathType.RAW_IMAGE, filename)
        card, error = extract_card(path,verbose = 1)
        if error != None:
            print("error:", error)
         
        # self.mtg_ocr_config.set_relative_coordinates(card, verbose =1)
        create_rois_from_filename(filename, self.mtg_ocr_config, card, verbose = 0)
    
        cardname = return_cardname_from_ROI(filename, self.scryfall_all_data, verbose =1)
        display_cardname(cardname)
        # display_cardname(cardname)
        self.assertEqual(cardname[0]["name"],"Food")
        self.assertEqual(cardname[0]["set"],"teld")
       
           

    def test_create_rois_from_filename_goblin(self):
        # Goblin Token GRN
        filename = "2.jpg"
        path = get_path(PathType.RAW_IMAGE, filename)
        card, error = extract_card(path,verbose = 0)
        if error != None:
            print("error:", error)
        # self.mtg_ocr_config.set_relative_coordinates(card, verbose =1)
        create_rois_from_filename(filename, self.mtg_ocr_config, card, verbose = 2)
        cardname = return_cardname_from_ROI(filename, self.scryfall_all_data, verbose =1)
        display_cardname(cardname)
        # display_cardname(cardname)
        self.assertEqual(cardname[0]["name"],"Goblin")
        # cant check for set because resolution  is to low
        # self.assertEqual(cardname[0]["set"],"grn")
   

    def test_create_rois_from_filename_asmo(self):
        # Asmoranomardicadaistinaculdacar from mh2
        filename = "1.jpg"
        path = get_path(PathType.RAW_IMAGE, filename)
        card, error = extract_card(path,verbose = 0)
        if error != None:
            print("error:", error)
        # self.mtg_ocr_config.set_relative_coordinates(card, verbose =1)
        create_rois_from_filename(filename, self.mtg_ocr_config, card, verbose = 0)
        cardname = return_cardname_from_ROI(filename, self.scryfall_all_data, verbose =1)
        display_cardname(cardname)

        self.assertEqual(cardname[0]["name"],"Asmoranomardicadaistinaculdacar")
        # cant check for set because resolution is to bad
        self.assertEqual(cardname[0]["set"],"mh2")
  
    def test_create_rois_from_filename_sword(self):
        # Asmoranomardicadaistinaculdacar from mh2
        filename = "5.jpg"
        path = get_path(PathType.RAW_IMAGE, filename)
        card, error = extract_card(path,verbose = 0)
        if error != None:
            print("error:", error)
        # self.mtg_ocr_config.set_relative_coordinates(card, verbose =1)
        create_rois_from_filename(filename, self.mtg_ocr_config, card, verbose = 0)
        cardname = return_cardname_from_ROI(filename, self.scryfall_all_data, verbose =1)
        display_cardname(cardname)

        self.assertEqual(cardname[0]["name"],"Sword of Forge and Frontier")
        # cant check for set because resolution is to bad
        self.assertEqual(cardname[0]["set"],"one")
  
if __name__ == '__main__':
    unittest.main()
    cv2.waitKey(0)
    cv2.destroyAllWindows()
