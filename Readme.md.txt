MtG-OCR

This script allows card identification of images. Only one card per
image, but easy implementable to allow more. Currently the whole card must be 
visisble.

Setup 

pip install -requirments
install pystessearct and set it to path
C:\Programm Files(x86)\Tesseract-OCR\





Safe cards to 
MtG-OCR\data\Card_Identification\raw_IMGs

and run main_Card_Identification in 

MtG-OCR\scr\Card_Identification\main_Card_Identification.py

a DATETIME.txt file with all the results in form of a list of scryfall_dicts and the image name will be created in 
MtG-OCR\data\Card_Identification\results

Notes:
if verbose >0, the program will display images as long as the user clicks any key. 
except when defining new ROIs to be analysed from the user, then read the window name:
by clicking in the image window the ROI can be defined, if defined correctly press ENTER so the ROI will be saved and analysed later. If finished with defining ROIS, quit by pressing 'q' 'Q' or 'ESC'
