# MtG-OCR


This program allows for Magic the Gathering Cards (MtG) identification recognition from images.

The program is structured in several steps which are located on several scripts. Each script has one main func and is currently able to get started by its own. 
To test the program either start the individual scripts or the tests stored in the ../../MtG-OCR/test/Card_Identification folder



1) card_extraction.py 	
path_to_img = ../../MtG-OCR/data/Card_Identification/raw_image/ imagename.jpg
def extract_card(path_to_img, verbose=0)
return card as cv2 images
# this func finds the image 


2) #process_card.py
def create_rois_from_filename(filename, mtg_ocr_config, card= None, verbose =0):
# gets input from extract_card() and creates ROIS in the directory
creates rois in ../../MtG-OCR/data/Card_Identification/processed_ROI/ imagename.jpg


3) #process_rois
def return_cardname_from_ROI(filename, scryfall_all_data, verbose = 0):
# checks the rois for information and 

Change to the project directory and run:

pip install -r requirements.txt