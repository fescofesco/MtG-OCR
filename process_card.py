# -*- coding: utf-8 -*-
"""
process_card.py
Created on Thu Nov 23 19:48:06 2023

@author: Felix Scope
"""
import cv2
import json
import os
from card_identification import identify_card


def create_rois_from_filename(filename, card= None):
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
       card = identify_card(filename, 0)
       
    title = filename.strip(".jpg")
    card = identify_card(filename,0)
    #  get relative coordinates is only necessary if rois are ill defined
    # get_relative_coordinates(card) 
    modes = ["exp", "ui", "name"]

    for mode in modes:
        coordinates = get_coordinates_from_file(mode)
        generated_roi = get_roi(card, coordinates, title=title, verbose=0)
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

 

def click_event(event, x, y, flags, param):
    """
    Remembers the clicks on an image to define rectangles as future ROIS for 
    subsequent OCR recognition. Saves the coordinates.

    Parameters
    ----------
    event : TYPE
        you can click 2 times.
    x : TYPE
        DESCRIPTION.
    y : TYPE
        DESCRIPTION.
    flags : TYPE
        DESCRIPTION.
    param : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    if event == cv2.EVENT_LBUTTONDOWN:
        param['clicked_points'].append((x, y))
        if len(param['clicked_points']) > 1:
            param['clicked_points'] = param['clicked_points'][-2:]  # Keep only the last 2 points
            draw_rectangle(param['image'], param['clicked_points'], param)

def draw_rectangle(image, points, param):
    """
    draws a rectanlge of the last 2 clicked points to define the coordinates
    for a ROI thats saved if enter is pressed.

    Parameters
    ----------
    image : TYPE
        DESCRIPTION.
    points : TYPE
        DESCRIPTION.
    param : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    if len(points) == 2:
        img_copy = image.copy()  # Create a copy of the image to draw the rectangle on
        cv2.rectangle(img_copy, points[0], points[1], (0, 255, 0), thickness=2)
        cv2.imshow(param['window_name'], img_copy)

def get_relative_coordinates(image, window_name='UI identifier, q to quit. Click coner points of UI, exp symbol or name and press enter after each selsection',
                             verbose =0, max_width=800, max_height=600):
    """
    this function help setting the coordinates for ui (unique identifier), name
    and expansion symbol. by clicking on both corner points of a rectangle that
    comprises the UI you want to safe the coordinates are written into
    paramters.txt file and can later be retrieved by 
    get_coordiantes_from_file("mode"), and be used to extract roi with 
    get_roi(card, coordinantes)
    
    clicking ... selects points that define the encompassing rectanlge 
    enter ... saves the rectangles coordinates depending on y- the position
        in "name",  "ui", "exp"
    'q' ... quits the function

    Parameters
    ----------
    image : cv2 image
        the card these identifiers shall be extracted from.
    window_name : STR, optional
        how to call the window.
        The default is 'UI identifier, q to quit. Click coner points of UI, 
        exp symbol or name and press enter after each selsection'.
    verbose : TYPE, optional
        DESCRIPTION. The default is 0.
    max_width : TYPE, optional
        DESCRIPTION. The default is 800.
    max_height : TYPE, optional
        DESCRIPTION. The default is 600.

    Returns
    -------
    None.

    """
    height, width, _ = image.shape
    scale = min(max_width / width, max_height / height)
    new_width = int(width * scale)
    new_height = int(height * scale)
    resized_image = cv2.resize(image, (new_width, new_height))

    param = {
        'width': new_width,
        'height': new_height,
        'image': resized_image,
        'clicked_points': [],
        'window_name': window_name
    }

    cv2.imshow(window_name, resized_image)
    cv2.setMouseCallback(window_name, click_event, param)

    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == 13:  # Check for 'Enter' key press
            points = tuple(param['clicked_points'])
            if len(points) == 2:
                relative_coordinates = [
                    (p[0] / param['width'], p[1] / param['height']) for p in points
                ]  # Calculate relative coordinates
                
                top_left = (min(relative_coordinates[0][0], relative_coordinates[1][0]), min(relative_coordinates[0][1], relative_coordinates[1][1]))
                bottom_right = (max(relative_coordinates[0][0], relative_coordinates[1][0]), max(relative_coordinates[0][1], relative_coordinates[1][1]))
                
                coordinates = (top_left, bottom_right)
                
                # coordinates = tuple(relative_coordinates)
                mode = determine_mode(relative_coordinates[0][1])  # Determine mode based on y position
                save_coordinates(mode, coordinates)  # Save coordinates to file based on mode
                get_roi(image, coordinates)  # Call get_roi function with mode and coordinates
                cv2.imshow(window_name, resized_image)
                cv2.setMouseCallback(window_name, click_event, param)
                
                if verbose > 0:
                    print(f"UI coordinates: {coordinates}")
 
    cv2.destroyWindow(window_name)
    cv2.destroyAllWindows()


def save_coordinates(mode, coordinates):
    with open('parameters.txt', 'r') as file:
        data = json.load(file)

    if mode not in data:
        data[mode] = []  # Create an empty list for the mode if it doesn't exist

    data[mode].append(coordinates)  # Append the new coordinates to the list

    with open('parameters.txt', 'w') as file:
        json.dump(data, file, indent=2)  # Save the updated data back to the file

def determine_mode(y_coordinate):
    """
    depends the relative height of the roi measured from the top of the card 
    to save it accordingly to either 
    
    'name' if roi is located on the top (0-0.35) of the card
    'exp'                    in the middle (0.36 - 0.7)
    'ui'                     at the bottom (0.71-1) of the card
    
    Parameters
    ----------
    y_coordinate : Float
       relative height of image

    Returns
    -------
    str
        mode 
        'name' name of the card
        'exp'  expansion smybol of the card
        'ui' unique identifier
              
    """
    if 0 <= y_coordinate <= 0.35:
        return 'name'
    elif 0.36 <= y_coordinate <= 0.7:
        return 'exp'
    elif 0.71 <= y_coordinate <= 1:
        return 'ui'
    else:
        return 'unknown'

    
def get_coordinates_from_file(mode):
    """
    gets the coordinates of the fie from the paramters.txt file 

    Parameters
    ----------
    mode : STR
        'ui', 'name' or 'exp'

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    with open('parameters.txt', 'r') as file:
        data = json.load(file)

    if mode in data:
        return data[mode]
    else:
        print("Error, parameters.txt not found or mode not found.")
        print(" mode: ", mode)
        
        return None


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
    
            
            
if __name__ == "__main__":
     
    filename = "1.jpg"
    card = identify_card(filename,0)
    create_rois_from_filename(filename, card)
    

    filename = "IMG_20231213_212201.jpg"
    create_rois_from_filename(filename)
   

