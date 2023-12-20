# -*- coding: utf-8 -*-
"""
# card_identification.py
V 1.0
Created on Thu Nov 16 08:39:30 2023

@author: Felix Scope


This scirpt allows card identification of images. Only one card per
image, but easy implementable to allow more. Currently the whole card must be 
visisble.

Main function is 
    identify_card(path_to_img_folder, verbose=1):

"""

import os
import cv2
import imutils
import numpy as np


def identify_card(path_to_img, verbose=0):
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

    """
    
    if not path_to_img.endswith('.jpg'):
        path_to_img = path_to_img + '.jpg'
        
    if not os.path.isabs(path_to_img):  # Check if the path is relative
        full_path = os.path.join("Img Storage", path_to_img)
    else:
        full_path = path_to_img  # Use the provided full path
                
    if verbose >= 2:
        print(full_path)
        
    # 1) Taking in our image input and resizing its width to 300 pixels for 
    #  easier contur identification
    original_image = cv2.imread(full_path)
    
    if original_image is None:
        print("Image not loaded. Check the image path.")
        return None
    else:
       # Proceed with image processing
       # image is the resized small image -> easier card contur identification 
       image = imutils.resize(original_image, width=300)
    
    
    if verbose ==2:
        cv2.imshow("original image", image)
    
    # 2) Converting the input image to greyscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if verbose ==2:
        cv2.imshow("greyed image", gray_image)
    
    # 3) Reducing the noise in the greyscale image
    gray_image = cv2.bilateralFilter(gray_image, 11, 17, 17) 
    if verbose ==2:
        cv2.imshow("smoothened image", gray_image)
    
    # 4) Detecting the edges of the smoothened image
    edged = cv2.Canny(gray_image, 25, 200) 
    if verbose >=2:
        cv2.imshow("edged image", edged)
        
    # 5) Finding the contours from the edged image
    cnts,_ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, 
                                cv2.CHAIN_APPROX_SIMPLE)
    image1=image.copy()
    cv2.drawContours(image1,cnts,-1,(0,255,0),3)
    if verbose >=2:
        cv2.imshow("contours external",image1)
        
    # 6) Sorting the identified contours
    cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:4]
    screenCnt = None
    
    if verbose >= 2:
        image2 = image.copy()
        cv2.drawContours(image2,cnts,-1,(0,255,0),2)
        display_image("Top 4 contours",image2)
 
    # 7) Finding the contour with four sides
    for c in cnts:
        perimeter = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.018 * perimeter, True)
        if len(approx) == 4: 
            screenCnt = approx
    
    if screenCnt is None:
        if verbose > 0:
            print("redo contours")
        
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
                          color=(255, 0, 255), thickness=3)
            
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

        return result
       
    else:
        
        # Add an indication if the contour isn't found
        if verbose > 0:
            print("Contour not found for:", path_to_img)  
        

        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        return None

def display_image(name, image, width=600):
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
    None.

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
    
    # print(input_corners)
  
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
if __name__ == "__main__":
    identify_card("test.jpg",1)
    identify_card("7.jpg",1)
    


 
    
    
    
    
    
    
