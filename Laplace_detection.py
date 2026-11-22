import argparse
import os
import shutil
import cv2
from imutils import paths


def variance_of_laplacian(image):
    return cv2.Laplacian(image, cv2.CV_64F).var()


# Argument Parser
ap = argparse.ArgumentParser()
ap.add_argument(
    "-i",
    "--images",
    default="/home/go69tuf/Desktop/raw_Data/EPAL_SK_152",
    help="Pfad zum Eingabeordner",
)
ap.add_argument(
    "-t",
    "--threshold",
    type=float,
    default=70.0,
    help="Schwellenwert für Unschärfe",
)
args = vars(ap.parse_args())

# Zielordner definieren
blur_dir = "/home/go69tuf/Desktop/Data_Input/EPAL_SK_152/Blurry"
sharp_dir = "/home/go69tuf/Desktop/Data_Input/EPAL_SK_152/images"

# Zielordner erstellen, falls sie noch nicht existieren
os.makedirs(blur_dir, exist_ok=True)
os.makedirs(sharp_dir, exist_ok=True)



		
# Über alle Bilder iterieren
for imagePath in paths.list_images(args["images"]):
    image = cv2.imread(imagePath)
    if image is None:
        continue

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    fm = variance_of_laplacian(gray)

    filename = os.path.basename(imagePath)

    # Nach Schwellenwert sortieren und verschieben
    if fm < args["threshold"]:
        target_path = os.path.join(blur_dir, filename)
        shutil.move(imagePath, target_path)
        print(f"[UNSCHARF ({fm:.2f})] Verschoben nach Blurry: {filename}")
    else:
        target_path = os.path.join(sharp_dir, filename)
        shutil.move(imagePath, target_path)
        print(f"[SCHARF ({fm:.2f})] Verschoben nach good_images: {filename}")

