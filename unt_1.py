# -*- coding: utf-8 -*-
"""
%(filename)
${file}
Created on %(date)s

author: Felix Scope
"""

import numpy as np
import cv2

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
    cv2.waitKey(0)
    


def find_innermost_corners(cnt):
    # Compute the centroid of the contour
    M = cv2.moments(cnt)
    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"])

    # Sort the contour points based on the distance from the centroid
    sorted_cnt = sorted(cnt, key=lambda point: np.linalg.norm(np.array(point[0]) - np.array([cx, cy])))

    # Return the first 4 points (innermost corners)
    return sorted_cnt[:4]

# Draw lines and filter contours
def draw_lines_and_filter_contours(img, innermost_corners):
    # Draw lines connecting the innermost corners
    for i in range(3):
        cv2.line(img, tuple(innermost_corners[i][0]), tuple(innermost_corners[i + 1][0]), (0, 255, 0), 2)
    cv2.line(img, tuple(innermost_corners[3][0]), tuple(innermost_corners[0][0]), (0, 255, 0), 2)

    # Convert innermost corners to numpy array
    innermost_corners = np.array(innermost_corners).reshape(-1, 2)

    # Filter contours that are near the lines
    filtered_contours = []
    for cnt in cnts:
        for point in cnt:
            if cv2.pointPolygonTest(innermost_corners, tuple(point[0]), False) >= 0:
                filtered_contours.append(cnt)
                break

    return filtered_contours


def create_bounding_rectangle(filtered_contours):
    # Merge filtered contours
    merged_contours = np.vstack(filtered_contours)

    # Create a bounding rectangle
    rect = cv2.boundingRect(merged_contours)

    # Draw the bounding rectangle
    cv2.rectangle(img, (rect[0], rect[1]), (rect[0] + rect[2], rect[1] + rect[3]), (0, 0, 255), 2)

    return img

# Read the image

cnts = [[[202,  74]],

       [[201,  75]],

       [[ 73,  75]],

       [[ 73, 128]],

       [[ 74, 129]],

       [[ 73, 130]],

       [[ 73, 136]],

       [[ 74, 137]],

       [[ 74, 202]],

       [[ 73, 203]],

       [[ 73, 206]],

       [[ 74, 207]],

       [[ 74, 208]],

       [[ 73, 209]],

       [[ 73, 238]],

       [[ 72, 239]],

       [[ 72, 287]],

       [[ 73, 288]],

       [[ 73, 295]],

       [[ 72, 296]],

       [[ 72, 339]],

       [[ 73, 340]],

       [[ 95, 340]],

       [[ 96, 341]],

       [[ 96, 344]],

       [[ 97, 345]],

       [[ 97, 356]],

       [[ 96, 357]],

       [[ 96, 359]],

       [[ 97, 360]],

       [[ 97, 363]],

       [[ 96, 364]],

       [[ 96, 366]],

       [[ 97, 367]],

       [[ 97, 370]],

       [[ 96, 371]],

       [[ 96, 396]],

       [[ 95, 397]],

       [[ 95, 399]],

       [[ 98, 399]],

       [[ 99, 398]],

       [[ 99, 375]],

       [[100, 374]],

       [[100, 345]],

       [[101, 344]],

       [[101, 341]],

       [[102, 340]],

       [[133, 340]],

       [[134, 339]],

       [[135, 340]],

       [[143, 340]],

       [[144, 339]],

       [[154, 339]],

       [[155, 340]],

       [[224, 340]],

       [[225, 339]],

       [[228, 339]],

       [[229, 340]],

       [[244, 340]],

       [[245, 339]],

       [[268, 339]],

       [[268, 297]],

       [[267, 296]],

       [[267, 254]],

       [[266, 253]],

       [[266, 216]],

       [[265, 215]],

       [[265, 178]],

       [[264, 177]],

       [[264, 138]],

       [[263, 137]],

       [[263, 106]],

       [[262, 105]],

       [[262,  81]],

       [[261,  80]],

       [[261,  74]],

       [[249,  74]],

       [[248,  75]],

       [[219,  75]],

       [[218,  74]]]

cnts = np.array(cnts)
print(cnts)

img = cv2.imread(r"C:\Users\unisp\Documents\Infoprojekte\MtG-OCR\data\Card_Identification\raw_IMGs\IMG_20240119_131203.jpg")

# Find innermost corners
innermost_corners = find_innermost_corners(cnts)


# Call the function with img and innermost_corners
filtered_contours = draw_lines_and_filter_contours(img.copy(), innermost_corners)

# Create bounding rectangle
result_img = create_bounding_rectangle(filtered_contours)

# Display the result
display_image("result", result_img)
    
img = cv2.imread(r"C:\Users\unisp\Documents\Infoprojekte\MtG-OCR\data\Card_Identification\raw_IMGs\IMG_20240119_131203.jpg")
display_image("original", img)
cv2.waitKey(0)