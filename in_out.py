import cv2
import os
from datetime import datetime

def in_out():
    cap = cv2.VideoCapture(0)
    entry_dir = "visitors/in"
    exit_dir = "visitors/out"
    os.makedirs(entry_dir, exist_ok=True)
    os.makedirs(exit_dir, exist_ok=True)

    ret, frame1 = cap.read()
    ret, frame2 = cap.read()

    entry_logged = False
    exit_logged = False

    while cap.isOpened():
        diff = cv2.absdiff(frame1, frame2)
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5,5), 0)
        _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
        dilated = cv2.dilate(thresh, None, iterations=3)
        contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        height, width = frame1.shape[:2]
        mid = width // 2

        for contour in contours:
            if cv2.contourArea(contour) < 2500:
                continue
            x, y, w, h = cv2.boundingRect(contour)
            center_x = x + w // 2

            if center_x < mid and not exit_logged:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{exit_dir}/out_{timestamp}.jpg"
                cv2.imwrite(filename, frame1)
                print(f"[EXIT] {filename}")
                exit_logged = True

            elif center_x > mid and not entry_logged:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{entry_dir}/in_{timestamp}.jpg"
                cv2.imwrite(filename, frame1)
                print(f"[ENTRY] {filename}")
                entry_logged = True

        if entry_logged and exit_logged:
            entry_logged = False
            exit_logged = False

        cv2.line(frame1, (mid, 0), (mid, height), (255, 0, 0), 2)
        cv2.imshow("In-Out Detection", frame1)

        frame1 = frame2
        ret, frame2 = cap.read()

        if not ret or cv2.waitKey(10) == 27:  # ESC to exit
            break

    cap.release()
    cv2.destroyAllWindows()