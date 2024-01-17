# -*- coding: utf-8 -*-
"""
%(filename)
${file}
Created on %(date)s

author: Felix Scope
"""


import shutil
from datetime import datetime
from tkinter import Tk, filedialog
import os
from src.Card_Identification.path_manager import (get_path, PathType)


def select_and_copy_images_to_data(path=None, verbose=0):
    # Print the instruction message
    print("Specify the Folder where the images are you want to get the Cardname & expansion symbol from.")
    print("Note, only one full card per image.")

    if path = None:
        path = PathType.RAW_IMAGE
    
    # Ask the user to select a folder containing images
    root = Tk()
    root.withdraw()  # Hide the main window
    folder_path = filedialog.askdirectory(title="Select Folder with Images")

    if not folder_path:
        print("No folder selected. Exiting.")
        root.destroy()  # Close the Tkinter window
        return

    # Specify the destination directory for copied images
    destination_directory = get_path(path)

    # Ensure the destination directory exists
    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)

    # Get the current datetime as a string (formatted)
    current_datetime_str = datetime.now().strftime("%Y%m%d%H%M%S")

    # List all files in the selected folder
    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    if not image_files:
        print("No image files found in the selected folder. Exiting.")
        root.destroy()  # Close the Tkinter window
        return

    # Create a subfolder using the current datetime
    subfolder_name = f"Images_{current_datetime_str}"
    subfolder_path = os.path.join(destination_directory, subfolder_name)

    if not os.path.exists(subfolder_path):
        os.makedirs(subfolder_path)

    # Move each existing image file in the destination directory to the subfolder
    for existing_image_file in os.listdir(destination_directory):
        if existing_image_file.lower().endswith(('.png', '.jpg', '.jpeg')):
            existing_source_path = os.path.join(destination_directory, existing_image_file)
            existing_destination_path = os.path.join(subfolder_path, existing_image_file)

            try:
                shutil.move(existing_source_path, existing_destination_path)
                print(f"Existing image '{existing_image_file}' moved to subfolder '{subfolder_name}'.")
            except Exception as e:
                print(f"Error moving existing image '{existing_image_file}': {e}")

    # Copy each new image file to the destination directory
    for image_file in image_files:
        source_path = os.path.join(folder_path, image_file)
        destination_path = os.path.join(destination_directory, image_file)

        try:
            shutil.copy2(source_path, destination_path)
            if verbose >2: print(f"Image '{image_file}' copied to '{destination_directory}'.")
        except Exception as e:
            print(f"Error copying '{image_file}': {e}")

    if verbose >1: print("Copying process completed.")
    
    root.destroy()  # Close the Tkinter window


if __name__ = '__main__':
        
    # Example usage
    select_and_copy_images()
    
    
    destination_directory = get_path(PathType.RAW_IMAGE)