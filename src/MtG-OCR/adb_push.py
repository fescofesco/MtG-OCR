# -*- coding: utf-8 -*-
"""
Created on Wed Dec 13 20:22:26 2023

@author: unisp
"""

##############################################################################
# install adb
# https://www.xda-developers.com/install-adb-windows-macos-linux/
# set adb to path 
# https://www.incredigeek.com/home/add-adb-to-windows-environment-variables/
# wireless debugging
# https://developer.android.com/tools/adb
##############################################################################


import subprocess
import os


verbose = 1
    

# Set the source and destination directories
source_directory = "/storage/sdcard0/DCIM/Camera/OpenCamera"
filename = source_directory + "/1.jpg"
print(filename)

# Get the current working directory
current_directory = os.getcwd()

# Name of the new directory
directory_name = "Open Camera"

# Path for the new directory
destination_directory = os.path.join(current_directory, directory_name)


# Check if the directory already exists, if not, create it
if not os.path.exists(destination_directory):
    os.makedirs(destination_directory)
    if verbose > 0:
        print(f"Directory '{directory_name}' created successfully at: {destination_directory}")
else:
    if verbose > 0:
        print(f"Directory '{directory_name}' already exists at: {destination_directory}")


# Set the source and destination directories
source_directory = "/storage/sdcard0/DCIM/Camera/OpenCamera"




# Use ADB to list and pull all .jpg files
list_command = f"adb shell find {source_directory} -name '*.jpg'"


# Start the ADB server
adb_start_command = "adb start-server"
subprocess.run(adb_start_command, shell=True)


# Use ADB to list and pull all .jpg files
list_command = f"adb shell find {source_directory} -name '*.jpg'"
file_list = subprocess.check_output(list_command, shell=True, text=True).strip().split('\n')
print("filelist", file_list)



for file_path in file_list:
    # Extract the filename from the full path
    file_name = file_path.split("/")[-1]
    print("name: ", file_name)
    destination_path = f"{destination_directory}\{file_name}"
  
    print("dpath: ", destination_path)
    
    # Use ADB to pull the file from the phone to the computer
    pull_command = f"adb pull {file_path} {destination_path}"
    subprocess.run(pull_command, shell=True)
    
    
# adb pull /storage/sdcard0/DCIM/Camera/OpenCamera/IMG_20231104_141255.jpg C:/Users/unisp/Documents/Infoprojekte/

  # destination_path = f"{destination_directory}"

"""
# destination_directory = "C:/Users/unisp/Documents/Infoprojekte/Textrecogintion from webcam_ChatGPT/OpenCamera"
# destination_directory = "C:/Users/unisp/Documents/Infoprojekte/Textrecogintion from webcam_ChatGPT"

# d_filename = destination_directory + "/1.jpg"
d_filename = destination_directory + "/2.jpg"

#"/path/to/destination/directory/on/your/computer"

# # Use ADB to copy files from the phone to your computer
command = f"adb pull {source_directory} {destination_directory}"
command = f"adb pull {filename} {d_filename}"

subprocess.run(command, shell=True)
list_command = f"adb shell find {destination_directory} -name '*.jpg'"
print(list_command)

print("done")

"""