import sounddevice as sd
import soundfile as sf
import numpy as np

class AudioRecorder:
    def __init__(self, samplerate=44100):
        self.samplerate = samplerate
        self.recording = False
        self.frames = []

    def start(self):
        self.frames = []
        self.recording = True
        self.stream = sd.InputStream(
            samplerate=self.samplerate,
            channels=1,
            callback=self.callback
        )
        self.stream.start()

    def callback(self, indata, frames, time, status):
        if self.recording:
            self.frames.append(indata.copy())

    def stop(self, filename):
        self.recording = False
        self.stream.stop()
        self.stream.close()
        audio = np.concatenate(self.frames, axis=0)
        sf.write(filename, audio, self.samplerate)
