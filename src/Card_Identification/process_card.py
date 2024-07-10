# -*- coding: utf-8 -*-
"""
process_card.py
Created on Thu Nov 23 19:48:06 2023

@author: Felix Scope

Main func of this script is create_rois_from_filename()
Three region of interest (ROIs) are extracted from each card provided as cv2 img.
These ROIs are then stored in data/ROIs

Example usage:
    
create_rois_from_filename(filename, mtg_ocr_config, card= None, verbose =0):

    
    
"""
import cv2
import os
from card_extraction import extract_card
from configuration_handler import MtGOCRData
from path_manager import (get_path, PathType)

def create_rois_from_filename(filename, mtg_ocr_config, card= None, verbose =0):
    """
    this is the main function of process_cards.py
    here, by providing a filename and possibly a card, ROIs (snippets of region
    of interest) are created and saved in the folder working directory /ROIs
    
    these images can then be accessed by the function 
    return_cardname_from_ROI(filename, scryfall_all_data, verbose = 0, 
                             roi_directory = 'ROIs'):
    from the file process_rois.py

    Parameters
    ----------
    filename : STR
        the filename
    card : CV2 image , optional
        the image of the card, not the card image.  
        The default is None. If not provided, the card snippet is provided 
        internally. But by doing so, it is more difficult to check if the image
        contains a card, this logic is normally implemented in main.py and 
        not giving a card should therefore only be done when knwoing that a card
        can be found -> in testing purposes.

    Returns
    -------
    None.
    but in the folder /ROIs the rois in the format 
    f"ROIs/{title}_{mode}_{version}.jpg"
    
    title = filename -.jpg, 
    mode = 'ui, 'exp', 'name' 
    version = counting up to so multiple rois of each mode / img can be created

    """
    if card is None:
       card = extract_card(get_path(PathType.RAW_IMAGE,filename), verbose)
    
    mtg_ocr_config = MtGOCRData()
    
    title = filename.strip(".jpg")
    modes = ["name", "ui", "exp", "full"]

    for mode in modes:
        if mode != "full":
            coordinates = mtg_ocr_config.get_coordinates_from_file(mode)
            generated_roi = get_roi(card, coordinates, title, verbose)
        elif mode == "full":
            generated_roi = get_roi(card =card,coordinates = [[[0,0],[1,1]]],title=title, verbose = verbose)
        else:
            print("Could not recognise mode : ",mode)
        for i, roi in enumerate(generated_roi):
            safe_card_roi(roi, title, mode, verbose)


def get_roi(card, coordinates=None, title=None, verbose=1):
    """
    Returns a ROI (region of interest) definded by the coordinates, the two 
    corner points defining a rectanlge from a provided cv2 image card.

    Parameters
    ----------
    card : TYPE
        DESCRIPTION.
    coordinates : TYPE, optional
        DESCRIPTION. The default is [[0.813, 0.56],[0.91, 0.63]].
    title : TYPE, optional
        DESCRIPTION. The default is "roi1".
    verbose : TYPE, optional
        DESCRIPTION. The default is 1.

    Yields
    ------
    roi : TYPE
        DESCRIPTION.

    """
    """
    def get_roi(card, coordinates=[[0.813, 0.56],[0.91, 0.63]], title="roi1", verbose=1):

    returns the region of interest (roi) of an image with the specified coordinates
    and the title if you want to save the picture as file
    if title == None no output is generated

    inputs

    card ... the cv2 image of the card the roi is to be extracted
    coordinates [[x0, y0], [x1, y1]]... the coordinates of the rectangular
         the card shall be extracted from
    verbose ... how much output the function has, if
            0 no output
            1 the rectangular snipping is displayed on top of the card file
            
    output
    roi ... generator of cv2 image inside the specified corner coordinats 
            [[x0,y0],[x1,y1]]

    """
    if title is None:
        title = "roi1"
        
    if coordinates is None:
        print("File doew not contain valid coordinates. Content:")
        print(coordinates)
        return None
    
    if not isinstance(coordinates[0][0], list):
      coordinates = [coordinates]
      print("coordinates were changed")
      print(coordinates)


    
    for coord_pair in coordinates:
        x0, y0 = coord_pair[0]
        x1, y1 = coord_pair[1]
        height, width, _ = card.shape
        top_left = (int(width * x0), int(height * y0))
        bottom_right = (int(width * x1), int(height * y1))
        
     
        roi = card[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
    
        if verbose > 3:
            print("title in get roi", title)
            cv2.imshow(title, roi)
            cv2.waitKey(0)
            if cv2.getWindowProperty(title, cv2.WND_PROP_VISIBLE) == 1:
                  cv2.destroyWindow(title)
        yield roi
      


def safe_card_roi(card_roi, title='filename', mode='roi', verbose=0):
    # Find the version number for the filename
    version = 1
    path_to_roi = get_path(PathType.PROCESSED_ROI)
    if verbose >2: print("path to roi", path_to_roi)
    while os.path.exists(f"{path_to_roi}/{title}_{mode}_{version}.jpg"):
        version += 1
        if verbose >2:
            print("version +1 of", 
                  f"{path_to_roi}/{title}_{mode}_{version}.jpg")

    # Construct the filename using the mode, title, and version
    out_path = f"{path_to_roi}/{title}_{mode}_{version}.jpg"
    cv2.imwrite(get_path(PathType.PROCESSED_ROI, out_path), card_roi)
  
    if verbose >2:
        print(f"Write ROIs {title}_{mode}_{version}.jpg")
        
    out_path_crop = f"{path_to_roi}/{title}_{mode}_{version}_crop.jpg"


   


            
if __name__ == "__main__":
    #  get the necessary parameters from confiog parameters.txt handler
    mtg_ocr_config  = MtGOCRData()
    # put iamage as filename in path
    filename = "1.jpg"
    path = get_path(PathType.TEST_RAW_IMAGE, filename)
    print("path: ",path)
    card, error = extract_card(path,verbose = 0)
    if error != None:
        print(error)
    create_rois_from_filename(filename, mtg_ocr_config, card,verbose =3)

