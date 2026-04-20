import sounddevice as sd
import numpy as np
import time

class AudioDetector:
    def __init__(self, threshold=0.03):
        self.threshold = threshold
        self.sound_detected = False

    def start(self):
        with sd.InputStream(callback=self.audio_callback):
            while True:
                time.sleep(0.1)

    def audio_callback(self, indata, frames, time_info, status):
        volume = np.linalg.norm(indata)
        if volume > self.threshold:
            self.sound_detected = True
        else:
            self.sound_detected = False
