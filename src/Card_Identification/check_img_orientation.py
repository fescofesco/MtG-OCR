# -*- coding: utf-8 -*-
"""
%(filename)
${file}
Created on %(date)s

author: Felix Scope
"""

import cv2
import pytesseract
import numpy as np


from src.Card_Identification.path_manager import (get_path, PathType, return_folder_image_contents)


path1 = path1 = "C:\\Users\\unisp\\Documents\\Infoprojekte\\MtG-OCR\\tests\\data\\Card_Identification\\raw_IMGs\\2023-12-24"
folder_img_contents = return_folder_image_contents(path1)
print(folder_img_contents)
# Step 1: Image Preprocessing


for img_path in folder_img_contents:
    
    print(img_path)
    
    img_path = path1 + "\\" +  img_path
    
    image = cv2.imread(img_path)
    cv2.imshow("Original Image", image)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # You may need additional preprocessing steps like thresholding or blurring
    
    # Step 2: Text Detection using PyTesseract
    custom_config = r'--oem 3 --psm 6'  # Adjust these parameters based on your needs
    text = pytesseract.image_to_string(gray, config=custom_config)
    
    
    rotated_image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    text = pytesseract.image_to_string(rotated_image, config=custom_config)

    
    
    # Extract orientation information from the recognized text
    # This is a simplified example, and you may need more robust methods
    if "upright" in text.lower():
        rotation_angle = 0
    elif "rotated" in text.lower():
        rotation_angle = 90
    else:
        rotation_angle = 0  # Default to no rotation
    
    # Step 3: Rotation Correction
    if rotation_angle != 0:
        rotated_image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    else:
        rotated_image = image
    
    # Display the original and rotated images
    cv2.imshow("Rotated Image", rotated_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()