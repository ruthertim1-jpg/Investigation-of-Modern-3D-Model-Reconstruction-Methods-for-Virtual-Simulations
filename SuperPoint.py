import argparse
import os
import shutil
import cv2
import torch
import pyiqa
from imutils import paths

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
    default=3.5,  # KI-Skala (Mean Opinion Score) geht von ca. 1.0 (sehr schlecht/unscharf) bis 5.0 (perfekt scharf)
    help="Schwellenwert für Unschärfe (KI-Skala 1-5)",
)
args = vars(ap.parse_args())

# Zielordner definieren
blur_dir = "/home/go69tuf/Desktop/Data_Input/EPAL_3_9/Blurry"
sharp_dir = "/home/go69tuf/Desktop/Data_Input/EPAL_3_9/images"

# Zielordner erstellen, falls sie noch nicht existieren
os.makedirs(blur_dir, exist_ok=True)
os.makedirs(sharp_dir, exist_ok=True)

# 1. Prüfen, ob eine Grafikkarte (GPU) verfügbar ist, sonst CPU nutzen
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"[INFO] Nutze Gerät: {device}")

# 2. Vortrainiertes KI-Modell einmalig VOR der Schleife laden
print("[INFO] Lade KI-Modell (DBCNN)...")
model = pyiqa.create_metric('dbcnn_mos').to(device)

# Über alle Bilder iterieren
for imagePath in paths.list_images(args["images"]):
    # Sicherheitscheck, ob die Datei existiert/lesbar ist
    if not os.path.exists(imagePath):
        continue

    # 3. KI-Bewertung durchführen
    try:
        with torch.no_grad(): # Schaltet das Lernen aus, spart enorm Speicher und Zeit
            score_tensor = model(imagePath)
            fm = score_tensor.item() # Konvertiert das PyTorch-Ergebnis in eine normale Fließkommazahl
    except Exception as e:
        print(f"[FEHLER] Konnte {imagePath} nicht verarbeiten. Grund: {e}")
        continue

    filename = os.path.basename(imagePath)

    # Nach Schwellenwert sortieren und verschieben
    # Da die KI bei Unschärfe ebenfalls kleinere Werte liefert, bleibt deine Logik gleich!
    if fm < args["threshold"]:
        target_path = os.path.join(blur_dir, filename)
        shutil.move(imagePath, target_path)
        print(f"[UNSCHARF ({fm:.2f})] Verschoben nach Blurry: {filename}")
    else:
        target_path = os.path.join(sharp_dir, filename)
        shutil.move(imagePath, target_path)
        print(f"[SCHARF ({fm:.2f})] Verschoben nach images: {filename}")
