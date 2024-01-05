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

# def preprocess_roi(roi, verbose =0):
"""


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

filename = 'IMG_20231222_111834_ui_19.jpg'

roi = cv2.imread(filename)
verbose = 1


# image = cv2.imread('1.png')
image = roi.copy()
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray, (7,7), 0)
thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,2))
tresh_bw = cv2.bitwise_not(thresh)
opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=3)

# Repair text
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7,7))
dilate = cv2.dilate(opening, kernel, iterations=2)

# Bitwise-and with input image
result = cv2.bitwise_and(image,image,mask=dilate)
result[dilate==0] = (255,255,255)

cv2.imshow('thresh', thresh)
cv2.imshow('thresh_bw', tresh_bw)
text = pytesseract.image_to_string(tresh_bw)
print("orig", text)

custom_config = r'--oem 3 --psm 6'  # Example options: OEM 3 for default LSTM OCR Engine, PSM 6 for a single block of text
text = pytesseract.image_to_string(tresh_bw, config=custom_config)
print("Modified:", text)

custom_config = r'--oem 3 --psm 6'  # Example options: OEM 3 for default LSTM OCR Engine, PSM 6 for a single block of text
text5 = pytesseract.image_to_string(thresh, config=custom_config)
print("Modified:", text5)




cv2.waitKey(0)
cv2.destroyAllWindows()
"""

# read image
img = cv2.imread("text_table.jpg")

# convert img to grayscale
gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

# do adaptive threshold on gray image
thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 11)

# write results to disk
cv2.imwrite("text_table_thresh.jpg", thresh)

# display it
cv2.imshow("thresh", thresh)
cv2.waitKey(0)
cv2.destroyAllWindows()


# Converting the input image to grayscale
gray_image = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
if verbose >= 2:
    display_image("grayed image", gray_image)

# Applying Gaussian blur to smoothen the image and reduce noise
blurred = cv2.GaussianBlur(gray_image, (5, 5), 0)
if verbose >= 2:
    display_image("blurred image", blurred)

# Adaptive thresholding to separate text from the background
thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
if verbose >= 2:
    display_image("thresholded image", thresh)

# Noise reduction (morphological operations)
kernel = np.ones((2, 2), np.uint8)
opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=3)
closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel, iterations=2)
if verbose >= 2:
    display_image("cleaned image", closing)

# Detecting edges
edged = cv2.Canny(closing, 30, 150)
if verbose >= 2:
    display_image("edged image", edged)

text = pytesseract.image_to_string(edged)
print("orig", text)
image_resized = imutils.resize(edged, width=300)
display_image("resiszed", image_resized)
text2 = pytesseract.image_to_string(image_resized)
print("text2",text2)
text3 = pytesseract.image_to_string(image_resized)
print("text orig", text3)

# Finding contours from the edged image
contours, _ = cv2.findContours(edged, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

threshold_value = 10

# Filter contours based on size
filtered_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > threshold_value]

# Sort contours from left to right
filtered_contours = sorted(filtered_contours, key=lambda x: cv2.boundingRect(x)[0])

if verbose > 0:
    cv2.imshow("Contours of ROIs", edged)
    cv2.waitKey(0)
    


if verbose >= 2:
    cv2.destroyWindow("Contours of ROIs")
    cv2.destroyWindow("grayed image")
    cv2.destroyWindow("blurred image")
    cv2.destroyWindow("thresholded image")
    cv2.destroyWindow("cleaned image")
    cv2.destroyWindow("edged image")

# Extract the bounding box for the first contour
if filtered_contours:
    x, y, w, h = cv2.boundingRect(filtered_contours[0])

    # Crop the region of interest (set code)
    roi_info = roi[y:y + h, x:x + w]
    display_image("info", roi_info)

cv2.waitKey(0)
cv2.destroyWindow("info")
cv2.destroyAllWindows()
"""
