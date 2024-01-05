# -*- coding: utf-8 -*-
"""
%(filename)
${file}
Created on %(date)s

author: Felix Scope
"""

import pytesseract
import cv2
from configuration_handler import MtGOCRData
from Levenshtein import distance as levenshtein_distance
import os
import re
from collections import Counter
import json
import filecmp
import numpy as np
import imutils


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
    None. but shows the resizable image

    """
    # Display the image in a resizable manner
    cv2.namedWindow(name, cv2.WINDOW_KEEPRATIO)
    length = int(width * image.shape[0] / image.shape[1])
    cv2.resizeWindow(name, width, length)
    cv2.imshow(name, image)

def preprocess_roi_UI(roi, verbose =0):
    """
    
    crops away the white part above the UI
    
    
    Parameters
    ----------
    roi : cv2 image
        DESCRIPTION.
    verbose : TYPE, optional
        DESCRIPTION. The default is 0.
    
    Returns
    -------
    TYPE
        DESCRIPTION.
    """
    
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (7,7), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    
    
    
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Find the largest contour
    largest_contour = max(contours, key=cv2.contourArea)
    
    # Create a mask for the largest contour
    mask_largest_contour = np.zeros_like(gray)
    cv2.drawContours(mask_largest_contour, [largest_contour], -1, 255, -1)
    
    # Bitwise AND operation to extract the area within the contour
    result = cv2.bitwise_and(roi, roi, mask=mask_largest_contour)
    
    # Find bounding rectangle of the largest contour
    x, y, w, h = cv2.boundingRect(largest_contour)
    
    # Crop the image excluding the black border
    cropped_image = result[y:y+h, x:x+w]
    
   
    if verbose >=2: 
        cv2.imshow('Cropped Image', cropped_image)
        cv2.imshow("Original Image", roi)
        cv2.imshow('Threshed Image', thresh)
    
        # Display the result
        cv2.waitKey(0)
        cv2.destroyWindow("Cropped Image")
    
        cv2.destroyAllWindows()
    
    return cropped_image


import re

def extract_set_info(set_code_roi, verbose=0):
    # Perform OCR to extract text from the set code ROI
    set_code_text1 = "YW 0129 LCt+ EN"  # Replace this line with your OCR result
    set_code_text = re.sub(r'[^A-Za-z0-9\s]', '', set_code_text1)

    # Extracting 3-letter words or numbers excluding special characters using regular expression
    pot_set = re.findall(r'[A-Z0-9]{3}', re.sub(r'[^A-Za-z0-9]', '', set_code_text))
    pot_set = re.findall(r'[a-zA-Z0-9]{3}', re.sub(r'[^A-Za-z0-9]', '', set_code_text))

    if verbose > 0:
        print("extract_set_info:\n", "set:", pot_set)
        
    if verbose >= 2:
        print("found text:", set_code_text) 
        print("from: ", set_code_text1)
    return pot_set

# Example usage:
sets = extract_set_info("YW 0129 LCt+ EN", verbose=2)
print("Sets:", sets)
