# -*- coding: utf-8 -*-
"""
process_card.py
Created on Thu Nov 23 19:48:06 2023

@author: Felix Scope
"""
import cv2
import os
from card_extraction import extract_card
from configuration_handler import MtGOCRData



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
       card = extract_card(filename, verbose = 0)
       
    title = filename.strip(".jpg")
    modes = ["exp", "ui", "name"]

    for mode in modes:
        coordinates = mtg_ocr_config.get_coordinates_from_file(mode)
        generated_roi = get_roi(card, coordinates, title, verbose)
        for i, roi in enumerate(generated_roi):
            safe_card_roi(roi, title=f"{title}", mode=mode)


def get_roi(card, coordinates=[[0.813, 0.56],[0.91, 0.63]], title="roi1", verbose=1):
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
    roi ... cv2 image inside the specified corner coordinats [[x0,y0],[x1,y1]]

    Currently the return function does not work, only yield to create a generator
    which can be unpacked with the fololwoing syntax
    """
    if not isinstance(coordinates[0][0], list):
        coordinates = [coordinates]
      
    # Currently the return function does not work, only yield to create a generator
    # which can be unpacked with the fololwoing syntax
    if len(coordinates) == 1:
        coord_pair = coordinates[0]
        x0, y0 = coord_pair[0]
        x1, y1 = coord_pair[1]
        height, width, _ = card.shape
        top_left = (int(width * x0), int(height * y0))
        bottom_right = (int(width * x1), int(height * y1))
        roi = card[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]

        if verbose > 0:
            cv2.imshow(title, roi)
            cv2.waitKey(0)
            cv2.destroyWindow(title)
        return roi
        
    else:
        for coord_pair in coordinates:
            x0, y0 = coord_pair[0]
            x1, y1 = coord_pair[1]
            height, width, _ = card.shape
            top_left = (int(width * x0), int(height * y0))
            bottom_right = (int(width * x1), int(height * y1))
            roi = card[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
            
            if verbose > 0:
                cv2.imshow(title, roi)
                cv2.waitKey(0)
                cv2.destroyWindow(title)
            yield roi  


def safe_card_roi(card_roi, title='filename', mode='roi', verbose=0):
    # Ensure the folder exists to save the ROIs
    if not os.path.exists("ROIs"):
        os.makedirs("ROIs")

    # Find the version number for the filename
    version = 1
    while os.path.exists(f"ROIs/{title}_{mode}_{version}.jpg"):
        version += 1

    # Construct the filename using the mode, title, and version
    filename = f"ROIs/{title}_{mode}_{version}.jpg"

    # Save the ROI with the constructed filename
    cv2.imwrite(filename, card_roi)
    if verbose >0:
        print("Try to write ROIs/{title}_{mode}_{version}.jpg",title,mode, version)
    
def checkif_imageloaded(result, error_message = None):
    if error_message == "Image not loaded":
        # Handle image loading error
        retry_count = 0
        max_retries = 3
        
        while retry_count < max_retries:
            mtg_ocr_config.set_image_location()
            retry_result, retry_error = extract_card("1.jpg")
            if retry_result is not None:
                return retry_result
            else:
                retry_count += 1
        
        print("Image not found even after retrying.")
        return None
    else:
        # Process the result when the image was loaded successfully
        # Do something with the result
        return result
            
if __name__ == "__main__":
    
    #  get the necessary parameters from confiog parameters.txt handler
    mtg_ocr_config  = MtGOCRData()
    storage_directory = mtg_ocr_config.get_img_directory()

    filename = "IMG_20231222_111834.jpg"   
    path = storage_directory + "/" + filename
    print(path)
    card, error = extract_card(path,verbose = 2)
    if error != None:
        print(error)
 
    mtg_ocr_config.get_relative_coordinates(card)
    create_rois_from_filename(filename, mtg_ocr_config, card)
    
    
   

