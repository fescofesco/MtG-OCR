# [MtG-OCR](https://github.com/fescofesco)
This program identifies [Magic the Gathering (MtG)](https://magic.wizards.com/en) cards from images by optical-character-recognition (OCR) _via_ [pytesseract](https://github.com/UB-Mannheim/tesseract).
The cards are safed as a [cubecobra](www.cubecobra.com) cube file in `~/git/MtG-OCR/data/Card_Identification/results/CubeCobra_DATETIME.csv`. 
The program requires one card per image. The card may not project out of the image.
# Setup 

Start by installing the required modules.
```text
  pip install -r requirements.txt
  
```

Install [pytesseract](https://github.com/UB-Mannheim/tesseract).
This version was tested with `tesseract-ocr-w64-setup-5.3.3.20231005.exe`.
Set pytesseract path to `C:/Programm Files(x86)/Tesseract-OCR/`.

 This step is optional:
 To use the `adb` mode, install [adb](https://github.com/google/python-adb) first. Enable debugging on your android device. See [https://developer.android.com/tools/adb](https://developer.android.com/tools/adb) for an explanation on how to enable debugging.
 Prepare a folder named `MTG-OCR` on your android device and safe card images there.

The package is not uploaded to pip yet. The modules cannot be imported via the package path, yet.



# Workflow

## Running the program
### Start the main function 
The main function is located in `~/git/MtG-OCR/scr/Card_Identification/main_Card_Identification.py` and called `main_Card_Identification(mode:str = None, verbose = 2)`.
The suggested mode is `quickstart`.

__Modes__
* `quickstart` Select the folder where the card images are present. The images are safed to the internal working direction. All already present images will be moved to subfolders with the current DATETIME. Only the selected cards will be processed.
* `all files`: The images must be safed to `~/git/MtG-OCR/data/Card_Identification/raw_IMGs` beforehand. Then the contents of the selected folder is processed within the working directory (`~/git/MtG-OCR/data/Card_Identification/raw_IMGs`).
All these images are processed. 
*  `adb`: At program start all images from the folder `MTG-OCR` on the connected android device  are downloaed and transfered _via_ adb to the working directory 
`~/git/MtG-OCR/data/Card_Identification/raw_IMGs`. All images from the android device are processed. 
*  `adb-live`: Like adb, but the image contents of the MtG-OCR folder are downloaed continuously and only the newest image is processed. After each processed card a new image needs to be taken. This mode is suited for live analysis.
### Output
The location of the safed files is 
`~/git/MtG-OCR/data/Card_Identification/results`.

__The__ results are safed as: 
* `results_DATETIME.txt`: identified card as a list of [scryfall data](https://scryfall.com/docs/api/cards) `[["filename1.jpg",{dict of scryfall_data of filename1}]]`
* `identified_cards_DATETIME.txt`:  a list of filename the correspondig list  
`[["filename1.jpg",[name,CMC,Type,Color,Set,Collector Number,Rarity,Color Category,status,Finish,maybeboard,image URL,image Back URL,tags,Notes,MTGO ID]]` 

* `unidentified_cards_DATETIME.txt`: a list of filenames which could not be identified
`[["filename1.jpg"]]`
* `CubeCobraCSV.csv`: Created from `identified_cards_DATETIME.txt`. This `.csv` file can be exported manually to [cubecobra](www.cubecobra.com) to exchange ones cube.
## Explanation of the program 
The scripts are safed in `~/git/MtG-OCR/scr/Card_Identification`



	
1. The program is started with the function  `main_Card_Identification(mode:str = None, verbose = 2)` in`~/git/MtG-OCR/scr/Card_Identification/main_Card_Identification.py`. 
2. The function `extract_card(path_to_image, verbose)` in `card_extraction.py` outputs just the card part of an image (displaying a single card) as a [CV2](https://github.com/opencv/opencv) image. `Error`  shall be `None` or is a `str` if something went wrong.
	
```python
path_to_img = ../../MtG-OCR/data/Card_Identification/raw_image/ imagename.jpg

	def extract_card(path_to_img, verbose=0)
	
	return error, card
```

3. The card is processed with `create_rois_from_filename(filename, mtg_ocr_config, card= None, verbose =0)`in `~/git/MtG-OCR/scr/Card_Identification/process_card.py`

	This function gets input from `extract_card()` and creates ROIs (pictures of regions of interest) in the directory
`~/git/MtG-OCR/data/Card_Identification/processed_ROI/ imagename.jpg`


4. The rois are pcoessed with ` return_cardname_from_ROI(filename, scryfall_all_data, verbose = 0) --> Cardname` in `~/git/MtG-OCR/scr/Card_Identification/process_rois.py`
	
	This function checks the rois for information to extract the cardname, set and collector_number. Output is `Cardname` which is a list of dicts of fitting scryfall entries. The list is sorted according to the [levenshtein distance](https://github.com/rapidfuzz/python-Levenshtein) of the identified cardnames, sets and collector_numbers in comparision to the scryfall card data. The first entry is the best fitting card data. 

5.  The user confirms the found cardname, collector_number, and set with `user_cardname_confirmation(filename, card_infos, card_data, card, scryfall_file, mtg_ocr_config, default_action=None)` in `~/git/MtG-OCR/scr/Card_Identification/user_dialog_cardname.py`.

6. The results are safed with `write_results_to_file(card_names, name=None, nodatetime=None, location=None)` in `~/git/MtG-OCR/scr/Card_Identification/save_results.py`.
	
## Notes
### Program Handling
If `verbose > 0` the program will keep displaying images, and not move on, until the
the user presses any key.
An exception to this rule is when the user defines new ROIs. Read the window name then.
The ROIs are defined by clicking inside the window. Green squares appear and define the ROI. To save the ROIs press `ENTER`. Quit the window by pressing `q`, `Q` or `ESC`.

### Verbose
Errors shall always be printed.
Output in terminal:
* `verbose == 0`: no output except the image of the card and the dialog to identify the card
* `verbose == 1`: the above and output of the filepath and the identified potential cardnames, sets and collector_number
* `verbose > 1`: the above and the display of internally createdd images and collected informations.

