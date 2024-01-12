# MtG-OCR

This program allows for Magic the Gathering Cards (MtG) identification recognition from images.

The program is structured in several steps which are located on several scripts. Each script has one main func and is currently able to get started by its own. 
To test the program either start the individual scripts or the tests stored in the ../../MtG-OCR/test/Card_Identification folder


# Setup 

pip install -requirments
install pystessearct and set it to path
C:\Programm Files(x86)\Tesseract-OCR\






# 0) 

Safe cards to 
MtG-OCR\data\Card_Identification\raw_IMGs

and run main_Card_Identification in 

MtG-OCR\scr\Card_Identification\main_Card_Identification.py



a DATETIME.txt file with all the results in form of a list of scryfall_dicts and the image name will be created in 
MtG-OCR\data\Card_Identification\results

# 1) card_extraction.py 	
path_to_img = ../../MtG-OCR/data/Card_Identification/raw_image/ imagename.jpg
def extract_card(path_to_img, verbose=0)
return card as cv2 images
this func finds the image 


# 2) #process_card.py
def create_rois_from_filename(filename, mtg_ocr_config, card= None, verbose =0):
gets input from extract_card() and creates ROIS in the directory
creates rois in ../../MtG-OCR/data/Card_Identification/processed_ROI/ imagename.jpg


# 3) #process_rois
def return_cardname_from_ROI(filename, scryfall_all_data, verbose = 0):
checks the rois for information and 

Change to the project directory and run:

pip install -r requirements.txt






Notes:
if verbose >0, the program will display images as long as the user clicks any key. 
except when defining new ROIs to be analysed from the user, then read the window name:
by clicking in the image window the ROI can be defined, if defined correctly press ENTER so the ROI will be saved and analysed later. If finished with defining ROIS, quit by pressing 'q' 'Q' or 'ESC'
