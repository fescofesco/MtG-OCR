# -*- coding: utf-8 -*-
"""
Created on Mon Nov 20 22:41:29 2023

@author: unisp
"""
import cv2
import json
import os
import re
from Levenshtein import Levenshtein.distance

def Roi_name(fixed_box, fixed,show):

     # value1=0.06 # x0
     # value2=0.04 #y0
     
     # value3=0.6 # x1
     # value4=0.1 #y1
     
     value1=0.06 # x0
     value2=0.055 #y0
     
     value3=0.55 # x1
     value4=0.1 #y1
     
     """
     value1, value2, value3, value4 = process_four_values()

     
     print("Value 1:", value1)
     print("Value 2:", value2)
     print("Value 3:", value3)
     print("Value 4:", value4)
     
     print(value1+value2+value3+value4)
         """
     width = fixed.shape[0]
     height = 88.9 / 63.5 * width

     
     top_right = (int(height*value1), int(width*value2))
     bottom_left = (int(height*value3), int(width*value4))
     
     
     top_right = (int(width*value1), int(height*value2))
     bottom_left = (int(width*value3), int(height*value4))
     
     
     rectangle_color = (0, 255, 255)  # BGR color (red in this case)
     cv2.rectangle(fixed_box, bottom_left, top_right, rectangle_color, thickness=2)
     
     # print(bottom_left, top_right)
     cv2.rectangle(fixed, (0,0), (1340,1800), (255, 255, 255), thickness=2)
     # if show == 1:
             # display_image("rotated_ROI_box.jpg", fixed_box)
     # display_image("frame", fixed_box)
     
     ###############################################################################
     # ROI
     ##############################################################################
     
     roi= fixed [top_right[1]: bottom_left[1],top_right[0]:bottom_left[0]]
     
     cv2.imshow("roi", roi)
     
     # if show ==1:
     #     display_image("roi {bottom_left} {top_right}",roi,(top_right[0]- bottom_left[0]))
     
     # print("save roi")
     Title = "roi name1.jpg"
     cv2.imwrite(Title,roi)
     cv2.waitKey(0)
     cv2.waitKey(1)
     cv2.destroyAllWindows()

     return roi
 
    

###############################################################################
#  correlates the extracted set name wit real sets
###############################################################################
def Levenshtein_txt(guessed_set = ["202","MEN"], guessed_setsize=332):
    with open('all_sets.json', 'r', encoding='utf-8') as all_sets:
        word_number_pairs = json.load(all_sets)
    
    
    # Your target three-letter word and max number
    target_word = guessed_set
    max_number = int(guessed_setsize)
    
    # Define the weights for word and number
    word_weight = 15  # Adjust as needed
    number_weight = 1  # Adjust as needed
    
    # Initialize variables to keep track of the closest neighbor
    closest_neighbor = None
    best_combined_similarity = float('inf')  # Initialize with a high value
    
    # Calculate combined similarity for each pair and find the closest neighbor
    for pair in word_number_pairs:
        word = pair["set"]
        number = pair["max_collector_number"]
        
        # Calculate word similarity using Levenshtein distance
        word_similarity = Levenshtein.distance(target_word, word)
        
        # Calculate number similarity as the absolute difference
        number_similarity = Levenshtein.distance(str(max_number), str(number))
    
        # Calculate combined similarity with adjusted weights
        combined_similarity = (word_similarity * word_weight) + (number_similarity * number_weight)
    
        if combined_similarity < best_combined_similarity:
            closest_neighbor = {"word": word, "max_collector_number": number}
            best_combined_similarity = combined_similarity
        
        
    
    print("Closest neighbor to", target_word, "with number", max_number, "is:", closest_neighbor)
    return closest_neighbor['word']


def Levenshtein_txt_name(scryfalldata, guessed_card_name = "Unburial Rtes", guessed_setsize=331, guessed_collectornumber="095"):
     
    # with open('all_sets.json', 'r', encoding='utf-8') as all_sets:
    #     word_number_pairs = json.load(all_sets)
    
    
    # scryfall_data = "default-cards-20231010090500.json"
    
    # with open(scryfall_data, 'r', encoding='utf-8') as full_data:
    #     scryfalldata = json.load(full_data)
    

    
    # guessed_card_name = "Shok"  # Your guessed card name
    closest_match = None
    closest_distance = float('inf')  # Initialize with a high value
    
    for card in scryfalldata:
        card_name = card["name"]
        distance = Levenshtein.distance(guessed_card_name, card_name)
    
        if distance < closest_distance:
            closest_distance = distance
            closest_match = card_name
    
    # Print the closest matching card name
    # print("Closest Match:", closest_match)
    
    # If the closest match is below a certain threshold, you can consider it a match
    threshold = 3  # Adjust as needed
    if closest_distance <= threshold:
        # print("Corrected Card Name:", closest_match)
        return closest_match
    else:
        print("No close match found.")
        return None
    
    
        


###############################################################################
#  extracts the set name and the collectro number of a string
###############################################################################
def TextExtraction(text= "100/300 2x2",debug=True):
    potential_sets = re.findall(r'\b[A-Za-z1-9]{3}\b', text)
    # Print the extracted 3-letter words
    
    # for word in three_letter_words:
    #     print("word", word)
    try:
        numbers = re.findall(r'\d+', text)  
    except IndexError:
        return None
    else:
        numbers = re.findall(r'\d+', text)  
    
    try:
        target_card_number = min(numbers)
        
    except ValueError: 
        return None
    else:
        target_card_number = min(numbers)
        
    try:
        target_set_number = numbers[1]
    except IndexError:
        return None
    else:
        # First number is the collector number
        target_card_number = numbers[0]
        # Second number is the maximum ammount of cards in a booster
        target_set_number = numbers[1]
        
 
    
    if debug==True:
        print(target_card_number, " / ", target_set_number)
    
    # Delete all non sets 
    potential_sets = [i for i in potential_sets if i not in numbers]
    
    potential_set = Levenshtein_txt(potential_sets, target_set_number)
    
    if debug==True:
        print("potential sets: ", potential_set)
        print("extracted card number,", target_card_number)
    return potential_set, target_card_number


###############################################################################
###############################################################################
# 
#   Start of Program
# 
###############################################################################
###############################################################################
def Init_CardIdentifiaction(scryfall_file, roi = "100/300 2x2", debug = True):


    if not os.path.isfile("all_sets.json"):
        update_set_list(debug = False)
    
    
      
    if debug == True:
        print("Check if set exists")
    
    
    

    
    
    if potential_sets == None:
        return None
    
    # for potential_set in potential_sets:
    #     if potential_set.lower() in all_set_names:
    #         if debug == True:
    #             print(f"The three-letter word '{potential_set}' is in the list.")
    #         target_set_name = (potential_set).lower()
    #     else:
    #         print(f"The three-letter word '{potential_set}' is not in the list.")
    #         print("Try again.")
    
    print(potential_sets)
    print(target_card_number)
    
    # if debug == True:
    #     for potential_set in potential_sets:
    #         print(potential_set)
    
    
    # found_cardname= "abc"
    
    # potential_sets = "ori"
    # target_card_number = 79
    # Iterate through the list of dictionaries
    for card_data in scryfall_file:
        # if card_data["set"] == potential_sets and card_data["collector_number"] == "95":
        if card_data["set"] == potential_sets and card_data["collector_number"] == target_card_number.strip("0"):
            found_cardname = card_data["name"]
            print(found_cardname)
            # print("Ho")
            return found_cardname
            
            

    return None
