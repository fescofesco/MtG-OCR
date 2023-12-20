# -*- coding: utf-8 -*-
"""
Created on Thu Dec  7 13:11:56 2023

@author: unisp
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Nov 23 19:48:06 2023

@author: unisp
"""
import cv2
"""
get_roi(card, coordinates = [0.04, 0.05, 0.55, 0.11], title="default", verbose)

returns the region of interest (roi) of an image with the specified coordinates
and the title if you want to save the picture as file
if title == None no output is generated

inputs

card ... the cv2 image of the card the roi is to be extracted
coordinates [x0, y0, x1, y1]... the coordinates of the rectangular
     the card shall be extracted from
verbose ... how much output the function has, if
        0 no output
        1 the rectangular snipping is displayed on top of the card file
        
output
roi ... cv2 image inside the specified corner coordinats [[x0,y0],[x1,y1]]
"""
"""
def get_roi(card, coordinates = [[0.04, 0.05],[0.55, 0.15]], verbose=1):


    x0 = coordinates[0][0]
    y0 = coordinates[0][1]
    x1 = coordinates[1][0]
    y1 = coordinates[1][1]

    if verbose > 1:
        print("x0: ", x0, ", y0: ", y0, "\n x1: ", x1, " y1: ", y1  )
    # width = card.shape[1]
    # height = card.shape[0]
    
    height, width, _ = card.shape
    
    print("w", width)
    print("h", height)
    # height = 88.9 / 63.5 * width    
    for coordinate in x0,x1:
        coordinate = (int(coordinate *  width))
    
    for coordinate in y0,y1:
        coordinate = (int(coordinate *  height))
    
    
    top_left = (int(height*y0),int(width*x0))
    bottom_right = (int(height*y1),int(width*x1))
    
    if verbose > 1:
        print("x0: ", x0, ", y0: ", y0, "\n x1: ", x1, " y1: ", y1  )
        
    rectangle_color = (0, 255, 255)  # BGR color (red in this case)
    # cv2.rectangle(card, top_left,bottom_right, rectangle_color, thickness=2)
     
    cv2.rectangle(card, top_left,bottom_right,  rectangle_color, thickness=2)

    cv2.rectangle(card, bottom_right, top_left,  (255, 255, 255) , thickness=2)

    ###########################################################################
    # ROI
    ###########################################################################
    
    # roi= card[top_left[1]: bottom_right[1],top_left[0]:bottom_right[0]]
    roi= card[top_left[0]: bottom_right[0],top_left[1]:bottom_right[1]]
    # roi= card[top_left: bottom_right]
# 
    # roi = card[x0:x1,y0:y1]
    
    print(top_left[1])
    print(top_left[0])
    
    print(bottom_right[1])
    print(bottom_right[0])
    # roi= card[x0: x1, y0 : y1]
        
    if verbose > 0:
        cv2.imshow("roi", roi)
        cv2.waitKey(0)
        cv2.waitKey(1)
        cv2.destroyAllWindows() 
    
    return roi
"""
def get_roi(card, coordinates=((0.04, 0.05), (0.55, 0.15)), title = "roi1", verbose=1):
    x0 = coordinates[0][0]
    y0 = coordinates[0][1]
    x1 = coordinates[1][0]
    y1 = coordinates[1][1]

    if verbose > 1:
        print("x0: ", x0, ", y0: ", y0, "\n x1: ", x1, " y1: ", y1)
    
    height, width, _ = card.shape
    
    # Calculate pixel values for coordinates
    top_left = (int(width * x0), int(height * y0))
    bottom_right = (int(width * x1), int(height * y1))
    
    if verbose > 1:
        print("top_left: ", top_left, ", bottom_right: ", bottom_right)
    
    rectangle_color = (0, 255, 255)  # BGR color (yellow in this case)
    
    # Draw the rectangle on the image
    cv2.rectangle(card, top_left, bottom_right, rectangle_color, thickness=2)
    
    # Extract the ROI using the calculated coordinates
    roi = card[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
    
    if verbose > 0:
        cv2.imshow(title, roi)
        cv2.waitKey(0)
        cv2.waitKey(1)
        cv2.destroyAllWindows() 
        
    return roi


        
def safe_card_roi(card_roi, title='filename', mode='roi', verbose=1):
    # ... some code ...

    match mode:
     
        case 'ui':
            # Handle 'ui' mode
            pass
        case 'name':
            # Handle 'title' mode
            pass
        case 'exp':
            # Handle 'exp' mode
            pass
        case _:
            # Handle any other case
            pass


    if not title.endswith(".jpg"):
        title += ".jpg"

    cv2.imwrite(title, card_roi)
    
def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        param['clicked_points'].append((x, y))
        if len(param['clicked_points']) > 2:
            param['clicked_points'] = param['clicked_points'][-2:]  # Keep only the last 2 points
            draw_rectangle(param['image'], param['clicked_points'], param)

def draw_rectangle(image, points, param):
    if len(points) == 2:
        img_copy = image.copy()  # Create a copy of the image to draw the rectangle on
        cv2.rectangle(img_copy, points[0], points[1], (0, 255, 0), thickness=2)
        cv2.imshow(param['window_name'], img_copy)

def get_relative_coordinates(image, window_name='Image', max_width=800, max_height=600):
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

    cv2.destroyWindow(window_name)
    # cv2.destroyAllWindows()

    cv2.destroyAllWindows()



def save_coordinates(mode, points):
    with open('parameters.txt', 'r') as file:
        lines = file.readlines()

    with open('parameters.txt', 'w') as file:
        for line in lines:
            if line.startswith(mode):
                line = f"{mode} = {points}\n"
            file.write(line)

def determine_mode(y_coordinate):
    if 0 <= y_coordinate <= 0.35:
        return 'name'
    elif 0.36 <= y_coordinate <= 0.8:
        return 'exp'
    elif 0.81 <= y_coordinate <= 1:
        return 'ui'
    else:
        return 'unknown'

    
def get_coordinates_from_file(mode):
    with open('parameters.txt', 'r') as file:
        lines = file.readlines()

    for line in lines:
        if line.startswith(mode):
            coords = line.split('=')[-1].strip()
            top_left, bottom_right = eval(coords)
            return top_left, bottom_right
    return None
    
if __name__ == "__main__":
    
    
    from card_identification import identify_card
    
    # Replace 'test.jpg' with the actual filename or path to your image
    # img = cv2.imread('test.jpg')

    # if img is not None:
    #     points = get_relative_coordinates(img, window_name='Resized Image')
    #     if points is not None and len(points) == 2:
    #         print(f"Clicked points: {points}")
    # else:
    #     print("Image not found or couldn't be loaded.")

     
    
    card = identify_card("21.jpg",0)
    
    # Load your image here
    # img = cv2.imread("test.jpg")
    
    # get_relative_coordinates(card)
    if card is not None:
        points = get_relative_coordinates(card, window_name='Click coner points of UI, exp symbol or name and press enter after each selsection')
        if points is not None and len(points) == 2:
            print(f"Clicked points: {points}")
    else:
        print("Image not found or couldn't be loaded.")
    
    ui_coordinates = get_coordinates_from_file('ui')
    if ui_coordinates:
        print(f"UI coordinates: {ui_coordinates}")
    else:
        print("UI coordinates not found or file doesn't contain the 'ui' mode.")
    



    name = get_roi(card,get_coordinates_from_file("name"),"name")

    ui = get_roi(card, ui_coordinates,"ui")

    exp = get_roi(card, get_coordinates_from_file('exp'),"exp")
    
    
    # card = get_roi(identify_card("test.jpg",1),[[0.9, 0.9],[0.95, 0.95]])