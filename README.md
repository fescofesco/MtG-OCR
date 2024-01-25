# [MtG-OCR](https://github.com/fescofesco)

This program allows for Magic the Gathering Cards (MtG) identification recognition from images.

The program is structured in several steps which are located on several scripts. Each script has one main func and is currently able to get started by its own. 
To test the program either start the individual scripts or the tests stored in the `~git/MtG-OCR/test/Card_Identification` folder


# Setup 

Start by installing the required modules.
```text
  pip install -r requirements.txt
  
```

install [pytesseract](https://digi.bib.uni-mannheim.de/tesseract/)

and set it to path
`C:/Programm Files(x86)/Tesseract-OCR/'

To use the "adb" mode, install 
[adb](https://github.com/google/python-adb) first.
In further versions adb  will change be replaced with [adb-shell](https://github.com/JeffLIrion/adb_shell).


# Workflow

1.  ### Start the main function 
The main function is located in `~/git/MtG-OCR/scr/Card_Identification/main_Card_Identification.py`
The suggested mode is `quickstart`.
* `quickstart` allows to select the folder the card images are present. Then the images are safed to the internal working direction. All already present images will be moved to subfolders with the current DATETIME. 
and then run 
`~/git/MtG-OCR/scr/Card_Identification/main_Card_Identification.py`
* `all files`: Alternatively, the images can be directoly safed  to 
`~/git/MtG-OCR/data/Card_Identification/raw_IMGs` 
and `~/git/MtG-OCR/scr/Card_Identification/main_Card_Identification.py` can be run with `all files`.
*  `adb` mode automatically downloads all images from the folder `MtG-OCR` on the android device  to the correct working directory 
`~/git/MtG-OCR/data/Card_Identification/raw_IMGs`. Debugging must be enabled. See [https://developer.android.com/tools/adb](https://developer.android.com/tools/adb) 



2. ### card_extraction.py 	
```python
path_to_img = ../../MtG-OCR/data/Card_Identification/raw_image/ imagename.jpg

	def extract_card(path_to_img, verbose=0)
	
	return error, card
```
A single card is returned as cv2 (cv2 is a pyton module) image from an image containing a single card. 



3. ### process_card.py
```python
def create_rois_from_filename(filename, mtg_ocr_config, card= None, verbose =0):
```
This func gets input from `extract_card()` and creates ROIS (pictures of regions of interest) in the directory
`~/git/MtG-OCR/data/Card_Identification/processed_ROI/ imagename.jpg`


4. ###  process_rois.py
```python
def return_cardname_from_ROI(filename, scryfall_all_data, verbose = 0):
```

This func checks the rois for information to extract the cardname, set and collectornumber.

5. ### user_dialog_cardname.py

The user confirms the found cardname, collector number, and set.  

6. ### safe_results.py
```python
def write_results_to_file(card_names, name=None, nodatetime=None, location=None):
```
The results are safed as 
results_DATETIME.txt --> identified card as a list of scryfall data 
identified_card_DATETIME.txt --> filename and a list  
"name,CMC,Type,Color,Set,Collector Number,Rarity,Color Category,status,Finish,maybeboard,image URL,image Back URL,tags,Notes,MTGO ID" which can be then safed as a .csv file to exported to [cubecobra](www.cubecobra.com)
unidentified_card_DATETIME.txt --> filenames which could not be identified
file with all the results in form of a list of 
scryfall_dicts and the image name will be created in 
`~MtG-OCR/data/Card_Identification/results`

# Results
The location of the safed files is 
`~/git/MtG-OCR/data/Card_Identification/results` 



# Notes
If verbose `> 0` the program will keep displaying images, and not move on, until the
the user presses any key.

Except when defining new ROIs to be analysed from the user, then read the window name:
by clicking in the image window the ROI can be defined, if defined correctly press `ENTER` so the ROI will be saved and analysed later. If finished with defining ROIS, quit by pressing `'q'`, `'Q'` or `'ESC'`
