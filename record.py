import cv2
from datetime import datetime
import os

def record():
    # Create recordings directory if not exists
    os.makedirs('recordings', exist_ok=True)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Error: Could not open camera.")
        return

    # Set video codec and output file
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    filename = f'recordings/{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.avi'
    out = cv2.VideoWriter(filename, fourcc, 20.0, (640, 480))

    print(f"🎥 Recording started. Saving to {filename}")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("⚠️ Failed to grab frame.")
                break

            # Add timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(frame, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, (255, 255, 255), 2)

            # Show and save the frame
            cv2.imshow("Press ESC to stop", frame)
            out.write(frame)

            # Exit on ESC key
            if cv2.waitKey(1) == 27:
                print("🛑 ESC pressed. Stopping recording.")
                break

    except KeyboardInterrupt:
        print("\n⛔ Recording interrupted manually.")
    
    finally:
        # Release everything safely
        cap.release()
        out.release()
        cv2.destroyAllWindows()
        print("✅ Resources released. Recording finished.")