# -*- coding: utf-8 -*-
"""
# card_extraction.py

Created on Thu Nov 16 08:39:30 2023

@author: Felix Scope

This scirpt allows card extraction of images. Only one card per
image, but easy implementable to allow more. Currently the whole card must be 
visisble.

Main function is 
    extract_card(path_to_img_folder, verbose=1):
        
This script is the first step of the project MtG-OCR after image aquisition and
location to data/Img_Storage.
A single card is identified from an image. Make sure that 
    the card is whole visible
    the background the ard is laying on has a contrast to the cards edges and
    is in the best case absent from any fractures / details -> just one color.

"""

import os
import cv2
import imutils
import numpy as np
from src.Card_Identification.path_manager  import get_path

def extract_card(path_to_img, verbose=0):
    """
    Identifies the card in an image and returns a image containing just the
    card. 
    First, card is resiszed to 300 px as then the outline "curcature" is easier
    to find for cv2.findContours . In the full size image the outline contur is 
    often not found correctly as it is to detailed. 
    if the controus are not found first, a iamge filter is overlayed for 
    upper and higher HSV oragne bounds
    Lower HSV (0,0,0)
    Upper HSV:  (179, 88, 255).

    Parameters
    ----------
    path_to_img : STR
    
        path_to_img  path to image file that needs to be 
                analysed can either be a relative path -> to call subfolder
                or full absolute path. The default subfolder is called /Img Storage
                
    verbose : INT, optional
        DESCRIPTION. The default is 1.
        verbose ... int 0,1,2 ... controls output for user 
            0 ... no output
            1 ... show card image that is the output for the next question
            2 ... show all internal created images during the program
            3 ... show how conrers are created

    Returns
    -------
    result : CV2 image of containing only the exracted card
            or None if no card area was found..
    error_message: error_message if no contours were found
    
    "Image not loaded. Check the image path"
    "Contours not found"
    
    """
    # Check if jpg or filename withoug .jpg was provided
    if not path_to_img.endswith('.jpg'):
        path_to_img = path_to_img + '.jpg'
    

    if not os.path.isabs(path_to_img):  # Check if the path is relative
        full_path = os.path.join(path_to_img)
    else:
        full_path = path_to_img  # Use the provided full path
                
    if verbose >= 2:
        print("path of image: ", full_path)
        
    original_image = cv2.imread(full_path)
    
    if original_image is None:
        error_message = "Image not loaded. Check the image path"
        if verbose >0: print(error_message)
        return None, error_message
    else:
       # Proceed with image processing
       # image is the resized small image -> easier card contur identification 
       # 1) Taking in our image input and resizing its width to 300 pixels for 
       # easier contur identification
       image = imutils.resize(original_image, width=300)
    
    if verbose >=2:
        cv2.imshow("original image", image)
    
    # 2) Converting the input image to greyscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if verbose >=2:
        cv2.imshow("greyed image", gray_image)
     

    # 3) Reducing the noise in the greyscale image
    gray_image = cv2.bilateralFilter(gray_image, 11, 17, 17) 
    if verbose >=2:
        cv2.imshow("smoothened image", gray_image)
    
    # 4) Detecting the edges of the smoothened image
    edged = cv2.Canny(gray_image, 25, 200) 
    if verbose >=2:
        cv2.imshow("edged image", edged)
        
    
    # 5) Dilate the image to join the edge
    # Calculate the percentage value for the kernel size
    kernel_percentage = 0.01  # Set the percentage 
    
    # Calculate the kernel size based on image width and height
    image_height, image_width = image.shape[:2]  # Retrieve image dimensions
    kernel_width = int(image_width * kernel_percentage)
    kernel_height = int(image_height * kernel_percentage)

    # Create a variable-sized kernel for dilation, 1 % of image size
    kernel = np.ones((kernel_width, kernel_height), np.uint8)
    
    # Dilating the edges using the variable-sized kernel
    dilated_edges = cv2.dilate(edged.copy(), kernel, iterations=1)
    
 
    # 6) Finding the contours from the edged image
    # cv2.RETR_EXTERNAL... retrieve only the most external controus,
    # cv2.chain_approx_simple ... and copy only the corners of defining points
    cnts,_ = cv2.findContours(dilated_edges.copy(), cv2.RETR_EXTERNAL, 
                                cv2.CHAIN_APPROX_SIMPLE)

    if verbose >=2:     # display the contours
        image1=image.copy()
        cv2.drawContours(image1,cnts,-1,(0,255,0),3)
        cv2.imshow("contours external",image1)
        
    # 7) Sorting the identified contours - > getting the contour with the most 
    # area
    cnts_sorted = sorted(cnts, key = cv2.contourArea, reverse = True)[:1]
    screenCnt = None
    
    if verbose >= 2:
        image2 = image.copy()
        cnts_top4 = sorted(cnts, key = cv2.contourArea, reverse = True)[:4]
        cv2.drawContours(image2,cnts_top4,-1,(0,255,0),2)
        display_image("Top 4 contours",image2)
 
    # 8) convert it to a contour with 4 sides
    for c in cnts_sorted:
        perimeter = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.025 * perimeter, True)
        if len(approx) == 4: 
            screenCnt = approx      
    
    # no contour with 4 sides was found, redo contours by thresshold
    if screenCnt is None:
        if verbose > 1:
            print("redo contours by frame threshold")
        
        frame_threshold = cv2.inRange(image.copy(), (0, 0, 0), (179, 88, 255))
      
        # 5) Finding the contours from the edged image
        cnts,_ = cv2.findContours(frame_threshold, cv2.RETR_EXTERNAL, 
                                    cv2.CHAIN_APPROX_SIMPLE)
       
        image1=frame_threshold.copy()
        cv2.drawContours(image1,cnts,-1,(0,255,0),3)
        if verbose >=2:
            cv2.imshow("contours external redone after filter 2",image1)
           
      
        # 7) Finding the contour with four sides
        for c in cnts:
            perimeter = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.018 * perimeter, True)
            if len(approx) == 4: 
                screenCnt = approx
    
    if screenCnt is not None:  # Check if the contour is found
        # Convert screenCnt corners to a usable format for perspective 
        #   transformation
        corners = screenCnt.reshape(4, 2).astype(np.float32)
        
        # Using the transformation -finding the corners - on the original image
        original_height, original_width = original_image.shape[:2]
        resized_height, resized_width = image.shape[:2]
        
        # calculate the dimension ratios
        height_ratio = original_height / resized_height
        width_ratio = original_width / resized_width
        original_corners = corners.copy() 
        
        # find the corners
        original_corners[:, 0] *= width_ratio  # Adjust x-coordinates
        original_corners[:, 1] *= height_ratio  # Adjust y-coordinates
               
        # Convert the original_corners to integers
        original_corners = original_corners.astype(np.int32)
        if verbose > 2:
            print("orginal corners:", original_corners)
            print("type of original corners: ", type( original_corners))
            
        original_corners = corner_points(original_corners)
            
        #Display the are that is extracted from the original image on top
        # of original image      
        if verbose >= 2:
            # Create an empty mask
            masked_image = original_image.copy()
            corners_int32 = np.array(original_corners, dtype=np.int32)
            
            # Draw the trapezoid on the masked_image
            cv2.polylines(masked_image, [corners_int32], isClosed=True, 
                          color=(255, 0, 255), thickness=10)
            
            display_image(
                'Trapezoid on Original Image - Area to extract', masked_image)
    
        # Suggest the card dimensions based on a bounding rectangle of the area
        #  to be extracted, suggest x,y,w width, h height.
        _, _, w, h = cv2.boundingRect(screenCnt)
        
        target_height = h 
        target_height *= height_ratio
        # Convert to int
        target_height = int(target_height)
        desired_ratio = 2.5 / 3.5
    
        target_width = int(target_height * desired_ratio)
        # Extract the corners of the target area
        target_corners = np.float32([[0, 0], [0, target_height - 1], 
                                       [target_width - 1, target_height - 1], 
                                       [target_width - 1, 0]])
        #  Align the corners in the same direction as the corners of the img 
        # before by using the same function
        target_corners_b = corner_points(target_corners)
        # Reshape to 4x2 matrix
        original_corners = original_corners.reshape(-1, 2)  
        # Convert to float32
        original_corners = original_corners.astype(np.float32)  
        # Crate the transformation matrix
        matrix = cv2.getPerspectiveTransform(original_corners, 
                                             target_corners_b)
        # Transfrom orignal image iwth the transformation matrix
        result = cv2.warpPerspective(original_image, matrix, 
                                     (target_width, target_height))
        if verbose > 0:
            display_image("Transformed Card Final", result)

        cv2.waitKey(0)
        cv2.destroyAllWindows()

        return result, None
       
    else:
        
        # Add an indication if the contour isn't found
        error_message = "Contours not found"
        if verbose > 0:
            print(error_message, " for ", path_to_img)  
            
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        return None, error_message

def display_image(name: str, image, width: int=600):
    """
    variation of cv2.imshow to implement different default settings: the window
    size created is displayed with a width=600 px and not orignial as large images
    extend the screen size otherwise and the details are not visible. window can 
    be resized

    Parameters
    ----------
    name : STR
        name of window created.
    image : cv2 image
        image to be displayed.
    width : int, optional
        width of the displayed window. The default is 600.

    Returns
    -------
    None. but shows the resizable image

    """
    # Display the image in a resizable manner
    cv2.namedWindow(name, cv2.WINDOW_KEEPRATIO)
    length = int(width * image.shape[0] / image.shape[1])
    cv2.resizeWindow(name, width, length)
    cv2.imshow(name, image)

def corner_points(input_corners):    
    """
    Identify the top right, top left, bottom right, bottom left corners 

    Parameters
    ----------
    input_corners : TYPE
        list of 4 corners [[x1 y1], [x2 y2] ,[x3 y3], [x4 y4]].

    Returns
    -------
    corners : TYPE
        [["top_left"], ["top_right"], ["bottom_right"],["bottom_left"]].
        same as input but ordered

    """
    # Calculate Center of Gravity (COG)
    cog_x = np.mean(input_corners[:, 0])
    cog_y = np.mean(input_corners[:, 1])
    
    # Determine corners based on their position relative to the COG
    corners = {
        "top_left": None,
        "top_right": None,
        "bottom_left": None,
        "bottom_right": None
    }
    
    for point in input_corners:
        if point[0] <= cog_x:
            if point[1] <= cog_y:
                corners["top_left"] = point
            else:
                corners["bottom_left"] = point
        else:
            if point[1] <= cog_y:
                corners["top_right"] = point
            else:
                corners["bottom_right"] = point         
    # Check if any corner is still None and assign it based on 
    # neighboring corner
    for corner, value in corners.items():
        if value is None:
            if corner == "top_left":
                corners[corner] = [corners["bottom_left"][0],
                                   corners["bottom_right"][1]]
            elif corner == "bottom_left":
                corners[corner] = [corners["top_right"][0],
                                   corners["bottom_right"][1]]
            elif corner == "top_right":
                corners[corner] = [corners["bottom_right"][0],
                                   corners["top_left"][1]]
            elif corner == "bottom_right":
                corners[corner] = [corners["top_right"][0],
                                   corners["bottom_left"][1]]
    # Store corner corners in a list
    corners = np.array([
        corners["top_left"],
        corners["top_right"],
        corners["bottom_right"],
        corners["bottom_left"]
    ], dtype=np.float32)

    return corners

def path_to_img_storage(filename: str, verbose : int = 0):
     """
 
     Return the path of an image from Mtg-OCR/ data/ Img_Storage
 
     Parameters
     ----------
     filename : str
         filename of image to retun from Img_Storage Folder
     verbose : TYPE, optional
         DESCRIPTION. The default is 0.
 
     Returns
     -------
     image_path : str
         path to image.
 
     """
     # Get the current file's directory
     current_directory = os.path.dirname(__file__)   
     # Navigate to the data directory
     data_directory = os.path.join(current_directory,  '..', '..', 'data')
    
     # Navigate to Img_Storage and access '1.jpg'
     image_path = os.path.join(data_directory, 'Img_Storage', filename)
  
     if verbose > 0:           
         print(data_directory)
         print(image_path)
     
     return image_path  
 

if __name__ == "__main__": 

     

    filename = 'test.jpg'

    # verbose 2
    card,error  = extract_card(get_path("raw_image",filename), 2)
    if error != None:
        print(error)
        
    # This card is not defined, program shall not crash
    filename = 'card_not_found.jpg'

    card,error  = extract_card(get_path("raw_image",filename), 2)
    if error != None:
        print(error)
   
    #without .jpg
    print("testing without .jpg")
    filename = '7'
    card,error  = extract_card(get_path("raw_image",filename), 2)


    
