#%%
import pytesseract
import cv2
import os
import re
import json
from pathlib import Path
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import subprocess





# Configure paths
folder_scryfall_file = Path("./data/Card_Identification/config")
folder_scryfall_file.mkdir(parents=True, exist_ok=True)  # Ensure folder exists
scryfall_url = "https://api.scryfall.com/catalog/card-names"

# Function to fetch Scryfall card names
def fetch_scryfall_cardnames():
    import requests  # Import requests here to keep the dependencies modular
    response = requests.get(scryfall_url)
    response.raise_for_status()
    return response.json()["data"]

# Manage Scryfall card names file
def update_scryfall_cardnames():
    existing_files = list(folder_scryfall_file.glob("scryfall_cardnames_*.json"))
    current_time = datetime.now()

    # Check for existing files
    for file in existing_files:
        match = re.search(r"scryfall_cardnames_(\d+)\.json", file.name)
        if match:
            file_datetime = datetime.strptime(match.group(1), "%Y%m%d%H%M%S")
            if current_time - file_datetime < timedelta(days=7):
                # File is valid and up-to-date
                with file.open("r") as f:
                    return json.load(f)

    # Fetch and save a new file if none is up-to-date
    cardnames = fetch_scryfall_cardnames()
    new_filename = folder_scryfall_file / f"scryfall_cardnames_{current_time.strftime('%Y%m%d%H%M%S')}.json"

    # Remove old files
    for file in existing_files:
        file.unlink()

    # Save the new file
    with new_filename.open("w") as f:
        json.dump(cardnames, f, indent=4)

    return cardnames

scryfall_cardnames = update_scryfall_cardnames()

print("ready")
#%%
pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Update this path if necessary

# Path to the image
path_to_folder = Path("../data/Deck_Identification")
path_to_image = path_to_folder / "IMG_20241001_143530.jpg"

print(path_to_image.resolve())


# Load the image
img_cv = cv2.imread(str(path_to_image))
if img_cv is None:
    raise FileNotFoundError(f"Image not found at {path_to_image}")

# Convert the image to RGB format
img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)

# Use pytesseract to extract text
detected_text = pytesseract.image_to_string(img_rgb, lang="eng")
detected_cardnames = detected_text.split("\n")

# Compare detected card names with Scryfall card names
matched_cardnames = [name for name in detected_cardnames if name.strip() in scryfall_cardnames]

# Plot the results
plt.figure(figsize=(12, 6))

# Original image
plt.subplot(1, 2, 1)
plt.imshow(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))
plt.title("Original Image")
plt.axis("off")

# Annotated image
annotated_img = img_cv.copy()
font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 0.6
font_thickness = 1
color = (0, 255, 0)  # Green text

for idx, name in enumerate(matched_cardnames):
    y_position = 30 + idx * 30
    cv2.putText(annotated_img, name, (10, y_position), font, font_scale, color, font_thickness, cv2.LINE_AA)

plt.subplot(1, 2, 2)
plt.imshow(cv2.cvtColor(annotated_img, cv2.COLOR_BGR2RGB))
plt.title("Annotated Image with Card Names")
plt.axis("off")

# Show the plots
plt.tight_layout()
plt.show()


# %%
