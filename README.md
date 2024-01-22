# MtG-OCR

This program allows for Magic the Gathering Cards (MtG) identification recognition from images.

The program is structured in several steps which are located on several scripts. Each script has one main func and is currently able to get started by its own. 
To test the program either start the individual scripts or the tests stored in the ../../MtG-OCR/test/Card_Identification folder


# Setup 

pip install -requirments

```text
  pip install -r requirements.txt
  
```

install pystessearct and set it to path
```text
  pip install pytesseract
  
```
and set it to path
`C:\Programm Files(x86)\Tesseract-OCR\'

if you want to use the "adb" mode, install 
[adb](https://github.com/google/python-adb)
Note, adb  will change in further releases to [adb-shell](https://github.com/JeffLIrion/adb_shell)


# Workflow

## 0) 
Run 
`~\git\MtG-OCR\scr\Card_Identification\main_Card_Identification.py`
wit the mode  `"quickstart"`
"quickstart" allows to select the folder the card images are present. Then the images are safed to the internal working direction. All already present images will be moved to subfolders with the current DATETIME. 

and then run 
`~\git\MtG-OCR\scr\Card_Identification\main_Card_Identification.py`



Alternatively, the images can be directoly safed  to 
`~\git\MtG-OCR\data\Card_Identification\raw_IMGs` 

and 
`~\git\MtG-OCR\scr\Card_Identification\main_Card_Identification.py` can be run with `"all files"`.

the `"adb"` mode automatically downloads all images to the correct working directory 
`~\git\MtG-OCR\data\Card_Identification\raw_IMGs` 



## 1) card_extraction.py 	
```python
path_to_img = ../../MtG-OCR/data/Card_Identification/raw_image/ imagename.jpg

	def extract_card(path_to_img, verbose=0)
```
return card as cv2 images
this func finds the image 


## 2) #process_card.py
```python
def create_rois_from_filename(filename, mtg_ocr_config, card= None, verbose =0):
```
gets input from extract_card() and creates ROIS in the directory
creates rois in `~\git\MtG-OCR\data\Card_Identification\processed_ROI\ imagename.jpg`


## 3) #process_rois
```python
def return_cardname_from_ROI(filename, scryfall_all_data, verbose = 0):
```

checks the rois for information and 



a DATETIME.txt file with all the results in form of a list of scryfall_dicts and the image name will be created in 
MtG-OCR\data\Card_Identification\results


Notes:
if `verbose >0`, the program will display images as long as the user clicks any key. 
except when defining new ROIs to be analysed from the user, then read the window name:
by clicking in the image window the ROI can be defined, if defined correctly press `ENTER` so the ROI will be saved and analysed later. If finished with defining ROIS, quit by pressing `'q'`, `'Q'` or `'ESC'`
