import argparse
import os
import shutil
import cv2
import numpy as np
from imutils import paths


def variance_of_fft(image, size=60):
    """Berechnet den Schärfewert eines Graustufenbildes mittels FFT."""
    h, w = image.shape
    cX, cY = int(w / 2.0), int(h / 2.0)

    # FFT berechnen und den Nullpunkt (tiefe Frequenzen) in die Mitte schieben
    fft = np.fft.fft2(image)
    fft_shifted = np.fft.fftshift(fft)

    # Den zentralen Bereich (niedrige Frequenzen/Flächen) auf Null setzen
    fft_shifted[cY - size : cY + size, cX - size : cX + size] = 0

    # Rücktransformation in den Raumbereich
    fft_ishift = np.fft.ifftshift(fft_shifted)
    recon = np.fft.ifft2(fft_ishift)

    # Magnitude berechnen und den Mittelwert als Schärfewert zurückgeben
    magnitude = 20 * np.log(np.abs(recon) + 1)
    return np.mean(magnitude)


# Argument Parser
ap = argparse.ArgumentParser()
ap.add_argument(
    "-i",
    "--images",
    default="/home/go69tuf/Desktop/raw_Data/EPAL_3_9",
    help="Pfad zum Eingabeordner",
)
ap.add_argument(
    "-t",
    "--threshold",
    type=float,
    default=37.0,  # Wichtig: FFT-Werte nutzen eine andere Skala als Laplace!
    help="Schwellenwert für Unschärfe (FFT-Skala)",
)
args = vars(ap.parse_args())

# Zielordner definieren
blur_dir = "/home/go69tuf/Desktop/Data_Input/EPAL_3_9/Blurry"
sharp_dir = "/home/go69tuf/Desktop/Data_Input/EPAL_3_9/images"

# Zielordner erstellen, falls sie noch nicht existieren
os.makedirs(blur_dir, exist_ok=True)
os.makedirs(sharp_dir, exist_ok=True)

# Über alle Bilder iterieren
for imagePath in paths.list_images(args["images"]):
    image = cv2.imread(imagePath)
    if image is None:
        continue

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # HIER JETZT FFT STATT LAPLACE
    fm = variance_of_fft(gray)

    filename = os.path.basename(imagePath)

    # Nach Schwellenwert sortieren und verschieben
    # (Da FFT-Werte bei Unschärfe ebenfalls kleiner werden, bleibt die Logik identisch)
    if fm < args["threshold"]:
        target_path = os.path.join(blur_dir, filename)
        shutil.move(imagePath, target_path)
        print(f"[UNSCHARF ({fm:.2f})] Verschoben nach Blurry: {filename}")
    else:
        target_path = os.path.join(sharp_dir, filename)
        shutil.move(imagePath, target_path)
        print(f"[SCHARF ({fm:.2f})] Verschoben nach images: {filename}")
