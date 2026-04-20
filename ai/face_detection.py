import cv2
import os
import sys


def resource_path(relative_path):
    """
    Get absolute path to resource.
    Works for both development and PyInstaller EXE.
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# Load Haar Cascade safely
cascade_path = resource_path(
    os.path.join("models", "haarcascade_frontalface_default.xml")
)

face_cascade = cv2.CascadeClassifier(cascade_path)

if face_cascade.empty():
    raise RuntimeError(
        f"❌ Failed to load Haar cascade from {cascade_path}"
    )


def detect_faces(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.3,
        minNeighbors=5,
        minSize=(30, 30)
    )
    return faces, gray