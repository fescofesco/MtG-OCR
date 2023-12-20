# -*- coding: utf-8 -*-
"""
Created on Wed Dec 13 20:42:50 2023

@author: unisp

img_from_adb.py

main function is transfer_images_from_device()

 transfers images from the android device from subfodler MTG-OCR 
 and stores them in the subfolder /Img Storage for further processing with
 identify_card from card_identification.py
 

"""
import subprocess
import os


def transfer_images_from_device(source_folder="MTG-OCR", 
                    destination_subfolder="Img Storage", verbose = 0):
    """
    transfers images from the android device from subfodler MTG-OCR 
    and stores them in the subfolder /Img Storage for further processing with
    identify_card from card_identification.py

##############################################################################
# install adb
# https://www.xda-developers.com/install-adb-windows-macos-linux/
# set adb to path 
# https://www.incredigeek.com/home/add-adb-to-windows-environment-variables/
# wireless debugging
# https://developer.android.com/tools/adb
##############################################################################

    Parameters
    ----------
    source_folder : STR, optional
            seraches the device for a folder that contains
            the images to be transferred to working directory, attention
            dont use normal DCIM because the function clears all images of the 
            specified folder in the process. The default is "MTG-OCR".
        
    destination_subfolder : TYPE, optional
        destination_subfolder="Img Storage": the folder the function sends the
            images to. The default is "Img Storage".
        
     verbose : TYPE, optional
         DESCRIPTION. The default is 0.

    Returns
    -------
    None
        No output but files get transferred.

    """
    # Check if the device is connected
    if not is_device_connected():
        print("img_fom_adb.py: transfer_images_form_device()")
        print("Device is not connected.")
        return None

    # ADB command to search for the source folder on the device
    adb_command = f"adb shell find /sdcard/ -type d -name '{source_folder}'"

    # Execute the ADB command and capture the output
    result = subprocess.run(adb_command, shell=True,
                            capture_output=True, text=True)

    # Check if the command was successful and process the output
    if result.returncode == 0:
        output = result.stdout.strip()
        if output and verbose > 0:
            print(f"Folder '{source_folder}' found at:")
            print(output)
        else:
            print(f"Folder '{source_folder}' not found on the device.")
            return  # Exit the function if source folder not found
    else:
        print("Error executing the ADB command.")
        return  # Exit the function if ADB command fails

    source_directory = output

    # Use ADB to list all .jpg files on the Android device
    list_command = f"adb shell find '{source_directory}' -name '*.jpg'"
    file_list = subprocess.check_output(list_command, \
                                shell=True, text=True).strip().splitlines()

    # Filter out empty strings from the file list
    file_list = [file_path for file_path in file_list if file_path]

    if verbose > 0:
        print("File list:", file_list)

    # Create the destination subfolder if it doesn't exist
    destination_directory = os.path.join(os.getcwd(), destination_subfolder)
    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)

    # Transfer images from the Android device to your computer
    for file_path in file_list:
        file_name = os.path.basename(file_path)
        destination_file = os.path.join(destination_directory, file_name)

        # Pull the images from the Android device to the computer
        pull_command = f"adb pull '{file_path}' '{destination_file}'"
        subprocess.run(pull_command, shell=True)

        # Remove each image from the Android device after successful transfer
        if os.path.exists(destination_file):
            remove_command = f"adb shell rm '{file_path}'"
            subprocess.run(remove_command, shell=True)

    if verbose > 0:
        print("Images transferred from the Android device",
              " and removed from the device.")

def is_device_connected():
    """
    checks if device is connected before stratin adb, used by 
    transfer_images_from_device()

    Returns
    
    -------
    TYPE
        DESCRIPTION.
    
    False if no device conneected -> Adb COMMAND failed

    """
    # ADB command to check devices connected
    adb_command = "adb devices"

    # Execute the ADB command and capture the output
    result = subprocess.run(adb_command, shell=True,
                            capture_output=True, text=True)

    # Check if the command was successful and process the output
    if result.returncode == 0:
        output = result.stdout.strip().splitlines()

        # Check if there are connected devices except the header
        return len(output) > 1
    else:
        return False  # ADB command failed, assuming device is not connected



# Example usage of the function
if __name__ == "__main__":
    transfer_images_from_device()
    
    transfer_images_from_device(source_folder="MTG-OCR", 
                        destination_subfolder="Img Storage",
                                verbose = 1)
