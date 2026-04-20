import cv2
import os
import time
import threading
import subprocess
import numpy as np
import sounddevice as sd
import soundfile as sf
from datetime import datetime

from ai.number_plate_detector import detect_number_plates
from ai.plate_ocr import read_plate_text
from ai.face_detection import detect_faces
from ai.emotion_detection import predict_emotion

from alert_system import send_alert_email
from database import (
    init_db,
    log_event,
    log_alert,
    log_plate
)

init_db()

# ==================================================
# GLOBAL USER EMAIL (SET FROM LOGIN)
# ==================================================
current_user_email = None

def set_current_user(email):
    global current_user_email
    current_user_email = email


# ==================================================
# AUDIO DETECTOR
# ==================================================
class AudioDetector:
    def __init__(self, threshold=0.03):
        self.threshold = threshold
        self.sound_detected = False

    def start(self):
        try:
            with sd.InputStream(callback=self.callback):
                while True:
                    time.sleep(0.1)
        except Exception as e:
            print("Audio detector error:", e)

    def callback(self, indata, frames, time_info, status):
        self.sound_detected = np.linalg.norm(indata) > self.threshold


# ==================================================
# AUDIO RECORDER
# ==================================================
class AudioRecorder:
    def __init__(self, samplerate=44100):
        self.samplerate = samplerate
        self.frames = []
        self.recording = False

    def start(self):
        self.frames = []
        self.recording = True
        self.stream = sd.InputStream(
            samplerate=self.samplerate,
            channels=1,
            callback=self.callback
        )
        self.stream.start()

    def callback(self, indata, frames, time_info, status):
        if self.recording:
            self.frames.append(indata.copy())

    def stop(self, filename):
        self.recording = False
        self.stream.stop()
        self.stream.close()
        if self.frames:
            audio = np.concatenate(self.frames, axis=0)
            sf.write(filename, audio, self.samplerate)


# ==================================================
# BACKGROUND THREAT HANDLER (ANTI-FREEZE)
# ==================================================
def handle_threat_async(emotion, frame, email):
    """
    Handles threat logging + email in background
    to prevent camera freeze
    """
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filename = f"{emotion}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"

        os.makedirs("Threat Alert", exist_ok=True)
        threat_path = os.path.join("Threat Alert", filename)

        # Save image
        cv2.imwrite(threat_path, frame)

        # Log in alerts table
        log_alert(timestamp, emotion, threat_path, email)

        # Log in events table
        log_event(timestamp, "THREAT", emotion, None, threat_path)

        # Send email (background)
        if email:
            send_alert_email(email, threat_path, timestamp, emotion)

    except Exception as e:
        print("Threat async error:", e)


# ==================================================
# MAIN SURVEILLANCE
# ==================================================
def start_ai_surveillance():
    print("AI Surveillance Started")

    os.makedirs("plates", exist_ok=True)
    os.makedirs("recordings", exist_ok=True)
    os.makedirs("visitors", exist_ok=True)

    audio_detector = AudioDetector()
    threading.Thread(target=audio_detector.start, daemon=True).start()
    audio_recorder = AudioRecorder()

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Camera not accessible")
        return

    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = None
    recording = False
    last_event_time = 0
    RECORD_DELAY = 5

    last_threat_time = 0
    THREAT_COOLDOWN = 10

    ret, prev_frame = cap.read()
    if not ret:
        return

    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # ==================================================
        # MOTION DETECTION
        # ==================================================
        diff = cv2.absdiff(prev_gray, gray)
        blur = cv2.GaussianBlur(diff, (5, 5), 0)
        _, thresh = cv2.threshold(blur, 25, 255, cv2.THRESH_BINARY)
        motion_detected = cv2.countNonZero(thresh) > 2000

        if motion_detected:
            cv2.putText(frame, "MOTION DETECTED", (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            last_event_time = time.time()

        # ==================================================
        # NUMBER PLATE DETECTION
        # ==================================================
        if motion_detected:
            plates = detect_number_plates(frame)

            for (x, y, w, h) in plates:
                plate_img = frame[y:y+h, x:x+w]
                if plate_img.size == 0:
                    continue

                plate_text = read_plate_text(plate_img)

                if plate_text:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    plate_path = f"plates/{plate_text}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"

                    cv2.imwrite(plate_path, plate_img)

                    log_plate(plate_text, timestamp, plate_path)

        # ==================================================
        # EMOTION DETECTION
        # ==================================================
        emotion_detected = False
        faces, gray_face = detect_faces(frame)

        for (x, y, w, h) in faces:
            face = gray_face[y:y+h, x:x+w]

            try:
                emotion = predict_emotion(face)
            except:
                continue

            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            cv2.putText(frame, emotion, (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            if emotion in ["Angry", "Fear"]:
                emotion_detected = True
                last_event_time = time.time()

                if time.time() - last_threat_time > THREAT_COOLDOWN:
                    last_threat_time = time.time()

                    # Run in background thread
                    threading.Thread(
                        target=handle_threat_async,
                        args=(emotion, frame.copy(), current_user_email),
                        daemon=True
                    ).start()

        # ==================================================
        # RECORDING LOGIC
        # ==================================================
        if motion_detected or emotion_detected:
            if not recording:
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                video_file = f"recordings/video_{ts}.avi"
                audio_file = f"recordings/audio_{ts}.wav"
                final_file = f"recordings/event_{ts}.mp4"

                out = cv2.VideoWriter(video_file, fourcc, 20.0, (640, 480))
                audio_recorder.start()
                recording = True

                log_event(
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "RECORDING",
                    "Triggered",
                    video_file,
                    None
                )

        if recording:
            out.write(frame)

            if time.time() - last_event_time > RECORD_DELAY:
                recording = False
                out.release()
                audio_recorder.stop(audio_file)

                subprocess.run([
                    "ffmpeg", "-y",
                    "-i", video_file,
                    "-i", audio_file,
                    "-c:v", "copy",
                    "-c:a", "aac",
                    final_file
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                if os.path.exists(video_file):
                    os.remove(video_file)
                if os.path.exists(audio_file):
                    os.remove(audio_file)

        cv2.imshow("Smart AI CCTV", frame)
        prev_gray = gray

        if cv2.waitKey(1) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()