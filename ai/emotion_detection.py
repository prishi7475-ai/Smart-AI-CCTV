import cv2
import numpy as np
from ai.emotion_model import emotion_model, emotions

def predict_emotion(face_img):
    face_img = cv2.resize(face_img, (48, 48))
    face_img = face_img.astype("float32") / 255.0
    face_img = np.reshape(face_img, (1, 48, 48, 1))

    preds = emotion_model.predict(face_img, verbose=0)
    return emotions[np.argmax(preds)]
