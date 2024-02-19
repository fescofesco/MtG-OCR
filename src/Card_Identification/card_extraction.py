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
from path_manager import (get_path, PathType)


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
                
    if verbose > 2:
        print("path of image: ", full_path)
        
    original_image = cv2.imread(full_path)
    
    filename = os.path.basename(full_path)
    
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
    
    if verbose >2:
        display_image(f"{filename} original image", image)
    
    # 2) Converting the input image to greyscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if verbose >2:
        display_image(f"{filename} greyed image", gray_image)
     

    # 3) Reducing the noise in the greyscale image
    gray_image = cv2.bilateralFilter(gray_image, 11, 17, 17) 
    if verbose >2:
        display_image(f"{filename} smoothened image", gray_image)
    
    # 4) Detecting the edges of the smoothened image
    edged = cv2.Canny(gray_image, 25, 200) 
    if verbose >2:
        display_image(f"{filename} edged image", edged)
        
    
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
    


    if verbose >1:     # display the contours
        image1=image.copy()
        cv2.drawContours(image1,cnts,-1,(0,255,0),3)
        display_image("contours external",image1)
        
    # 7) Sorting the identified contours - > getting the contour with the most 
    # area
    cnts_sorted = sorted(cnts, key = cv2.contourArea, reverse = True)[:1]
    screenCnt = None

    cnts_sorted1 = filter_and_sort_contours(cnts_sorted, image, verbose)
    # filtered_contours = cnts_sorted

    # if verbose > 2:
    #     image2 = image.copy()
    #     cnts_top4 = sorted(filtered_contours, key = cv2.contourArea, reverse = True)[:4]
    #     cv2.drawContours(image2,cnts_top4,-1,(0,255,0),2)
    #     display_image("Top 4 contours filtered",image2)
 
    # 8) convert it to a contour with 4 sides
    for c in cnts_sorted1:
        perimeter = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.025 * perimeter, True)
        if len(approx) == 4: 
            screenCnt = approx


    # 8) convert it to a contour with 4 sides
    for c in cnts_sorted:
        perimeter = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.025 * perimeter, True)
        if len(approx) == 4: 
            screenCnt = approx
            
    
    # no contour with 4 sides was found, redo contours by thresshold
    if screenCnt is None:
        error = "redo contours by frame threshold"
        return None, error
    
    
    if screenCnt is not None:  # Check if the contour is found
        # Convert screenCnt corners to a usable format for perspective 
        #   transformation
        corners = screenCnt.reshape(4, 1, 2).astype(np.float32)
        original_height, original_width = original_image.shape[:2]
        resized_height, resized_width = image.shape[:2]
        
        # Calculate the dimension ratios
        height_ratio = original_height / resized_height
        width_ratio = original_width / resized_width
        
        # Make a copy of corners to preserve the original
        original_corners = corners.copy()
        
        # Adjust x-coordinates
        original_corners[:, 0, 0] *= width_ratio
        # Adjust y-coordinates
        original_corners[:, 0, 1] *= height_ratio
               
        # Convert the original_corners to integers
        original_corners = original_corners.astype(np.int32)
        if verbose > 2:
            print("orginal corners:", original_corners)
            print("type of original corners: ", type( original_corners))
            # for corner in original_corners:
            #    cv2.circle(image, tuple(corner), 5, (0, 255, 0), -1)  # Draw a filled green circle
            
            for point in original_corners:
                pt = tuple(point.squeeze())  # Convert the contour to a tuple of coordinates
                cv2.circle(image, pt, radius=1, color=(0, 255, 0), thickness=1)

             # Display the image with corner points
            display_image('Original Corners', image)
            
        
        original_corners_aligned = align_corner_points(original_corners)
            
        #Display the are that is extracted from the original image on top
        # of original image      
        if verbose > 2:
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
   
        original_corners_aligned = align_corner_points(original_corners)
        original_corners_reshaped = original_corners_aligned.reshape(4,2)
        original_corners_typed = original_corners_reshaped.astype(np.float32)  
        
        target_corners_aligned = align_corner_points(target_corners)
        target_corners_reshaped = target_corners_aligned.reshape(4,2)
        target_corners_typed =  target_corners_reshaped.astype(np.float32)  
        
        # Now, original_corners_reshaped should have the shape (4, 1, 2)

        # Convert to float32
  
       

        # Crate the transformation matrix
        
        # Check if both arrays have 4 points each
        assert original_corners_typed.shape == (4, 2), "original_corners should have shape (4, 2)"
        assert target_corners_typed.shape == (4, 2), "target_corners_b should have shape (4, 2)"
        
        
        
  


        matrix = cv2.getPerspectiveTransform(original_corners_typed, 
                                             target_corners_typed)
        # Transfrom orignal image iwth the transformation matrix
        result = cv2.warpPerspective(original_image, matrix, 
                                     (target_width, target_height))
        
        # target_corners1 = target_corners
        # target_corners1[1]= target_corners[3]
        # target_corners1[3]= target_corners[1]
        
        # matrix = cv2.getPerspectiveTransform(original_corners, 
        #                                      target_corners)
        # # Transfrom orignal image iwth the transformation matrix
        # result = cv2.warpPerspective(original_image, matrix, 
        #                              (target_width, target_height))
   
        if verbose > 0:
            display_image(f"{filename} Transformed Card Final", result)

        cv2.waitKey(0)
        if verbose == 1:
            cv2.waitKey(1)
            return result, None
        else:
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
    
def filter_and_sort_contours(contours, original_image, margin=-0.05, verbose=0):
    """
    Filters and sorts contours based on proximity to line equations with a margin.

    Args:
        cnts: List of contours to filter.
        original_image: Original image for visualization (optional).
        margin: Percentage margin applied to line equations.
        verbose: Verbosity level (0-3) for displaying images.

    Returns:
        List of filtered contours.
    """
    contour = contours[0]
    
    for cts in contours:
    #     cv2.drawContours(original_image, cts, -1, (0, 255, 255), 1)
        cv2.drawContours(original_image, cts, -1, (0, 255, 255),3)

    if verbose > 2:
        display_image("Orig Contours", original_image)
    
        

     
    image3 = original_image.copy()


    # Approximate the contour with a polygon
    epsilon = 0.01 * cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, epsilon, True)

    try:
        innermost_points = find_innermost_corners(approx, image3, verbose)
    except ZeroDivisionError:
        return None, "Card cannot touch image corners"

    if verbose>2: print("innermost_points=", innermost_points)
   
    innermost_points_aligned = align_corner_points(innermost_points)
    if verbose >2: print("innermost_points_aligned=", innermost_points_aligned)
    # Calculate line equations with margin
    line_eqs = []

    for corner in innermost_points_aligned:
        cv2.circle(image3, corner[0], 5, (0, 255, 0), -1)  # Draw a filled green circle
    
    if verbose > 2:
        display_image("Innermost Corners after align", image3)
      
    
    # Calculate line equations
    for i in range(len(innermost_points_aligned)):
  
        x1, y1 = innermost_points[i][0]
        x2, y2 = innermost_points[(i + 1) % len(innermost_points)][0]
        m = (y2 - y1) / (x2 - x1) if x2 != x1 else float('inf')
        b = y1 - m * x1
        line_eqs.append((m, b))

    # Find points inside and outside the region
    inside_points = []
    outside_points = []



    # Iterate over each point in contour_points
    for point in contour:
        x, y = point[0]
        # Check each line equation separately
        for i, (m, b) in enumerate(line_eqs):
            # Apply different checks for each line_eq
            if i == 1:
                if (y - b - m * x) * (1 + margin) > 0:  # Change the sign for line_eqs[1]
                    inside_points.append(point)
                else:
                    outside_points.append(point)
                    break  # If a point is found outside by any line_eq, break the inner loop
            elif i == 2:
                 if (y - b - m * x) * (1 + margin) < 0:  # Change the sign for line_eqs[1]
                     inside_points.append(point)
                 else:
                     outside_points.append(point)
                     break  # If a point is found outside by any line_eq, break the inner loop
            elif i == 3:
                 if (y - b - m * x) * (1 + margin) < 0:  # Change the sign for line_eqs[1]
                     inside_points.append(point)
                 else:
                     outside_points.append(point)
                     break  # If a point is found outside by any line_eq, break the inner loop
                     
            else:
                if (y - b - m * x) * (1 + margin) > 0:
                    inside_points.append(point)
                else:
                    outside_points.append(point)
                    break  # If a point is found outside by any line_eq, break the inner loop


    for point in innermost_points_aligned:
        inside_points.append(point)

    # Draw contours using different colors for inside and outside points
    color_inside = (0, 255, 0)  # Green color for points inside the region
    color_outside = (0, 0, 255)  # Red color for points outside the region
    image4 = original_image.copy()
    
    
    if verbose >2:
           
        for point in inside_points:
            pt = tuple(point.squeeze())  # Convert the contour to a tuple of coordinates
            cv2.circle(image4, pt, radius=1, color=color_inside, thickness=2)
        
        for point in outside_points:
            pt = tuple(point.squeeze())  # Convert the contour to a tuple of coordinates
            cv2.circle(image4, pt, radius=1, color=color_outside, thickness=2)
            
            
        
        display_image("Filtered Contours", image4)
        
    
    
    return inside_points



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


def find_innermost_corners(cnt, img, verbose=0):
    # Compute moments and centroid
    M = cv2.moments(cnt)
    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"])

    # Adaptive epsilon for better corner approximation
    epsilon = 0.02 * cv2.arcLength(cnt, True)
    if len(cnt) < 50:  # Adjust for smaller contours
        epsilon = 0.1 * cv2.arcLength(cnt, True)

    # Approximate polygon with adjusted epsilon
    corners = cv2.approxPolyDP(cnt, epsilon, True)
 
    # Filter corners based on distance from centroid and angle
    min_distance = 0.1 * cv2.arcLength(cnt, True)  # Adjust as needed
    max_angle_deviation = 30  # Degrees
    filtered_corners = []
    for corner in corners:
        dist = np.linalg.norm(np.array(corner[0]) - np.array([cx, cy]))
        angle = np.arctan2(*corner[0][::-1] - [cx, cy]) * 180 / np.pi  # Adjust for desired angle range
        if dist >= min_distance and 0 <= angle <= max_angle_deviation:
            filtered_corners.append(corner)

        if verbose >1:
            for corner in corners:
                cv2.circle(img, tuple(corner[0]), 1, (0, 0, 0), thickness=2)  # Black circle with radius 1
            display_image("All corners", img)
            if verbose >2: print("innermost_corners=",corners)


    # Sort filtered corners by distance from centroid
    # sorted_corners = sorted(filtered_corners, key=lambda point: np.linalg.norm(np.array(point[0]) - np.array([cx, cy])))
    sorted_corners = sorted(corners, key=lambda point: np.linalg.norm(np.array(point[0]) - np.array([cx, cy])))

    if verbose >2: print("sorted_corners=",sorted_corners)

    # Return the first 4 points (innermost corners)
    return np.array(sorted_corners[:4], dtype=np.float32)

def align_corner_points(input_corners):    
    """
    Identify the top right, top left, bottom right, bottom left corners 

    Parameters
    ----------
    input_corners : np.array
        Array of 4 corners [[x1, y1], [x2, y2], [x3, y3], [x4, y4]] or 
        [[[x1, y1]], [[x2, y2]], [[x3, y3]], [[x4, y4]]].

    Returns
    -------
    corners : np.array
        Array of ordered corners: [[top_left_x, top_left_y], [top_right_x, top_right_y],
                                    [bottom_right_x, bottom_right_y], [bottom_left_x, bottom_left_y]].

    """
    # Check if input_corners has shape (4, 2) or (4, 1, 2)
    if input_corners.shape == (4, 2):
        # Order points if necessary
         mode = "4,2"
         input_corners_copy = input_corners
    elif len(input_corners.shape) == 3 and input_corners.shape[1] == 1 and input_corners.shape[2] == 2:
        mode = "4,1,2"
        input_corners_copy = input_corners.reshape(4, 2)
    else:
        raise ValueError("Invalid input shape. Expected (4, 2) or (4, 1, 2).")

           
    # Calculate Center of Gravity (COG)
    cog_x = np.mean(input_corners_copy[:, 0])
    cog_y = np.mean(input_corners_copy[:, 1])

    # Determine corners based on their position relative to the COG
    corners = {
        "top_left": None,
        "top_right": None,
        "bottom_left": None,
        "bottom_right": None
    }
    
    for point in input_corners_copy:
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
    
    # Check if any corner is still None and assign it based on neighboring corner
    try:
        for corner, value in corners.items():
            if value is None:
                if corner == "top_left":
                    corners[corner] = [corners["bottom_left"][0], corners["bottom_right"][1]]
                elif corner == "bottom_left":
                    corners[corner] = [corners["top_right"][0], corners["bottom_right"][1]]
                elif corner == "top_right":
                    corners[corner] = [corners["bottom_right"][0], corners["top_left"][1]]
                elif corner == "bottom_right":
                    corners[corner] = [corners["top_right"][0], corners["bottom_left"][1]]
    except TypeError:
        return None 

    # Store corner corners in a list
    corners = np.array([
        [corners["top_left"]],
        [corners["top_right"]],
        [corners["bottom_right"]],
        [corners["bottom_left"]]
    ], dtype=np.int32)
    
    if mode == "4,1,2":
        corners_return = corners.reshape(4, 1, 2)
    else:
        corners_return = corners
    

    return corners_return





if __name__ == "__main__":
    cv2.destroyAllWindows()
    # asmo
    # filename = "1.jpg"
    # goblin cut top
    filename = "2.jpg"
    # food
    filename = "3.jpg"
    # vsiage of dread
    # filename = "4.jpg"

    # sword
    filename = "5.jpg"
    mypath = get_path(PathType.TEST_RAW_IMAGE,filename)
    card, error = extract_card(mypath, verbose =3)
    if error:
        print(error)
    cv2.destroyAllWindows()