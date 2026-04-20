import os
import sys
from tensorflow.keras.models import load_model


def resource_path(relative_path):
    """
    Get absolute path to resource.
    Works for development and for PyInstaller EXE.
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def load_emotion_model():
    model_path = resource_path(os.path.join("models", "emotion_model.h5"))

    model = load_model(
        model_path,
        compile=False
    )

    # FORCE correct input shape (FER2013)
    model.build((None, 48, 48, 1))
    return model


emotion_model = load_emotion_model()

emotions = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']
